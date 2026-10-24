import os
import pandas as pd
import matplotlib.pyplot as plt

main_folder = "output"
exclude_word = "parameters"

def build_graphic(data_file, graph_folder):
    try:
        data = pd.read_csv(data_file)
    except FileNotFoundError:
        print(f"File {data_file} was not found")
        return

    file_name = os.path.basename(data_file).replace('.csv', '')

    plt.figure(figsize=(12, 6))
    plt.plot(data['trial'], data['current_db'], marker='o', linestyle='-', color='b', label='Results')
    plt.xlabel('Trial number')
    plt.ylabel('Maskee intensity [dB]')
    plt.title(f'Experiment - {file_name}')
    plt.legend()
    plt.grid()

    graph_path = os.path.join(graph_folder, f"{file_name.replace('.txt', '.png')}")
    plt.savefig(graph_path)
    plt.close()

# All folders in output
for subfolder in os.listdir(main_folder):
    subfolder_path = os.path.join(main_folder, subfolder)

    if os.path.isdir(subfolder_path):
        print(f"Folder: {subfolder_path}")

        graph_folder_name = f"{subfolder}_graph"
        folder_graph = os.path.join(main_folder, graph_folder_name)
        os.makedirs(folder_graph, exist_ok=True)

        # All files for each subfolder
        for file in os.listdir(subfolder_path):
            if file.endswith(".csv") and exclude_word not in file:
                file_path = os.path.join(subfolder_path, file)
                print(f"CSV-file: {file_path}")
                build_graphic(file_path, folder_graph)

