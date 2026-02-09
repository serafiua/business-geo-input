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

st.title("Form Input Data Lokasi Usaha")

# Input identitas usaha
nama_usaha = st.text_input("Nama Usaha", placeholder="Contoh: Burjo (ARI)")

# Pengambilan data lokasi secara pasif
js_key = f"get_loc_{int(time.time() / 10)}"
loc_data = get_geolocation(component_key=js_key)

if st.button("Ambil Koordinat & Alamat Secara Otomatis"):
    if loc_data:
        st.session_state.lat = loc_data['coords']['latitude']
        st.session_state.lon = loc_data['coords']['longitude']
        
        with st.spinner("Mengidentifikasi lokasi..."):
            jalan, kecamatan = get_address_details(st.session_state.lat, st.session_state.lon)
            st.session_state.jalan = jalan
            st.session_state.kecamatan = kecamatan
        st.success("Lokasi berhasil diambil.")
    else:
        st.warning("Menunggu respon GPS... Klik sekali lagi jika data tidak muncul.")

# Input field yang dapat disesuaikan manual
jalan_input = st.text_input("Nama Jalan", value=st.session_state.jalan)
kecamatan_input = st.text_input("Kecamatan", value=st.session_state.kecamatan)

col1, col2 = st.columns(2)
with col1:
    st.number_input("Latitude", value=st.session_state.lat, format="%.15f", disabled=True)
with col2:
    st.number_input("Longitude", value=st.session_state.lon, format="%.15f", disabled=True)

# Eksekusi penyimpanan data
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
            
        st.success("Data berhasil disimpan.")
        
        # Pembersihan state input
        st.session_state.lat = 0.0
        st.session_state.lon = 0.0
        st.session_state.jalan = ""
        st.session_state.kecamatan = ""
    else:
        st.warning("Lengkapi data usaha dan koordinat.")

# Visualisasi dan manajemen data tersimpan
st.divider()
st.subheader("Preview Data")
file_path = "data_usaha.csv"

if os.path.exists(file_path):
    df_preview = pd.read_csv(file_path)
    st.dataframe(df_preview, use_container_width=True)
    
    col_dl, col_del = st.columns([1, 1])
    
    with col_dl:
        # Fitur unduh file CSV
        csv_bytes = df_preview.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Data CSV",
            data=csv_bytes,
            file_name="data_usaha.csv",
            mime="text/csv",
        )
    
    with col_del:
        # Fitur penghapusan data permanen
        confirm_delete = st.checkbox("Konfirmasi Hapus Semua Data")
        if st.button("Hapus Semua Data", type="primary", disabled=not confirm_delete):
            os.remove(file_path)
            st.warning("Semua data telah dihapus permanen.")
            time.sleep(1)
            st.rerun()
else:
    st.info("Belum ada data yang tersimpan di server.")
