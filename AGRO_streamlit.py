import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="CP Foods - Dashboard Produksi Telur",
    page_icon="🥚",
    layout="wide"
)

# CP Foods theme colors
CP_COLORS = {
    'primary': '#003399',    # Biru CP
    'secondary': '#FF6600',  # Oranye CP
    'success': '#28a745',
    'warning': '#ffc107',
    'danger': '#dc3545',
    'light': '#f8f9fa',
    'dark': '#343a40'
}

# Generate static data for one month
def create_static_data():
    dates = pd.date_range(end=datetime.now(), periods=30)
    
    data = {
        'tanggal': dates,
        'total_telur': [
            82500, 83000, 82800, 83200, 82900, 82700, 82600,  # Week 1
            83500, 83600, 83400, 83800, 83700, 83500, 83400,  # Week 2
            84000, 84200, 84100, 84300, 84200, 84000, 83900,  # Week 3
            84500, 84600, 84400, 84800, 84700, 84500, 84400,  # Week 4
            84900, 85000  # Last two days
        ],
        'ayam_sehat': [
            100000 - i * 10 for i in range(30)  # Slight decrease over time
        ],
        'konsumsi_pakan_kg': [
            12000 + np.random.normal(0, 100) for _ in range(30)
        ],
        'angka_kematian': [
            0.1 + i * 0.001 for i in range(30)  # Slight increase over time
        ],
        'jumlah_sakit': [
            45 + i for i in range(30)  # Gradual increase
        ],
        'skor_kesehatan': [
            8.5 - i * 0.02 for i in range(30)  # Slight decrease
        ],
        'berat_ayam_rata': [
            1.8 + i * 0.01 for i in range(30)  # Gradual increase
        ],
        'uniformitas': [
            85 - i * 0.1 for i in range(30)  # Slight decrease
        ],
        'konsumsi_air_l': [
            20000 + np.random.normal(0, 200) for _ in range(30)
        ],
        'berat_telur_rata': [
            60 + i * 0.1 for i in range(30)  # Gradual increase
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate derived metrics
    df['hen_day_production'] = (df['total_telur'] / df['ayam_sehat']) * 100
    df['fcr'] = df['konsumsi_pakan_kg'] / (df['total_telur'] * df['berat_telur_rata']/1000)
    df['rasio_air_pakan'] = df['konsumsi_air_l'] / df['konsumsi_pakan_kg']
    
    return df

# Custom CSS
st.markdown("""
    <style>
    .stMetric .metric-label { font-size: 16px !important; }
    .stMetric .metric-value { color: #003399 !important; }
    .reportview-container { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# Header
st.title("🏢 Sistem AI untuk Bisnis Telur AGRO")
st.markdown("Monitoring produksi telur secara real-time")

# Load data
df = create_static_data()

# Sidebar filters
st.sidebar.header("Filter Data")
selected_date = st.sidebar.date_input(
    "Pilih Tanggal",
    value=datetime.now()
)

selected_farm = st.sidebar.selectbox(
    "Pilih Lokasi Kandang",
    ["Kandang A - Jakarta", "Kandang B - Surabaya", "Kandang C - Bandung"]
)

# KPI Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Produksi Telur Harian",
        f"{df['total_telur'].iloc[-1]:,.0f}",
        f"{df['total_telur'].iloc[-1] - df['total_telur'].iloc[-2]:,.0f}"
    )

with col2:
    st.metric(
        "HDP (%)",
        f"{df['hen_day_production'].iloc[-1]:.1f}%",
        f"{df['hen_day_production'].iloc[-1] - df['hen_day_production'].iloc[-2]:.1f}%"
    )

with col3:
    st.metric(
        "FCR",
        f"{df['fcr'].iloc[-1]:.2f}",
        f"{df['fcr'].iloc[-1] - df['fcr'].iloc[-2]:.2f}"
    )

with col4:
    st.metric(
        "Mortalitas",
        f"{df['angka_kematian'].iloc[-1]:.2f}%",
        f"{df['angka_kematian'].iloc[-1] - df['angka_kematian'].iloc[-2]:.2f}%"
    )

# Production Trend
st.subheader("Tren Produksi Telur")
fig_prod = go.Figure()
fig_prod.add_trace(go.Scatter(
    x=df['tanggal'],
    y=df['total_telur'],
    name='Produksi Telur Harian',
    line=dict(color=CP_COLORS['primary'], width=2),
    fill='tozeroy'
))
fig_prod.update_layout(height=400)
st.plotly_chart(fig_prod, use_container_width=True)

# Health Metrics
st.subheader("Metrik Kesehatan")
col1, col2 = st.columns(2)

with col1:
    fig_health = make_subplots(specs=[[{"secondary_y": True}]])
    fig_health.add_trace(
        go.Scatter(x=df['tanggal'], y=df['skor_kesehatan'],
                  name='Skor Kesehatan',
                  line=dict(color=CP_COLORS['primary'])),
        secondary_y=False
    )
    fig_health.add_trace(
        go.Scatter(x=df['tanggal'], y=df['angka_kematian'],
                  name='Mortalitas (%)',
                  line=dict(color=CP_COLORS['danger'])),
        secondary_y=True
    )
    fig_health.update_layout(height=400)
    st.plotly_chart(fig_health, use_container_width=True)

with col2:
    fig_weight = go.Figure()
    fig_weight.add_trace(go.Histogram(
        x=df['berat_ayam_rata'],
        nbinsx=20,
        name='Distribusi Berat'
    ))
    fig_weight.update_layout(height=400)
    st.plotly_chart(fig_weight, use_container_width=True)

# Detailed Data Table
st.subheader("Data Harian Detail")

# Rename columns for display
column_names = {
    'tanggal': 'Tanggal',
    'total_telur': 'Total Telur',
    'ayam_sehat': 'Ayam Sehat',
    'konsumsi_pakan_kg': 'Konsumsi Pakan (kg)',
    'angka_kematian': 'Mortalitas (%)',
    'jumlah_sakit': 'Jumlah Sakit',
    'skor_kesehatan': 'Skor Kesehatan',
    'berat_ayam_rata': 'Berat Ayam (kg)',
    'uniformitas': 'Uniformitas (%)',
    'konsumsi_air_l': 'Konsumsi Air (L)',
    'berat_telur_rata': 'Berat Telur (g)',
    'hen_day_production': 'HDP (%)',
    'fcr': 'FCR',
    'rasio_air_pakan': 'Rasio Air:Pakan'
}

df_display = df.copy()
df_display['tanggal'] = df_display['tanggal'].dt.strftime('%Y-%m-%d')
df_display = df_display.rename(columns=column_names)
df_display = df_display.round(2)

st.dataframe(
    df_display,
    use_container_width=True,
    hide_index=True
)

# Download button
csv = df_display.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Data CSV",
    data=csv,
    file_name="data_produksi_telur.csv",
    mime="text/csv"
)

