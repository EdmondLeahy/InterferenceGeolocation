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


logging.basicConfig(level=logging.INFO)
_logger = logging.getLogger('PHJA_logger')
# _logger.setLevel(logging.DEBUG)

class Epoch:
    def __init__(self, week, second):
        self.week = week
        self.second = second

    def __eq__(self, eq_class):
        return self.week == eq_class.week and self.second == eq_class.second

    def __hash__(self):
        return hash((self.week, self.second))

    def __repr__(self):
        return f'{self.week}:{self.second}'

    def __lt__(self, other):
        if self.week < other.week:
            return True
        elif self.week > other.week:
            return False
        elif self.second < other.second:
            return True
        else:
            return False

    def __gt__(self, other):
        return False if self < other else True


def get_obs_from_files(obs_filenames, start_loc=1, max_size=10000):
    """
    Function for retrieving the sprinkler observations from the file given. Places each parsed log in to a list
    Args:
        obs_filenames (list of str): List of filenames to parse.
        start_loc (int): The start location to parse. Use if you want to skip the start of the file for some reason
        max_size (int): The end location to parse. Use to limit size, or to stop before the end of file.
    """
    obs_arrays = []
    for obs_filename in obs_filenames:
        with open(obs_filename, 'r+') as datafile:
            _logger.info(f'Reading {obs_filename}...')
            raw_sprinkles = datafile.readlines()
            _logger.info('Done')
        spkrlr_data = [log.split(',') for log in raw_sprinkles[start_loc:start_loc+max_size]]
        obs_arrays.append(spkrlr_data)
    return obs_arrays





def get_all_epoch_in_logs(logs):
    """Function to return all the unique epochs present in the logs """
    epochs = []
    for log in logs:
        epoch = get_epoch_from_log(log)
        if epoch not in epochs:
            epochs.append(epoch)

    return epochs


def get_pos_from_log(log):
    """ Simple function to extrac the location from a log """
    pos_e = float(log[-3])
    pos_n = float(log[-2])
    pos_u = float(log[-1])
    return pos_e, pos_n, pos_u


def get_epoch_from_log(log):
    """ Simple function to extract the epoch of a specific log """
    epoch_week = float(log[0])
    epoch_second = float(log[1])
    ep = Epoch(epoch_week, epoch_second)
    return ep


def complexify(sig):
    """ Given a list (sig), make every second value the imaginary value of a complex number """
    i = []
    q = []
    for j in range(len(sig)):
        if j % 2 == 0:
            i.append(sig[j])
        else:
            q.append(sig[j])
    i = np.array(i)
    q = np.array(q)
    return i + 1j*q


def fft_ccor(a, b):
    """
    Complete the cross correlation of signal a to signal b. This uses the scipy.fftpack function.

    Equation: cross_correlation = inv_fft(fft(sig_a) + conjugate(fft(sig_b)))

    """
    fft_a = fft.fft(a)
    fft_b = np.conj((fft.fft(b)))
    fft_crosscorr = np.fft.fftshift(np.fft.ifft(fft_a * fft_b))
    return fft_crosscorr


def get_corr_axis(corr_array):
    """ Creates the horizontal axis ticks, with 0 centered (to plot the correlation shift)"""
    half_size = int(len(corr_array)/2)
    if half_size*2 < len(corr_array):
        x = np.arange(-half_size, half_size+1)
    elif half_size*2 > len(corr_array):
        x = np.arange(-half_size, half_size-1)
    else:
        x = np.arange(-half_size, half_size)
    return x


def get_corr_offset(df1, df2):
    """
        Find the value of the correlation at the peak of the correlation spike (normalized to max value).
        The real portion of the correlation is used here, as the imaginary value is to do with power of the
        correlated signal and is not useful.

        Todo: Find reference for this

    """
    rx1_obs = complexify([obs for data in df1['Data'].to_list() for obs in data])
    rx2_obs = complexify([obs for data in df2['Data'].to_list() for obs in data])

    corr = fft_ccor(rx1_obs, rx2_obs)
    corr.real /= np.max(abs(corr.real))
    x = get_corr_axis(corr)
    max_shift = x[np.argmax(corr.real)]
    #     _logger.info(f'Location of max: {max_shift}')
    return max_shift, abs(corr.real), x


def check_for_corr(corr_series, thresh=7):
    """ Simple function to check if a correlation was found """
    base = np.mean(corr_series)
    spike_max = np.max(corr_series)
    return (spike_max / base) > thresh


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


def filter_for_timesteering(obs_dfs):
    filtered_dfs = []
    for df in obs_dfs:
        # filtered_dfs.append(df[df['Second'] == epoch.second & df['Week'] == epoch.week])
        pass


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
                corr_offset = get_corr_offset(epoch_obs[i], epoch_obs[j])
                new_obs = [i, j, corr_offset[0], check_for_corr(corr_offset[1])]
                obs.append(new_obs)
                if new_obs[3]:
                    pass
    return obs


def calc_tdoa_obs(epochs, obs_dfs):
    detected_obs = []
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
