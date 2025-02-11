# Open and read the file
with open('acceleration_data.txt', 'r') as f:
    acceleration_values = [float(value) for line in f for value in line.split()]

# Downsample the data by picking every 99th sample
downsampled_values = acceleration_values[::99]

# Save the new data to a file
with open('downsampled_acceleration_data.txt', 'w') as f:
    for value in downsampled_values:
        if float(value)==0:
            continue
        f.write(f"{value}\n")

# Print the length to verify
print(len(downsampled_values))  
