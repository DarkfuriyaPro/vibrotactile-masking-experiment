import time

from calibration import *
from acc_interface import Acc_Interface
import utils as u

def calibrate_level(channel,load_filter=True):
    fs = 2800
    fs_audio = fs
    reference_level_rms = 0.05
    f_calib = 250

    player = Player(fs,False,True)
    if load_filter:
        player.load_filter()

    sig_time = 1
    t = np.linspace(0, sig_time, int(fs * sig_time), endpoint=False)
    signal = np.sin(2 * np.pi * f_calib * t)
    signal = u.normalize_to_rms(signal, reference_level_rms)
    zeros = np.zeros_like(signal)

    N = len(signal)

    acc_interface = Acc_Interface(fs,2)
    acc_interface.start_recording()
    player.play_sound_mono(signal,channel)
    time.sleep(3.5)
    data = acc_interface.obtain_data()
    acc_interface.stop_recording()


    len_noise = len(signal)
    acc_z2 = data[2]
    acc_z2 = extract_signal(acc_z2,len_noise)

    rms_sig = u.calculate_rms(signal)
    rms_rec = u.calculate_rms(acc_z2)
    print("level output [dB]: "+ str(u.lin2db(rms_sig)))
    print("level measured [dB]: "+ str(u.lin2db(rms_rec)))

    gain = rms_sig/rms_rec

    save_calibration_gain(gain, channel)

    player.load_gain()

    acc_interface = Acc_Interface(fs,2)
    acc_interface.start_recording()
    player.play_sound_mono(signal,channel)
    time.sleep(3.5)
    data = acc_interface.obtain_data()
    acc_interface.stop_recording()


    len_noise = len(signal)
    acc_z2 = data[2]
    acc_z2 = extract_signal(acc_z2,len_noise)

    rms_rec = u.calculate_rms(acc_z2)
    print("level output [dB]: "+ str(u.lin2db(rms_sig)))
    print("level measured [dB]: "+ str(u.lin2db(rms_rec)))

if __name__ == "__main__":
    channel = 0
    calibrate_level(channel)