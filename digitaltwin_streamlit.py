# -*- coding: utf-8 -*-
"""
Roertunnel Digital Twin – Preventive Maintenance Concept
"""

# =========================
# IMPORTS
# =========================
import requests
import statistics
import pandas as pd
import random
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import plotly.graph_objects as go

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Roertunnel Digital Twin",
    layout="wide"
)

# =========================
# INPUT DATA
# =========================
df = pd.read_excel("traffic_data.xlsx", parse_dates=["timestamp"])
traffic_total = df["total_vehicles"].tolist()

assert len(traffic_total) == 14 * 24

# =========================
# SIDEBAR CONTROLS
# =========================
st.sidebar.header("Scenario Controls")

HEAVY_VEHICLE_RATIO = st.sidebar.slider(
    "Heavy vehicle ratio (%)",
    min_value=5,
    max_value=30,
    value=15
) / 100

FREEZE_TEMP_THRESHOLD = st.sidebar.slider(
    "Freeze temperature threshold (°C)",
    min_value=-10,
    max_value=5,
    value=0
)

RERUN = st.sidebar.button("Run Health Assessment")

# =========================
# DERIVED INPUTS
# =========================
traffic_heavy = [int(t * HEAVY_VEHICLE_RATIO) for t in traffic_total]

random.seed(42)
noise_levels = [random.uniform(70, 90) for _ in range(14 * 24)]

# =========================
# WEATHER FORECAST
# =========================
def get_temperature_forecast_72h():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=51.19&longitude=5.99"
        "&hourly=temperature_2m"
        "&forecast_days=3"
    )
    data = requests.get(url).json()
    return data["hourly"]["temperature_2m"][:72]

temps_72h = get_temperature_forecast_72h()

# =========================
# CALCULATION FUNCTIONS
# =========================
def calculate_traffic_fatigue(total, heavy):
    total_norm = min(sum(total) / 300_000, 1.0)
    heavy_norm = min(sum(heavy) / 70_000, 1.0)
    return (0.6 * total_norm + 0.4 * heavy_norm) * 100

def calculate_thermal_stress(temps):
    min_temp = min(temps)
    freeze_hours = sum(t < FREEZE_TEMP_THRESHOLD for t in temps)
    variation = max(temps) - min(temps)

    stress = 0
    if min_temp < 1:
        stress += 0.4
    if freeze_hours >= 12:
        stress += 0.4
    if variation >= 10:
        stress += 0.2

    return min(stress, 1.0) * 100

def calculate_noise_anomaly(noise):
    baseline = statistics.mean(noise[:7*24])
    recent = statistics.mean(noise[7*24:])
    delta = recent - baseline

    if delta < 1:
        return 10
    elif delta < 3:
        return 40
    else:
        return 80

# =========================
# RUN ASSESSMENT
# =========================
traffic_score = calculate_traffic_fatigue(traffic_total, traffic_heavy)
thermal_score = calculate_thermal_stress(temps_72h)
noise_score = calculate_noise_anomaly(noise_levels)

health_index = (
    100
    - 0.4 * traffic_score
    - 0.4 * thermal_score
    - 0.2 * noise_score
)

health_index = max(round(health_index, 1), 0)

# =========================
# STATUS LOGIC
# =========================
if health_index >= 70:
    status = "Healthy"
    advice = "No maintenance required. Continue monitoring."
elif health_index >= 50:
    status = "Warning"
    advice = "Joint degradation likely. Plan inspection or maintenance window."
else:
    status = "Critical"
    advice = "Preventive maintenance recommended within short term."

# =========================
# TREND ANALYSIS
# =========================
noise_trend = (
    statistics.mean(noise_levels[7*24:])
    - statistics.mean(noise_levels[:7*24])
)

# =========================
# DASHBOARD HEADER
# =========================
st.title("Roertunnel Asphalt Joint Digital Twin")
st.caption("Preventive maintenance decision support")

