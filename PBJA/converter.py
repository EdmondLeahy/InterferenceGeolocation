import os
import pandas as pd

POS_FILENAME = 'BESTPOS'
SPKL_FILENAME = 'SPRINKLERDATA'

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
    raise NotImplementedError('Need to spawn Nconvert here')


def parse_imput_files(filepath):
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