import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

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

def create_weather_temp_heatmap(df):
    pivot_weather_temp = df.pivot_table(
        index='weather_cluster', 
        columns='temp_cluster', 
        values='cnt', 
        aggfunc='mean'
    )
    pivot_weather_temp = pivot_weather_temp.reindex(columns=['Cold', 'Mild', 'Hot'], 
                                                   index=['Clear', 'Misty', 'Bad Weather'])
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot_weather_temp, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax)
    return fig
def create_weather_rentals_df(df):
    # Groupby data cuaca
    weather_clustering = df.groupby('weather_cluster')[['casual', 'registered']].mean().reset_index()
    
    # Melt untuk plot berdampingan (Casual vs Registered)
    melted_weather = weather_clustering.melt(
        id_vars='weather_cluster',
        value_vars=['casual', 'registered'],
        var_name='user_type',
        value_name='average_rentals'
    )
    
    # Memastikan urutan kategorinya konsisten di dashboard
    melted_weather['weather_cluster'] = pd.Categorical(
        melted_weather['weather_cluster'],
        categories=['Clear', 'Misty', 'Bad Weather'],
        ordered=True
    )
    return melted_weather.sort_values('weather_cluster')

def create_season_df(df):
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    df['season_label'] = df['season'].map(season_mapping)
    return df.groupby('season_label')['cnt'].sum().reset_index()

# ----------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

def load_data():
    day_path = os.path.join(BASE_DIR, "main_data.csv")
    hour_path = os.path.join(ROOT_DIR, "data", "hour.csv")

    day_df = pd.read_csv(day_path)
    hour_df = pd.read_csv(hour_path)

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
# LOGIKA FILTERING (SUDAH DIPERBAIKI)
# ----------------------------------------------------------------
main_day_df = day_df[(day_df["dteday"].dt.date >= start_date) & (day_df["dteday"].dt.date <= end_date)]
main_hour_df = hour_df[(hour_df["dteday"].dt.date >= start_date) & (hour_df["dteday"].dt.date <= end_date)]

if selected_season != 'All':
    season_map_for_hour = {'Spring': 1, 'Summer': 2, 'Fall': 3, 'Winter': 4}
    
    # Filter day_df menggunakan TEKS (karena main_data.csv sudah berupa teks)
    main_day_df = main_day_df[main_day_df['season'] == selected_season]
    
    # Filter hour_df menggunakan ANGKA (karena hour.csv masih data mentah)
    main_hour_df = main_hour_df[main_hour_df['season'] == season_map_for_hour[selected_season]]

if workingday_option != 'All':
    # Konversi input filter menjadi nilai yang cocok untuk masing-masing dataset
    work_val_day = "Working Day" if workingday_option == "Hari Kerja" else "Holiday/Weekend"
    work_val_hour = 1 if workingday_option == "Hari Kerja" else 0
    
    # Filter dengan tipe data yang sesuai
    main_day_df = main_day_df[main_day_df['workingday'] == work_val_day]
    main_hour_df = main_hour_df[main_hour_df['workingday'] == work_val_hour]

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
        
        st.markdown("---")
        st.subheader("Dampak Cuaca Terhadap Tipe Pengguna")
       
        # Panggil helper function
        weather_rentals_df = create_weather_rentals_df(main_day_df) # Pastikan variabel dataframe utamamu sesuai, misal main_day_df

        # Buat canvas Matplotlib
        fig_weather, ax_weather = plt.subplots(figsize=(10, 6))

        # Eksekusi visualisasi Seaborn
        sns.barplot(
            x='weather_cluster',
            y='average_rentals',
            hue='user_type',
            data=weather_rentals_df,
            palette='viridis',
            ax=ax_weather
        )

        # Kustomisasi
        ax_weather.set_title('Rata-Rata Penyewaan Sepeda (Casual vs Registered) per Cuaca', fontsize=14, fontweight='bold')
        ax_weather.set_xlabel('Kondisi Cuaca', fontsize=12)
        ax_weather.set_ylabel('Rata-rata Penyewaan', fontsize=12)

        # Tampilkan di Streamlit
        st.pyplot(fig_weather)

with col2:
    st.markdown("**Dampak Suhu Terhadap Tipe Pengguna**")
    if not temp_cluster_df.empty:
        # Set index ke temp_cluster lalu tampilkan bar_chart untuk casual & registered
        st.bar_chart(data=temp_cluster_df.set_index('temp_cluster')[['casual', 'registered']], use_container_width=True)
    st.markdown("---")
    st.subheader("Analisis Lanjutan: Interaksi Cuaca & Suhu")
    fig_heatmap = create_weather_temp_heatmap(main_day_df)
    st.pyplot(fig_heatmap)
    
st.caption('Created by Alvis Aditya | Dicoding Data Analytics Submission')