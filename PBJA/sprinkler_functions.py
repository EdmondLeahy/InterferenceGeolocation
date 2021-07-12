
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

    corr = abs(fft_ccor(rx1_obs, rx2_obs).real)
    corr /= np.max(corr)
    x = get_corr_axis(corr)
    max_ind = np.argmax(corr)
    #     _logger.info(f'Location of max: {max_shift}')
    return max_ind, abs(corr), x


def check_for_corr(corr_series, thresh=7):
    """ Simple function to check if a correlation was found """
    base = np.mean(corr_series)
    spike_max = np.max(corr_series)
    return (spike_max / base) > thresh


def find_descriminator_corr_values(corr_offset, corr_series):

    prompt = corr_series[corr_offset]
    early = corr_series[corr_offset - 1]
    late = corr_series[corr_offset + 1]




def apply_descriminator(early, prompt, late, ts=1):
    """
        Descriminator function that interpolates between three correlation values to find the interpolated maximum
        correlation.



    """
    # Handle if early is higher than late
    middle = prompt
    if early[1] > late[1]:
        swap = True
        first = late
        last = early
    else:
        swap = False
        first = early
        last = late

    m = (middle[1] - first[1]) / ts
    tos = (ts * (last[1] - first[1])) / (2 * (middle[1] - first[1]))
    y = m * tos + prompt[1]

    tos = -1 * tos if swap else tos
    x = middle[0] + tos
    return x, y

