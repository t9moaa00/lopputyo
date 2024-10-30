import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from scipy.signal import find_peaks, welch
import numpy as np
import matplotlib.pyplot as plt

# Load the data
url = "https://raw.githubusercontent.com/t9moaa00/lopputyo/refs/heads/main/Location.csv"
url2 = "https://raw.githubusercontent.com/t9moaa00/lopputyo/refs/heads/main/Linear%20Acceleration.csv"
df_location = pd.read_csv(url)
df_accel = pd.read_csv(url2)

st.title('Fysiikan lopputyö')

# Average Speed from GPS Data
avg_speed = df_location['Velocity (m/s)'].mean()
st.write(f"Keskinopeus on: {avg_speed:.2f} m/s")

# Total Distance from GPS Data
time_diff = np.diff(df_location['Time (s)'])
distances = df_location['Velocity (m/s)'][:-1] * time_diff
total_distance = distances.sum() / 1000  # Convert to km
st.write(f"Kokonaismatka on: {total_distance:.2f} km")

# Step Count using Filtered Acceleration Data (Z-axis)
accel_z = df_accel['Linear Acceleration z (m/s^2)']
time_accel = df_accel['Time (s)']
peaks, _ = find_peaks(accel_z, height=1, distance=20)
step_count_filtered = len(peaks)
st.write(f"Askelmäärä suodatetusta kiihtyvyysdatasta: {step_count_filtered}")

# Step Count using Fourier Analysis
frequencies, power_density = welch(accel_z, fs=1/np.mean(np.diff(time_accel)), nperseg=256)
step_freq = frequencies[np.argmax(power_density)]
step_count_fourier = int(step_freq * (time_accel.iloc[-1] - time_accel.iloc[0]))
st.write(f"Askelmäärä Fourier-analyysin perusteella: {step_count_fourier}")

# Step Length Calculation
if step_count_filtered > 0:
    step_length = total_distance * 1000 / step_count_filtered  # converting km to m
    st.write(f"Askelpituus: {step_length:.2f} m")
else:
    st.write("Askelpituutta ei voitu laskea, koska askelmäärä on 0.")

# Plot Filtered Acceleration Data for Step Detection
st.subheader("Suodatettu kiihtyvyysdata")
plt.figure(figsize=(10, 4))
plt.plot(time_accel, accel_z, label="Z-axis Acceleration")
plt.plot(time_accel[peaks], accel_z[peaks], "x", label="Detected Steps", color="red")
plt.xlabel("Time (s)")
plt.ylabel("Acceleration (m/s^2)")
plt.legend()
st.pyplot(plt)

# Power Spectral Density Plot with Matplotlib
st.subheader("Kiihtyvyysdatan tehospektritiheys")
plt.figure(figsize=(10, 4))

# Convert to dB and plot with manual axis limits
power_density_db = 10 * np.log10(power_density)
plt.plot(frequencies, power_density_db)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power (dB)")
plt.title("Power Spectral Density")

# Optional: Set y-axis limits to focus on visible range
plt.ylim([np.min(power_density_db)-10, np.max(power_density_db)+10])

st.pyplot(plt)

# Create Route Map with Folium
start_lat = df_location['Latitude (°)'].mean()
start_long = df_location['Longitude (°)'].mean()
map = folium.Map(location=[start_lat, start_long], zoom_start=14)
folium.PolyLine(df_location[['Latitude (°)', 'Longitude (°)']], color='blue', weight=3.5, opacity=1).add_to(map)

# Display the map
st.subheader("Reittisi kartalla")
st_map = st_folium(map, width=900, height=650)
