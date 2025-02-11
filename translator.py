import requests
import json
import time
import math
from collections import deque
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
        """Zero-value transmission matching original format"""
        zero_data = {
            "velocity": 0,
            "displacement": 0,
            "richter": 0,
            "acceleration": 0,
            "station_id": self.station_id,
            "epicenter_distance": 0,
            "a0_correction": 0
        }
        try:
            response = self.session.post("http://localhost:3001/addevent", 
                                       json=zero_data, 
                                       timeout=0.1)
           
        except requests.RequestException:
            pass
    def fetch_data(self):
        """Fetch data from the API endpoint"""
        try:
            response = self.session.get("http://localhost:5045", timeout=0.1)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return None

    def send_data(self, result):
        """Send processed data to the server"""
        data = {
            "velocity": result['velocity'],
            "displacement": result['displacement'],
            "richter": result['richter'],
            "acceleration": result['acceleration'],
            "station_id": self.station_id,
            "epicenter_distance": result['epicenter_distance'],
            "a0_correction": result['a0_correction']
        }
        try:
            response = self.session.post("http://localhost:3001/addevent", json=data, timeout=0.1)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error sending data: {e}")

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
        if not self.s_wave_detected or self.a0_correction == 0:
            return 0  # Don't calculate before S-wave detection
       
        if total_displacement > 0:
            richter = math.log10(total_displacement)+self.a0_correction 
            print(richter,self.a0_correction,total_displacement)
            return min(max(richter, 0), 9.5)
        return 0

    def main_loop(self):
        """Main processing loop matching original code flow"""
        while True:
            try:
               
                data = self.fetch_data()
                
                # Immediate reset on empty data or zero acceleration
                if not data or data[0]['acceleration']==0:
                    self.reset_state()
                    time.sleep(0.1)
                    continue

                # Process valid data
                acceleration = abs(data[0]['acceleration'])*9.82#remove 9.82 in real test yasta as the data in g-force
                if acceleration == 0:
                    self.reset_state()
                    time.sleep(0.1)
                    continue
                current_time = time.time()
                
                # Initialize event timing
                if not self.event_start:
                    self.event_start = current_time
                    self.last_integration_time = current_time
                    print("New event detected - starting measurements")

                    continue  # Skip first frame for delta calculation

                # Calculate time delta
                elapsed_time = current_time - self.last_integration_time
                if elapsed_time <= 0:
                    continue

                # Perform integration (original method)
                delta_v, delta_d ,temp= self.trapezoidal_integration(acceleration, elapsed_time)
                # Update totals as in original code
                #self.total_displacement += temp #or +=delta_d
                self.total_displacement +=delta_d
                self.max_displacement = max(self.max_displacement, delta_d)
                
                # Update initial values (EXACT original approach)
                self.initial_velocity = delta_v
                self.initial_displacement = delta_d
                self.last_integration_time = current_time

                # S-wave detection
                self.acceleration_buffer.append(acceleration)
                
                ratio = self.detect_S_wave()
                if ratio and ratio > self.DETECTION_THRESHOLD:
                        self.s_wave_detected = True
                        self.s_wave_time = current_time - self.event_start
                        self.ed, self.a0_correction = self.calculate_epicenter(self.s_wave_time,current_time)
                        print(f"S-wave detected at {self.s_wave_time:.2f}s")

                # Prepare and send results
                result = {
                    'velocity':  self.initial_velocity,
                    'displacement':self.initial_displacement ,
                    #'richter': self.estimate_richter(self.max_displacement),#or total_displacemen?
                    'richter': self.estimate_richter(self.total_displacement),#or total_displacemen?
                    'acceleration': acceleration,
                    'epicenter_distance': self.ed,
                    'a0_correction': self.a0_correction
                }
                self.send_data(result)

            except KeyboardInterrupt:
                print("Shutting down...")
                break
            except Exception as e:
                print(f"Error: {e}")
                self.reset_state()
                time.sleep(1)


if __name__ == "__main__":
    processor = EarthquakeProcessor(station_id=1)
    processor.main_loop()
