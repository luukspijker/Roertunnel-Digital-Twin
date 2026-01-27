# Roertunnel Digital Twin – Asphalt Joint Health Monitoring

This project implements a **conceptual digital twin** for estimating asphalt joint degradation in a tunnel and supporting maintenance decisions.  
The model integrates traffic, noise, and weather data, calculates a health index, and visualizes results in an interactive **Streamlit dashboard**.

---

## Overview

The digital twin supports:

- **A4** – Estimation of joint degradation  
- **A5** – Maintenance advice and reporting (conceptual)

Input data is mocked or retrieved from public sources such as **NDW** and **OpenMeteo**.  
The model outputs a **health index (0–100)** and a corresponding maintenance recommendation.

---

## Input Data

### Traffic
- Vehicle counts over the past **14 days**
- Heavy vehicle share configurable via dashboard slider
- Heavy vehicles contribute more strongly to degradation

### Noise
- Mocked historical noise levels (dB) for 14 days
- Represents joint anomalies and deterioration trends

### Weather
- 72-hour temperature forecast retrieved from **OpenMeteo**
- Used to model thermal stress (freezing and temperature variation)

---

## Model Logic

Three stress indicators are calculated using rule-based logic:

### Traffic Fatigue
- Based on total and heavy vehicle traffic
- Weighted: **60% total traffic**, **40% heavy traffic**
- Output: score from 0–100

### Thermal Stress
- Based on minimum temperature, freezing hours, and temperature variation
- Weighted: **40% low temperature**, **40% freezing duration**, **20% variation**
- Output: score from 0–100

### Noise Anomaly
- Difference between average noise in the last 7 days and the previous 7 days
- Higher noise indicates worsening joint condition
- Output: score from 0–100

---

## Health Index

The overall health index is calculated as:

Health Index = 100 − 0.4 × Traffic − 0.4 × Thermal − 0.2 × Noise


Status thresholds:

- **Healthy (≥ 70)** – No maintenance required
- **Warning (50–69)** – Plan inspection or maintenance
- **Critical (< 50)** – Preventive maintenance recommended

---

## Dashboard Features

- **Radial health gauge** (green / orange / red)
- **Traffic and noise time series plots** (dark theme)
- **Key KPIs**:
  - Average traffic
  - Minimum forecast temperature
  - Noise trend
- **Noise trend indicator**:
  - Green arrow → decreasing noise
  - Red arrow → increasing noise
- **Maintenance recommendation** with color-coded alerts
- **Recalculate button** to rerun the model dynamically

---

## Technology Stack

- Python
- Pandas
- Requests
- Plotly
- Streamlit

---

## Notes

- Rules and thresholds are **conceptual**
- Intended as a demonstration of digital twin logic
- Future work includes real sensor integration, expert-calibrated rules, and predictive maintenance timing
