import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="RF Planning & Optimization",
    layout="wide"
)

st.title("📡 RF Planning & Optimization Toolkit")

st.markdown("""
This app supports radio planners and optimization teams. Explore technologies, visualize drive test data, 
calculate capacity, and estimate basic RF coverage.
""")

# ---- RF Technology Overview ----
st.header("📜 RF Technology Overview")
rf_technologies = {
    "GSM (2G)": {
        "Description": "Global System for Mobile Communications — foundational cellular tech for voice & SMS.",
        "Features": ["Circuit-switched voice", "Roaming & SMS", "Wide coverage worldwide"]
    },
    "LTE (4G)": {
        "Description": "Long-Term Evolution — high-speed broadband & low latency.",
        "Features": ["OFDM-based radio interface", "VoLTE support", "Higher data rates"]
    },
    "Wi-Fi": {
        "Description": "Wireless Fidelity — short-range broadband internet for local networks.",
        "Features": ["Unlicensed spectrum use", "High throughput", "Short range"]
    },
    "HSDPA (3G)": {
        "Description": "High-Speed Downlink Packet Access — enhances downlink capacity & speeds.",
        "Features": ["Faster data rates (up to 14.4 Mbps)", "Mobile broadband"]
    },
    "HSUPA (3G)": {
        "Description": "High-Speed Uplink Packet Access — improves uplink speeds.",
        "Features": ["Better video call support", "Higher uplink bandwidth"]
    },
    "Carrier Aggregation (LTE/5G)": {
        "Description": "Combining multiple spectrum bands to boost capacity & throughput.",
        "Features": ["Higher bandwidth", "Improved cell edge performance"]
    },
    "Massive MIMO (4G/5G)": {
        "Description": "Multiple Input Multiple Output — dozens of antennas for enhanced capacity & range.",
        "Features": ["Spatial multiplexing", "Spectral efficiency gains"]
    }
}
selected_tech = st.selectbox(
    "Choose a technology to explore:",
    list(rf_technologies.keys())
)
st.write(f"**Description:** {rf_technologies[selected_tech]['Description']}")
st.markdown("**Key Features:**")
st.markdown("\n".join([f"- {f}" for f in rf_technologies[selected_tech]['Features']]))

st.markdown("---")

# ---- Drive Test Data Visualization ----
st.header("📊 Drive Test Signal Strength Visualization")

uploaded_file = st.file_uploader(
    "Upload CSV file with columns ['distance_km', 'rssi_dbm']", type=["csv"]
)

if uploaded_file:
    data = pd.read_csv(uploaded_file)
    st.write("Data preview:", data.head())
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data['distance_km'], data['rssi_dbm'], marker='o')
    ax.set_title('Signal Strength vs Distance')
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('RSSI (dBm)')
    ax.grid(True)
    st.pyplot(fig)

st.markdown("---")

# ---- Capacity Calculator ----
st.header("🧮 Site Capacity Calculator")
st.markdown("Estimate sector capacity based on carrier bandwidth & spectral efficiency:")
bw = st.number_input('Bandwidth per carrier (MHz)', value=10.0)
speff = st.number_input('Spectral Efficiency (bps/Hz)', value=1.5)
num_carriers = st.number_input('Number of carriers', value=1, min_value=1)
sector_capacity_mbps = bw * 1e6 * speff * num_carriers / 1e6  # in Mbps
st.success(f"Estimated sector capacity: {sector_capacity_mbps:.2f} Mbps")

st.markdown("---")

# ---- RF Coverage Estimation ----
st.header("📡 Coverage Estimation")
st.markdown("Estimate received power at distance based on transmit power and path loss:")

pt_dbm = st.number_input('Transmit power (dBm)', value=43.0)
antenna_gain_db = st.number_input('Antenna gain (dBi)', value=15.0)
path_loss_db = st.number_input('Estimated path loss (dB)', value=120.0)

received_power_dbm = pt_dbm + antenna_gain_db - path_loss_db
st.info(f"Estimated received power: {received_power_dbm:.2f} dBm")

st.markdown(
    "_More detailed simulations require propagation models like Okumura-Hata, COST231, etc._"
)