# =========================
# METRICS ROW
# =========================
col1, col2, col3 = st.columns(3)
col1.metric("Health Index", f"{health_index}/100", delta=None)
col2.metric("Status", status)
col3.metric(
    "Noise Trend (7d) [dB]",
    f"{noise_trend:.1f}",
    delta=round(-noise_trend, 1)
)


# =========================
# RADIAL GAUGE (MAIN)
# =========================
st.subheader("Overall Joint Health")

fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=health_index,
    number={'suffix': " / 100"},
    gauge={
        'axis': {'range': [0, 100]},
        'bar': {'color': "darkblue"},
        'steps': [
            {'range': [0, 50], 'color': "red"},
            {'range': [50, 70], 'color': "orange"},
            {'range': [70, 100], 'color': "green"},
        ]
    }
))
st.plotly_chart(fig, use_container_width=True)

# =========================
# SECONDARY GAUGES
# =========================
st.subheader("Contributing Health Factors")

c1, c2, c3 = st.columns(3)

def small_gauge(value, title):
    return go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        gauge={'axis': {'range': [0, 100]}},
        title={'text': title}
    ))

c1.plotly_chart(small_gauge(traffic_score, "Traffic Fatigue"), use_container_width=True)
c2.plotly_chart(small_gauge(thermal_score, "Thermal Stress"), use_container_width=True)
c3.plotly_chart(small_gauge(noise_score, "Noise Anomaly"), use_container_width=True)

# =========================
# TIME SERIES PLOTS
# =========================
st.subheader("Observed Trends")

# Traffic plot
fig_traffic = go.Figure()
fig_traffic.add_trace(
    go.Scatter(
        y=traffic_total,
        mode="lines",
        line=dict(color="deepskyblue", width=2),
        name="Traffic"
    )
)

fig_traffic.update_layout(
    title=dict(
        text="Traffic (14 days)",
        x=0.5,            # centers the title
        xanchor='center',  # ensures alignment is correct
        yanchor='top',
        font=dict(color="white", size=20)
    ),
    xaxis_title="Hours",
    yaxis_title="Vehicles/hour",
    plot_bgcolor="rgba(0,0,0,0)",  # transparent plot area
    paper_bgcolor="rgba(0,0,0,0)",  # transparent figure
    font=dict(color="white"),
    xaxis=dict(showgrid=True, gridcolor="gray", gridwidth=0.3),
    yaxis=dict(showgrid=True, gridcolor="gray", gridwidth=0.3)
)

st.plotly_chart(fig_traffic, use_container_width=True)


# Noise plot
fig_noise = go.Figure()
fig_noise.add_trace(
    go.Scatter(
        y=noise_levels,
        mode="lines",
        line=dict(color="red", width=2),
        name="Noise"
    )
)

fig_noise.update_layout(
    title=dict(
        text="Noise (14 days)",
        x=0.5,            # centers the title
        xanchor='center',  # ensures alignment is correct
        yanchor='top',
        font=dict(color="white", size=20)
    ),
    xaxis_title="Hours",
    yaxis_title="Noise (dB)",
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="white"),
    xaxis=dict(showgrid=True, gridcolor="gray", gridwidth=0.3),
    yaxis=dict(showgrid=True, gridcolor="gray", gridwidth=0.3)
)

st.plotly_chart(fig_noise, use_container_width=True)


# =========================
# MAINTENANCE ADVICE
# =========================
st.subheader("Maintenance Recommendation")
if status == "Healthy":
    st.success(advice)
elif status == "Warning":
    st.warning(advice)
else:
    st.error(advice)

# =========================
# DOWNLOADABLE REPORT
# =========================
report_text = f"""
Roertunnel Asphalt Joint Health Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Health Index: {health_index}/100
Status: {status}

Traffic fatigue score: {traffic_score:.1f}
Thermal stress score: {thermal_score:.1f}
Noise anomaly score: {noise_score:.1f}

Maintenance advice:
{advice}
"""

st.download_button(
    "Download Health Report",
    report_text,
    file_name="joint_health_report.txt"
)
