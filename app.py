import streamlit as st
from streamlit_js_eval import get_geolocation
import pandas as pd
import requests
import os
import time

# Konfigurasi halaman utama
st.set_page_config(page_title="Input Data Usaha", layout="centered")

def get_address_details(lat, lon):
    """Fungsi pengambilan detail alamat melalui Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'GeoBizApp-Survey/1.4'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        address = data.get('address', {})
        
        road = address.get('road', '')
        suburb = address.get('suburb', address.get('village', address.get('town', '')))
        
        return road, suburb
    except Exception:
        return "", ""

# Inisialisasi session state agar data tidak hilang saat interaksi UI
if 'lat' not in st.session_state:
    st.session_state.lat = 0.0
if 'lon' not in st.session_state:
    st.session_state.lon = 0.0
if 'jalan' not in st.session_state:
    st.session_state.jalan = ""
if 'kecamatan' not in st.session_state:
    st.session_state.kecamatan = ""

st.title("📍 Form Input Data Usaha")

# Input Nama Usaha (di luar form agar tidak ter-reset saat ambil GPS)
nama_usaha = st.text_input("Nama Usaha", placeholder="Contoh: Burjo (ARI)")

st.subheader("Detail Lokasi")

# Tombol GPS diletakkan di luar form agar eksekusi JavaScript tidak terhambat
if st.button("🌐 Ambil Koordinat & Alamat"):
    js_key = f"get_loc_{int(time.time())}"
    location = get_geolocation(component_key=js_key)
    
    if location:
        st.session_state.lat = location['coords']['latitude']
        st.session_state.lon = location['coords']['longitude']
        
        with st.spinner("Mengidentifikasi lokasi..."):
            jalan, kecamatan = get_address_details(st.session_state.lat, st.session_state.lon)
            st.session_state.jalan = jalan
            st.session_state.kecamatan = kecamatan
        st.success("Lokasi berhasil ditarik!")
    else:
        st.error("GPS tidak merespon. Pastikan izin lokasi aktif.")

# Menggunakan kolom input yang terikat langsung ke session state
jalan_input = st.text_input("Nama Jalan", value=st.session_state.jalan, key="jalan_widget")
kecamatan_input = st.text_input("Kecamatan", value=st.session_state.kecamatan, key="kec_widget")

col1, col2 = st.columns(2)
with col1:
    st.number_input("Latitude", value=st.session_state.lat, format="%.15f", disabled=True)
with col2:
    st.number_input("Longitude", value=st.session_state.lon, format="%.15f", disabled=True)

# Logika penyimpanan data
if st.button("Simpan ke CSV"):
    # Validasi data sebelum simpan
    if nama_usaha and st.session_state.lat != 0.0:
        data_baru = {
            "Nama Usaha": [nama_usaha],
            "Nama Jalan": [jalan_input], # Mengambil inputan terbaru dari widget
            "Kecamatan": [kecamatan_input], # Mengambil inputan terbaru dari widget
            "Latitude": [st.session_state.lat],
            "Longitude": [st.session_state.lon]
        }
        df_baru = pd.DataFrame(data_baru)
        
        file_name = "data_usaha.csv"
        # Penulisan data ke CSV (Append Mode)
        if not os.path.isfile(file_name):
            df_baru.to_csv(file_name, index=False)
        else:
            df_baru.to_csv(file_name, mode='a', index=False, header=False)
            
        st.balloons()
        st.success(f"Data '{nama_usaha}' berhasil ditambahkan.")
        
        # Reset input setelah simpan (opsional, agar siap input data berikutnya)
        st.session_state.lat = 0.0
        st.session_state.lon = 0.0
        st.session_state.jalan = ""
        st.session_state.kecamatan = ""
    else:
        st.warning("Lengkapi Nama Usaha dan ambil koordinat terlebih dahulu.")

# Preview Tabel CSV
st.divider()
st.subheader("📊 Preview Data Terkumpul")
if os.path.exists("data_usaha.csv"):
    df_preview = pd.read_csv("data_usaha.csv")
    st.dataframe(df_preview, use_container_width=True)
    
    # Tombol Download untuk mendapatkan file CSV utuh
    csv_data = df_preview.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV",
        data=csv_data,
        file_name="data_usaha_total.csv",
        mime="text/csv",
    )
else:
    st.info("Belum ada data yang tersimpan.")
