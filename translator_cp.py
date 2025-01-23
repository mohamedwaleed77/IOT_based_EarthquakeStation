import requests
import json
import time
import math
import numpy as np
import scipy.signal as signal

# Constants
initial_velocity = 0  # Initial velocity in m/s
initial_displacement = 0  # Initial displacement in meters
total_displacement=0 # Total displacement for Richter calculation
reset_done = False  # Flag to ensure resetting and sending zero values only once
zero_sent = False  # Flag to ensure zeros are sent only once when the API is empty
events=0
max_displacement=0
max_richter=0

# Function to calculate velocity and displacement using trapezoidal integration
def trapezoidal_integration(acceleration, elapsed_time, initial_velocity, initial_displacement):
    velocity = initial_velocity + 0.5*elapsed_time*(acceleration)
    displacement = initial_displacement + 0.5 * (velocity+initial_velocity) * elapsed_time
    return velocity, displacement

# detect P-wave by finding the first peak (later in the project we can just say its 0 but its here to help test better)
def detect_p_wave(data, threshold=0.01):
    start_idx = np.argmax(np.abs(data) > threshold)

    if start_idx == 0:
        return None

    data_segment = data[start_idx:]
    peaks, _ = signal.find_peaks(data_segment)

    if len(peaks) > 0:
        return start_idx + peaks[0]
    else:
        return None

# detect S-wave using STA/LTA (sta is small window and lta is long window)
def detect_s_wave(data, tp_idx, sta_window=0.5, lta_window=5, threshold=2):
    data_segment = data[tp_idx:]

    sta_samples = int(sta_window * fs)
    lta_samples = int(lta_window * fs)

    sta = np.convolve(data_segment**2, np.ones(sta_samples)/sta_samples, mode='same')
    lta = np.convolve(data_segment**2, np.ones(lta_samples)/lta_samples, mode='same')

    ratio = np.zeros_like(data_segment)
    ratio[lta > 0] = sta[lta > 0] / lta[lta > 0]

    arrival_idx = np.argmax(ratio > threshold)

    return tp_idx + arrival_idx

#calculate epicentral distance based on S-P time difference, we can update later to make it tp = 0 but for testing we will use p-wave as well
def calculate_epicentral_distance(tp, ts):
    delta_t = ts - tp
    return 8.4 * delta_t

def calculate_logA0(ed):
    return -(1.60775e-10) * ed**4 + (2.1429e-7) * ed**3 - 0.000100878 * ed**2 + 0.023678 * ed + 1.45704

# Function to estimate Richter scale based on total displacement
def estimate_richter(total_displacement, ed):

    global max_displacement, max_richter
    if total_displacement > 0:
        #negative_log_a0=-0.00000846375 * (total_displacement)**2 + 0.00996671 * (total_displacement) + 1.87826
        #richter_magnitude=math.log10(total_displacement)+negative_log_a0


        richter_magnitude = math.log10(max_displacement) + calculate_logA0(ed)

        #richter_magnitude=math.log10(total_displacement) + 6

        if richter_magnitude<max_richter:
            return max_richter
        max_richter=richter_magnitude

        if richter_magnitude > 9.5:
            return 9.5

        return richter_magnitude
    return 0

# Function to fetch data from localhost:5045
def fetch_data(session):
    try:
        response = session.get("http://localhost:5045", timeout=0.1)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return None

# Function to send data to localhost:3001/addevent
def send_data(session, velocity, displacement, richter_magnitude, acceleration, station_id):
    data = {
        "velocity": velocity,
        "displacement": displacement,
        "richter": richter_magnitude,
        "acceleration": acceleration,
        "station_id": station_id,
    }
    try:
        response = session.post("http://localhost:3001/addevent", json=data, timeout=0.3)
        response.raise_for_status()
        print("Data sent successfully")
    except requests.RequestException as e:
        print(f"Error sending data: {e}")

