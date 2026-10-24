import numpy as np
from scipy.signal import butter, sosfilt

""" dB to amplitude """
def db_to_amplitude(db):
    return 10 ** (db / 20)

""" dB to linear """
def lin2db(lin):
    return 20 * np.log10(lin)

"""Calculate the current amplitude"""
def calculate_rms(sig):
    return np.sqrt(np.mean(np.square(sig)))

""" Normalize signal to target RMS """
def normalize_to_rms(sig, rms):
    current_rms = calculate_rms(sig)
    return sig * (rms / current_rms)

def bandpass_filter(data, low_frequency, high_frequency, fs, order=4):
    sos = butter(order, [low_frequency, high_frequency], btype='bandpass', fs=fs, output='sos')
    y = sosfilt(sos, data)
    return y

def windowing(sig, window_length):
    #create window with a given length
    window = np.hanning(window_length * 2)
    # beginning of the signal
    sig[:window_length] *= window[:window_length]
    # end of the signal
    sig[-window_length:] *= window[window_length:]
    return sig

def amp2mag(spectrum,N):
    return 2.0/N * np.abs(spectrum)