import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json
import io

# Common household appliances with their typical power consumption
COMMON_APPLIANCES = {
    "Pilih perangkat...": 0,
    "AC (1 PK)": 700,
    "TV LED (32-inch)": 50,
    "TV LED (42-inch)": 60,
    "TV LED (55-inch)": 100,
    "Kulkas 1 Pintu": 100,
    "Kulkas 2 Pintu": 150,
    "Rice Cooker": 700,
    "Kipas Angin Meja": 35,
    "Kipas Angin Berdiri": 50,
    "Kipas Angin Gantung": 75,
    "Mesin Cuci": 500,
    "Setrika": 1000,
    "Oven Microwave": 800,
    "Komputer Desktop": 200,
    "Laptop": 65,
    "Pengisi Daya Ponsel": 5,
    "Lampu LED 5W": 5,
    "Lampu LED 9W": 9,
    "Lampu LED 13W": 13,
    "Pompa Air": 125,
    "Dispenser": 350,
    "Water Heater": 350,
}

# PLN tariff categories (2024)
PLN_TARIFFS = {
    "R1 / 450 VA - Subsidi": 415.0,
    "R1 / 900 VA - Subsidi": 605.0,
    "R1 / 900 VA": 1352.0,
    "R1 / 1300 VA": 1444.70,
    "R1 / 2200 VA": 1444.70,
    "R2 / 3500-5500 VA": 1699.53,
    "R3 / 6600 VA keatas": 1699.53,
}

def calculate_power_consumption(power_watts, hours_per_day, days):
    power_kw = power_watts / 1000
    kwh = power_kw * hours_per_day * days
    return kwh

def calculate_cost(kwh, rate_per_kwh):
    return kwh * rate_per_kwh

def add_devices(appliances):
    st.session_state.devices.append(appliances)
    st.session_state.devices.sort(key=lambda x: x["Biaya"], reverse=True)

