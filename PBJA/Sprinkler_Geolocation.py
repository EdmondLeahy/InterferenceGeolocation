import time
import argparse
import sys
import logging
# from progress.bar import IncrementalBar as ProgressBar

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
_logger = logging.getLogger('PBJA_logger')
# _logger.setLevel(logging.DEBUG)

SPEED_OF_LIGHT = 299792458
SAMPLE_RATE = 12000000  # SPS according to the Paper


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

    # epoch_prog = ProgressBar('\rProcessing Epochs', max=len(epoch_obs), file=None)
    # epoch_prog.file = sys.stderr

    for i, rxs in enumerate(epoch_obs):
        for j in range(i, num_obs):
            if i != j:
                max_corr_ind, corr_series, corr_axis = get_corr_offset(epoch_obs[i], epoch_obs[j])
                check = check_for_corr(corr_series)
                if check:
                    # Apply descriminator
                    prompt = (corr_axis[max_corr_ind], corr_series[max_corr_ind])
                    early = (corr_axis[max_corr_ind - 1], corr_series[max_corr_ind - 1])
                    late = (corr_axis[max_corr_ind + 1], corr_series[max_corr_ind + 1])
                    corr_offset, corr_val = apply_descriminator(early, prompt, late)
                    # Convert from samples to meters
                    dist_offset = (corr_offset / SPEED_OF_LIGHT) * SAMPLE_RATE
                    new_obs = [i, j, dist_offset, check]
                    obs.append(new_obs)
    #     epoch_prog.next()
    # epoch_prog.finish()

    return obs


def calc_tdoa_obs(epochs, obs_dfs, poi=None):
    detected_obs = []
    est_epochs = []
    # Find all epochs with correlation candidates
    for epoch in epochs:
        epoch_obs = filter_for_epoch(obs_dfs, epoch)
        tdoa_obs = create_combination_obs(epoch_obs)
        if all([t[3] for t in tdoa_obs]):
            # _logger.info(f'{tdoa_obs}')
            detected_obs.append(tdoa_obs)

            epoch_ls = SprinklerLS(tdoa_obs, obs_dfs, x0=poi)

            ret_code = epoch_ls.iterate()
            _logger.info(f'{epoch} returned {ret_code}')
            est_epochs.append((epoch, epoch_ls.est_x, ret_code))

    return est_epochs


def main(args):
    obs_dfs = parse_input_files(args.filepath, expansion=args.source_location)
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
    pbja_args.add_argument('-sl', '--source_location', default=None, nargs=3, type=float,
                           help='Location of the interference source, if known. Also used for point of expansion '
                                'in both ENU calc and LS calc')

    return pbja_args.parse_args()


if __name__ == '__main__':
    sys.exit(main(get_args()))
