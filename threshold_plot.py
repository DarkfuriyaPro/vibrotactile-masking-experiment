import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

main_folder = "evaluation"
csv_folder_name = "evaluation_results/evaluation_results_all.csv"
csv_file_path = os.path.join(main_folder, csv_folder_name)

graph_folder_name = "evaluation_results_plot"
evaluation_graph_folder = os.path.join(main_folder, graph_folder_name)
os.makedirs(evaluation_graph_folder, exist_ok=True)

data = pd.read_csv(csv_file_path)

plt.figure(figsize=(12, 6))

# Цвета для каждого эксперимента
colors = {1: "blue", 2: "gray", 3: "gray", 4: "lightblue"}

# Проходим по каждому эксперименту
for exp in data["experiment"].unique():
    exp_data = data[data["experiment"] == exp]

    exp_data_sorted = exp_data.sort_values("maskee frequency")

    if exp == 4:
        # Для эксперимента 4 точки не соединяются
        true_masker = exp_data_sorted[exp_data_sorted["play_masker"] == True]
        false_masker = exp_data_sorted[exp_data_sorted["play_masker"] == False]

        # Используем разные цвета для "Masker=True" и "Masker=False"
        plt.plot(true_masker["maskee frequency"], true_masker["threshold"],
                 marker="o", linestyle="None", color=colors[exp],
                 label=f'Participant 1, Masker=True, Maskee=200Hz')  # Название "Participant 1"
        plt.plot(false_masker["maskee frequency"], false_masker["threshold"],
                 marker="s", linestyle="None", color=colors[exp],
                 label=f'Participant 1, Masker=False, Maskee=200Hz')  # Название "Participant 1"
    else:
        true_masker = exp_data_sorted[exp_data_sorted["play_masker"] == True]
        if exp == 2 or exp == 3:
            plt.plot(true_masker["maskee frequency"], true_masker["threshold"],
                     marker="o", linestyle="-", color=colors[exp], alpha=0.3)
        else:
            plt.plot(true_masker["maskee frequency"], true_masker["threshold"],
                     marker="o", linestyle="-", color=colors[exp], label=f'Participant {exp}, Masker=True')

        false_masker = exp_data_sorted[exp_data_sorted["play_masker"] == False]
        if exp == 2 or exp == 3:
            plt.plot(false_masker["maskee frequency"], false_masker["threshold"],
                     marker="s", linestyle="None", color=colors[exp], alpha=0.3)
        else:
            plt.plot(false_masker["maskee frequency"], false_masker["threshold"],
                     marker="s", linestyle="None", color=colors[exp], label=f'Participant {exp}, Masker=False')

# Добавляем подписи
plt.xlabel("Maskee frequency [Hz]")
plt.ylabel("Threshold")
plt.title("Thresholds for Participants [1, 2, 3]")
plt.legend()
plt.grid(True)

# Показываем график
plt.show()

