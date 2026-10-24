import matplotlib.pyplot as plt
import time
import numpy as np

from acc_interface import Acc_Interface
from calibration import *
import utils as u


def calibrate_response(channel, plot=False):

    fs = 2800
    fs_audio = fs
    siglength = 3 #s
    N_filter = 128

    player = Player(fs,False)
    player.load_gain()

    noise = np.random.normal(0, 1, int(fs_audio * siglength))
    #noise = noise / np.max(np.abs(noise)) * 0.25
    noise = u.normalize_to_rms(noise,0.05)

    acc_interface = Acc_Interface(fs,siglength+0.5)
    acc_interface.start_recording()
    player.play_sound_mono(noise,channel)
    time.sleep(4)
    acc_z = acc_interface.obtain_data()[2]
    acc_interface.stop_recording()


    len_noise = len(noise)
    acc_z = extract_signal(acc_z,len_noise)

    noise_samples, acc_z_samples = separate_recording(noise,acc_z,N_filter)
    filt_ir, filt_ir_short, H_smooth = filter_construction(noise_samples, acc_z_samples)



    H,noise_fft_mag,acc_fft_mag = build_transfer_function(noise,acc_z) #only for eval

    save_calibration_filter(filt_ir,H_smooth,channel)

    freq = get_freqs(fs,len_noise)


    """
    plt.plot(freq, u.lin2db(noise_fft_mag[:-1]))
    plt.plot(freq, u.lin2db(acc_fft_mag[:-1]))
    plt.grid()
    plt.xscale('log')
    plt.xlim([10,1400])
    plt.show()
    """

    if plot:
        plt.plot(filt_ir)
        plt.plot(filt_ir_short)
        plt.show()

    player.load_filter()
    acc_interface = Acc_Interface(fs,2)
    acc_interface.start_recording()
    player.play_sound_mono(noise, channel)
    time.sleep(4)
    acc_z2 = acc_interface.obtain_data()[2]
    acc_interface.stop_recording()


    len_noise = len(noise)
    N = len_noise
    acc_z2 = extract_signal(acc_z2,len_noise)

    acc_fft2 = calc_fft(acc_z2)
    acc_fft2_mag = u.amp2mag(acc_fft2[0:N//2+1],N)

    freq = get_freqs(fs,len_noise)
    freq2 = get_freqs(fs,N_filter)

    noise_fft_smooth = octave_smoothing(noise_fft_mag,12)
    acc_fft_smooth = octave_smoothing(acc_fft_mag,12)
    acc_fft2_smooth = octave_smoothing(acc_fft2_mag,12)

    print ("calibration of channel "+ str(channel) +" finished")

    if plot:
        plt.plot(freq, u.lin2db(noise_fft_smooth[:-1]))
        plt.plot(freq, u.lin2db(acc_fft_smooth[:-1]))
        plt.plot(freq, u.lin2db(acc_fft2_smooth[:-1]))
        plt.plot(freq2, u.lin2db(H_smooth[:-1]))
        plt.grid()
        plt.xscale('log')
        plt.xlim([10,1400])
        plt.ylim([-90,10])
        plt.legend(["input noise","measured","filtered measured","transfer function"])
        plt.show()

        print("test")

if __name__ == "__main__":
    channel = 0
    calibrate_response(channel,True)