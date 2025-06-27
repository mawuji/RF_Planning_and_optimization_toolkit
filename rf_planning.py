import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
import base64
import xml.etree.ElementTree as ET

st.set_page_config(page_title="RF Planning & Optimization Toolkit", layout="wide")

st.title("📡 RF Planning & Optimization Toolkit")

st.markdown(
    "This app supports radio planners with tools for drive test analysis, capacity calculation, coverage maps, and automated report generation."
)

# ---- RF Technology Overview ----
st.header("📜 RF Technology Overview")
rf_technologies = {
    "GSM (2G)": {
        "Description": "Global System for Mobile Communications — foundational voice & SMS.",
        "Features": ["Circuit-switched voice", "Roaming & SMS", "Coverage worldwide"]
    },
    "LTE (4G)": {
        "Description": "Long-Term Evolution — high-speed broadband & low latency.",
        "Features": ["OFDM radio interface", "VoLTE support", "High-speed data rates"]
    },
    "Wi-Fi": {
        "Description": "Wireless Fidelity — broadband internet for short range.",
        "Features": ["High throughput", "Short range", "Unlicensed bands"]
    },
    "HSDPA (3G)": {
        "Description": "High-Speed Downlink Packet Access — faster 3G data rates.",
        "Features": ["Up to 14.4 Mbps downlink", "Mobile broadband access"]
    },
    "HSUPA (3G)": {
        "Description": "High-Speed Uplink Packet Access — better uplink capacity.",
        "Features": ["Faster video calling", "Higher uplink rates"]
    },
    "Carrier Aggregation (LTE/5G)": {
        "Description": "Combines carriers to boost capacity & throughput.",
        "Features": ["Increased bandwidth", "Improved cell-edge rates"]
    },
    "Massive MIMO (4G/5G)": {
        "Description": "Many antennas for better capacity & range.",
        "Features": ["Spectral efficiency", "Spatial multiplexing"]
    }
}
selected_tech = st.selectbox(
    "Choose a technology to explore:", list(rf_technologies.keys())
)
st.write(f"**Description:** {rf_technologies[selected_tech]['Description']}")
st.markdown("\n".join([f"- {f}" for f in rf_technologies[selected_tech]['Features']]))
st.markdown("---")

# ---- Initialization ----
uploaded_file = st.file_uploader(
    "Upload drive test CSV file with columns ['distance_km', 'rssi_dbm']", type=["csv"]
)
avg_rssi = None
good_coverage_pct = None

# ---- Drive Test Analysis ----
st.header("📊 Drive Test Analyzer")
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    avg_rssi = data['rssi_dbm'].mean()
    good_coverage_pct = (data['rssi_dbm'] > -100).mean() * 100

    st.write(f"Average RSSI: {avg_rssi:.2f} dBm")
    st.write(f"Coverage (% RSSI > -100 dBm): {good_coverage_pct:.1f}%")

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(data['distance_km'], data['rssi_dbm'], marker='o')
    ax.set_title('Signal Strength vs Distance')
    ax.set_xlabel('Distance (km)')
    ax.set_ylabel('RSSI (dBm)')
    ax.grid(True)
    st.pyplot(fig)

st.markdown("---")

# ---- Coverage Map ----
st.header("🗺️ Coverage Map from Tower Locations")
kml_file = st.file_uploader(
    "Upload .kml file of tower locations:", type=["kml"]
)
if kml_file:
    tree = ET.parse(kml_file)
    root = tree.getroot()
    namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
    coords = []
    for placemark in root.findall(".//kml:Placemark/kml:Point/kml:coordinates", namespace):
        lon, lat, *_ = placemark.text.strip().split(',')
        coords.append((float(lat), float(lon)))
    if coords:
        tower_map = folium.Map(location=coords[0], zoom_start=10)
        marker_cluster = MarkerCluster().add_to(tower_map)
        for lat, lon in coords:
            folium.Marker(location=[lat, lon], icon=folium.Icon(color='blue', icon='signal')).add_to(marker_cluster)
        st_folium(tower_map, width=700, height=500)

st.markdown("---")

# ---- Capacity Calculator ----
st.header("🧮 Site Capacity Calculator")
bw = st.number_input('Bandwidth per carrier (MHz)', value=10.0)
speff = st.number_input('Spectral Efficiency (bps/Hz)', value=1.5)
num_carriers = st.number_input('Number of carriers', value=1, min_value=1)
sector_capacity_mbps = bw * 1e6 * speff * num_carriers / 1e6
st.success(f"Estimated sector capacity: {sector_capacity_mbps:.2f} Mbps")

st.markdown("---")

# ---- Coverage Estimation ----
st.header("📡 Coverage Estimation")
pt_dbm = st.number_input('Transmit power (dBm)', value=43.0)
antenna_gain_db = st.number_input('Antenna gain (dBi)', value=15.0)
path_loss_db = st.number_input('Estimated path loss (dB)', value=120.0)
received_power_dbm = pt_dbm + antenna_gain_db - path_loss_db
st.info(f"Estimated received power: {received_power_dbm:.2f} dBm")

st.markdown("---")

# ---- Automated Report ----
st.header("📝 Generate Automated Report")
if avg_rssi is not None:
    report_content = f"""
=== RF PLANNING & OPTIMIZATION REPORT ===
Selected Technology: {selected_tech}
Description: {rf_technologies[selected_tech]['Description']}

Drive Test Analysis:
Average RSSI: {avg_rssi:.2f} dBm
Coverage (% RSSI > -100 dBm): {good_coverage_pct:.1f}%

Site Capacity: {sector_capacity_mbps:.2f} Mbps
Estimated Received Power: {received_power_dbm:.2f} dBm
"""
    b64 = base64.b64encode(report_content.encode()).decode()
    href = f'<a href="data:file/txt;base64,{b64}" download="rf_report.txt">📥 Download Report</a>'
    st.markdown(href, unsafe_allow_html=True)
else:
    st.info("Please upload drive test data to generate the report.")

st.markdown(
    "_This report can be customized with further KPIs, signal maps, and detailed tower data._"
)
# ---- Heatmap of Signal Strength ----
st.markdown("---")
st.header("🔥 Signal Strength Heatmap")

heatmap_file = st.file_uploader(
    "Upload drive test CSV file with 'latitude', 'longitude', 'rssi_dbm' columns:", type=["csv"]
)
if heatmap_file:
    heatmap_df = pd.read_csv(heatmap_file)
    if all(col in heatmap_df.columns for col in ['latitude', 'longitude', 'rssi_dbm']):
        # Normalize RSSI to a 0-1 range for heatmap intensity
        intensity = (heatmap_df['rssi_dbm'] - heatmap_df['rssi_dbm'].min()) / (heatmap_df['rssi_dbm'].max() - heatmap_df['rssi_dbm'].min())
        heat_data = list(zip(heatmap_df['latitude'], heatmap_df['longitude'], intensity))

        # Create a folium map centered on mean lat/lon
        center_lat = heatmap_df['latitude'].mean()
        center_lon = heatmap_df['longitude'].mean()
        signal_map = folium.Map(location=[center_lat, center_lon], zoom_start=12)

        # Add heatmap
        from folium.plugins import HeatMap
        HeatMap(heat_data, radius=15).add_to(signal_map)

        st_folium(signal_map, width=700, height=500)
    else:
        st.warning("Your file must contain 'latitude', 'longitude', and 'rssi_dbm' columns to plot a heatmap.")
