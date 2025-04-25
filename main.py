import streamlit as st
import pandas as pd
from scheduler import jalankan_simulasi
import os
import sys
import shutil

st.set_page_config(page_title="Fuzzy Dokter Scheduler", layout="wide")

st.title("🩺 Fuzzy Dokter Scheduler")

st.markdown("## ✍️ Edit Data CSV")
file_to_edit = st.selectbox("Pilih file yang ingin diedit:", [
    "data/Data Dummy Peserta.csv",
    "data/Data Dummy Wahana.csv",
    "data/Jumlah Pasien.csv"
])

if st.button("💾 Simpan Perubahan", key=f"simpan_{file_to_edit}"):
    backup_file = file_to_edit + ".bak"
    shutil.copy(file_to_edit, backup_file)  # create a backup
    edited_df.to_csv(file_to_edit, index=False)
    st.success(f"Data berhasil disimpan dan backup dibuat di `{os.path.basename(backup_file)}`")

# Load CSV
df_edit = pd.read_csv(file_to_edit)
st.write("📄 Data Saat Ini:")
edited_df = st.data_editor(df_edit, num_rows="dynamic")

# Save Button
if st.button("💾 Simpan Perubahan"):
    edited_df.to_csv(file_to_edit, index=False)
    st.success(f"Perubahan pada `{os.path.basename(file_to_edit)}` berhasil disimpan.")

rs_df = pd.read_csv("data/Data Dummy Wahana.csv")
rs_list = list(rs_df["Nama Wahana"])
rs_tutup = st.selectbox("Pilih Rumah Sakit yang Ditutup (Opsional)", ["Tidak ada"] + rs_list)

# Input jumlah peserta
jumlah_peserta = st.number_input("Jumlah Total Peserta", min_value=1, max_value=100, value=35)
hasil_simulasi, dokter_to_spesialisasi, rs_to_spesialisasi, data_peserta = jalankan_simulasi(jumlah_peserta, rs_tutup)

# Pilih tanggal
tanggal_list = list(hasil_simulasi.keys())
selected_tanggal = st.selectbox("Pilih Tanggal", tanggal_list)

if selected_tanggal:
    data = hasil_simulasi[selected_tanggal]

    st.subheader(f"Hasil untuk Tanggal: {selected_tanggal}")
    
    # Tabel Penjadwalan
    st.markdown("### 📋 Tabel Fuzzy Penjadwalan")
    st.dataframe(pd.DataFrame([{
        "RS": row["RS"],
        "Pasien": row["Pasien"],
        "Jumlah Dokter Awal": row["Jumlah Dokter Awal"],
        "Rasio": row["Rasio"],
        "Aksi": row["Aksi"],
        "Fuzzy Dominan": max({
            'Under Berat': row['Under Berat'],
            'Under Ringan': row['Under Ringan'],
            'Optimal': row['Optimal'],
            'Over Ringan': row['Over Ringan'],
            'Over Berat': row['Over Berat']
        }, key=lambda x: row[x])

    } for row in data["jadwal"]]))

    # Tabel Distribusi Dokter Akhir
    st.markdown("### 🧑‍⚕️ Distribusi Dokter per RS (Setelah Redistribusi)")
    st.dataframe(pd.DataFrame([{
        "RS": row["RS"],
        "Dokter": row["Dokter"],
        "Jumlah Dokter": row["Jumlah Dokter"],
        "Rasio Baru": row["Rasio Baru"]
    } for row in data["jadwal"]]))

    # Tabel Detail Fuzzy
    st.markdown("### 🔍 Detail Fuzzy State per RS")
    for row in data["jadwal"]:
        with st.expander(f"RS: {row['RS']}"):
            st.write(pd.DataFrame({
                "Fuzzy State": [
                    "Underutilized Berat",
                    "Underutilized Ringan",
                    "Optimal",
                    "Overload Ringan",
                    "Overload Berat"
                ],
                "Nilai": [
                    row["Under Berat"],
                    row["Under Ringan"],
                    row["Optimal"],
                    row["Over Ringan"],
                    row["Over Berat"]
                ]
            }))

    st.markdown("## 🧠 Tabel Spesialisasi Dokter")

    semua_spesialisasi = set(rs_to_spesialisasi.values())

    tabel_data = []
    for id_d, sudah_dikerjakan in dokter_to_spesialisasi.items():
        belum_dikerjakan = semua_spesialisasi - sudah_dikerjakan
        tabel_data.append({
            "ID Dokter": id_d,
            "Nama": data_peserta[id_d],
            "Spesialisasi Dikerjakan": ', '.join(sorted(sudah_dikerjakan)),
            "Belum Dikerjakan": ', '.join(sorted(belum_dikerjakan))
        })

    df_spesialisasi = pd.DataFrame(data["rekap_spesialisasi"])
    st.dataframe(df_spesialisasi)

