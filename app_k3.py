import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="KUIS SHE", page_icon="👷", layout="centered")

# --- HEADER KORPORAT ---
st.title("KUIS SHE")
st.subheader("PT SUMBAWA JUTARAYA")
st.caption("SHE & BIODIVERSITY DEPARTMENT")
st.markdown("---")

# --- LOAD DATABASE EXCEL / CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("Bank_Soal.csv")
    
    # 💡 ANTI-SPASI GAIB: Membersihkan spasi tersembunyi di semua judul kolom CSV
    df.columns = df.columns.str.strip()
    
    # Hanya panggil soal yang sudah Ready
    df = df[(df['Status Validasi'] == '✅ Ready') | (df['Status Validasi'].isna())]
    df = df.dropna(subset=['ID Soal'])
    return df

try:
    df_soal = load_data()
except FileNotFoundError:
    st.error("🚨 File Bank_Soal.csv tidak ditemukan di folder ini.")
    st.stop()

# --- FORM IDENTITAS ---
st.write("Silakan lengkapi identitas untuk memulai kuis.")
nama_peserta = st.text_input("Nama Lengkap:")
departemen = st.selectbox("Departemen / Area:", ["Pilih", "RDE", "SHE", "MSM", "Legal", "HCGS", "Risk Management & Internal Audit", "CSR", "PCM", "IOT", "FAM"])

# --- ENGINE KUIS INTERAKTIF ---
if nama_peserta and departemen != "Pilih":
    with st.form("formulir_kuis"):
        st.markdown("### 📋 Lembar Ujian Uji Kompetensi")
        jawaban_user = {}
        
        # Looping memunculkan soal secara otomatis
        for index, row in df_soal.iterrows():
            id_soal = row['ID Soal']
            pertanyaan = row['Teks Pertanyaan']
            tipe = str(row['Tipe Soal']).strip()
            
            st.markdown(f"**{id_soal} | {pertanyaan}**")
            
            if tipe == 'Pilihan Ganda':
                opsi = [f"A. {row['Opsi A']}", f"B. {row['Opsi B']}", f"C. {row['Opsi C']}", f"D. {row['Opsi D']}"]
                pilihan = st.radio(f"Jawaban {id_soal}:", opsi, key=id_soal, index=None, label_visibility="collapsed")
                if pilihan:
                    jawaban_user[id_soal] = pilihan[0] # Mengambil huruf depannya saja (A/B/C/D)
                else:
                    jawaban_user[id_soal] = ""
                
            elif tipe == 'Benar/Salah':
                pilihan = st.radio(f"Jawaban {id_soal}:", ["BENAR", "SALAH"], key=id_soal, index=None, label_visibility="collapsed")
                if pilihan:
                    jawaban_user[id_soal] = pilihan
                else:
                    jawaban_user[id_soal] = ""
                
            st.write("") 
            
        st.markdown("---")
        submitted = st.form_submit_button("Submit & Evaluasi Otomatis", type="primary")
        
        # --- MESIN PENILAIAN & PENYIMPANAN OTOMATIS ---
        if submitted:
            # Validasi: Cek apakah ada soal yang belum dijawab
            belum_dijawab = False
            for index, row in df_soal.iterrows():
                id_soal = row['ID Soal']
                if not jawaban_user.get(id_soal):
                    belum_dijawab = True
                    break
            
            if belum_dijawab:
                st.warning("⚠️ Mohon jawab semua pertanyaan terlebih dahulu sebelum melakukan submit!")
            else:
                skor_total = 0
                for index, row in df_soal.iterrows():
                    id_soal = row['ID Soal']
                    kunci = str(row['Kunci Jawaban']).strip().upper()
                    jawab = str(jawaban_user.get(id_soal, '')).strip().upper()
                    
                    # 💡 KONVERSI AMAN: Mencegah error tipe data desimal/float dari pandas
                    try:
                        bobot_angka = int(float(row['Bobot Nilai']))
                    except (ValueError, TypeError):
                        bobot_angka = 0
                    
                    if jawab == kunci:
                        skor_total += bobot_angka
                
                # Menentukan status kelulusan (KKM: 120)
                status_hasil = "LULUS" if skor_total >= 120 else "GAGAL"
                
                # --- SIMPAN DATA KE CSV REKAP ---
                data_baru = pd.DataFrame({
                    "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                    "Nama": [nama_peserta],
                    "Departemen": [departemen],
                    "Skor Akhir": [skor_total],
                    "Status": [status_hasil]
                })
                
                file_rekap = "rekap_nilai_she.csv"
                if os.path.exists(file_rekap):
                    df_existing = pd.read_csv(file_rekap)
                    df_updated = pd.concat([df_existing, data_baru], ignore_index=True)
                else:
                    df_updated = data_baru
                    
                df_updated.to_csv(file_rekap, index=False)
                
                # Tampilan Hasil Eksekutif
                st.markdown("### 📊 Hasil Asesmen")
                if status_hasil == "LULUS":
                    st.balloons()
                    st.success(f"**STATUS: LULUS** 🎉")
                    st.write(f"Selamat **{nama_peserta}** dari departemen **{departemen}**, skor akhir Anda: **{skor_total} Poin**.")
                    st.info("💡 Kompetensi Keselamatan dan Pengelolaan Lingkungan Operasional Anda telah memenuhi standar.")
                else:
                    st.error(f"**STATUS: GAGAL** ❌")
                    st.write(f"Maaf **{nama_peserta}**, skor Anda **{skor_total} Poin** (KKM: 120).")
                    st.warning("Silakan pelajari kembali modul prosedur dan coba lagi.")

# --- PANEL ADMIN: MELIHAT REKAP NILAI PESERTA ---
st.markdown("---")
with st.expander("🔐 Panel Khusus Admin: Rekapitulasi Nilai Peserta Kuis"):
    st.markdown("<p style='font-size: 0.85rem; color: #64748b;'>Masukkan kata sandi admin untuk mengakses database nilai seluruh responden.</p>", unsafe_allow_html=True)
    password_admin = st.text_input("Password Admin:", type="password", key="input_password_admin")
    
    if password_admin == "sjr2026":  # Password dapat diubah sesuai kebutuhan
        file_rekap = "rekap_nilai_she.csv"
        if os.path.exists(file_rekap):
            df_hasil = pd.read_csv(file_rekap)
            st.markdown("#### Daftar Nilai & Hasil Ujian Peserta")
            st.dataframe(df_hasil, use_container_width=True)
            
            # Tombol Unduh Rekap Nilai
            csv_data_quiz = df_hasil.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Unduh Rekap Nilai (.CSV)",
                data=csv_data_quiz,
                file_name="Rekap_Nilai_Kuis_SHE.csv",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
        else:
            st.info("Belum ada data peserta yang terekam di sistem.")
    elif password_admin != "":
        st.error("Kata sandi admin tidak valid.")

# --- FOOTER ---
st.markdown("---")
st.caption("Dikembangkan dan dikelola oleh: **Ananda Wahyu N | SHE & Biodiversity Intern** | 2026")
