""" WatchCalibration Class """
import copy
import csv
import os

from bokeh.plotting import figure, output_file, save
import librosa
import matplotlib
# matplotlib.rcParams['figure.subplot.top'] = 1   # Extend plot to top of figure
from matplotlib import pyplot as plt
import numpy as np
import scipy as sp
from scipy import signal as sps
import soundfile as sf
from scipy.io.wavfile import write

try:
    import sounddevice as sd
    SND_DEFINED = True
except:
    SND_DEFINED = False

class WatchCalibration:
    """ WatchCalibration class  """

    def __init__(self, fs=44100):
        """ Initialize Watch-Calibration. """

        self.fs = fs

    def __repr__(self):
        """ Return Watch-Calibration name. """

        return self.__class__.__name__


    def query_devices(self):
        if not SND_DEFINED:
            print("sounddevice library could not be loaded.")
            return

        print(sd.query_devices())


    def save_audio_to_file(self, duration, outfile="output.wav", input_device=None, generate=False):
        if not SND_DEFINED:
            print("sounddevice library could not be loaded.")
            return

        mic_recording = sd.rec(int(duration * self.fs), samplerate=self.fs, channels=1, device=input_device)

        sd.wait()  # Wait until recording is finished
        write(outfile, self.fs, mic_recording)  # Save as WAV file


    def play_audio(self, filename, output_device=sd.default.device):
        if not SND_DEFINED:
            print("sounddevice library could not be loaded.")
            return

        # Extract data and sampling rate from file
        data, fs = sf.read(filename, dtype='float32')
        sd.play(data, fs, device=output_device)
        status = sd.wait()  # Wait until file is done playing


    # TODO change filename to archive loc and support s3 pulls?
    def load_audio(self, filename="data_W241130_W241130.wav"):
        return librosa.load(filename, sr=self.fs)


    def plot_audio(self, audio):
        fig = plt.figure(figsize=(8,2))
        fig.canvas.header_visible = False
        plt.plot(audio)
        plt.ylim(np.min(audio), np.max(audio))
        plt.title("Audio signal")
        plt.show()

        fig = plt.figure(figsize=(8,2))
        fig.canvas.header_visible = False
        A = np.abs(sp.fft.fft(audio))[:self.fs//2]
        peaks = sps.find_peaks(A, height=40, distance=100)[0]
        plt.plot(A)
        plt.plot(peaks, A[peaks], 'x')
        plt.title(f"FFT and peaks at: {peaks} (Hz)")
        plt.show()

        # spectral
        fig = plt.figure(figsize=(8,2))
        fig.canvas.header_visible = False
        D = librosa.amplitude_to_db(np.abs(librosa.stft(audio)), ref=np.max)
        librosa.display.specshow(D)
        plt.title("Spectrogram")


    # TODO
    # https://stackoverflow.com/questions/41492882/find-time-shift-of-two-signals-using-cross-correlation
    def corr_wins(self, w1, w2):
        corr = sps.correlate(w1, w2)
        shift_amt = np.argmax(corr) - len(corr) // 2
        return shift_amt

    def perform_analysis(self, audio=None):
        if audio is None:
            audio, _ = self.load_audio()

        FREQ_GUESS = 6.
        WINDOW_LEN = 2000
        PEAK_PROMINENCE = 0.003

        # throw out first and last ticks
        distance = int(self.fs/FREQ_GUESS*.9)
        win_size = int(self.fs/FREQ_GUESS)
        comp_audio = audio[win_size:-win_size]
        # filtered_audio, envelope = calculate_envelope(comp_audio)

        peaks = sps.find_peaks(comp_audio, distance=distance, prominence=PEAK_PROMINENCE, wlen=distance)[0]
        # throw out first and last peaks
        peaks = peaks[1:-1]

        shifted_peaks = copy.copy(peaks)
        for i in range(len(peaks)-1):
            win1_start = peaks[i]-WINDOW_LEN//2
            if win1_start < 0:
                win1_start = 0
            win1_end = peaks[i]+WINDOW_LEN//2 + 1
            if win1_end > len(comp_audio):
                win1_end = len(comp_audio)
            win1 = comp_audio[win1_start:win1_end]

            win2_start = peaks[i+1]-WINDOW_LEN//2
            if win2_start < 0:
                win2_start = 0
            win2_end = peaks[i+1]+WINDOW_LEN//2
            if win2_end > len(comp_audio):
                win2_end = len(comp_audio)
            win2 = comp_audio[win2_start:win2_end]

            shift_amt = self.corr_wins(win1, win2)
            shifted_peaks[i+1] -= shift_amt


        onset_times = peaks / self.fs
        diffs = np.diff(onset_times)
        print(np.sum((diffs>.3).astype(int)))

        audio_dur = len(audio) / self.fs
        f_fund = 6
        print(len(onset_times))
        print(onset_times[0] + (len(onset_times) - 1) * 1./f_fund)

        actual_last_click_time = onset_times[-1]
        ideal_last_click_time = onset_times[0] + (len(onset_times) - 1) * 1./f_fund

        drift = ideal_last_click_time - actual_last_click_time
        drift_per_sec = drift / audio_dur

        print(f"first click time: {onset_times[0]}")
        print(f"actual last click time: {actual_last_click_time}")
        print(f"ideal last click time: {ideal_last_click_time}")
        print(f"{drift} shift in {audio_dur} s")

        def print_drift_over_time(drift_per_sec, seconds, dur_string):
            drift = drift_per_sec * seconds
            units = "s"
            if abs(drift) > 60:
                drift /= 60.
                units = "m"
            print(f"{drift:.2f} {units} drift in a {dur_string}")


        # day
        SEC_IN_DAY = 86400
        print_drift_over_time(drift_per_sec, SEC_IN_DAY, "day")

        # week
        SEC_IN_WEEK = SEC_IN_DAY * 7
        print_drift_over_time(drift_per_sec, SEC_IN_WEEK, "week")
        # month
        SEC_IN_MONTH = SEC_IN_DAY * 30
        print_drift_over_time(drift_per_sec, SEC_IN_MONTH, "month (30 days)")

        # year
        SEC_IN_YEAR =  SEC_IN_DAY * 365
        print_drift_over_time(drift_per_sec, SEC_IN_YEAR, "year (365 days)")


    def generate_figures(self, audio=None):
        # load data from store
        if audio is None:
            audio, _ = self.load_audio()

        # create figures
        fig = plt.figure(figsize=(8,2))
        fig.canvas.header_visible = False
        plt.plot(audio)
        plt.axis('off')
        plt.gca().set_position([0, 0, 1, 1])
        plt.savefig("fig1.svg")

        # create HTML bokeh page
        p = figure(title="Basic Title")#, plot_width=300, plot_height=300)
        p.circle([1, 2], [3, 4])
        output_file("fig1.html")
        save(p)

