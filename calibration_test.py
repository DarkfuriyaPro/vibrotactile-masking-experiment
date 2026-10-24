from calibration import *

N = 1024
fs = 44100

#noise signal
noise_orig = np.random.randn(1024)


#simulated filtered noise
filter_pre = np.array([0.05,0.2,0.5,0.2,0.05])
noise = np.convolve(noise_orig,filter_pre)
noise = noise[:N]


#fft of original and filtered
noise_fft = calc_fft(noise)
noise_orig_fft = calc_fft(noise_orig)

#magnitude
mag = u.amp2mag(noise_fft[0:N//2+1],N)
mag = u.amp2mag(noise_fft[0:N//2+1],N)
orig_mag = u.amp2mag(noise_orig_fft[0:N//2+1],N)

#transfer function
H = transfer_function(orig_mag,mag)
H_db = u.lin2db(H)

#smoothing (nth-octave)
H_smooth = octave_smoothing(H,n=12)

#frequency vector
freq = get_freqs(fs,N)

#plot spectra
plt.plot(freq, u.lin2db(mag[:-1]))
plt.plot(freq, u.lin2db(orig_mag[:-1]))
plt.plot(freq, H_db[:-1])
plt.plot(freq, u.lin2db(H_smooth[:-1]))
plt.grid()
plt.xscale('log')
plt.show()

#construct inverse filter
filt_ir = construct_filter(H_smooth,N)

#TODO: normalize at 250 Hz (or normalize output after filtering)

#pruning, windowing
filt_ir_short = prune_filter(filt_ir,pruned_size=128)


#plot IR
plt.plot(filt_ir)
plt.plot(filt_ir_short)
plt.show()


#apply filter
noise_filt = apply_filter(noise,filt_ir_short)

#plot corrected noise
plt.plot(noise_orig)
plt.plot(noise_filt)
plt.show()






filt_fft = calc_fft(noise_filt)
filt_mag = 2.0/N * np.abs(filt_fft[0:N//2+1])

plt.plot(freq, u.lin2db(orig_mag[:-1]))
plt.plot(freq, u.lin2db(filt_mag[:-1]))
plt.grid()
plt.xscale('log')
plt.show()