import tkinter as tk

import experiment as e
import threshold as t
import pandas as pd

BORDER = 0

current_index = 0
current_param = None

class GUI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Experiment")
        self.window.geometry("360x160")
        self.window.resizable(False, False)

        self.frame1 = tk.Frame(self.window, width=100, height=100, bg="gray")
        self.frame1.place(x=10, y=50)
        self.frame1.pack_propagate(False)

        self.frame2 = tk.Frame(self.window, width=100, height=100, bg="gray")
        self.frame2.place(x=130, y=50)
        self.frame2.pack_propagate(False)

        self.frame3 = tk.Frame(self.window, width=100, height=100, bg="gray")
        self.frame3.place(x=250, y=50)
        self.frame3.pack_propagate(False)

        self.finish_frame = tk.Frame(self.window, bg="#8710c7", width=300, height=100, bd=10, relief="sunken")
        self.finish_label = tk.Label(self.finish_frame, text="Experiment finished.", font=("Arial", 14), fg="#62f7fc", bg="#8710c7")

        self.pause_frame = tk.Frame(self.window, bg="#8710c7", width=360, height=160)
        self.pause_label = tk.Label(self.pause_frame, text="Make a tea break, then press the 'Continue' button.", font=("Arial", 14), fg="#8710c7", bg="#62f7fc", bd = 4, relief="sunken",
            wraplength=340,
            justify="center"
        )

        self.start_button = tk.Button(self.window, text="Start", command=lambda: (self.on_start_pressed(), self.start_experiment()))
        self.start_button.place(relx=0.4, rely=0)

        self.next_button = tk.Button(self.window, text="Next", state=tk.DISABLED, command=lambda: self.on_next_pressed())

        self.left_button = tk.Button(self.frame1, text="1", command=lambda: self.answer_selected(1), state=tk.DISABLED, font=("Arial", 20), fg="black", highlightbackground="gray", borderwidth=BORDER)
        self.left_button.pack(padx=10, pady=10, expand=True, fill="both")

        self.center_button = tk.Button(self.frame2, text="2", command=lambda: self.answer_selected(2), state=tk.DISABLED, font=("Arial", 20), fg="black", highlightbackground="gray", borderwidth=BORDER)
        self.center_button.pack(padx=10, pady=10, expand=True, fill="both")

        self.right_button = tk.Button(self.frame3, text="3", command=lambda: self.answer_selected(3), state=tk.DISABLED, font=("Arial", 20), fg="black", highlightbackground="gray", borderwidth=BORDER)
        self.right_button.pack(padx=10, pady=10, expand=True, fill="both")

        self.continue_button = tk.Button(self.window, text="Continue", state=tk.DISABLED, command=lambda: (self.on_continue_pressed(), self.on_next_pressed()))




    def on_start_pressed(self):
        self.start_button.place_forget()
        self.next_button.place(relx=0.4, rely=0)

    def start_experiment(self):
        global current_index, current_param
        self.disable_next_button()
        if current_index < len(e.combinations):
            current_param = e.combinations[current_index]
            print(f"Maskee frequency: {current_param.maskee_frequency}")
            if current_param.reversal_counter >= 3:
                print("Reversal counter reached 3:", current_param.step_size_db)
                e.save_to_csv(current_index, current_param)
                self.disable_answer_buttons()
                if current_index == e.len_absolute_thresholds-1:
                    self.show_pause_window()
                return
            else:
                current_param.play_stimulus(self.highlight_frame)
                self.enable_answer_buttons()
        else:
            print("Experiment finished.")

    def answer_selected(self, chosen_interval):
        global current_param
        self.reset_highlight()
        self.disable_answer_buttons()
        if current_index < len(e.combinations):
            current_param = e.combinations[current_index]
            current_param.choose_answer(chosen_interval, self.highlight_frame, self.reset_highlight)
            self.start_experiment()
            self.enable_next_button()

    def on_next_pressed(self):
        global current_index, current_param
        self.reset_highlight()
        self.disable_answer_buttons()

        if current_index < len(e.combinations) - 1:
            current_index += 1
            print(f"Current index {current_index}")
            current_param = e.combinations[current_index]
            print(f"Switched to parameter {current_index + 1}")
            self.disable_next_button()
            current_param.play_stimulus(self.highlight_frame)
            self.enable_answer_buttons()
        else:
            print("Experiment finished.")
            self.disable_next_button()
            self.disable_answer_buttons()
            #evaluate_results()
            self.finish_experiment()



    def show_pause_window(self):
        global current_param
        self.disable_answer_buttons()
        self.pause_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.pause_label.pack(expand=True)
        self.next_button.place_forget()
        self.continue_button.place(relx=0.4, rely=0)
        self.enable_continue_button()
        # evaluate results
        found_folders = t.find_folder()
        t.select_csv(found_folders)
        data_file = t.get_output_filename()
        # filter for current participant
        data = pd.read_csv(data_file)
        experiment_index = e.EXPERIMENT_INDEX
        data = data[data['experiment'] == experiment_index]
        # looop:
        for parameters in e.combinations:
            if parameters.play_masker:
                threshold = data[data['maskee frequency'] == parameters.masker_frequency]
                threshold = threshold['threshold'].iloc[0]
                parameters.initial_maskee_db = threshold + 45
                parameters.current_db = threshold + 45
                parameters.initial_masker_db = threshold + 25
                print("threshold used for experiment at "+str(parameters.masker_frequency)+" Hz: "+str(threshold))


    def on_continue_pressed(self):
        self.pause_frame.place_forget()
        self.continue_button.place_forget()
        self.next_button.place(relx=0.4, rely=0)

    def finish_experiment(self):
        for widget in self.window.winfo_children():
            widget.place_forget()
        self.finish_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.finish_label.pack(expand=True)



    def enable_answer_buttons(self):
        self.left_button.config(state=tk.NORMAL)
        self.center_button.config(state=tk.NORMAL)
        self.right_button.config(state=tk.NORMAL)

    def disable_answer_buttons(self):
        self.left_button.config(state=tk.DISABLED)
        self.center_button.config(state=tk.DISABLED)
        self.right_button.config(state=tk.DISABLED)

    def disable_next_button(self):
        self.next_button.config(state = tk.DISABLED)

    def enable_next_button(self):
        self.next_button.config(state=tk.NORMAL)

    def enable_continue_button(self):
        self.continue_button.config(state = tk.NORMAL)


    """ Change the color of the frame for each interval. """
    def highlight_frame(self, interval):
        if interval == 1:
            self.frame1.config(bg="lightblue")
            self.left_button.config(highlightbackground="lightblue", borderwidth=BORDER)
        elif interval == 2:
            self.frame2.config(bg="lightyellow")
            self.center_button.config(highlightbackground="yellow", borderwidth=BORDER)
        elif interval == 3:
            self.frame3.config(bg="lightgreen")
            self.right_button.config(highlightbackground="lightgreen", borderwidth=BORDER)
        self.window.update()

    """ Resetting the color selection after all intervals are played. """
    def reset_highlight(self):
        self.frame1.config(bg="gray")
        self.left_button.config(highlightbackground="gray", borderwidth=BORDER)
        self.frame2.config(bg="gray")
        self.center_button.config(highlightbackground="gray", borderwidth=BORDER)
        self.frame3.config(bg="gray")
        self.right_button.config(highlightbackground="gray", borderwidth=BORDER)
        self.window.update()

if __name__ == "__main__":
    new_folder = e.create_experiment_folder()
    gui = GUI()
    gui.window.mainloop()