# Function to send zero values when acceleration is 0 or API is empty
def send_zero_values(session, station_id):
    global initial_velocity, initial_displacement,events, total_displacement, last_integration_time,max_displacement,max_richter
    time.sleep(0)
    data = {
        "velocity": 0,
        "displacement": 0,
        "richter": 0,
        "acceleration": 0,
        "station_id": station_id,
    }
    max_richter=0
    max_displacement=0
    initial_velocity = 0
    initial_displacement = 0
    total_displacement=0
    events=0
    last_integration_time = None  # Reset elapsed time marker
    try:
        response = session.post("http://localhost:3001/addevent", json=data, timeout=0.1)
        response.raise_for_status()
        print("Zero values sent successfully")
    except requests.RequestException as e:
        print(f"Error sending zero values: {e}")

# Function to reset values properly
def reset_values(session, station_id):
    global initial_velocity, initial_displacement, total_displacement, reset_done, last_integration_time,events,max_displacement,max_richter
    max_richter=0
    max_displacement=0
    initial_velocity = 0
    initial_displacement = 0
    total_displacement=0  # Reset total displacement
    last_integration_time = None  # Reset elapsed time marker
    events=0
    send_zero_values(session, station_id)  # Send zero values after reset
    reset_done = True

# Main loop
def main():
    global initial_velocity, initial_displacement, total_displacement, reset_done, zero_sent, last_integration_time,events,max_displacement
    last_integration_time = None  # Initialize as None
    station_id = 1  # Default station ID
    session = requests.Session()
    max_displacement=0
    while True:
        
        data = fetch_data(session)

        if not data:  # If API is empty
            
            if not zero_sent:  # Only send zeros once
                send_zero_values(session, station_id)
                zero_sent = True
            continue

        acceleration_data = np.array([d['acceleration'] for d in data])
       
        zero_sent = False  # Reset flag when data is received
        acceleration = data[0].get('acceleration') if data else 0
        station_id=data[0].get('station_id') if data else 1

        if (acceleration is None and not reset_done) or acceleration == 0:
            if not reset_done:  # Only reset if not already reset
                print("Acceleration is 0. Resetting all values.")
                zero_sent = True
                reset_values(session, station_id)  # Properly reset and send zero values
            continue

        if acceleration is not None:

            reset_done = False
            current_time = time.time()
            if last_integration_time is None:
                last_integration_time = current_time  # Initialize the integration time marker

            elapsed_time = current_time - last_integration_time
            print('elapsed time: ', elapsed_time)

            if elapsed_time > 0:  # Process only if some time has passed
                events+=1
                velocity, displacement = trapezoidal_integration(
                    acceleration, elapsed_time, initial_velocity, initial_displacement
                )

                velocity -= initial_velocity
                displacement -= initial_displacement
                if displacement>max_displacement:
                    max_displacement=displacement
                total_displacement+=displacement
                
                # Detect P-wave and S-wave arrivals
                tp_idx = detect_p_wave(acceleration_data)
                if tp_idx is None:
                  print("P-wave not detected.")
                  continue

                ts_idx = detect_s_wave(acceleration_data, tp_idx)

                # Calculate epicentral distance and -logA0
                tp = tp_idx / fs
                ts = ts_idx / fs
                epicentral_distance = calculate_epicentral_distance(tp, ts)

                # Calculate maximum displacement and Richter magnitude
                richter_magnitude = estimate_richter(total_displacement, epicentral_distance)
                
                print(f"Acceleration: {acceleration} m/s^2")
                print(f"Velocity: {velocity} m/s")
                print(f"Displacement: {displacement} meters")
                print(f"Richter Magnitude: {richter_magnitude}")
                print("total displacement:",total_displacement)
                print(f"Events: {events}")
                send_data(session, velocity, max_displacement, richter_magnitude, acceleration, station_id)

                # Update values for the next iteration
                initial_velocity = velocity
                initial_displacement = displacement
                last_integration_time = current_time


if __name__ == "__main__":
    main()
