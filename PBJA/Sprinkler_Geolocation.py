import time
import argparse
import sys

# Python Package Imports
import os
import numpy as np
import scipy.fftpack as fft
import numpy.random as rnd
import random
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd

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
            print(f'Reading {obs_filename}...')
            raw_sprinkles = datafile.readlines()
            print('Done')
        spkrlr_data = [log.split(',') for log in raw_sprinkles[start_loc:start_loc+max_size]]
        obs_arrays.append(spkrlr_data)
    return obs_arrays

def get_series_from_log(log):
    """ Function to return a series from an individual sprinkler log """
    series = [int(dat) for dat in log[8:-4]]
    return series


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
    pos_E = float(log[-3])
    pos_N = float(log[-2])
    pos_U = float(log[-1])
    return pos_E, pos_N, pos_U

def get_epoch_from_log(log):
    """ Simple function to extract the epoch of a specific log """
    epoch_week = float(log[0])
    epoch_second = float(log[1])
    ep = Epoch(epoch_week, epoch_second)
    return ep

def complexify(sig):
    """ Given a list (sig), make every second value the imaginary value of a complex number """
    i=[]
    q=[]
    for j in range(len(sig)):
        if j%2 == 0:
            i.append(sig[j])
        else:
            q.append(sig[j])
    i = np.array(i)
    q = np.array(q)
    return (i + 1j*q)


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


def get_corr_offset(log1, log2, epoch):
    """
        Find the value of the correlation at the peak of the correlation spike (normalized to max value). The real portion of the correlation
        is used here, as the imaginary value is to do with power of the correlated signal and is not useful.

        Todo: Find reference for this

    """
    rx_epoch_obs = []
    corr_epoch = epoch
    for rx_file in [log1, log2]:
        epoch_series = []
        for log in rx_file:
            if get_epoch_from_log(log) == corr_epoch:
                epoch_series.extend(get_series_from_log(log))
        rx_epoch_obs.append(epoch_series)

    complex_rx_series = []
    for series in rx_epoch_obs:
        complex_rx_series.append(complexify(series))

    corr = fft_ccor(complex_rx_series[0], complex_rx_series[1])
    corr.real /= np.max(abs(corr.real))
    x = get_corr_axis(corr)
    max_shift = x[np.argmax(corr.real)]
    #     print(f'Location of max: {max_shift}')
    return abs(corr.real), x

def make_pandas_arrays(list_obs):
    pd_obs = []
    for obs in list_obs:
        arr_heads = [t[:8] for t in obs]
        payload = [get_series_from_log(t) for t in obs]
        obs_df = pd.DataFrame(arr_heads)
        obs_df = obs_df.apply(pd.to_numeric)
        obs_df['Data'] = payload
        obs_df.columns = ['Second', 'Week', 'Lat', 'Lon', 'Height', 'DataLen', 'Samples', 'AlsoLen', 'Data'] # Todo: Get actual names for this
        pd_obs.append(obs_df)
    return pd_obs


def get_epoch_set(lst_data_obs, all_viewed=False):
    sets = []
    for obs_df in lst_data_obs:
        s_new  = list(obs_df['Second'])
        w_new  = list(obs_df['Week'])
        eps = [Epoch(e[0], e[1]) for e in list(zip(w_new, s_new))]
        sets.append(set(eps))

    if all_viewed:
        result = set(sets[0]).intersection(*sets)
    else:
        result = list(set(sets[0]).union(*sets))

    return result

def calc_tdoa_obs(obs_dfs):






def main():
    # Find all the filenames in the directory that end with .csv
    # file_loc = f"/home/edmond/Documents/Projects/Sandbox/DataSandbox/Observations/"
    file_loc = f"/mnt/BigSlowBoi/DOCUMENTS/Projects/InterferenceGeolocation/Sprinkler/Data/Observations"
    obs_filenames = [os.path.join(file_loc, f) for f in os.listdir(file_loc) if f.endswith('.csv')]
    print(f'found {len(obs_filenames)} observation files')
    obs_arrays = get_obs_from_files(obs_filenames)
    obs_dfs = make_pandas_arrays(obs_arrays)
    # get all the epochs that are found in the first file
    epochs = get_epoch_set(obs_dfs)
    print(f'found {len(epochs)} epochs total in the file')

    # Process all epochs


if __name__ == '__main__':
    sys.exit(main())