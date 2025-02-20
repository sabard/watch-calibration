# filter signal

def apply_filter(signal):
    # b, a = sps.butter(4, 100, 'lp', analog=True)
    # filtered = sps.filtfilt(b, a, signal)

    sos = sps.butter(10, 20., 'lp', fs=wc.fs, output='sos')
    filtered = sps.sosfilt(sos, signal)

    # TODO use filtfilt
    # use 6 order FIR filter

    return filtered


# https://github.com/mkmcc/watch-calibration

# apply butterworth lowpass to watch audio
filtered = apply_filter(watch_audio)

plt.figure()
plt.plot(filtered)
plt.show()

# no filtering
# filtered = watch_audio

# calculate FFT in unit of decibels
A = 20 * np.log10(np.abs(np.fft.rfft(filtered)))

# plot A between frequencies of interest
BW = [0.5, 10.]

timestep = 1. / wc.fs
freq = np.fft.rfftfreq(watch_audio.shape[0], d=timestep)
b1 = np.argmax(freq > BW[0])
b2 = np.argmax(freq > BW[1])

plt.plot(freq[b1:b2], A[b1:b2])
plt.show

# plot A on log plot
plt.figure()
plt.semilogx(freq, A)
plt.show()

sps.find_peaks_cwt(A[b1:b2], np.arange(1,10))

# watch-calibration output
# initial guess: 6.0 p/m 0.00833 Hz
# updated guess: 6.0000004 p/m 8.35e-07 Hz
# error consistent with zero.  below is an upper limit.
# record for a longer time and repeat

# error is 2.2 seconds / month



# MIR example

filtered = watch_audio
plt.plot(filtered)
plt.show()

x = filtered

# this doesn't work with hop_length too large since larger frames introduce too much noise
hop_length = 4
onset_frames = librosa.onset.onset_detect(
    y=x, sr=wc.fs, hop_length=hop_length, units="frames",
    wait=1000, pre_max=500, post_max=500
) # pre_avg=1000, post_avg=1000, delta=0.1,

# discard first and last onset frames since they may be in the middle of a tick
onset_frames = onset_frames[1:-1]

onset_times = librosa.frames_to_time(onset_frames, sr=wc.fs, hop_length=hop_length)
print(len(onset_times))
# print(onset_times)

diffs = []
for i in range(len(onset_times)-1):
    diffs.append(onset_times[i+1] - onset_times[i])
print(1./6)
# print(diffs)

sig_max = np.max(x)
sig_min = np.min(x)

S = librosa.stft(x)
logS = librosa.amplitude_to_db(abs(S))

plt.figure(figsize=(14, 5))
librosa.display.specshow(logS, sr=wc.fs, x_axis='time', y_axis='log', cmap='Reds')
plt.vlines(onset_times, 0, 10000, color='#3333FF')

plt.figure(figsize=(14, 5))
librosa.display.waveshow(x, sr=wc.fs)
plt.vlines(onset_times, sig_min, sig_max, color='r', alpha=0.8)

clicks = librosa.clicks(frames=onset_frames, sr=wc.fs, length=len(x))

plt.figure()
plt.plot(clicks)

diff_arr = np.array(diffs)
print(np.where(diff_arr>.17))
print(np.where(diff_arr<.16))
print(np.where(diff_arr<.16)[0])
print(diff_arr[np.where(np.array(diffs)<.16)[0]])

cutoff = 44100
plt.figure(figsize=(14, 5))
librosa.display.waveshow(x[0:cutoff], sr=wc.fs)
plt.vlines(onset_times[np.where(onset_times<cutoff/wc.fs)], sig_min, sig_max, color='r', alpha=0.8)

cutoff = 44100
plt.figure(figsize=(14, 5))
window_start = (len(watch_audio)-cutoff)/wc.fs
librosa.display.waveshow(x[-cutoff:], sr=wc.fs, offset=window_start)
plt.vlines(onset_times[np.where(onset_times>window_start)], sig_min, sig_max, color='r', alpha=0.8)

print(len(onset_times))
onset_diffs = (np.diff(onset_times) * wc.fs).astype(int)
# print(onset_times)
anomaly_idx = np.where(onset_diffs<7000)[0]
print(anomaly_idx)
anomaly_diffs = onset_times[np.where(onset_diffs<7000)[0]]

w_len = 44100 * 2
vline_len = 6 * 3

for i, anomaly in enumerate(anomaly_diffs):
    plt.figure(figsize=(14, 5))
    window_start = anomaly - w_len//2/wc.fs
    sig_start = int(anomaly*wc.fs)-w_len//2
    sig_end = int(anomaly*wc.fs)+w_len//2
    if sig_start < 0:
        sig_start = 0
    if window_start < 0:
        window_start = 0
    librosa.display.waveshow(watch_audio[sig_start:sig_end], sr=wc.fs, offset=window_start)
    plt.vlines(onset_times[anomaly_idx[i]-vline_len//2:anomaly_idx[i]+vline_len//2], sig_min, sig_max, color='r', alpha=0.8)
