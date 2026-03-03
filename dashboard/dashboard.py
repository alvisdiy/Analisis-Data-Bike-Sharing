import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Set konfigurasi halaman Streamlit
st.set_page_config(page_title="Capital Bikeshare Dashboard", page_icon="", layout="wide")
sns.set(style='dark')

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
    # Mapping angka musim ke teks langsung di dalam dashboard
    season_mapping = {1: 'Spring', 2: 'Summer', 3: 'Fall', 4: 'Winter'}
    df['season_label'] = df['season'].map(season_mapping)
    
    return df.groupby('season_label')['cnt'].sum().reset_index()
# ----------------------------------------------------------------
# LOAD DATA
# ----------------------------------------------------------------
@st.cache_data
def load_data():
    day_df = pd.read_csv("main_data.csv")
    hour_df = pd.read_csv("data/hour.csv")
    
    day_df['dteday'] = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    return day_df, hour_df

day_df, hour_df = load_data()

# ----------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------
with st.sidebar:
    st.title("Capital Bikeshare")
    st.markdown("---")
    st.markdown("**Analisis Data Historis (2011 - 2012)**")
    st.markdown("Dashboard ini menyajikan ringkasan performa penyewaan sepeda berdasarkan kondisi lingkungan dan waktu operasional.")

# Generate DataFrames menggunakan Helper
daily_rentals_df = create_daily_rentals_df(day_df)
hourly_pattern_df = create_hourly_pattern_df(hour_df)
temp_cluster_df = create_temp_cluster_df(day_df)
season_df = create_season_df(day_df)

# ----------------------------------------------------------------
# MAIN DASHBOARD 
# ----------------------------------------------------------------
st.title('Bike Sharing Analytics Dashboard')

# --- METRIK UTAMA ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Penyewaan", value=f"{day_df['cnt'].sum():,}")
col2.metric("Pengguna Kasual", value=f"{day_df['casual'].sum():,}")
col3.metric("Pengguna Terdaftar", value=f"{day_df['registered'].sum():,}")
col4.metric("Rata-rata Harian", value=f"{round(day_df['cnt'].mean()):,}")

st.markdown("---")

# --- ROW 1: TREN HARIAN & MUSIM ---
st.subheader("Tren Penyewaan & Faktor Musiman")
col1, col2 = st.columns([2, 1])

with col1:
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.plot(daily_rentals_df["dteday"], daily_rentals_df["cnt"], linewidth=1.5, color="#2E86C1", alpha=0.9)
    ax.set_title("Dinamika Penyewaan Harian (2011-2012)", fontsize=14)
    ax.set_ylabel("Jumlah Penyewaan")
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']
    ax.pie(season_df['cnt'], labels=season_df['season_label'], autopct='%1.1f%%', colors=colors, startangle=90, wedgeprops={'edgecolor': 'white'})
    ax.set_title("Proporsi Berdasarkan Musim", fontsize=14)
    st.pyplot(fig)

st.markdown("---")

# --- ROW 2: PERTANYAAN BISNIS UTAMA ---
st.subheader("Analisis Perilaku Pengguna (User Behavior)")
col1, col2 = st.columns(2)

with col1:
    st.markdown("**Pola Jam Sibuk (Hari Kerja vs Libur)**")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x='hr', y='cnt', hue='workingday', data=hourly_pattern_df, palette=['#FF9999', '#66B2FF'], linewidth=3, ax=ax)
    ax.set_xlabel('Jam (0-23)')
    ax.set_ylabel('Rata-rata Penyewaan')
    ax.legend(title='Hari Kerja (1=Ya, 0=Tidak)')
    ax.set_xticks(range(0, 24, 2))
    st.pyplot(fig)
    st.info("**Insight:** Puncak komuter terjadi di jam 08:00 dan 17:00 pada hari kerja. Akhir pekan didominasi peminjaman rekreasi di siang hari.")

with col2:
    st.markdown("**Dampak Suhu Terhadap Tipe Pengguna**")
    melted_cluster = temp_cluster_df.melt(id_vars='temp_cluster', value_vars=['casual', 'registered'], var_name='user_type', value_name='average_rentals')
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x='temp_cluster', y='average_rentals', hue='user_type', data=melted_cluster, palette='viridis', order=['Cold', 'Mild', 'Hot'], ax=ax)
    ax.set_xlabel("Kategori Suhu")
    ax.set_ylabel("Rata-rata Penyewaan")
    st.pyplot(fig)
    st.info("**Insight:** Pengguna kasual sangat sensitif cuaca (suka suhu hangat). Pengguna terdaftar (komuter) jauh lebih tangguh menghadapi cuaca dingin.")

# --- FOOTER ---
st.caption(' Created by Alvis Aditya | Dicoding Data Analytics Submission')