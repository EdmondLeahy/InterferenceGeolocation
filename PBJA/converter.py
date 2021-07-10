import os
import pandas as pd
import numpy as np
import logging

POS_FILENAME = 'BESTPOS'
SPKL_FILENAME = 'SPRINKLERDATA'

ELLIPSE_A = 6378137.0
ELLIPSE_E_SQ = 0.0066943799901413165

_logger = logging.getLogger(__name__)


def ecef_to_enu(ecef, geodetic_0):
    """ECEF to ENU

    Convert ECEF x, y, z to ENU e, n, u about geodetic_0 lat_0, long_0, height_0.

    height_0 must be ellipsoidal height.

    Args:
        ecef (list of float): ECEF coordinate in form [x, y, z]
        geodetic_0 (list of float): Geodetic coordinate in
            form [lat_0, long_0, height_0] about which to calculate ENU

    Returns:
        (tuple of float): ENU w.r.t geodetic_0 in
            form (easting, northing, up)

    STOLEN FROM NOVATEL_COORDINATES.TRANSFORMATIONS!

    """

    x = ecef[0]
    y = ecef[1]
    z = ecef[2]

    lat0 = geodetic_0[0]
    lon0 = geodetic_0[1]

    lam = np.radians(lat0)  # Latitude in Radians
    phi = np.radians(lon0)  # Longitude in Radians

    sin_lambda = np.sin(lam)
    cos_lambda = np.cos(lam)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    ecef_0 = geodetic_to_ecef(geodetic_0)
    xd = x - ecef_0[0]
    yd = y - ecef_0[1]
    zd = z - ecef_0[2]

    n = -cos_phi * sin_lambda * xd - sin_lambda * sin_phi * yd + cos_lambda * zd
    e = -sin_phi * xd + cos_phi * yd
    u = cos_lambda * cos_phi * xd + cos_lambda * sin_phi * yd + sin_lambda * zd

    # account for Pandas series, and np float typecasting
    e = float(e) if type(e) == np.float64 else e
    n = float(n) if type(n) == np.float64 else n
    u = float(u) if type(u) == np.float64 else u

    return e, n, u


def geodetic_to_ecef(geodetic):
    """Geodetic to ECEF. Convert Geodetic lat, long, height to ECEF x, y ,z.

    Note: Height must be ellipsoidal height

    Args:
        geodetic (list of float): Geodetic coordinate in form [lat, long, height]


    Returns:
        (tuple of float): ECEF coordinate in form (x, y, z)

    STOLEN FROM NOVATEL_COORDINATES.TRANSFORMATIONS!

    """

    lat = geodetic[0]
    lon = geodetic[1]
    h = geodetic[2]

    lam = np.radians(lat)  # Latitude in Radians
    phi = np.radians(lon)  # Longitude in Radians
    s = np.sin(lam)
    n = ELLIPSE_A / np.sqrt(1 - ELLIPSE_E_SQ * s * s)

    sin_lambda = np.sin(lam)
    cos_lambda = np.cos(lam)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    x = (h + n) * cos_lambda * cos_phi
    y = (h + n) * cos_lambda * sin_phi
    z = (h + (1 - ELLIPSE_E_SQ) * n) * sin_lambda

    return x, y, z


def geodetic_to_enu(geodetic, geodetic_0):
    """Geodetic To ENU

    Convert Geodetic lat, long, height to ENU e, n, u about geodetic_0 lat_0, long_0, height_0.

    Heights must be ellipsoidal heights.

    Args:
        geodetic (list of float): Geodetic coordinate in form [lat, long, height]
        geodetic_0 (list of float): Geodetic coordinate in
            form [lat_0, long_0, height_0] about which to calculate ENU

    Returns:
        (tuple of float): ENU w.r.t geodetic_0 in
            form (easting, northing, up)


    STOLEN FROM NOVATEL_COORDINATES.TRANSFORMATIONS!


    """
    ecef = geodetic_to_ecef(geodetic)
    enu = ecef_to_enu(list(ecef), geodetic_0)
    return enu


def convert_to_enu(row, expansion):
    enu = geodetic_to_enu([float(row['Lat']), float(row['Long']), float(row['Height'])], expansion)
    return enu


def get_series_from_log(log):
    """ Function to return a series from an individual sprinkler log """
    series = [int(dat) for dat in log[12:-1]]
    return series


