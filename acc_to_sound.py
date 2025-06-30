"""
This file is used to convert acceleration to sound, to help simulate
an earthquake using the bass shaker as talked about in the book.
"""
import pandas as pd
import numpy as np
import scipy.io.wavfile as wavfile
import os

# Reload and convert data to numeric values
x = pd.read_csv("x.V2c", header=None).squeeze("columns").apply(pd.to_numeric, errors='coerce')
y = pd.read_csv("y.V2c", header=None).squeeze("columns").apply(pd.to_numeric, errors='coerce')
z = pd.read_csv("z.V2c", header=None).squeeze("columns").apply(pd.to_numeric, errors='coerce')

# Drop any rows with NaNs
valid = ~(x.isna() | y.isna() | z.isna())
x, y, z = x[valid], y[valid], z[valid]

# Compute magnitude
accel = np.sqrt(x**2 + y**2 + z**2)

# Normalize to range [-1, 1]
accel_normalized = 2 * (accel - accel.min()) / (accel.max() - accel.min()) - 1

# Convert to 16-bit PCM
scaled = np.int16(accel_normalized * 32767)

# Save to .wav file
output_path = "earthquake.wav"
wavfile.write(output_path, 10000, scaled)  # 1000 Hz sample rate

output_path