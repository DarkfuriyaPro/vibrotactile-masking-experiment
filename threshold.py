import os
import pandas as pd
import numpy as np

main_folder = "output"
eval_folder = "evaluation"
output_filename = "evaluation_results.csv"
files_by_folder = {}

exclude_words = {"graph", "windowing"}
word_results = "results"
word_parameters = "parameters"
specific_column = 'current_db'
threshold_values = []
evaluation_table = []
maskee_frequency_column = "maskee_frequency"
masker_frequency_column = "masker_frequency"
is_masker_column = "play_masker"


def find_folder():
    folders = []
    '''Scans everything in folder output'''
    for subfolder_name in os.listdir(main_folder):
        '''Creates a full path to folder or file'''
        subfolder_path = os.path.join(main_folder, subfolder_name)
        '''Check if it is a folder'''
        if os.path.isdir(subfolder_path):
            if any(word in subfolder_name for word in exclude_words):
                '''Skip folders'''
                continue

            '''Check if the folder is empty'''
            if not os.listdir(subfolder_path):
                #print(f"Folder '{subfolder_name}' is empty.")
                continue

            '''Add to the list with found folders'''
            folders.append(subfolder_path)

    folders.sort()
    print(folders)
    return folders

def select_csv(folders):
    for folder in folders:
        experiment_index = extract_experiment_index(folder)
        '''Scan everything in each folder'''
        for file_name in os.listdir(folder):
            if file_name.endswith('.csv'):
                #print(file_name)
                split_files(folder, file_name)

        for i, files in files_by_folder.get(folder, {}).items():
            print(f"Files with index {i} in folder {folder}: {files}")
            threshold = None
            maskee_frequency = None
            masker_frequency = None
            play_masker = None
            for file_name in files:
                '''Full path to the file'''
                file_path = os.path.join(folder, file_name)
                if word_results in file_name:
                    threshold = find_column_threshold(file_path, file_name)
                elif word_parameters in file_name:
                    if maskee_frequency is None:  # Avoid overwriting
                        masker_frequency, maskee_frequency, play_masker = find_column_param(file_path, file_name)

            if threshold is not None and maskee_frequency is not None and masker_frequency is not None and play_masker is not None:
                evaluation_table.append({
                    "experiment": experiment_index,
                    "threshold": threshold,
                    "maskee frequency": maskee_frequency,
                    "masker frequency": masker_frequency,
                    "play_masker": play_masker
                })


    save_to_csv()

def extract_experiment_index(folder_path):
    folder_name = os.path.basename(folder_path)
    experiment_index = folder_name.split('_')[-1]
    return experiment_index

def split_files(folder, file_name):
    '''
        Example:
        Folder experiment1 has experiment_parameters0 и experiment_results0,
        Folder experiment2 has experiment_parameters0 и experiment_results0.
    '''

    '''Array for all folders to differentiate them'''
    if folder not in files_by_folder:
        files_by_folder[folder] = {}
    files_by_index = files_by_folder[folder]

    x = file_name.split("_")[-1]
    x = x.split(".")[0]
    x = int(x)
    # print(x)
    if x not in files_by_index:
        files_by_index[x] = []
    '''Each index for each folder in different arrays'''
    files_by_index[x].append(file_name)
    #print(files_by_folder)


def find_column_threshold(path_to_file, file_name):
    # Read data from files with the same index
    df = pd.read_csv(path_to_file)
    if specific_column in df.columns:
        column_values = df[specific_column].tolist()
        print(f"Values in column '{specific_column}': {column_values}")
        threshold = define_threshold(column_values)
        if threshold is not None:
            print(f"Threshold for file {file_name}: {threshold}")
            return threshold

def find_column_param(path_to_file, file_name):
    # Read data from files with the same index
    df = pd.read_csv(path_to_file)
    masker_values = 0
    maskee_values = 0
    play_masker = None
    if maskee_frequency_column in df.columns:
        maskee_values = df[maskee_frequency_column].tolist()[0]
        print(f"Values in column '{maskee_frequency_column}': {maskee_values}")

    if  masker_frequency_column in df.columns:
        masker_values = df[masker_frequency_column].tolist()[0]
        print(f"Values in column '{masker_frequency_column}': {masker_values}")

    if is_masker_column in df.columns:
        play_masker = df[is_masker_column].tolist()[0]
        print(f"Values in column '{is_masker_column}': {play_masker}")

    return masker_values, maskee_values, play_masker


def define_threshold(column_values):
    for i in range(1, len(column_values)):
        difference = column_values[i] - column_values[i - 1]
        if difference == 0.5:
            threshold = np.mean(column_values[i:])
            #print(f"Threshold: {threshold}")
            return threshold
    print(f"List of threshold values: {threshold_values}")

    print("No threshold calculated.")
    return None



def save_to_csv():
    #Create new folder with evaluation results in output
    folder_evaluation = get_output_folder()
    if not os.path.exists(folder_evaluation):
        os.makedirs(folder_evaluation, exist_ok=False)

    #Save data in csv file
    path = os.path.join(folder_evaluation, output_filename)
    fd = pd.DataFrame(evaluation_table, columns=['experiment','threshold', 'maskee frequency', 'masker frequency', 'play_masker'])
    fd.to_csv(path, index=False)

    print(f"Data saved to {path}")

def get_output_folder():
    evaluation_folder_name = "evaluation_results"
    return os.path.join(eval_folder, evaluation_folder_name)

def get_output_filename():
    return os.path.join(get_output_folder(), output_filename)

if __name__ == "__main__":
    found_folders = find_folder()
    select_csv(found_folders)


