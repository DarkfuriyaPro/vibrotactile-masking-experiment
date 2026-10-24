import sounddevice as sd
import time

from calibration import *
from acc_interface import Acc_Interface

fs = 2800
fs_audio = fs
channel = 0

player = Player(fs,True)


noise = np.random.normal(0, 1, int(fs_audio * 1.5))
noise = noise / np.max(np.abs(noise)) * 0.25
zeros = np.zeros_like(noise)

N = len(noise)

noise_fft = calc_fft(noise)
noise_fft_mag = u.amp2mag(noise_fft[0:N//2+1],N)

acc_interface = Acc_Interface(fs,2)
acc_interface.start_recording()
player.play_sound_mono(noise,channel)
time.sleep(3.5)
data = acc_interface.obtain_data()
acc_interface.stop_recording()


len_noise = len(noise)
acc_z2 = data[2]
acc_z2 = extract_signal(acc_z2,len_noise)

acc_fft2 = calc_fft(acc_z2)
acc_fft2_mag = u.amp2mag(acc_fft2[0:N//2+1],N)

freq = get_freqs(fs,len_noise)

noise_fft_smooth = octave_smoothing(noise_fft_mag,12)
acc_fft2_smooth = octave_smoothing(acc_fft2_mag,12)

plt.plot(freq, u.lin2db(noise_fft_smooth[:-1]))
plt.plot(freq, u.lin2db(acc_fft2_smooth[:-1]))
plt.grid()
plt.xscale('log')
plt.xlim([10,1400])
plt.show()