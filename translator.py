import requests
import json
import time
import math
import socket
import numpy as np
import websocket
import matplotlib.pyplot as plt
from collections import deque
import time
import pickle

with open('random_forest_200.pkl', 'rb') as model_file:
    ml_model = pickle.load(model_file)

UDP_IP = "0.0.0.0"  # Listen on all interfaces
UDP_PORT = 5005     # Listening port

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))
sock.settimeout(2.0)  # Set timeout to prevent blocking forever
last_richter=0
def predict_with_model(acceleration_data):
    # You may need to preprocess or reshape the data depending on your model
    # Example: flatten and wrap in list to simulate a 2D array for scikit-learn
    features = [acceleration_data]  # shape: (1, N) if needed
    prediction = ml_model.predict(features)
    return prediction[0] == 1

def compute_fft_peak_frequency(acceleration_data, fs):
    # Number of data points
    n = len(acceleration_data)

    if n == 0:
        raise ValueError("Error: The acceleration data array is empty.")

    # Compute FFT
    fft_result = np.fft.fft(acceleration_data)
    frequencies = np.fft.fftfreq(n, d=1/fs)

    # Take only positive frequencies
    pos_mask = frequencies > 0
    frequencies = frequencies[pos_mask]
    fft_magnitude = np.abs(fft_result[pos_mask])
     
    # Find peak frequency
    peak_index = np.argmax(fft_magnitude)
    peak_frequency = frequencies[peak_index]
    '''
    plt.figure(figsize=(8, 4))
    plt.plot(frequencies, fft_magnitude, label="FFT Magnitude")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.title("FFT Spectrum of Acceleration Data")
    plt.grid()
    plt.legend()
    plt.show()'''
    #if (peak_frequency>0.001 and peak_frequency<0.1) or (peak_frequency>1 and peak_frequency<20):
    if (peak_frequency>0.001 and peak_frequency<0.1)  :
        return True
    return False

def send_message(message, target_ip, target_port):
    """Send a UDP message to the specified target IP and port."""
    try:
        sock.sendto(str(message).encode(), (target_ip, target_port))
        #print(f"Sent to {target_ip}:{target_port} -> {message}")
    except Exception as e:
        print(f"Error sending message: {e}")

def movement_detection():
    try:
        data, addr = sock.recvfrom(1024)  # Receive message
        message = data.decode()
        value = float(message.split(":")[1])  # Extract acceleration value
        return value, addr
    except socket.timeout:
        return None, None
    except (ValueError, IndexError):
        return None, None

