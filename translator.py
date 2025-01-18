import requests
import json
import time
import math

# Constants
initial_velocity = 0  # Initial velocity in m/s
initial_displacement = 0  # Initial displacement in meters
total_displacement = 0  # Total displacement for Richter calculation
reset_done = False  # Flag to ensure resetting and sending zero values only once
zero_sent = False  # Flag to ensure zeros are sent only once when the API is empty

# Function to calculate velocity and displacement using trapezoidal integration
def trapezoidal_integration(acceleration, elapsed_time, initial_velocity, initial_displacement):
    velocity = initial_velocity + 0.5 * acceleration * elapsed_time
    displacement = initial_displacement + initial_velocity * elapsed_time + 0.5 * acceleration * (elapsed_time ** 2)
    return velocity, displacement

# Function to estimate Richter scale based on total displacement
def estimate_richter(total_displacement):
    if total_displacement > 0:
        richter_magnitude = math.log10(total_displacement / 0.1e-6)
        return richter_magnitude
    return 0

# Function to fetch data from localhost:5045
def fetch_data():
    try:
        response = requests.get("http://localhost:5045")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

# Function to send data to localhost:3001/addevent
def send_data(velocity, displacement, richter_magnitude, acceleration, station_id):
    data = {
        "velocity": velocity,
        "displacement": displacement,
        "richter": richter_magnitude,
        "acceleration": acceleration,
        "station_id": station_id,
    }
    try:
        response = requests.post("http://localhost:3001/addevent", json=data)
        response.raise_for_status()
        print("Data sent successfully")
    except requests.RequestException as e:
        print(f"Error sending data: {e}")

# Function to send zero values when acceleration is 0 or API is empty
def send_zero_values(station_id):
    data = {
        "velocity": 0,
        "displacement": 0,
        "richter": 0,
        "acceleration": 0,
        "station_id": station_id,
    }
    try:
        response = requests.post("http://localhost:3001/addevent", json=data)
        response.raise_for_status()
        print("Zero values sent successfully")
    except requests.RequestException as e:
        print(f"Error sending zero values: {e}")

# Main loop
def main():
    global initial_velocity, initial_displacement, total_displacement, reset_done, zero_sent

    last_integration_time = time.time()
    station_id = 1  # Default station ID

    while True:
        data = fetch_data()

        if not data:  # If API is empty
            if not zero_sent:  # Only send zeros once
                send_zero_values(station_id)
                zero_sent = True
            continue

        zero_sent = False  # Reset flag when data is received
        acceleration = data[0].get('acceleration') if data else 0


        #men hena


        
        if acceleration is None and not reset_done:
            print("Acceleration is 0. Resetting all values.")
            initial_velocity = 0
            initial_displacement = 0
            total_displacement = 0
            send_zero_values(station_id)
            reset_done = True
            continue

        if acceleration is not None:
            reset_done=False
            current_time = time.time()
            elapsed_time = current_time - last_integration_time

            if elapsed_time > 0:  # Process only if some time has passed
                velocity, displacement = trapezoidal_integration(
                    acceleration, elapsed_time, initial_velocity, initial_displacement
                )
                total_displacement += displacement
                richter_magnitude = estimate_richter(total_displacement)

                print(f"Acceleration: {acceleration} m/s^2")
                print(f"Velocity: {velocity} m/s")
                print(f"Displacement: {displacement} meters")
                print(f"Total Displacement: {total_displacement} meters")
                print(f"Richter Magnitude: {richter_magnitude}")

                send_data(velocity, displacement, richter_magnitude, acceleration, station_id)

                # Update values for the next iteration
                initial_velocity = velocity
                initial_displacement = displacement
                last_integration_time = current_time

if __name__ == "__main__":
    main()