def main():
    # set the devices
    if 'devices' not in st.session_state:
        st.session_state.devices = []

    # Set page config with custom theme
    st.set_page_config(
        page_title="Kalkulator Biaya Listrik",
        page_icon="⚡",
        layout="wide",
    )
    
    # Custom CSS untuk memperbaiki tampilan
    st.markdown("""
        <style>
        .stButton button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #FF4B4B;
            color: white;
        }
        .stTextInput > div > div > input {
            border-radius: 5px;
        }
        .stNumberInput > div > div > input {
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header dengan warna dan emoji
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>⚡ Kalkulator Biaya Listrik</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2em;'>Hitung biaya listrik Anda dengan mudah!</p>", unsafe_allow_html=True)
    
    # Buat dua kolom untuk input dan output
    input_col, output_col = st.columns([4, 5], gap="large")

    with input_col:
        st.markdown("### 📝 Form Input")
        
        # Bagian Tarif Listrik dengan card-like container
        with st.expander("💰 Tarif Listrik", expanded=True):
            rates = PLN_TARIFFS
            selected_tariff = st.selectbox(
                "Pilih kategori tarif PLN Anda",
                options=list(rates.keys()),
                help="Anda dapat menemukan kategori tarif di tagihan listrik PLN"
            )
            
            rate = rates[selected_tariff]
            st.info(f"Tarif: Rp {rate:,.2f} per kWh")
            
            custom_rate = st.number_input(
                "Atau masukkan tarif khusus per kWh",
                min_value=0.0,
                max_value=10000.0,
                value=float(rate),
                step=0.1,
                help="Masukkan tarif listrik spesifik Anda jika diketahui"
            )
            
            if custom_rate != rate:
                rate = custom_rate

        # Bagian Input Perangkat
        with st.expander("🔌 Detail Perangkat", expanded=True):
            name = st.text_input(
                "Nama Perangkat",
                placeholder="Contoh: AC Ruang Tamu",
                help="Masukkan nama atau lokasi perangkat untuk identifikasi"
            )

            selected_appliance = st.selectbox(
                "Pilih perangkat dari daftar",
                options=list(COMMON_APPLIANCES.keys()),
                help="Pilih perangkat dari daftar umum perangkat rumah tangga"
            )
            power = COMMON_APPLIANCES[selected_appliance]
            if power > 0:
                st.info(f"💡 Daya: {power} watt")
            
            st.markdown("##### Input Manual")
            custom_power = st.number_input(
                "Sesuaikan daya (watt)",
                min_value=0,
                value=power if power > 0 else 0,
                help="Sesuaikan daya sesuai dengan spesifikasi perangkat Anda"
            )

            st.markdown("##### Input berdasarkan Tegangan dan Arus")
            voltage = st.number_input(
                "Masukkan tegangan (Volt)",
                min_value=0.0,
                value=220.0,
                help="Masukkan tegangan dalam Volt (default: 220V)"
            )
            ampere = st.number_input(
                "Masukkan arus (Ampere)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                help="Masukkan arus dalam Ampere"
            )
            
            # Calculate power if voltage and ampere are provided
            if ampere > 0:
                calculated_power = voltage * ampere
                st.info(f"💡 Daya terhitung dari V×A: {calculated_power:.1f} watt")
        
        # Bagian Pola Penggunaan
        with st.expander("⏰ Pola Penggunaan", expanded=True):
            usage_pattern = st.radio(
                "Berapa lama perangkat digunakan?",
                ["24 Jam (Harian)", "Beberapa jam per hari", "Kustom"],
                index=1,
                help="Pilih pola penggunaan perangkat"
            )
            
            if usage_pattern == "24 Jam (Harian)":
                hours = 24.0
                st.info("⚡ Perangkat akan dihitung untuk penggunaan 24 jam")
            elif usage_pattern == "Beberapa jam per hari":
                hours = st.slider(
                    "Jam per hari",
                    0.0, 24.0, 8.0,
                    help="Geser untuk memilih jumlah jam penggunaan per hari"
                )
            else:
                hours = st.number_input(
                    "Masukkan jam per hari",
                    min_value=0.0,
                    max_value=24.0,
                    value=8.0,
                    help="Masukkan jumlah jam penggunaan spesifik per hari"
                )

            period = st.radio(
                "Pilih periode perhitungan",
                ["1 hari", "1 minggu", "1 bulan", "Kustom"],
                index=2,
                help="Pilih periode waktu untuk perhitungan"
            )
            
            if period == "1 hari":
                days = 1
            elif period == "1 minggu":
                days = 7
            elif period == "1 bulan":
                days = 30
            else:
                days = st.number_input(
                    "Jumlah hari",
                    min_value=1,
                    value=30,
                    help="Masukkan jumlah hari spesifik untuk perhitungan"
                )

        # Tombol untuk menambahkan perangkat
        if st.button("➕ Tambah Perangkat", use_container_width=True):
            if not name:
                st.error("⚠️ Mohon masukkan nama perangkat!")
                return

            if ampere > 0 and custom_power > 0:
                st.error("⚠️ Ambil salah satu antara hitung daya ampere atau masukkan daya sendiri!")
                return

            # Determine final power based on inputs
            if ampere > 0:
                final_power = calculated_power
            else:
                final_power = custom_power

            if final_power <= 0:
                st.error("⚠️ Daya perangkat harus lebih dari 0 watt!")
                return

            # Hitung konsumsi dan biaya
            kwh = calculate_power_consumption(final_power, hours, days)
            cost = calculate_cost(kwh, rate)
            
            appliances = {
                "Nama": name,
                "Daya": final_power,
                "KWH": kwh,
                "Biaya": cost,
                "Jam per hari": hours,
                "Hari": days
            }

            # Tambahkan perangkat ke daftar
            add_devices(appliances)
            st.success("✅ Perangkat berhasil ditambahkan!")

    with output_col:
        st.markdown("### 📊 Hasil Perhitungan")
        
        devices = st.session_state.devices
        
        if not devices:
            st.info("💡 Belum ada perangkat yang ditambahkan. Silakan tambahkan perangkat di panel kiri.")
        else:
            # Tampilkan ringkasan total
            total_cost = sum(device["Biaya"] for device in devices)
            total_kwh = sum(device["KWH"] for device in devices)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Total Konsumsi Listrik",
                    f"{total_kwh:.1f} kWh",
                    delta=f"{len(devices)} perangkat"
                )
            with col2:
                st.metric(
                    "Total Biaya",
                    f"Rp {total_cost:,.0f}",
                    delta=f"Rp {total_cost/30:,.0f}/hari" if total_cost > 0 else None
                )

            # Tampilkan tabel perangkat
            st.markdown("#### Daftar Perangkat")
            df = pd.DataFrame(devices)
            df.index += 1
            
            # Format kolom dengan Rupiah dan unit yang sesuai
            formatted_df = df.style.format({
                "Daya": "{:.0f} W",
                "KWH": "{:.1f} kWh",
                "Biaya": "Rp {:,.0f}",
                "Jam per hari": "{:.1f} jam",
                "Hari": "{:.0f} hari"
            })
            
            st.dataframe(
                formatted_df,
                use_container_width=True,
                height=150 if len(devices) < 5 else 300
            )

            # Tampilkan grafik
            st.markdown("#### Visualisasi")
            tab1, tab2 = st.tabs(["📊 Grafik Biaya", "⚡ Grafik Konsumsi"])
            
            with tab1:
                cost_chart_data = pd.DataFrame(devices).sort_values("Biaya", ascending=True)
                st.bar_chart(
                    data=cost_chart_data,
                    x="Nama",
                    y="Biaya",
                    use_container_width=True
                )
            
            with tab2:
                power_chart_data = pd.DataFrame(devices).sort_values("KWH", ascending=True)
                st.bar_chart(
                    data=power_chart_data,
                    x="Nama",
                    y="KWH",
                    use_container_width=True
                )

            if st.button("🗑️ Hapus Semua", use_container_width=True):
                st.session_state.devices = []
                st.rerun()

            # Tampilkan tips hemat energi
            if total_cost > 500000:
                st.warning("""
                💡 Tips Hemat Energi:
                1. Gunakan perangkat hemat energi (Energy Star)
                2. Matikan perangkat saat tidak digunakan
                3. Manfaatkan cahaya alami di siang hari
                4. Atur suhu AC pada 24-26°C
                5. Gunakan timer untuk perangkat yang tidak perlu menyala 24 jam
                """)

if __name__ == "__main__":
    main()