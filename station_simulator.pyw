import tkinter as tk
from tkinter import filedialog
from flask import Flask, jsonify
import threading
import time
 

# Initialize Flask API
app = Flask(__name__)
 
# Global variables
acceleration = 0.0
station_id = 1
pause_api = False
acceleration_values = []
current_index = 0

# Function to generate acceleration data and return station ID
@app.route('/')
def get_acceleration_data():
    global pause_api, acceleration

    if pause_api or not acceleration_values:
        return jsonify([])  # Empty response when the API is paused or no data

    return jsonify([{'acceleration': round(acceleration, 20), 'station_id': station_id}])

# Tkinter GUI setup
class AccelerationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Earthquake Station Simulator")

        # Set window size and make it non-resizable
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Create a frame to hold all widgets and center them
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        # Configure the grid to center elements horizontally
        for i in range(8):
            frame.grid_rowconfigure(i, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Acceleration Label
        self.acceleration_label = tk.Label(frame, text=f"Acceleration: {round(acceleration, 12)} m/s²", font=('Arial', 14))
        self.acceleration_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Load File Button
        self.load_file_button = tk.Button(frame, text="Load File", width=20, height=2, command=self.load_file)
        self.load_file_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Start Button
        self.start_button = tk.Button(frame, text="Start Sending Data", width=20, height=2, command=self.start_sending_data)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Station ID Entry Label
        self.station_id_entry_label = tk.Label(frame, text="Enter Station ID:", font=('Arial', 10))
        self.station_id_entry_label.grid(row=3, column=0, pady=10)

        # Station ID Entry
        self.station_id_entry = tk.Entry(frame, width=15)
        self.station_id_entry.insert(0, str(station_id))  # Default station ID
        self.station_id_entry.grid(row=3, column=1, pady=10)

        # Submit Button
        self.submit_button = tk.Button(frame, text="Submit Station ID", width=20, height=2, command=self.update_station_id)
        self.submit_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Stop Button
        self.stop_button = tk.Button(frame, text="Stop", width=20, height=2, command=self.stop_sending_data)
        self.stop_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.running = False

    def load_file(self):
        """Load acceleration data from a file."""
        global acceleration_values
        file_path = filedialog.askopenfilename(title="Select Acceleration Data File", filetypes=[("Text Files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    # Parse the file and convert values to floats
                    acceleration_values = [float(value) for line in file for value in line.split()]
                print(f"Loaded {len(acceleration_values)} acceleration values from {file_path}.")
                print("events: ", len(acceleration_values))
            except Exception as e:
                print(f"Error loading file: {e}")

    def start_sending_data(self):
        global pause_api
        if not acceleration_values:
            print("No data loaded. Please load a file first.")
            return

        pause_api = False
        self.running = True
        self.send_data()

    def send_data(self):
        global acceleration, current_index, acceleration_values
        while self.running and current_index < len(acceleration_values):
            acceleration = acceleration_values[current_index]
            self.acceleration_label.config(text=f"Acceleration: {round(acceleration, 20)} m/s²")
            current_index += 1
            self.root.update()  # Update the GUI to avoid freezing
            time.sleep(0.1)

        if current_index >= len(acceleration_values):
            print("Reached the end of the data file.")
            self.stop_sending_data()

    def stop_sending_data(self):
        global acceleration, pause_api, current_index
        self.running = False
        acceleration = 0.0  # Reset the acceleration to 0 when stopping
        current_index = 0  # Reset index to start from the beginning
        self.acceleration_label.config(text=f"Acceleration: {round(acceleration, 20)} m/s²")
        pause_api = True

    def update_station_id(self):
        global station_id
        try:
            station_id = int(self.station_id_entry.get())
            print(f"Station ID updated to: {station_id}")
        except ValueError:
            print("Invalid station ID")

# Start the Flask API in a separate thread
def run_flask():
    app.run(host='0.0.0.0', port=5045)

# Run Flask API and Tkinter GUI simultaneously
def start_gui():
    root = tk.Tk()
    app = AccelerationApp(root)
    root.mainloop()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    start_gui()
