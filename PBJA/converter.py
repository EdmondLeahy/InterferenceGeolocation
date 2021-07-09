import os
import pandas as pd

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


def convert_to_ENU(row, expansion):
    enu = geodetic_to_enu(expansion, (float(row['Lat']), float(row['Long']), float(row['Height'])))
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

    return merged_df


def add_ENU(merged_df, expansion):
    # Convert to ENU
    merged_df['E'] = merged_df.apply(lambda row: convert_to_ENU(row, expansion)[0], axis=1)
    merged_df['N'] = merged_df.apply(lambda row: convert_to_ENU(row, expansion)[1], axis=1)
    merged_df['U'] = merged_df.apply(lambda row: convert_to_ENU(row, expansion)[2], axis=1)

    return merged_df

def run_nconvert(filename):
    pass

def parse_imput_files(filepath):

    for filename in os.listdir(filepath):
        if '.GPS' not in filename:
            continue

        # Run nconvert to split
        run_nconvert(filename)

        # Check for pos file:
        pos_ascii_file = filename + '.' + POS_FILENAME
        if not os.path.exists(pos_ascii_file):
            raise UserWarning(f'No {POS_FILENAME} file found. Is it in the dataset?')

        # Check for pos file:
        spkl_ascii_file = filename + '.' + SPKL_FILENAME
        if not os.path.exists(spkl_ascii_file):
            raise UserWarning(f'No {SPKL_FILENAME} file found. Is it in the dataset?')

        make_obs_arrays(pos_ascii_file, spkl_ascii_file)

