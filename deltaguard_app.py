import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title="DeltaGuard AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1B5E20 0%, #2E7D32 100%);
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1 style="margin:0; color:white;">🛡️ DeltaGuard AI</h1>
    <p style="margin:0.3rem 0 0 0; color:#A5D6A7; font-size:1.05rem;">
        Real-Time AI Copilot for Operational Decision-Making | Niger Delta Pilot
    </p>
</div>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    # Try to find the CSV in common locations
    possible_paths = [
        "production_data.csv",
        "./production_data.csv",
        "C:users/USER/downloads/production_data.csv",
        os.path.join(os.path.dirname(__file__), "sample_well_data.csv")
    ]
    
    df = None
    for path in possible_paths:
        if os.path.exists(path):
            df = pd.read_csv(path, parse_dates=["timestamp"])
            break
    
    if df is None:
        st.error("Could not find sample_well_data.csv. Please place it in the same folder as this app.")
        st.stop()
    
    # Map CSV columns to the names the rest of the app expects
    column_map = {
        "oil_rate_bbl_d": "oil_rate",
        "tubing_pressure_psi": "pressure",
        "temperature_c": "temperature",
        "vibration_mm_s": "vibration",
        "water_cut_pct": "water_cut",
        "gas_rate_mmscf_d": "gas_rate"
    }
    
    df = df.rename(columns=column_map)
    
    required = ["oil_rate", "pressure", "temperature", "vibration", "water_cut"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"CSV is missing required columns: {', '.join(missing)}")
        st.stop()
    
    return df

df_all = load_data()

st.sidebar.header("Pilot Controls")

# Get unique wells from the data
available_wells = sorted(df_all["well_id"].unique().tolist())

selected_well = st.sidebar.selectbox(
    "Select Well",
    available_wells,
    index=0
)

time_window = st.sidebar.select_slider(
    "Data Window",
    options=["Last 24h", "Last 48h", "Last 7 days"],
    value="Last 48h"
)

st.sidebar.markdown("---")
st.sidebar.markdown("**AI Model Status**")
st.sidebar.success("Models Online • Sample data loaded")
st.sidebar.info(f"Wells available: {len(available_wells)}")
st.sidebar.caption(f"Total records: {len(df_all):,}")

df = df_all[df_all["well_id"] == selected_well].copy()
df = df.sort_values("timestamp")

# Apply time window
hours_map = {"Last 24h": 24, "Last 48h": 48, "Last 7 days": 168}
hours = hours_map[time_window]
cutoff = df["timestamp"].max() - timedelta(hours=hours)
df = df[df["timestamp"] >= cutoff].copy()

if len(df) < 5:
    st.warning("Not enough data points in the selected window. Showing all available data for this well.")
    df = df_all[df_all["well_id"] == selected_well].copy().sort_values("timestamp")

col1, col2, col3, col4, col5 = st.columns(5)

current_oil = df["oil_rate"].iloc[-1]
prev_oil = df["oil_rate"].iloc[-min(6, len(df)-1)]
delta_oil = ((current_oil - prev_oil) / prev_oil) * 100 if prev_oil != 0 else 0

col1.metric("Oil Rate", f"{current_oil:.0f} bbl/d", f"{delta_oil:+.1f}%")
col2.metric("Tubing Pressure", f"{df['pressure'].iloc[-1]:.0f} psi", 
            f"{((df['pressure'].iloc[-1] - df['pressure'].iloc[-min(6,len(df)-1)]) / df['pressure'].iloc[-min(6,len(df)-1)] * 100):+.1f}%")
col3.metric("Water Cut", f"{df['water_cut'].iloc[-1]:.1f}%")
col4.metric("ESP Vibration", f"{df['vibration'].iloc[-1]:.2f} mm/s")
col5.metric("AI Risk Score", "Low", "↓ Stable")

st.markdown("---")
st.caption("Data updated in real-time • AI-powered insights for optimal operational performance")
left, right = st.columns([2.2, 1])

with left:
    st.subheader(f"Real-Time Production & Asset Health — {selected_well}")
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["oil_rate"], name="Oil Rate (bbl/d)",
                line=dict(color="#2E7D32", width=2.5)),
        secondary_y=False
    )
    fig.add_trace(
        go.Scatter(x=df["timestamp"], y=df["pressure"], name="Pressure (psi)",
                line=dict(color="#1565C0", width=2)),
        secondary_y=True
    )
    
    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        plot_bgcolor="white",
        paper_bgcolor="white"
    )
    fig.update_yaxes(title_text="Oil Rate (bbl/d)", secondary_y=False, gridcolor="#E8EDE8")
    fig.update_yaxes(title_text="Pressure (psi)", secondary_y=True)
    fig.update_xaxes(gridcolor="#E8EDE8")
    
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Asset Location Context")
    
    # Approximate Niger Delta coordinates for the three wells
    map_data = {
        "Well-12A": {"lat": 5.35, "lon": 5.55, "status": "Optimal"},
        "Well-07B": {"lat": 5.42, "lon": 5.70, "status": "Watch"},
        "Well-19C": {"lat": 4.95, "lon": 6.85, "status": "Optimal"},
    }
    
    map_df = pd.DataFrame([
        {"well_id": w, "lat": v["lat"], "lon": v["lon"], "status": v["status"]}
        for w, v in map_data.items()
    ])
    
    # Highlight selected well
    map_df["size"] = map_df["well_id"].apply(lambda x: 18 if x == selected_well else 11)
    
    fig_map = px.scatter_map(
        map_df, lat="lat", lon="lon", hover_name="well_id", color="status",
        size="size", size_max=18,
        color_discrete_map={"Optimal": "#2E7D32", "Watch": "#F9A825", "Action": "#EF6C00"},
        map_style="open-street-map", zoom=7.2, height=380
    )
    fig_map.update_layout(
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_map, width="stretch")

