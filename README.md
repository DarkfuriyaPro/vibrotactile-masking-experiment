# Vibrotactile Masking Experiment

Python software for a psychophysical experiment that measures **vibrotactile masking thresholds on the hand**. It was developed for the bachelor thesis *"Spatial Masking of Vibrotactile Signals on the Hand"* (LMU Munich, Department of Informatics, 2025).

A band-limited noise **masker** is played together with a sinusoidal **maskee**. The participant has to find the interval that contains the maskee. The maskee amplitude is adapted until the detection (masking) threshold is found.

## How it works

- **Method:** three-alternative forced choice (3AFC), 3 intervals per trial, the maskee is in one random interval.
- **Adaptive procedure:** 1-up 3-down staircase. Initial step 8 dB, halved at each reversal down to 0.5 dB. A condition ends after three reversals at the minimum step size.
- **Timing:** 1 s stimulus, 0.5 s pause between intervals, 1 s pause between trials.
- **Signals:** sine wave (maskee) and band-pass filtered white noise (masker, +-10 % around the masker frequency). Sample rate 2800 Hz, RMS normalization, Hann window (50 ms) at onset and offset.
- **Two parts:**
  1. Absolute threshold: maskee at 200 Hz, no masker.
  2. Masked thresholds: masker at 200 Hz, maskee at 140-260 Hz (step 20 Hz), random order. Start levels are derived from the measured threshold (maskee: threshold + 45 dB, masker: threshold + 25 dB).
- **Output:** one folder per experiment in `output/` with CSV files (trials and parameters) and PNG plots.

## Hardware

The experiment needs vibrotactile hardware and was run with:

- vibrotactile actuators connected to the audio output (channel 0: masker, channel 1: maskee)
- an accelerometer with a National Instruments DAQ (used **only for calibration**)

Without this hardware the program can start, but the stimuli will not have the intended physical levels.

## Installation

Python 3.10+ is recommended.

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

Notes:

- `tkinter` is part of the standard library. On some Linux systems it has to be installed separately (`sudo apt install python3-tk`).
- `nidaqmx` is needed only for calibration and requires the NI-DAQmx driver from National Instruments.
- The `keyboard` package needs root rights on Linux.

## Usage

Run all commands from the repository root.

1. **Calibration** (before the first experiment, and after any hardware change):
   ```bash
   python calibration_level.py
   ```
2. **Run the experiment** (opens the GUI, press *Start*; after the first part there is a break, then press *Continue*):
   ```bash
   python gui.py
   ```
3. **Plot staircases** (one graph per condition, saved to `output/<experiment>_graph/`):
   ```bash
   python experiment_results_plot.py
   ```
4. **Plot thresholds** (reads `evaluation/evaluation_results/evaluation_results_all.csv`, which is a merge of the `evaluation_results.csv` files of all participants):
   ```bash
   python threshold_plot.py
   ```

## Project structure

| File | Purpose |
|---|---|
| `gui.py` | Entry point. Tkinter GUI, experiment flow, break between the two parts |
| `experiment.py` | List of conditions, experiment folders, saving CSV files |
| `parameters.py` | One condition: signal generation, playback, staircase logic |
| `utils.py` | dB conversion, RMS normalization, band-pass filter, windowing |
| `threshold.py` | Computes thresholds from the saved trials |
| `calibration*.py`, `acc_interface.py` | Calibration of the actuators with an accelerometer |
| `experiment_results_plot.py` | Staircase plots |
| `threshold_plot.py` | Threshold plots |
| `windowing_plot.py` | Plot of original vs. windowed signal |

## Output format

`output/experiment_<n>/`

- `experiment_results_<i>.csv`: columns `trial`, `answer`, `current_db`, `current_amplitude_maskee`
- `experiment_parameters_<i>.csv`: columns `maskee_frequency`, `maskee_db`, `masker_frequency`, `play_masker`

`evaluation/evaluation_results/evaluation_results.csv`: one threshold per condition and experiment.

All levels are given in dB relative to 1 m/s^2 after calibration.

## Thesis

The thesis describes the study design and results in detail: [`docs/thesis.pdf`](docs/thesis.pdf)

## Citation

```
K. Telegina, "Spatial Masking of Vibrotactile Signals on the Hand",
Bachelor thesis, LMU Munich, 2025.
```

## License

The code is released under the MIT License (see `LICENSE`). The thesis text is licensed under CC BY-SA 4.0.
