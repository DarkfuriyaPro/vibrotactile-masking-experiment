import numpy as np
from scipy.fft import fft, ifft, fftfreq
import matplotlib.pyplot as plt
import utils as u
import pandas as pd
import sounddevice as sd
import warnings
import os

class Player:
    ir = [None,None]
    gain = [None,None]
    def __init__(self, fs=2800, init=False, headroom=False):
        #for setting the right output device
        #devices = sd.query_devices()
        #print(devices)
        #sd.default.device = 3
        sd.default.samplerate = fs
        self.headroom = headroom
        if init:
            self.load_filter()
            self.load_gain()
    
    def load_filter(self):
        if os.path.isfile("calibration/IR0.csv"):
            self.ir[0] = load_calibration_filter(0)
        else:
            print("no filter IR for channel 0 found. Continuing without filter calibration.")
        if os.path.isfile("calibration/IR1.csv"):
            self.ir[1] = load_calibration_filter(1)
        else:
            print("no filter IR for channel 1 found. Continuing without filter calibration.")

    def load_gain(self):
        if os.path.isfile("calibration/gain0.csv"):
            self.gain[0] = load_calibration_gain(0)
        else:
            print("no gain for channel 0 found. Continuing without level calibration.")
        if os.path.isfile("calibration/gain1.csv"):
            self.gain[1] = load_calibration_gain(1)
        else:
            print("no gain for channel 1 found. Continuing without level calibration.")

    def play_sound_mono(self, signal, channel=0):
        zeros = np.zeros_like(signal)
        if self.ir[channel] is not None:
            signal = apply_filter(signal,self.ir[channel])
        if self.gain[channel] is not None:
            signal = signal * self.gain[channel]
        if channel == 0:
            stereo_signal = np.column_stack((signal, zeros))
        else:
            stereo_signal = np.column_stack((zeros, signal))
        if self.headroom:
            max_value = np.max(np.abs(signal))
            print("maximum audio value: "+str(max_value))
            print("headroom [dB]: " + str(u.lin2db(1/max_value)))
        if np.max(np.abs(signal)) >= 1:
            warnings.warn("Output clipped!")
        
        sd.play(stereo_signal)

    def play_sound_stereo(self, signal):
        if self.ir[0] is not None:
            signal[0] = apply_filter(signal[0],self.ir[0])
            signal[1] = apply_filter(signal[1],self.ir[1])
        if self.gain[0] is not None:
            signal[0] = signal[0] * self.gain[0]
            signal[1] = signal[1] * self.gain[1]
        if self.headroom:
            max_value = np.max(np.abs(signal))
            print("maximum audio value: "+str(max_value))
            print("headroom [dB]: " + str(u.lin2db(1/max_value)))
        if np.max(np.abs(signal)) >= 1:
            warnings.warn("Output clipped!")
        
        sd.play(signal)



def save_calibration_filter(ir,H,channel):
    df = pd.DataFrame({'H': H})
    df.to_csv('calibration/H'+str(channel)+'.csv', index=False)
    df = pd.DataFrame({'IR': ir})
    df.to_csv('calibration/IR'+str(channel)+'.csv', index=False) 

def load_calibration_filter(channel):
    ir = pd.read_csv('calibration/IR'+str(channel)+'.csv')
    return ir.IR

def save_calibration_gain(gain,channel):
    df = pd.DataFrame({'gain': [gain]})
    df.to_csv('calibration/gain'+str(channel)+'.csv', index=False)

def load_calibration_gain(channel):
    gain = pd.read_csv('calibration/gain'+str(channel)+'.csv')
    return gain.gain[0]

def extract_signal(acc,length):

    acc = acc - np.mean(acc) # remove DC. Filter instead?
    acc_e = acc * acc
    e_max = 0
    i_max = 0
    for i in range(len(acc)-length):
        energy = np.sum(acc_e[i:i+length])
        if energy > e_max:
            e_max = energy
            i_max = i
    return acc[i_max:i_max+length]

def calc_fft(sig):
    return fft(sig)

def get_freqs(fs,N):
    T = 1.0 / fs
    return fftfreq(N, T)[:N//2]

def build_transfer_function(input,output):
    input_fft = calc_fft(input)
    output_fft = calc_fft(output)
    N = len(input_fft)
    input_fft_mag = u.amp2mag(input_fft[0:N//2+1],N)
    output_fft_mag = u.amp2mag(output_fft[0:N//2+1],N)

    H = transfer_function(input_fft_mag,output_fft_mag)
    return H,input_fft_mag,output_fft_mag

def separate_recording(noise,acc_z,N_filter):
    len_noise = len(noise)
    noise_samples = [noise[:N_filter]]
    acc_z_samples = [acc_z[:N_filter]]
    n_blocks = len_noise//N_filter
    for i in range(1,n_blocks):
        noise_samples.append(noise[N_filter*i:N_filter*(i+1)])
        acc_z_samples.append(acc_z[N_filter*i:N_filter*(i+1)])
    return noise_samples, acc_z_samples

def filter_construction(noise_samples, acc_z_samples):
    H = None
    for i in range(len(noise_samples)):
        H_temp,noise_fft_mag,acc_fft_mag = build_transfer_function(noise_samples[i],acc_z_samples[i])
        if H is None:
            H = H_temp
        else:
            H = H + H_temp
    H = H / len(noise_samples)
    N = len(noise_samples[0])

    #H_smooth = octave_smoothing(H,n=3)
    H_smooth = H
    #freqs = get_freqs(2800,len(H_smooth))
    #index = freqs > 250
    #index = index.tolist().index(True)
    #H_smooth = H_smooth / H_smooth[index]
    filt_ir = construct_filter(H_smooth,N)
    filt_ir_short = prune_filter(filt_ir,pruned_size=64)

    return filt_ir, filt_ir_short, H_smooth

def transfer_function(input, output):
    return output/input

def octave_smoothing(spectrum, n):
    smooth = np.zeros_like(spectrum)
    for k in range(len(spectrum)):
        a = round(k*2**(-1/(2*n)))
        b = round(k*2**(1/(2*n)))
        weight = 1/(b-a+1)
        temp = 0
        for i in range(a,b+1):
            if i < len(spectrum):
                temp += spectrum[i]
            else:
                temp += spectrum[-1]
        smooth[k] = weight * temp
    return smooth

def construct_filter(H, N):
    filt_fft = 1 / H
    filt_fft2 = np.zeros(N)
    N_half = N//2
    filt_fft2[:N_half+1] = filt_fft
    filt_fft2[N_half+1:] = np.flip(filt_fft[1:-1])

    filt_ir_temp = np.real(ifft(filt_fft2))

    filt_ir = np.zeros_like(filt_ir_temp)
    filt_ir[:N//2-1] = filt_ir_temp[N//2+1:]
    filt_ir[N//2-1:] = filt_ir_temp[:N//2+1]
    return filt_ir

def prune_filter(ir,pruned_size):
    N = len(ir)
    ir_short = ir[N//2-(pruned_size//2):N//2+(pruned_size//2)]
    ir_short = u.windowing(ir_short,int(pruned_size*0.05))
    return ir_short


def apply_filter(sig,ir):
    sig_filt = np.convolve(sig,ir)
    N_filt = len(ir)
    sig_filt = sig_filt[N_filt//2+1:-N_filt//2+2]
    return sig_filt