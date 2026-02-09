import streamlit as st
from streamlit_js_eval import get_geolocation
import pandas as pd
import requests
import os

# Konfigurasi halaman utama
st.set_page_config(page_title="Input Data Usaha", layout="centered")

def get_address(lat, lon):
    """Fungsi pengambilan alamat jalan dan kecamatan melalui Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'GeoBizApp/1.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        address = data.get('address', {})
        
        # Ekstraksi detail lokasi: jalan dan wilayah administrasi
        road = address.get('road', 'Jalan tidak terdeteksi')
        suburb = address.get('suburb', address.get('village', address.get('town', 'Kecamatan tidak terdeteksi')))
        
        return f"{road}, {suburb}"
    except Exception:
        return "Gagal mendapatkan detail alamat otomatis"

st.title("Form Input Data Lokasi Usaha")

# Input identitas usaha
nama_usaha = st.text_input("Nama Usaha", placeholder="Contoh: Burjo (ARI)")

# Fitur pengambilan data lokasi otomatis
st.subheader("Lokasi")
if st.button("Ambil Koordinat & Alamat"):
    location = get_geolocation()
    if location:
        lat = location['coords']['latitude']
        lon = location['coords']['longitude']
        
        # Penyimpanan koordinat ke session state
        st.session_state.lat = lat
        st.session_state.lon = lon
        
        # Proses reverse geocoding otomatis oleh sistem
        with st.spinner("Sistem sedang mengidentifikasi alamat..."):
            alamat_detail = get_address(lat, lon)
            st.session_state.alamat = alamat_detail
            
        st.success("Data lokasi berhasil ditarik oleh sistem!")
    else:
        st.error("Gagal mengambil lokasi. Pastikan izin GPS aktif di browser.")

# Tampilan koordinat dan alamat (Read-Only)
col1, col2 = st.columns(2)
with col1:
    lat_input = st.number_input("Latitude", 
                                value=st.session_state.get('lat', 0.0), 
                                format="%.15f", 
                                disabled=True) # User tidak bisa edit manual
with col2:
    lon_input = st.number_input("Longitude", 
                                value=st.session_state.get('lon', 0.0), 
                                format="%.15f", 
                                disabled=True) # User tidak bisa edit manual

# Alamat otomatis oleh sistem
alamat_sistem = st.text_area("Alamat", 
                              value=st.session_state.get('alamat', ""), 
                              help="Alamat ini diisi otomatis oleh sistem berdasarkan GPS.",
                              disabled=True) # User tidak bisa input manual

# Validasi dan penyimpanan data
if st.button("Simpan Data"):
    if nama_usaha and lat_input != 0.0 and st.session_state.get('alamat'):
        data_baru = {
            "Nama Usaha": [nama_usaha],
            "Latitude": [lat_input],
            "Longitude": [lon_input],
            "Alamat": [st.session_state.alamat]
        }
        df_baru = pd.DataFrame(data_baru)
        
        file_name = "data_usaha.csv"
        # Penulisan data ke CSV dengan metode append
        if not os.path.isfile(file_name):
            df_baru.to_csv(file_name, index=False)
        else:
            df_baru.to_csv(file_name, mode='a', index=False, header=False)
            
        st.balloons()
        st.success(f"Data '{nama_usaha}' telah tersimpan secara otomatis.")
    else:
        st.warning("Silakan ambil koordinat terlebih dahulu agar alamat terisi otomatis.")