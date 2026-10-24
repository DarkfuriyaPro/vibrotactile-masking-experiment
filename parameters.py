import numpy as np
import time
from random import randint
import sounddevice as sd
import windowing_plot
import utils as u
from calibration import Player

class Parameters:

    #constants (not changing between runs)
    stimulus_duration = 1.0  # 1s
    pause_duration = 0.5  # 600ms
    pause_choice = 1.0  # 1s
    sample_rate = 2800
    reference_level_lin = 1 #TODO: set to 1 or remove for final version
    target_rms = 1
    window_time = 0.05  # in seconds
    correct_answers = 0
    interval_with_maskee = None
    reversal = None
    track_last_answer = None  # Track the last answer correctness to identify reversals
    reversal_counter = 0
    step_size_db = 8
    plot_saved = False


    player = Player(sample_rate,True)

    def __init__(self, maskee_frequency, initial_maskee_db, masker_frequency, play_masker):
        self.play_masker = play_masker

        self.maskee_frequency = maskee_frequency
        self.initial_maskee_db = initial_maskee_db
        self.current_db = self.initial_maskee_db

        self.experiment_data = []

        self.width = 0.1
        self.initial_masker_db = -10
        self.masker_frequency = masker_frequency
        self.low_masker_frequency = self.masker_frequency * (1 - self.width)
        self.high_masker_frequency = self.masker_frequency * (1 + self.width)

    """ Maskee """
    def generate_sine_wave(self):
        amplitude = u.db_to_amplitude(self.current_db) * self.reference_level_lin
        t = np.linspace(0, self.stimulus_duration, int(self.sample_rate * self.stimulus_duration), endpoint=False)
        wave = np.sin(2 * np.pi * self.maskee_frequency * t)
        wave = u.normalize_to_rms(wave, self.target_rms)
        wave = amplitude * wave
        original_wave = wave.copy()
        # 5% from signal
        wave = u.windowing(wave, int(self.sample_rate * self.window_time))
        if not self.plot_saved:
            windowing_plot.plot_windowed_signal(t, original_wave, wave, "Sine Wave with Windowing")
            print("Windowing saved")
            self.plot_saved = True
        #print("Max amplitude of sine wave:", np.max(np.abs(wave)))
        return wave

    """ Masker """
    def generate_white_noise(self):
        amplitude = u.db_to_amplitude(self.initial_masker_db) * self.reference_level_lin
        noise = np.random.normal(0, 1, int(self.sample_rate * self.stimulus_duration))
        noise = u.bandpass_filter(noise, self.low_masker_frequency, self.high_masker_frequency, self.sample_rate)
        noise = u.normalize_to_rms(noise, self.target_rms)
        noise = amplitude * noise
        original_noise = noise.copy()
        # 5% from signal
        noise = u.windowing(noise, int(self.sample_rate * self.window_time))
        if not self.plot_saved:
            windowing_plot.plot_windowed_signal(np.linspace(0, self.stimulus_duration, len(original_noise)),original_noise, noise, "White Noise with Windowing")
            print("Windowing saved")
            self.plot_saved = False
        #print("Max amplitude of white noise:", np.max(np.abs(noise)))
        return noise
    
    """ Play three intervals """
    def play_stimulus(self, highlight_frame):
        # Randomly-selected interval with maskee
        self.interval_with_maskee = randint(1, 3)
        print(f"Interval with maskee: {self.interval_with_maskee}")

        masker = self.generate_white_noise() if self.play_masker else None
        #if self.play_masker:
            #print("Normalized RMS amplitude of masker:", u.calculate_rms(masker))
        maskee = self.generate_sine_wave()
        #print("Normalized RMS amplitude of maskee:", u.calculate_rms(maskee))

        for interval in range(1, 4):
            highlight_frame(interval)
            if self.interval_with_maskee == interval:
                if self.play_masker:
                    # Combine sounds so the masker and maskee sound together
                    stereo_signal = np.column_stack((masker, maskee))
                    sd.play(stereo_signal)

                    max_val = np.max(np.abs(stereo_signal))
                    if max_val >= 1.0 or max_val <= -1.0:
                        print("WARNING: Signal level too high")
                else:
                    zeros = np.zeros_like(maskee)
                    stereo_signal = np.column_stack((zeros, maskee))
                    self.player.play_sound_stereo(stereo_signal)
            else:
                if self.play_masker:

                    zeros = np.zeros_like(masker)
                    stereo_signal = np.column_stack((masker, zeros))
                    sd.play(stereo_signal)  # Only masker plays

                    max_val = np.max(np.abs(stereo_signal))
                    if max_val >= 1.0 or max_val <= -1.0:
                        print("WARNING: Signal level too high")
                else:
                    zeros = np.zeros_like(maskee)
                    stereo_signal = np.column_stack((zeros, zeros))
                    self.player.play_sound_stereo(stereo_signal)

            time.sleep(self.pause_duration + self.stimulus_duration)

    """ Subject chooses the interval. """
    def choose_answer(self, chosen_interval, highlight_frame, reset_highlight):

        trial_data = {
            'trial': len(self.experiment_data) + 1,
            'answer': "correct" if chosen_interval == self.interval_with_maskee else "wrong",
            'current_db': self.current_db,
            'current_amplitude_maskee': u.db_to_amplitude(self.current_db) * self.reference_level_lin
        }

        if chosen_interval == self.interval_with_maskee:
            print("Correct!")
            self.correct_answers += 1
            if self.correct_answers == 3:
                self.experiment_data.append(trial_data)

                if self.track_last_answer is False:  # Reversal detected
                    if self.step_size_db <= 0.5:
                        self.reversal_counter += 1
                        print("Reversal counter: ", self.reversal_counter)
                    else:
                        self.step_size_db /= 2
                self.track_last_answer = True

                # Reduction in the amplitude of the maskee (dB)
                self.current_db -= self.step_size_db
                # Convert difference to amplitude
                current_amplitude_maskee = u.db_to_amplitude(self.current_db) * self.reference_level_lin
                print(f"Current amplitude: {current_amplitude_maskee:.3f}, reduction of the amplitude: {self.step_size_db}, current dB value: {self.current_db}")

                self.correct_answers = 0

            else:
                self.experiment_data.append(trial_data)
                self.current_db = self.current_db
        else:
            print("Wrong!")
            self.correct_answers = 0
            # Increase the amplitude of the maskee
            self.experiment_data.append(trial_data)
            self.current_db += self.step_size_db
            current_amplitude_maskee = u.db_to_amplitude(self.current_db) * self.reference_level_lin
            print(f"Current amplitude: {current_amplitude_maskee:.3f}, increase of the amplitude: {self.step_size_db}, current dB value: {self.current_db}")
            self.track_last_answer = False

        reset_highlight()
        time.sleep(self.pause_choice)