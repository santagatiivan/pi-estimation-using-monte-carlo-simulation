import math
import tkinter as tk
from tkinter import simpledialog, ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import os

def get_download_folder():
    """Return the default downloads path for Linux or Windows"""
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            return winreg.QueryValueEx(key, downloads_guid)[0]
    return os.path.join(os.path.expanduser('~'), 'downloads')

def draw_circle_and_square(ax):
    ax.clear()
    ax.set_xlim(-1, 1)
    ax.set_ylim(-1, 1)
    ax.set_aspect('equal')
    circle = plt.Circle((0, 0), 1, edgecolor='blue', facecolor='none', linewidth=1.5)
    ax.add_patch(circle)
    square = plt.Rectangle((-1, -1), 2, 2, edgecolor='black', fill=None, linewidth=1.5)
    ax.add_patch(square)
    ax.axhline(0, color='black', linewidth=0.5)
    ax.axvline(0, color='black', linewidth=0.5)

class MonteCarloPiSimulator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pi Estimation Using Monte Carlo Simulation")
        self.geometry("600x625")  # Optional: Adjust size as needed
        
        self.NUM_POINTS_PER_FRAME = 1000
        self.DELAY_MS = 10
        self.MARKER_SIZE = 1
        self.ALPHA = 0.6
        self.sim_running = False

        self.fig, self.ax = plt.subplots(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=2, column=0, columnspan=4)
        
        self.draw_circle_and_square()

        self.control_frame = tk.Frame(self)
        self.control_frame.grid(row=0, column=0, columnspan=5, sticky="ew", padx=20, pady=10)

        self.setup_sliders()
        self.setup_buttons()
        self.setup_labels()

    def setup_sliders(self):
        tk.Label(self.control_frame, text="Speed:").grid(row=0, column=0, sticky="w")
        self.speed_control = ttk.Scale(self.control_frame, from_=1, to_=100, orient="horizontal",
                                       command=self.adjust_speed)
        self.speed_control.grid(row=1, column=0, padx=10)
        self.speed_control.set(10)

        tk.Label(self.control_frame, text="Marker Size:").grid(row=0, column=1, sticky="w")
        self.marker_size_control = ttk.Scale(self.control_frame, from_=1, to_=10, orient="horizontal",
                                             command=self.adjust_marker_size)
        self.marker_size_control.grid(row=1, column=1, padx=10)
        self.marker_size_control.set(1)

        tk.Label(self.control_frame, text="Alpha:").grid(row=0, column=2, sticky="w")
        self.alpha_control = ttk.Scale(self.control_frame, from_=0.1, to_=1.0, orient="horizontal",
                                       command=self.adjust_alpha)
        self.alpha_control.grid(row=1, column=2, padx=10)
        self.alpha_control.set(0.6)

    def setup_buttons(self):
        start_button = tk.Button(self, text="Start", command=self.start_simulation)
        start_button.grid(row=3, column=0, padx=5, pady=5)

        pause_button = tk.Button(self, text="Pause", command=self.stop_simulation)
        pause_button.grid(row=3, column=1, padx=5, pady=5)

        reset_button = tk.Button(self, text="Reset", command=self.reset_simulation)
        reset_button.grid(row=3, column=2, padx=5, pady=5)

        save_button = tk.Button(self, text="Save Results", command=self.save_results)
        save_button.grid(row=3, column=3, padx=5, pady=5)

    def setup_labels(self):
        self.total_points = 0
        self.points_inside_circle = 0
        self.pi_estimate = 0
        self.absolute_error_value = 0  
        self.percentage_error_value = 0  
        self.total_points_label = tk.Label(self, text="Total Points: 0")
        self.total_points_label.grid(row=4, column=0, pady=(0,10))
        self.points_inside_label = tk.Label(self, text="Points Inside Circle: 0")
        self.points_inside_label.grid(row=4, column=1, pady=(0,10))
        self.pi_estimate_label = tk.Label(self, text="Pi Estimate: 0.000000")
        self.pi_estimate_label.grid(row=4, column=2, pady=(0,10))
        self.absolute_error = tk.Label(self, text="Absolute error: 0.000000")
        self.absolute_error.grid(row=4, column=3, pady=(0,10))  
        self.percentage_error = tk.Label(self, text="%Error: 0.000000")
        self.percentage_error.grid(row=4, column=4, pady=(0,10))


    def draw_circle_and_square(self):
        draw_circle_and_square(self.ax)
        self.canvas.draw_idle()

    def adjust_speed(self, value):
        self.NUM_POINTS_PER_FRAME = int(float(value)) * 10
        self.DELAY_MS = max(1, 110 - int(float(value)))

    def adjust_marker_size(self, value):
        self.MARKER_SIZE = int(float(value))

    def adjust_alpha(self, value):
        self.ALPHA = float(value)

    def start_simulation(self):
        if not self.sim_running:
            self.sim_running = True
            self.simulate_pi()

    def stop_simulation(self):
        self.sim_running = False

    def reset_simulation(self):
        self.total_points = 0
        self.points_inside_circle = 0
        self.pi_estimate = 0
        self.draw_circle_and_square()
        self.update_labels()

    def save_results(self):
        try:
            downloads_path = get_download_folder()
            directory_name = simpledialog.askstring("Directory Name", "Enter the name of the directory to save results:")
            if directory_name:
                full_path = os.path.join(downloads_path, directory_name)
                if not os.path.exists(full_path):
                    os.makedirs(full_path)
                self.fig.savefig(os.path.join(full_path, "graph.png"))
                with open(os.path.join(full_path, "data.txt"), 'w') as file:
                    file.write(f"Total Points: {self.total_points}\n")
                    file.write(f"Points Inside Circle: {self.points_inside_circle}\n")
                    file.write(f"Pi Estimate: {self.pi_estimate}\n")
                    file.write(f"Absolute Error: {self.absolute_error_value:.6f}")  
                    file.write(f"%Error: {self.percentage_error_value:.6f}&percnt;")  

        except Exception as e:
            messagebox.showerror("Error Saving Results", str(e))


    def simulate_pi(self):
        if self.sim_running:
            inside_x = []
            inside_y = []
            outside_x = []
            outside_y = []

            for _ in range(self.NUM_POINTS_PER_FRAME):
                x, y = random.uniform(-1, 1), random.uniform(-1, 1)
                if x**2 + y**2 <= 1:
                    self.points_inside_circle += 1
                    inside_x.append(x)
                    inside_y.append(y)
                else:
                    outside_x.append(x)
                    outside_y.append(y)

            self.ax.plot(inside_x, inside_y, 'go', markersize=self.MARKER_SIZE, alpha=self.ALPHA)
            self.ax.plot(outside_x, outside_y, 'ro', markersize=self.MARKER_SIZE, alpha=self.ALPHA)

            self.total_points += self.NUM_POINTS_PER_FRAME
            self.pi_estimate = 4 * self.points_inside_circle / self.total_points
            
            absolute_error, percentage_error = self.calculate_error()
            self.absolute_error_value = absolute_error
            self.percentage_error_value = percentage_error

            self.update_labels()

            self.canvas.draw_idle()
            self.after(self.DELAY_MS, self.simulate_pi)  


    def update_labels(self):
        self.total_points_label.config(text=f"Total Points: {self.total_points}")
        self.points_inside_label.config(text=f"Points Inside Circle: {self.points_inside_circle}")
        self.pi_estimate_label.config(text=f"Pi Estimate: {self.pi_estimate:.6f}")
        self.absolute_error.config(text=f"Absolute error: {self.absolute_error_value:.6f}")  
        self.percentage_error.config(text=f"%Error: {self.percentage_error_value:.6f}") 


    def calculate_error(self):
        true_pi = math.pi
        absolute_error = abs(true_pi - self.pi_estimate)
        percentage_error = (absolute_error / true_pi) * 100
        return absolute_error, percentage_error

if __name__ == "__main__":
    app = MonteCarloPiSimulator()
    app.mainloop()
