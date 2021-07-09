import os
import pandas as pd
import np

POS_FILENAME = 'BESTPOS'
SPKL_FILENAME = 'SPRINKLERDATA'


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


def geodetic_to_ecef(geodetic, datum=DATUMS['WGS84']):
    """Geodetic to ECEF. Convert Geodetic lat, long, height to ECEF x, y ,z.

    Note: Height must be ellipsoidal height

    Args:
        geodetic (list of float): Geodetic coordinate in form [lat, long, height]
        datum (:obj:`Datum`): Datum(ellipsoid) to use for conversion constants (defaults to WGS84)

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
    n = datum.ellipsoid.a / np.sqrt(1 - datum.ellipsoid.e_sq * s * s)

    sin_lambda = np.sin(lam)
    cos_lambda = np.cos(lam)
    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    x = (h + n) * cos_lambda * cos_phi
    y = (h + n) * cos_lambda * sin_phi
    z = (h + (1 - datum.ellipsoid.e_sq) * n) * sin_lambda

    return x, y, z


def geodetic_to_enu(geodetic, geodetic_0, datum=DATUMS['WGS84']):
    """Geodetic To ENU

    Convert Geodetic lat, long, height to ENU e, n, u about geodetic_0 lat_0, long_0, height_0.

    Heights must be ellipsoidal heights.

    Args:
        geodetic (list of float): Geodetic coordinate in form [lat, long, height]
        geodetic_0 (list of float): Geodetic coordinate in
            form [lat_0, long_0, height_0] about which to calculate ENU
        datum (:obj:`Datum`): Datum(ellipsoid) to use for conversion constants (defaults to WGS84)

    Returns:
        (tuple of float): ENU w.r.t geodetic_0 in
            form (easting, northing, up)


    STOLEN FROM NOVATEL_COORDINATES.TRANSFORMATIONS!


    """
    ecef = geodetic_to_ecef(geodetic, datum=datum)
    enu = ecef_to_enu(list(ecef), geodetic_0)
    return enu


def convert_to_ENU(row, expansion):
    enu = geodetic_to_enu([float(row['Lat']), float(row['Long']), float(row['Height'])], expansion)
    return enu


def make_obs_arrays(pos_log_filename, sprinkler_log_filename):
    with open(pos_log_filename) as bestpos_file:
        bestpos_data = bestpos_file.readlines()

    with open(sprinkler_log_filename) as sprinkler_file:
        sprinkler_data = sprinkler_file.readlines()

    pre_df_bestpos_data = [n.split(',') for n in bestpos_data]
    pre_df_sprinkler_data = [n.split(',') for n in sprinkler_data]

    bestpos_df = pd.DataFrame(pre_df_bestpos_data)
    sprinkler_df = pd.DataFrame(pre_df_sprinkler_data)

    pos_df = bestpos_df[[5, 6, 11, 12, 13]]
    pos_df.columns = ['Week', 'GPSTime', 'Lat', 'Long', 'Height']
    pos_df = pos_df.set_index('GPSTime')

    sprklr_df = sprinkler_df.drop([0, 1, 2, 3, 4, 7, 8, 9, 1035], axis=1)
    sprklr_df = sprklr_df.set_index(6)

    merged_df = pd.merge(pos_df, sprklr_df, left_index=True, right_index=True)

    expansion = [float(merged_df['Lat'][0]),
                 float(merged_df['Long'][0]),
                 float(merged_df['Height'][0])]

    enu_added_df = add_ENU(merged_df, expansion)

    return enu_added_df


def add_ENU(merged_df, expansion):
    # Convert to ENU
    merged_df['E'] = merged_df.apply(lambda row: convert_to_ENU(row, expansion)[0], axis=1)
    merged_df['N'] = merged_df.apply(lambda row: convert_to_ENU(row, expansion)[1], axis=1)
    merged_df['U'] = merged_df.apply(lambda row: convert_to_ENU(row, expansion)[2], axis=1)

    return merged_df


def run_nconvert(filename):
    raise NotImplementedError('Need to spawn Nconvert here')

def parse_input_files(filepath):
    obs_arrays = []
    for filename in [f for f in os.listdir(filepath) if '.GPS' in f]:
        pos_ascii_file = filename + '.' + POS_FILENAME
        spkl_ascii_file = filename + '.' + SPKL_FILENAME
        base_name = os.path.basename(filename).replace('.GPS', '')

        # check if need to run nconvert:
        if not os.path.exists(pos_ascii_file) or not os.path.exists(spkl_ascii_file):
            # Run nconvert to split
            run_nconvert(filename)

            # Check for pos file:
            if not os.path.exists(pos_ascii_file):
                raise UserWarning(f'No {POS_FILENAME} file found. Is it in the dataset?')

            # Check for pos file:
            if not os.path.exists(spkl_ascii_file):
                raise UserWarning(f'No {SPKL_FILENAME} file found. Is it in the dataset?')

        obs_arrays.append(make_obs_arrays(pos_ascii_file, spkl_ascii_file))

    return obs_arrays