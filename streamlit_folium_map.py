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
st.write("Keskinopeus on:", avg_speed, 'm/s')

# Total Distance from GPS Data
# Since distance is not directly available, estimate it by summing segments of velocity*time.
time_diff = np.diff(df_location['Time (s)'])  # Compute time differences between samples
distances = df_location['Velocity (m/s)'][:-1] * time_diff  # Calculate segment distances
total_distance = distances.sum() / 1000  # Convert from meters to km
st.write("Kokonaismatka on:", total_distance, 'km')

# Step Count using Filtered Acceleration Data (Z-axis)
accel_z = df_accel['Linear Acceleration z (m/s^2)']
time_accel = df_accel['Time (s)']

# Use find_peaks to detect steps based on peaks in Z-axis acceleration signal
peaks, _ = find_peaks(accel_z, height=1, distance=20)  # Adjust `height` and `distance` for optimal detection
step_count_filtered = len(peaks)
st.write("Askelmäärä suodatetusta kiihtyvyysdatasta:", step_count_filtered)

# Step Count using Fourier Analysis
frequencies, power_density = welch(accel_z, fs=1/np.mean(np.diff(time_accel)), nperseg=256)
step_freq = frequencies[np.argmax(power_density)]  # Dominant frequency peak
step_count_fourier = int(step_freq * (time_accel.iloc[-1] - time_accel.iloc[0]))  # Estimated steps
st.write("Askelmäärä Fourier-analyysin perusteella:", step_count_fourier)

# Step Length (calculated from distance and step count)
if step_count_filtered > 0:
    step_length = total_distance * 1000 / step_count_filtered  # converting km to m
    st.write("Askelpituus:", step_length, 'm')
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

# Power Spectral Density Plot for Fourier Analysis
st.subheader("Kiihtyvyysdatan tehospektritiheys")
plt.figure(figsize=(10, 4))
plt.semilogy(frequencies, power_density)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power Spectral Density")
st.pyplot(plt)

# Create Route Map with Folium
start_lat = df_location['Latitude (°)'].mean()
start_long = df_location['Longitude (°)'].mean()
map = folium.Map(location=[start_lat, start_long], zoom_start=14)

# Add Polyline to the map for route visualization
folium.PolyLine(df_location[['Latitude (°)', 'Longitude (°)']], color='blue', weight=3.5, opacity=1).add_to(map)

# Display the map
st.subheader("Reittisi kartalla")
st_map = st_folium(map, width=900, height=650)