def make_obs_arrays(pos_log_filename, sprinkler_log_filename, fine_filt=True, pos_filt_status=None):
    with open(pos_log_filename) as bestpos_file:
        _logger.info(f'Reading {pos_log_filename}')
        bestpos_data = bestpos_file.readlines()

    with open(sprinkler_log_filename) as sprinkler_file:
        _logger.info(f'Reading {sprinkler_log_filename}')
        sprinkler_data = sprinkler_file.readlines()

    pre_df_bestpos_data = [n.split(',') for n in bestpos_data]
    pre_df_sprinkler_data = [n.split(',') for n in sprinkler_data]

    # sprinkler processing
    _logger.info('Processing sprinkler data')
    arr_heads = [[t[5], t[6], t[11]] for t in pre_df_sprinkler_data]
    payload = [get_series_from_log(t) for t in pre_df_sprinkler_data]
    sprinkler_df = pd.DataFrame(arr_heads)
    sprinkler_df = sprinkler_df.apply(pd.to_numeric)
    sprinkler_df.columns = ['Week', 'Second', 'NumObs']
    sprinkler_df['Data'] = payload
    sprinkler_df = sprinkler_df.set_index('Second')

    # Bestpos processing
    _logger.info('Processing position data')
    bestpos_df = pd.DataFrame(pre_df_bestpos_data)
    if fine_filt:
        bestpos_df = bestpos_df[bestpos_df[4] == 'FINESTEERING']
    if pos_filt_status:
        bestpos_df = bestpos_df[bestpos_df[10] == pos_filt_status]
    else:
        bestpos_df = bestpos_df[bestpos_df[10] != 'UNKNOWN']

    pos_df = bestpos_df[[5, 6, 11, 12, 13]]
    pos_df.columns = ['Week', 'GPSTime', 'Lat', 'Long', 'Height']
    pos_df = pos_df.apply(pd.to_numeric)
    pos_df = pos_df.set_index('GPSTime')

    # sprklr_df = sprinkler_df.drop([0, 1, 2, 3, 4, 7, 8, 9, 1035], axis=1)

    # sprklr_df = sprklr_df.set_index(6)

    _logger.info('Merging position and sprinkler data')
    merged_df = pd.merge(pos_df, sprinkler_df, left_index=True, right_index=True)

    expansion = [float(merged_df['Lat'].iloc[0]),
                 float(merged_df['Long'].iloc[0]),
                 float(merged_df['Height'].iloc[0])]

    _logger.info('Adding ENU data')
    enu_added_df = add_enu(merged_df, expansion)

    ret_df = enu_added_df.reset_index().rename(columns={'index': 'Second', 'Week_y': 'Week'}).drop('Week_x', axis=1)

    return ret_df[['Second', 'Week', 'Lat', 'Long', 'Height',  'NumObs', 'Data', 'E', 'N', 'U']]  # Just to reorder


def add_enu(merged_df, expansion):
    # Convert to ENU
    merged_df['E'] = merged_df.apply(lambda row: convert_to_enu(row, expansion)[0], axis=1)
    merged_df['N'] = merged_df.apply(lambda row: convert_to_enu(row, expansion)[1], axis=1)
    merged_df['U'] = merged_df.apply(lambda row: convert_to_enu(row, expansion)[2], axis=1)

    return merged_df


def parse_input_files(filepath):
    sprinkler_files = []
    pos_files = []

    obs_arrays = []
    for filename in set([f for f in os.listdir(filepath) if '.GPS' in f]):

        if POS_FILENAME in filename:
            pos_files.append(filename)
        elif SPKL_FILENAME in filename:
            sprinkler_files.append(filename)

    if len(sprinkler_files) == 0 or len(pos_files) == 0:
        raise UserWarning('Cant find the observation files. Please use Nconvert to split the files, and ensure that the'
                          'BESTPOS and SPRINKLERDATA files are in the given folder.')

    for sp_dat_file in sprinkler_files:

        pos_dat_file = [f for f in pos_files if sp_dat_file.split('.')[0] in f][0]
        full_sp_file_path = os.path.join(filepath, sp_dat_file)
        full_pos_file_path = os.path.join(filepath, pos_dat_file)
        obs_arrays.append(make_obs_arrays(full_pos_file_path, full_sp_file_path))

    return obs_arrays
