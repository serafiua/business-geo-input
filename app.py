import streamlit as st
from streamlit_js_eval import get_geolocation
import pandas as pd
import requests
import os

# Konfigurasi halaman utama
st.set_page_config(page_title="Input Data Usaha", layout="centered")

def get_address_details(lat, lon):
    """Fungsi ekstraksi detail jalan dan kecamatan melalui Nominatim API"""
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}"
        headers = {'User-Agent': 'GeoBizApp-Survey/1.2'}
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        address = data.get('address', {})
        
        # Ekstraksi komponen alamat: jalan dan wilayah administrasi
        road = address.get('road', '')
        suburb = address.get('suburb', address.get('village', address.get('town', '')))
        
        return road, suburb
    except Exception:
        return "", ""

st.title("Form Input Data Lokasi Usaha")

# Input identitas usaha
nama_usaha = st.text_input("Nama Usaha", placeholder="Contoh: Burjo (ARI)")

# Input lokasi yang dapat diisi manual atau otomatis
jalan_input = st.text_input("Nama Jalan", 
                            value=st.session_state.get('jalan', ""))

kecamatan_input = st.text_input("Kecamatan", 
                                value=st.session_state.get('kecamatan', ""))


# Tombol untuk menarik koordinat dan saran alamat
if st.button("Ambil Koordinat"):
    location = get_geolocation(component_key="get_location_button")
    
    if location:
        lat = location['coords']['latitude']
        lon = location['coords']['longitude']
        
        # Penyimpanan koordinat ke session state
        st.session_state.lat = lat
        st.session_state.lon = lon
        
        # Pengambilan saran detail jalan dan kecamatan
        with st.spinner("Mengidentifikasi lokasi..."):
            jalan, kecamatan = get_address_details(lat, lon)
            st.session_state.jalan = jalan
            st.session_state.kecamatan = kecamatan
            
        st.rerun() 
    else:
        st.error("Gagal menarik lokasi. Pastikan GPS aktif dan izin browser diberikan.")

# Tampilan koordinat (Tetap dikunci demi akurasi sistem)
col1, col2 = st.columns(2)
with col1:
    st.number_input("Latitude", value=st.session_state.get('lat', 0.0), format="%.15f", disabled=True)
with col2:
    st.number_input("Longitude", value=st.session_state.get('lon', 0.0), format="%.15f", disabled=True)

# Logika penyimpanan data ke CSV
if st.button("Simpan Data"):
    lat_val = st.session_state.get('lat', 0.0)

    if nama_usaha and lat_val != 0.0 and jalan_input and kecamatan_input:
        data_baru = {
            "Nama Usaha": [nama_usaha],
            "Nama Jalan": [jalan_input],
            "Kecamatan": [kecamatan_input],
            "Latitude": [lat_val],
            "Longitude": [st.session_state.get('lon', 0.0)]
        }
        df_baru = pd.DataFrame(data_baru)
        
        file_name = "data_usaha.csv"
        
        if not os.path.isfile(file_name):
            df_baru.to_csv(file_name, index=False)
        else:
            df_baru.to_csv(file_name, mode='a', index=False, header=False)
            
        st.balloons()
        st.success("Data berhasil disimpan ke tabel.")
    else:
        st.warning("Lengkapi Nama Usaha, Jalan, Kecamatan, dan pastikan Koordinat sudah diambil.")

# Preview Tabel CSV
st.divider()
st.subheader("📊 Preview Data Usaha")
if os.path.exists("data_usaha.csv"):
    df_preview = pd.read_csv("data_usaha.csv")
    st.dataframe(df_preview, use_container_width=True)
else:
    st.info("Belum ada data yang tersimpan.")
