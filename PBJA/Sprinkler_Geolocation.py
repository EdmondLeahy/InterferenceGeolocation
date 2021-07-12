import time
import argparse
import sys
import logging

# Python Package Imports
import os
import numpy as np
import scipy.fftpack as fft
import numpy.random as rnd
import random
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd

# Local imports
from Sprinkler_LeastSquares import SprinklerLS
from converter import parse_input_files
from sprinkler_functions import *


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('PHJA_logger')
# _logger.setLevel(logging.DEBUG)


def get_epoch_set(lst_data_obs, all_viewed=False):
    sets = []
    for obs_df in lst_data_obs:
        s_new = list(obs_df['Second'])
        w_new = list(obs_df['Week'])
        eps = [Epoch(e[0], e[1]) for e in list(zip(w_new, s_new))]
        sets.append(set(eps))

    if all_viewed:
        result = set(sets[0]).intersection(*sets)
    else:
        result = list(set(sets[0]).union(*sets))
    result.sort()
    return result


def filter_for_epoch(obs_dfs_full, epoch):
    filtered_dfs = []
    for df in obs_dfs_full:
        f1 = df['Second'] == epoch.second
        f2 = df['Week'] == epoch.week
        filtered_dfs.append(df[f1 & f2])

    return filtered_dfs


def create_combination_obs(epoch_obs):
    num_obs = len(epoch_obs)
    obs = []
    for i, rxs in enumerate(epoch_obs):
        for j in range(i, num_obs):
            if i != j:
                corr_offset, corr_series, corr_axis = get_corr_offset(epoch_obs[i], epoch_obs[j])
                check = check_for_corr(corr_series)
                if check:
                    # Apply descriminator
                    prompt = corr_series[corr_offset]
                    early = corr_series[corr_offset - 1]
                    late = corr_series[corr_offset + 1]
                    corr_val, corr_offset = apply_descriminator(early, prompt, late)
                new_obs = [i, j, corr_offset, check]

                obs.append(new_obs)
    return obs


def calc_tdoa_obs(epochs, obs_dfs):
    detected_obs = []
    # Find all epochs with correlation candidates
    for epoch in epochs:
        epoch_obs = filter_for_epoch(obs_dfs, epoch)
        tdoa_obs = create_combination_obs(epoch_obs)
        if all([t[3] for t in tdoa_obs]):
            # _logger.info(f'{tdoa_obs}')
            detected_obs.append(tdoa_obs)

    epoch_ls = SprinklerLS(detected_obs, obs_dfs)

    _logger.info(f'The number of epochs with found corr spikes: {len(detected_obs)}')
    return detected_obs


def main(args):
    obs_dfs = parse_input_files(args.filepath)
    # obs_dfs_filtered =
    # get all the epochs that are common to both files
    epochs = get_epoch_set(obs_dfs)
    _logger.info(f'found {len(epochs)} epochs total in the file')
    _logger.info(f'Running TDOA on epochs')
    tdoa_obs = calc_tdoa_obs(epochs, obs_dfs)
    _logger.info('Processing complete')

    # Process all epochs


def get_args():
    pbja_args = argparse.ArgumentParser()
    pbja_args.add_argument('-f', '--filepath', default=os.getcwd(),
                           help='Filepath to location of observations. Defaults to CWD')

    return pbja_args.parse_args()


if __name__ == '__main__':
    sys.exit(main(get_args()))
