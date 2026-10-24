import matplotlib.pyplot as plt
import os


def plot_windowed_signal(time, original_signal, windowed_signal, title):
    plt.figure(figsize=(10, 6))
    #Original signal
    plt.plot(time, original_signal, label="Original Signal", alpha=0.7)
    #Windowed signal
    plt.plot(time, windowed_signal, label="Windowed Signal", alpha=0.7)
    plt.title(title)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid(True)

    filename = title.replace(" ", "_").lower() + ".png"
    subfolder = os.path.join("output", "windowing_results")
    file_path = os.path.join(subfolder, filename)
    plt.savefig(file_path)
    print(f"Graphic saved in: {filename}")

    plt.close()
