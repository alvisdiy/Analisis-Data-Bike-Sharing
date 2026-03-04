# 📊 Bike Sharing Data Analysis & Dashboard

## Deskripsi Proyek

Proyek ini bertujuan untuk menganalisis dataset Bike Sharing dan membangun dashboard interaktif menggunakan Streamlit untuk menampilkan insight dari data.

Analisis dilakukan melalui tahapan:
1. Data Gathering
2. Data Cleaning
3. Exploratory Data Analysis (EDA)
4. Explanatory Analysis
5. Dashboard Development

---

## 📂 Struktur Direktori

```text
submission/
├── dashboard/
│   ├── dashboard.py
│   └── main_data.csv
├── data/
│   ├── hour.csv
│   └── day.csv
├── notebook.ipynb
├── requirements.txt
├── README.md
└── url.txt
```

---

## 📊 Insight yang Diperoleh

### 1. Data Gathering
Dataset terdiri dari data penyewaan sepeda per hari dan per jam dengan berbagai variabel seperti cuaca, musim, suhu, dan jumlah penyewaan.

### 2. Data Cleaning
- Mengubah kolom tanggal menjadi format `datetime`
- Memastikan tidak ada missing values signifikan
- Memastikan tipe data sesuai

### 3. Exploratory Data Analysis
- Penyewaan meningkat pada musim tertentu
- Cuaca memiliki pengaruh terhadap jumlah penyewaan
- Pola penyewaan per jam menunjukkan puncak di jam berangkat dan pulang kerja

### 4. Explanatory Analysis
- Musim dan cuaca merupakan faktor utama dalam variasi jumlah penyewaan
- Hari kerja dan akhir pekan menunjukkan pola penggunaan berbeda
- Terdapat pola komuter yang jelas pada data per jam

---

## 🚀 Cara Menjalankan Dashboard Secara Lokal

### 1. Clone Repository

```bash
git clone https://github.com/alvisdiy/Analisis-Data-Bike-Sharing.git
cd submission
```

### 2. Buat Virtual Environment

```bash
python -m venv venv
```

Aktifkan environment:

- **Windows**
  ```bash
  venv\Scripts\activate
  ```

- **Mac/Linux**
  ```bash
  source venv/bin/activate
  ```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan Streamlit

```bash
streamlit run dashboard/dashboard.py
```

---

## 🌐 Dashboard Online

Tautan dashboard dapat ditemukan pada file [url.txt](url.txt).

## 🛠 Tools & Library

- Python
- Pandas
- Matplotlib
- Seaborn
- Streamlit