class EarthquakeProcessor:
    def __init__(self, station_id=1):
        self.station_id = station_id
        self.session = requests.Session()
        
        # Constants
        self.STA_WINDOW = 10
        self.LTA_WINDOW = 50
        #the more the diff between sta and lta the more the accuracy but slower to calc richter
        self.DETECTION_THRESHOLD = 2
        
        # Initial reset
        self.reset_state()

    def reset_state(self):
        """Full system reset with zero values sent"""
        # Clear all buffers and states
        self.event_start = None
        self.s_wave_detected = False
        self.acceleration_buffer = deque(maxlen=self.LTA_WINDOW)
        
        # Reset physical parameters to match original code
        self.initial_velocity = 0
        self.initial_displacement = 0
        self.total_displacement = 0
        self.max_displacement = 0
        self.max_richter = 0
        
        # Reset S-wave parameters
        self.s_wave_time = 0
        self.ed = 0
        self.a0_correction = 0
        
        # Send zero values immediately
        self.send_zero_values()

    def send_zero_values(self):
        """Send zero-values using the persistent WebSocket connection"""

        if not hasattr(self, 'ws') or self.ws is None:
            import websocket  # Import inside to avoid unnecessary dependency if not used
            self.ws = websocket.WebSocket()
            self.ws.connect("ws://localhost:3001")  # Connect only once

        zero_data = {
            "type": "addEvent",
            "velocity": 0,
            "displacement": 0,
            "richter": 0,
            "acceleration": 0,
            "station_id": self.station_id
        }

        try:
            self.ws.send(json.dumps(zero_data))  # Send data over WebSocket
            print("Zero-values sent successfully via WebSocket")

 

        except Exception as e:
            print(f"Error sending zero-values via WebSocket: {e}")
            
    def fetch_data(self):
        
        """Fetch acceleration data from UDP, extract station_id and acceleration, and return as JSON."""
            
        try:
            data, addr = sock.recvfrom(1024)  # Receive message
            message = data.decode().strip()
 
            # Expecting format: "Station X: Y.YYYYYYYY"
            parts = message.split(":")  
 
            station_part = parts[0].strip()  # "Station 1"
            acceleration_part = parts[1].strip()  # "0.00000000"

            # Extract station number

            station_id = station_part.split()[1]  # Extract "1" from "Station 1"

            # Convert acceleration to float
            acceleration = float(acceleration_part)  
            
            return {
                "station_id": station_id,
                "acceleration": acceleration
            }
            

        except socket.timeout:
                print("timeout")
                return None  # Timeout case
       # except (ValueError, IndexError):
       #     return None  #

    def send_data(self,result):
        """Send event data using a synchronous WebSocket connection"""
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:3001")  # Connect to WebSocket server

        event_data = {
            "type": "addEvent",
            "velocity": result['velocity'],
            "displacement": result['displacement'],
            "richter": result['richter'],
            "acceleration": result['acceleration'],
            "station_id": self.station_id
        }
        #time.sleep(0.1)#delay to make it readable
        ws.send(json.dumps(event_data))  # Send event data
  

 

       


    def trapezoidal_integration(self, acceleration, elapsed_time):
        """EXACT replica of original integration method"""
        # Original calculation
        velocity = self.initial_velocity + 0.5 * elapsed_time * acceleration
        displacement = self.initial_displacement + 0.5 * (
            velocity + self.initial_velocity
        ) * elapsed_time
        
        # Original delta calculation
        delta_v = velocity - self.initial_velocity
        delta_d = displacement - self.initial_displacement
        return delta_v, delta_d,displacement

    def detect_S_wave(self):
        """Detect S-wave using STA/LTA ratio"""
        if len(self.acceleration_buffer) < self.LTA_WINDOW:
            return None
        
        sta = sum(abs(x) for x in list(self.acceleration_buffer)[-self.STA_WINDOW:]) / self.STA_WINDOW
        lta = sum(abs(x) for x in list(self.acceleration_buffer)[-self.LTA_WINDOW:]) / self.LTA_WINDOW
        
        return sta / lta if lta != 0 else 0

    def calculate_epicenter(self, s_wave_delay,current_time):
        """Calculate epicenter distance and A₀ correction"""
        if not s_wave_delay or s_wave_delay <= 0:
            return 0.0, 0.0
        
        ed = 8.4* (s_wave_delay)
        x = ed
        a0_correction = -1.60775e-10 * x**4 + 2.1429e-7 * x**3 - 0.000100878 * x**2 + 0.023678 * x + 1.45704
        print(x,a0_correction )
        return ed, a0_correction 

    def estimate_richter(self, total_displacement):
        """Estimate Richter magnitude (updated)"""
        global last_richter
        if not self.s_wave_detected or self.a0_correction == 0:
            return 0  # Don't calculate before S-wave detection
       
        if total_displacement > 0:
            richter = math.log10(total_displacement)+self.a0_correction 
            if richter<last_richter:
                return last_richter
            last_richter=richter
            return min(max(richter, 0), 9.5)
        return 0

    def main_loop(self):
        """Main processing loop matching original code flow"""
        while True:
            try:
                # Fetch new data
                data = self.fetch_data()
                if not data:  # If fetch_data() returns None, skip iteration
                    print("No valid data received. Skipping...")
                    
                    self.reset_state()
                    break

                acceleration = abs(data['acceleration'])   # Convert to m/s²

 
 
                current_time = time.time()

                # First-time event setup
                if not self.event_start:
                    self.event_start = current_time
                    self.last_integration_time = current_time
                    print("New event detected - starting measurements")
                    continue  # Skip first frame

                # Compute time elapsed
                elapsed_time = current_time - self.last_integration_time
                if elapsed_time <= 0:
                    continue

                # Perform integration
                delta_v, delta_d, temp = self.trapezoidal_integration(acceleration, elapsed_time)
                self.total_displacement += delta_d
                self.max_displacement = max(self.max_displacement, delta_d)

                # Update initial values
                self.initial_velocity = delta_v
                self.initial_displacement = delta_d
                self.last_integration_time = current_time

                # S-wave detection
                self.acceleration_buffer.append(acceleration)
                ratio = self.detect_S_wave()
                if ratio and ratio > self.DETECTION_THRESHOLD:
                    self.s_wave_detected = True
                    self.s_wave_time = current_time - self.event_start
                    self.ed, self.a0_correction = self.calculate_epicenter(self.s_wave_time, current_time)
                    print(f"S-wave detected at {self.s_wave_time:.2f}s")

                # Prepare and send results
                result = {
                    'velocity': self.initial_velocity,
                    'displacement': self.initial_displacement,
                    'richter': self.estimate_richter(self.total_displacement),
                    'acceleration': acceleration,
                    'epicenter_distance': self.ed,
                    'a0_correction': self.a0_correction
                }
                
                #print("Sending result:", result)  # Debug output
                self.send_data(result)

            except KeyboardInterrupt:
                print("Shutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")  # Print the actual error message
                self.reset_state()
                time.sleep(1)

if __name__ == "__main__":
    fs =200  # Sampling frequency (Hz)

    while True:
        station_id=0
        acceleration_data = []
        sender_address = None

        # Collect 200 acceleration samples
        while len(acceleration_data) < fs:
            acc, addr = movement_detection()
            if acc is not None:
                acceleration_data.append(acc)
                sender_address = addr  # Store sender's address for response
            else:
                print("no possibility for earthquake")
                acceleration_data=[]

        if sender_address:
            if predict_with_model(acceleration_data): #ml model first
                is_earthquake = compute_fft_peak_frequency(acceleration_data, fs)
                if not is_earthquake:
                    print(acceleration_data[0])
                    send_message(0, sender_address[0], sender_address[1])  # Send response
                print(f"Is earthquake?: {is_earthquake}")
                if is_earthquake:
                    time.sleep(1)
                    last_richter=0
                    earthquake_processor = EarthquakeProcessor()
                    earthquake_processor.main_loop() 
           
