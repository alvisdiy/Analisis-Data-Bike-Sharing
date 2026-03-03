import pandas as pd
import streamlit as st

st.set_page_config(page_title="Capital Bikeshare Dashboard", page_icon="🚲", layout="wide")

# ----------------------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------------------
def create_daily_rentals_df(df):
    return df.groupby('dteday').agg({'cnt': 'sum'}).reset_index()

def create_hourly_pattern_df(df):
    return df.groupby(['hr', 'workingday'])['cnt'].mean().reset_index()

def create_temp_cluster_df(df):
    return df.groupby('temp_cluster')[['casual', 'registered']].mean().reset_index()

def create_season_df(df):
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    df['season_label'] = df['season'].map(season_mapping)
    return df.groupby('season_label')['cnt'].sum().reset_index()

# ----------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    day_df = pd.read_csv("dashboard\main_data.csv")
    hour_df = pd.read_csv("data/hour.csv") 
    
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    return day_df, hour_df

day_df, hour_df = load_data()

# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
with st.sidebar:
    st.title("🚲 Capital Bikeshare")
    st.markdown("---")
    st.markdown("**Analisis Data Historis (2011 - 2012)**")
    st.markdown("Dashboard ini menyajikan ringkasan performa penyewaan sepeda berdasarkan kondisi lingkungan dan waktu operasional.")
    st.markdown("### Filter Data")
    
    min_date = day_df['dteday'].min()
    max_date = day_df['dteday'].max()

    date_range = st.date_input(
        "Pilih Rentang Tanggal", 
        [min_date, max_date], 
        min_value=min_date, 
        max_value=max_date
    )

    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        st.warning("Silakan pilih tanggal akhir (rentang waktu) di kalender.")
        st.stop()

    selected_season = st.selectbox("Pilih Musim", ['All', 'Spring', 'Summer', 'Fall', 'Winter'])
    workingday_option = st.selectbox("Tipe Hari", ["All", "Hari Kerja", "Libur"])

# ----------------------------------------------------------------
# LOGIKA FILTERING
# ----------------------------------------------------------------
main_day_df = day_df[(day_df["dteday"].dt.date >= start_date) & (day_df["dteday"].dt.date <= end_date)]
main_hour_df = hour_df[(hour_df["dteday"].dt.date >= start_date) & (hour_df["dteday"].dt.date <= end_date)]

if selected_season != 'All':
    season_map = {'Spring': 1, 'Summer': 2, 'Fall': 3, 'Winter': 4}
    main_day_df = main_day_df[main_day_df['season'] == season_map[selected_season]]
    main_hour_df = main_hour_df[main_hour_df['season'] == season_map[selected_season]]

if workingday_option != 'All':
    work_val = 1 if workingday_option == "Hari Kerja" else 0
    main_day_df = main_day_df[main_day_df['workingday'] == work_val]
    main_hour_df = main_hour_df[main_hour_df['workingday'] == work_val]

# Generate DataFrames 
daily_rentals_df = create_daily_rentals_df(main_day_df)
hourly_pattern_df = create_hourly_pattern_df(main_hour_df)
temp_cluster_df = create_temp_cluster_df(main_day_df)
season_df = create_season_df(main_day_df)

# ----------------------------------------------------------------
# MAIN DASHBOARD 
# ----------------------------------------------------------------
st.title('Bike Sharing Analytics Dashboard')

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", value=f"{main_day_df['cnt'].sum():,}")
col2.metric("Pengguna Kasual", value=f"{main_day_df['casual'].sum():,}")
col3.metric("Pengguna Terdaftar", value=f"{main_day_df['registered'].sum():,}")
avg_harian = round(main_day_df['cnt'].mean()) if not main_day_df.empty else 0
col4.metric("Rata-rata Harian", value=f"{avg_harian:,}")

st.markdown("---")

# --- ROW 1: TREN HARIAN & MUSIM ---
st.subheader("Tren Penyewaan & Faktor Musiman")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**Dinamika Penyewaan Harian (2011-2012)**")
    if not daily_rentals_df.empty:
        st.line_chart(data=daily_rentals_df, x='dteday', y='cnt', use_container_width=True)

with col2:
    st.markdown("**Proporsi Berdasarkan Musim**")
    if not season_df.empty:
        # Streamlit tidak punya pie_chart native, kita gunakan bar_chart sebagai alternatif yang lebih baik untuk perbandingan
        st.bar_chart(data=season_df.set_index('season_label'), y='cnt', use_container_width=True)

st.markdown("---")

# --- ROW 2: PERTANYAAN BISNIS UTAMA ---
st.subheader("Analisis Perilaku Pengguna (User Behavior)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pola Jam Sibuk (Hari Kerja vs Libur)**")
    if not hourly_pattern_df.empty:
        # Pivot data agar 'workingday' menjadi kolom untuk multiple lines di st.line_chart
        pivot_hourly = hourly_pattern_df.pivot(index='hr', columns='workingday', values='cnt')
        pivot_hourly.columns = ['Libur', 'Hari Kerja'] if len(pivot_hourly.columns) == 2 else pivot_hourly.columns
        st.line_chart(pivot_hourly, use_container_width=True)

with col2:
    st.markdown("**Dampak Suhu Terhadap Tipe Pengguna**")
    if not temp_cluster_df.empty:
        # Set index ke temp_cluster lalu tampilkan bar_chart untuk casual & registered
        st.bar_chart(data=temp_cluster_df.set_index('temp_cluster')[['casual', 'registered']], use_container_width=True)

st.caption('Created by Alvis Aditya | Dicoding Data Analytics Submission')