"""
# Отбираем данные, где play_masker=False и play_masker=True
false_masker_df = data[data["play_masker"] == False]  # play_masker = False
true_masker_df = data[data["play_masker"] == True]  # play_masker = True

# Создаём пустой список для разниц threshold
differences = []

# Вычисляем разницу threshold для каждого эксперимента
for exp in data["experiment"].unique():
    false_thresholds = false_masker_df[false_masker_df["experiment"] == exp]["threshold"].values
    true_thresholds = true_masker_df[true_masker_df["experiment"] == exp][["threshold", "maskee frequency"]]

    # Если есть хотя бы одно значение с play_masker=False, вычитаем из всех play_masker=True
    if len(false_thresholds) > 0:
        diff_values = []
        for _, row in true_thresholds.iterrows():
            diff = row["threshold"] - false_thresholds[0]  # Берём первое значение threshold для play_masker=False
            diff_values.append({"experiment": exp, "maskee frequency": row["maskee frequency"], "difference": diff})

        differences.extend(diff_values)

# Создаём DataFrame с разностями
diff_df = pd.DataFrame(differences)

# Визуализация
plt.figure(figsize=(12, 6))
colors = {1: "blue", 2: "green", 3:  "red"}

for exp in diff_df["experiment"].unique():
    exp_data = diff_df[diff_df["experiment"] == exp]
    sorted_data = exp_data.sort_values("maskee frequency")  # Сортируем по частоте
    plt.plot(sorted_data["maskee frequency"], sorted_data["difference"],
             marker="o", color=colors[exp], linestyle="-", label=f'Experiment {exp}')

plt.xlabel("Maskee Frequency")
plt.ylabel("Threshold")
plt.title("Difference between Thresholds (play_masker=True - play_masker=False)")
plt.legend()
plt.grid(True)
plt.show()


# --- Функция для расчета Mittelwert и Standardabweichung ---
def plot_mean_std(diff_df):
    grouped = diff_df.groupby("maskee frequency")["difference"].agg(["mean", "std"]).reset_index()

    plt.figure(figsize=(12, 6))
    plt.errorbar(grouped["maskee frequency"], grouped["mean"], yerr=grouped["std"],
                 fmt="o-", capsize=5, label="Mean ± Std")

    plt.xlabel("Maskee Frequency")
    plt.ylabel("Threshold")
    plt.title("Mittelwert und Standardabweichung der Threshold Difference")
    plt.legend()
    plt.grid(True)
    plt.show()


# Вызываем функцию для построения Mittelwert и Standardabweichung
plot_mean_std(diff_df)
"""



"""
# График 2: Средние значения и стандартные отклонения
means = data.groupby('maskee frequency')['threshold'].mean()
stds = data.groupby('maskee frequency')['threshold'].std()

means_adjusted = grouped_adjusted.mean()
stds_adjusted = grouped_adjusted.std()

plt.figure(figsize=(12, 6))
plt.errorbar(means.index, means, yerr=stds, fmt='o-', capsize=5, label='Mean ± Std')
plt.errorbar(means_adjusted.index, means_adjusted, yerr=stds_adjusted, fmt='o-', capsize=5, linestyle='dashed', label='Adjusted Mean ± Std')
plt.xlabel('Maskee Frequency (Hz)')
plt.ylabel('Threshold')
plt.title('Mean and Adjusted Thresholds with Standard Deviation')
plt.legend()
plt.grid()
graph_path_mean_std = os.path.join(evaluation_graph_folder, "mean_std_adjusted_thresholds.png")
plt.savefig(graph_path_mean_std)
plt.show()
"""


"""
for i, exp in enumerate(selected_experiments):
    for play_masker_value, marker in zip([True, False], ['o', 's']):
        exp_data = data[(data['experiment'] == exp) & (data['play_masker'] == play_masker_value)]
        data_group = exp_data.groupby('maskee frequency')
        threshold = data_group['normalized_threshold'].mean()

        plt.plot(threshold.index, threshold, marker=marker, linestyle='-',
                 color=colors[i % len(colors)], label=f'Participant {exp}, Masker={play_masker_value}')

plt.xlabel('Maskee frequency [Hz]')
plt.ylabel('Threshold relative to mean [dB]')
plt.title('Relative Thresholds for Participants')
plt.legend()
plt.grid()

graph_path = os.path.join(evaluation_graph_folder, "relative_thresholds.png")
plt.savefig(graph_path)
plt.show()

# 📌 2. График среднего значения threshold и стандартного отклонения
plt.figure(figsize=(12, 6))

mean_threshold = data.groupby("maskee frequency")["threshold"].mean()
std_threshold = data.groupby("maskee frequency")["threshold"].std()

plt.errorbar(mean_threshold.index, mean_threshold, yerr=std_threshold, fmt='o-', capsize=5, color='b', label="Mean ± Std Dev")

plt.xlabel("Maskee frequency [Hz]")
plt.ylabel("Threshold [dB]")
plt.title("Mean and Standard Deviation of Thresholds")
plt.legend()
plt.grid()

graph_path = os.path.join(evaluation_graph_folder, "mean_std_thresholds.png")
plt.savefig(graph_path)
plt.show()
"""