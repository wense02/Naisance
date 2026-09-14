import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="DeltaGuard AI", page_icon="🛡️", layout="wide")

st.title("🛡️ DeltaGuard AI – Real-Time Operational Copilot")
st.caption("Renaissance Africa Energy | Niger Delta Pilot")

# Sidebar
st.sidebar.header("Pilot Controls")
selected_well = st.sidebar.selectbox("Select Well / Asset", ["Well-12A (Swamp)", "Well-07B (Onshore)", "Well-19C (Shallow Water)"])
refresh = st.sidebar.button("Refresh Live Data")

# Simulated live data
np.random.seed(42)
hours = pd.date_range(end=datetime.now(), periods=48, freq="h")
df = pd.DataFrame({
    "timestamp": hours,
    "well": selected_well,
    "oil_rate": 850 + np.cumsum(np.random.randn(48)*3),
    "pressure": 1850 + np.cumsum(np.random.randn(48)*5),
    "temperature": 78 + np.random.randn(48)*0.8,
    "vibration": 2.1 + np.abs(np.random.randn(48)*0.3)
})

# KPI row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Oil Rate", f"{df['oil_rate'].iloc[-1]:.0f} bbl/d", "+4.2%")
col2.metric("Tubing Pressure", f"{df['pressure'].iloc[-1]:.0f} psi", "-1.1%")
col3.metric("Predicted Failure Risk", "Low", "↓ 18%")
col4.metric("AI Recommendation", "Adjust Choke +8%", "High Confidence")

# Charts
st.subheader("Real-Time Production & Health Trends")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df["timestamp"], y=df["oil_rate"], name="Oil Rate (bbl/d)", line=dict(color="#2E8B57")))
fig.add_trace(go.Scatter(x=df["timestamp"], y=df["pressure"], name="Pressure (psi)", yaxis="y2", line=dict(color="#1E90FF")))
fig.update_layout(yaxis2=dict(overlaying="y", side="right"), height=400, margin=dict(l=20,r=20,t=30,b=20))
st.plotly_chart(fig, width="stretch")

# AI Recommendations panel
st.subheader("AI Decision Recommendations")
with st.expander("Active Recommendations", expanded=True):
    st.success("""
    **Recommendation 1 – High Priority**  
    Well-12A: Increase choke by 8%  
    Expected impact: +55–70 bbl/d | Risk: Low | Confidence: 87%  
    Rationale: Stable pressure trend + favourable reservoir response in last 6 hours.
    """)
    st.info("""
    **Recommendation 2**  
    Schedule vibration check on ESP within 48 hours.  
    Predicted degradation probability: 22% in next 7 days.
    """)
    st.warning("""
    **Anomaly Alert**  
    Unusual pressure signature detected on flowline segment near Well-07B.  
    Possible third-party interference risk. Recommend enhanced surveillance.
    """)

# Simple prediction mock
st.subheader("7-Day Production Forecast (AI)")
future = pd.date_range(start=datetime.now(), periods=7, freq="D")
forecast = df["oil_rate"].iloc[-1] + np.cumsum(np.random.randn(7)*8)
fig2 = px.line(x=future, y=forecast, labels={"x": "Date", "y": "Projected Oil Rate (bbl/d)"})
st.plotly_chart(fig2, width="stretch")

st.markdown("---")
st.caption("Prototype for Renaissance Innovation Week 2026 | Challenge 4 – Leveraging AI for Operational Decision-Making")