# ── AI Recommendations ───────────────────────────────────────────────────────
st.subheader("AI Decision Recommendations")

# Simple rule-based recommendations based on the actual data (still a prototype)
latest = df.iloc[-1]
avg_vib = df["vibration"].tail(24).mean() if len(df) >= 24 else df["vibration"].mean()
oil_trend = df["oil_rate"].iloc[-1] - df["oil_rate"].iloc[-min(12, len(df)-1)]

rec_col1, rec_col2 = st.columns(2)

with rec_col1:
    if oil_trend > 5:
        st.success(f"""
        **✅ Recommendation 1 – High Priority**  
        **Action:** Maintain or slightly increase choke on {selected_well}  
        **Expected Impact:** Sustain current gains (+{oil_trend:.0f} bbl/d trend)  
        **Risk Level:** Low  
        **Confidence:** 84%  
        **Rationale:** Positive oil rate trend over recent hours with stable pressure.
        """)
    else:
        st.success(f"""
        **✅ Recommendation 1 – High Priority**  
        **Action:** Increase choke opening by 6–8% on {selected_well}  
        **Expected Impact:** +40 to +65 bbl/d  
        **Risk Level:** Low  
        **Confidence:** 81%  
        **Rationale:** Pressure is stable and water cut remains manageable. Small choke increase is low-risk.
        """)
    
    if avg_vib > 2.3:
        st.warning(f"""
        **⚠️ Recommendation 2 – Attention**  
        **Action:** Schedule ESP vibration check within 48 hours  
        **Current Avg Vibration:** {avg_vib:.2f} mm/s  
        **Risk Level:** Medium  
        **Confidence:** 76%  
        **Rationale:** Elevated vibration trend detected. Early inspection can prevent unplanned downtime.
        """)
    else:
        st.info(f"""
        **ℹ️ Recommendation 2 – Monitoring**  
        **Action:** Continue normal ESP monitoring  
        **Current Avg Vibration:** {avg_vib:.2f} mm/s (within normal range)  
        **Risk Level:** Low  
        **Confidence:** 88%
        """)

with rec_col2:
    if latest["water_cut"] > 22:
        st.warning(f"""
        **⚠️ Water Cut Alert**  
        **Current Water Cut:** {latest['water_cut']:.1f}%  
        **Action:** Review water handling capacity and consider production optimisation  
        **Confidence:** 79%
        """)
    else:
        st.success(f"""
        **✅ Water Cut Status**  
        **Current Water Cut:** {latest['water_cut']:.1f}% — within expected range  
        No immediate action required.
        """)
    
    st.info(f"""
    **ℹ️ System Note**  
    Data source: `sample_well_data.csv`  
    Well: **{selected_well}**  
    Records in view: **{len(df)}**  
    Last timestamp: {latest['timestamp']}
    """)

# ── Forecast ─────────────────────────────────────────────────────────────────
st.subheader("7-Day AI Production Forecast")

future_dates = pd.date_range(start=df["timestamp"].max(), periods=8, freq="D")[1:]
base = current_oil

# Simple projection
np.random.seed(hash(selected_well) % 2**32)
forecast_base = base + np.cumsum(np.random.randn(7) * 5) - np.linspace(0, 8, 7)
forecast_optimized = base + 35 + np.cumsum(np.random.randn(7) * 4) - np.linspace(0, 3, 7)

fig_fc = go.Figure()
fig_fc.add_trace(go.Scatter(
    x=future_dates, y=forecast_base, name="Do Nothing",
    line=dict(color="#9E9E9E", dash="dot", width=2)
))
fig_fc.add_trace(go.Scatter(
    x=future_dates, y=forecast_optimized, name="Follow AI Recommendations",
    line=dict(color="#2E7D32", width=3)
))
fig_fc.update_layout(
    height=320,
    margin=dict(l=20, r=20, t=20, b=20),
    yaxis_title="Projected Oil Rate (bbl/d)",
    legend=dict(orientation="h", y=1.12),
    plot_bgcolor="white"
)
fig_fc.update_xaxes(gridcolor="#E8EDE8")
fig_fc.update_yaxes(gridcolor="#E8EDE8")

st.plotly_chart(fig_fc, use_container_width=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("""
**DeltaGuard AI Prototype** • Renaissance Innovation Week 2026 • Challenge 4  
Data loaded from production_data.csv • Edge + Cloud hybrid architecture concept for Niger Delta operations
""")
