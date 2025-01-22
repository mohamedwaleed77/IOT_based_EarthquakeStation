import tkinter as tk
from flask import Flask, jsonify
import threading
import time
import random

# Initialize Flask API
app = Flask(__name__)

# Global variables
acceleration = 0.0
station_id = 1
pause_api = False
min_acceleration = 0.001
max_acceleration = 0.006
MAX_ACCELERATION_LIMIT = 50

# Function to generate acceleration data and return station ID
@app.route('/')
def get_acceleration_data():
    global pause_api
    
    if pause_api:
        print("API is paused. Returning empty data.")
        return jsonify([])  # Empty response when the API is paused

    return jsonify([{'acceleration': round(acceleration, 8), 'station_id': station_id}])

# Tkinter GUI setup
class AccelerationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Earthquake Station Simulator")

        # Set window size and make it non-resizable
        self.root.geometry("600x350")  # Increased height for duration input
        self.root.resizable(False, False)  # Prevent resizing

        # Create a frame to hold all widgets and center them
        frame = tk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True)

        # Configure the grid to center elements horizontally
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=1)
        frame.grid_rowconfigure(4, weight=1)
        frame.grid_rowconfigure(5, weight=1)
        frame.grid_rowconfigure(6, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Acceleration Label
        self.acceleration_label = tk.Label(frame, text=f"Acceleration: {round(acceleration, 8)} m/s²", font=('Arial', 14))
        self.acceleration_label.grid(row=0, column=0, columnspan=2, pady=20)

        # Start Button
        self.start_button = tk.Button(frame, text="Start Random Acceleration", width=20, height=2, command=self.start_random_acceleration)
        self.start_button.grid(row=1, column=0, columnspan=2, pady=10)

        # Station ID Entry Label
        self.station_id_entry_label = tk.Label(frame, text="Enter Station ID:", font=('Arial', 10))
        self.station_id_entry_label.grid(row=2, column=0, pady=10)

        # Station ID Entry
        self.station_id_entry = tk.Entry(frame, width=15)
        self.station_id_entry.insert(0, str(station_id))  # Default station ID
        self.station_id_entry.grid(row=2, column=1, pady=10)

        # Submit Button
        self.submit_button = tk.Button(frame, text="Submit Station ID", width=20, height=2, command=self.update_station_id)
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Stop Button
        self.stop_button = tk.Button(frame, text="Stop", width=20, height=2, command=self.stop_acceleration)
        self.stop_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Min and Max Acceleration range inputs
        self.min_label = tk.Label(frame, text="Min Acceleration:", font=('Arial', 10))
        self.min_label.grid(row=5, column=0, pady=5)

        self.min_entry = tk.Entry(frame, width=15)
        self.min_entry.insert(0, str(min_acceleration))  # Default min acceleration
        self.min_entry.grid(row=5, column=1, pady=5)

        self.max_label = tk.Label(frame, text="Max Acceleration:", font=('Arial', 10))
        self.max_label.grid(row=6, column=0, pady=5)

        self.max_entry = tk.Entry(frame, width=15)
        self.max_entry.insert(0, str(max_acceleration))  # Default max acceleration
        self.max_entry.grid(row=6, column=1, pady=5)

        # Duration Label
        self.duration_label = tk.Label(frame, text="Duration (Seconds):", font=('Arial', 10))
        self.duration_label.grid(row=7, column=0, pady=5)

        # Duration Entry
        self.duration_entry = tk.Entry(frame, width=15)
        self.duration_entry.insert(0, "10")  # Default duration
        self.duration_entry.grid(row=7, column=1, pady=5)

        self.running = False

    def update_acceleration(self):
        global acceleration, min_acceleration, max_acceleration, MAX_ACCELERATION_LIMIT
        try:
            min_acceleration = float(self.min_entry.get())
            max_acceleration = float(self.max_entry.get())
            
            if min_acceleration >= max_acceleration:
                print("Min acceleration should be less than max acceleration!")
                return
            
            if max_acceleration > MAX_ACCELERATION_LIMIT:
                print(f"Max acceleration should not exceed {MAX_ACCELERATION_LIMIT} m/s².")
                max_acceleration = MAX_ACCELERATION_LIMIT

        except ValueError:
            print("Invalid input for acceleration range.")
            return
        
        # Generate a random acceleration value within the range
        acceleration = round(random.uniform(min_acceleration, max_acceleration), 8)

        # Update the acceleration label
        self.acceleration_label.config(text=f"Acceleration: {round(acceleration, 8)} m/s²")
 

    def start_random_acceleration(self):
        global pause_api
        pause_api = False
        self.running = True
        duration = int(self.duration_entry.get())  # Get the duration from the entry field
        self.run_random_acceleration(duration)

    def run_random_acceleration(self, duration):
        end_time = time.time() + duration  # Set the end time based on the duration
        while self.running and time.time() < end_time:
            self.update_acceleration()
            time.sleep(0.1)
            self.root.update()  # Update the GUI to avoid freezing
        self.stop_acceleration()  # Stop after the duration ends

    def stop_acceleration(self):
        global acceleration, pause_api
        self.running = False
        acceleration = 0.0  # Reset the acceleration to 0 when stopping
        self.acceleration_label.config(text=f"Acceleration: {round(acceleration, 8)} m/s²")

     
        # Set the pause API flag to True (permanent)
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
