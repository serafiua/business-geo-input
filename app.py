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
        headers = {'User-Agent': 'GeoBizApp-Survey/1.6'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        address = data.get('address', {})
        
        road = address.get('road', '')
        suburb = address.get('suburb', address.get('village', address.get('town', '')))
        
        return road, suburb
    except Exception:
        return "", ""

# Inisialisasi session state untuk menjaga persistensi data
if 'lat' not in st.session_state: st.session_state.lat = 0.0
if 'lon' not in st.session_state: st.session_state.lon = 0.0
if 'jalan' not in st.session_state: st.session_state.jalan = ""
if 'kecamatan' not in st.session_state: st.session_state.kecamatan = ""

st.title("📍 Form Input Data Usaha")

# Input Nama Usaha
nama_usaha = st.text_input("Nama Usaha", placeholder="Contoh: Burjo (ARI)")

st.subheader("Detail Lokasi")

# Tombol GPS menggunakan key unik untuk menghindari cache browser
# Kita taruh di atas agar eksekusi JS menjadi prioritas pertama
js_key = f"get_loc_{int(time.time() / 10)}" # Key berubah setiap 10 detik agar stabil
loc_data = get_geolocation(component_key=js_key)

if st.button("🌐 Ambil Koordinat & Alamat"):
    if loc_data:
        st.session_state.lat = loc_data['coords']['latitude']
        st.session_state.lon = loc_data['coords']['longitude']
        
        with st.spinner("Mengidentifikasi lokasi..."):
            jalan, kecamatan = get_address_details(st.session_state.lat, st.session_state.lon)
            st.session_state.jalan = jalan
            st.session_state.kecamatan = kecamatan
        st.success("Lokasi berhasil ditarik!")
    else:
        st.warning("Menunggu respon GPS... Pastikan izin lokasi aktif dan klik tombol sekali lagi jika tidak muncul.")

# Input Field yang bisa diedit manual
jalan_input = st.text_input("Nama Jalan", value=st.session_state.jalan)
kecamatan_input = st.text_input("Kecamatan", value=st.session_state.kecamatan)

col1, col2 = st.columns(2)
with col1:
    st.number_input("Latitude", value=st.session_state.lat, format="%.15f", disabled=True)
with col2:
    st.number_input("Longitude", value=st.session_state.lon, format="%.15f", disabled=True)

# Simpan Data
if st.button("Simpan Data"):
    if nama_usaha and st.session_state.lat != 0.0:
        data_baru = {
            "Nama Usaha": [nama_usaha],
            "Nama Jalan": [jalan_input],
            "Kecamatan": [kecamatan_input],
            "Latitude": [st.session_state.lat],
            "Longitude": [st.session_state.lon]
        }
        df_baru = pd.DataFrame(data_baru)
        
        file_name = "data_usaha.csv"
        if not os.path.isfile(file_name):
            df_baru.to_csv(file_name, index=False)
        else:
            df_baru.to_csv(file_name, mode='a', index=False, header=False)
            
        st.balloons()
        st.success("Data berhasil disimpan ke tabel.")
        
        # Reset state setelah simpan agar form bersih untuk input berikutnya
        st.session_state.lat = 0.0
        st.session_state.lon = 0.0
        st.session_state.jalan = ""
        st.session_state.kecamatan = ""
    else:
        st.warning("Lengkapi Nama Usaha dan klik Ambil Koordinat dulu.")

# Preview Tabel CSV
st.divider()
st.subheader("📊 Preview Data")
if os.path.exists("data_usaha.csv"):
    df_preview = pd.read_csv("data_usaha.csv")
    st.dataframe(df_preview, use_container_width=True)
    
    # Tombol Download
    csv_bytes = df_preview.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Data CSV",
        data=csv_bytes,
        file_name="data_usaha.csv",
        mime="text/csv",
    )
else:
    st.info("Belum ada data.")
