import pandas as pd
import os
import random

from parameters import Parameters

# Initialize a list to store experiment data
EXPERIMENT_FOLDER = None
EXPERIMENT_INDEX = None
param0 = Parameters(maskee_frequency=200,  initial_maskee_db=-20, masker_frequency=100, play_masker=False)
#param1 = Parameters(maskee_frequency=500,  initial_maskee_db=-20, masker_frequency=200, play_masker=False)
#param2 = Parameters(maskee_frequency=100, initial_maskee_db=-20, masker_frequency=300, play_masker=False)

# params for automatic change of parameters
param3 = Parameters(maskee_frequency=140, initial_maskee_db=-20, masker_frequency=200, play_masker=True)
param4 = Parameters(maskee_frequency=160, initial_maskee_db=-20, masker_frequency=200, play_masker=True)
param5 = Parameters(maskee_frequency=180, initial_maskee_db=-20, masker_frequency=200, play_masker=True)
param6 = Parameters(maskee_frequency=200, initial_maskee_db=-20, masker_frequency=200, play_masker=True)
param7 = Parameters(maskee_frequency=220, initial_maskee_db=-20, masker_frequency=200, play_masker=True)
param8 = Parameters(maskee_frequency=240, initial_maskee_db=-20, masker_frequency=200, play_masker=True)
param9 = Parameters(maskee_frequency=260, initial_maskee_db=-20, masker_frequency=200, play_masker=True)
combinations = [param0]
len_absolute_thresholds = len(combinations)
random.shuffle(combinations)
combinations_masker = [param3,param4,param5,param6,param7,param8,param9]
random.shuffle(combinations_masker)
combinations.extend(combinations_masker)

def create_experiment_folder(base_path="output", prefix="experiment"):
    global EXPERIMENT_FOLDER, EXPERIMENT_INDEX
    os.makedirs(base_path, exist_ok=True)

    number = 1
    while True:
        folder_name = f"{prefix}_{number}"
        folder_path = os.path.join(base_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder created: {folder_path}")
            EXPERIMENT_FOLDER = folder_path
            EXPERIMENT_INDEX = number
            return folder_path
        number += 1

""" Function to save data to CSV """
def save_to_csv(i, parameters: Parameters):
    global EXPERIMENT_FOLDER
    if not EXPERIMENT_FOLDER:
        raise ValueError("Experiment folder is not set. Please create it before saving data.")
    else:
        file_path = os.path.join(EXPERIMENT_FOLDER, f"experiment_results_{i}.csv")
        df = pd.DataFrame(parameters.experiment_data, columns=['trial', 'answer', 'current_db', 'current_amplitude_maskee'])
        df.to_csv(file_path, index=False)

        parameters = [parameters.maskee_frequency, parameters.initial_maskee_db , parameters.masker_frequency, parameters.play_masker]
        df = pd.DataFrame([parameters], columns=['maskee_frequency', 'maskee_db', 'masker_frequency', 'play_masker'])
        file_path = os.path.join(EXPERIMENT_FOLDER, f"experiment_parameters_{i}.csv")
        df.to_csv(file_path, index=False)

        print(f"Data saved to {file_path}")



