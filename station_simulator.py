import tkinter as tk
from flask import Flask, jsonify
import threading
import time
import random  # Import random for generating random values

# Initialize Flask API
app = Flask(__name__)

# Global variables
acceleration = 0.0
station_id = 1  # Default station ID
pause_api = False  # Flag to control whether the API should be paused
min_acceleration = 0.01  # Default min acceleration
max_acceleration = 0.12  # Default max acceleration
MAX_ACCELERATION_LIMIT = 0.20  # Set a maximum cap for acceleration

# Function to generate acceleration data and return station ID
@app.route('/')
def get_acceleration_data():
    global pause_api
    
    if pause_api:
        # If pause is set, return an empty response and never resume
        print("API is paused. Returning empty data.")
        return jsonify([])  # Empty response when the API is paused

    # Otherwise, return normal acceleration data
    return jsonify([{'acceleration': round(acceleration, 2), 'station_id': station_id}])

# Tkinter GUI setup
class AccelerationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Acceleration Control")

        # Set window size and make it non-resizable
        self.root.geometry("400x500")  # Set the window size (Width x Height)
        self.root.resizable(False, False)  # Prevent resizing

        self.acceleration_label = tk.Label(root, text=f"Acceleration: {round(acceleration, 2)} m/s²", font=('Arial', 14))
        self.acceleration_label.pack(pady=20)

        self.start_button = tk.Button(root, text="Start Random Acceleration", width=20, height=2, command=self.start_random_acceleration)
        self.start_button.pack(pady=10)

        self.station_id_entry_label = tk.Label(root, text="Enter Station ID:", font=('Arial', 10))
        self.station_id_entry_label.pack(pady=10)

        self.station_id_entry = tk.Entry(root, width=15)
        self.station_id_entry.insert(0, str(station_id))  # Default station ID
        self.station_id_entry.pack(pady=10)

        self.submit_button = tk.Button(root, text="Submit Station ID", width=20, height=2, command=self.update_station_id)
        self.submit_button.pack(pady=10)

        self.stop_button = tk.Button(root, text="Stop", width=20, height=2, command=self.stop_acceleration)
        self.stop_button.pack(pady=10)

        # Min and Max Acceleration range inputs
        self.min_label = tk.Label(root, text="Min Acceleration:", font=('Arial', 10))
        self.min_label.pack(pady=5)

        self.min_entry = tk.Entry(root, width=15)
        self.min_entry.insert(0, str(min_acceleration))  # Default min acceleration
        self.min_entry.pack(pady=5)

        self.max_label = tk.Label(root, text="Max Acceleration:", font=('Arial', 10))
        self.max_label.pack(pady=5)

        self.max_entry = tk.Entry(root, width=15)
        self.max_entry.insert(0, str(max_acceleration))  # Default max acceleration
        self.max_entry.pack(pady=5)

        self.running = False

    def update_acceleration(self):
        global acceleration, min_acceleration, max_acceleration, MAX_ACCELERATION_LIMIT
        # Update the acceleration randomly between min and max values specified by the user
        try:
            min_acceleration = float(self.min_entry.get())
            max_acceleration = float(self.max_entry.get())
            
            if min_acceleration >= max_acceleration:
                print("Min acceleration should be less than max acceleration!")
                return  # Do nothing if the range is invalid
            
            if max_acceleration > MAX_ACCELERATION_LIMIT:
                print(f"Max acceleration should not exceed {MAX_ACCELERATION_LIMIT} m/s².")
                max_acceleration = MAX_ACCELERATION_LIMIT  # Enforce the maximum limit

        except ValueError:
            print("Invalid input for acceleration range.")
            return
        
        # Generate a random acceleration value within the range
        acceleration = round(random.uniform(min_acceleration, max_acceleration), 2)

        # Update the acceleration label
        self.acceleration_label.config(text=f"Acceleration: {round(acceleration, 2)} m/s²")

        # Print the current acceleration to the console
        print(f"Acceleration: {round(acceleration, 2)} m/s²")

    def start_random_acceleration(self):
        global pause_api
        pause_api = False  # Reset the API pause flag
        self.running = True
        self.run_random_acceleration()

    def run_random_acceleration(self):
        while self.running:
            self.update_acceleration()
            time.sleep(0.1)  # Wait for 0.1 seconds before updating again
            self.root.update()  # Update the GUI to avoid freezing

    def stop_acceleration(self):
        global acceleration, pause_api
        self.running = False
        acceleration = 0.0  # Reset the acceleration to 0 when stopping
        self.acceleration_label.config(text=f"Acceleration: {round(acceleration, 2)} m/s²")  # Update the GUI label

        # Print that the acceleration has been stopped
        print(f"Acceleration stopped. Reset to {round(acceleration, 2)} m/s²")

        # Set the pause API flag to True (permanent)
        pause_api = True

    def update_station_id(self):
        global station_id
        # Fetch the current station ID from the GUI input and update it
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
    # Start Flask API in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Tkinter GUI
    start_gui()
