import streamlit as st
import pandas as pd

# --- KONFIGURASI HALAMAN ---
st.set_page_config(page_title="KUIS SHE", page_icon="👷", layout="centered")

# --- HEADER KORPORAT ---
st.title("KUIS SHE")
st.subheader("PT SUMBAWA JUTARAYA")
st.caption("SHE & BIODIVERSITY DEPARTMENT")
st.markdown("---")

# --- LOAD DATABASE EXCEL ---
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
        
        # --- MESIN PENILAIAN ---
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
                        
                # Tampilan Hasil Eksekutif
                st.markdown("### 📊 Hasil Asesmen")
                if skor_total >= 120:
                    st.balloons()
                    st.success(f"**STATUS: LULUS** 🎉")
                    st.write(f"Selamat **{nama_peserta}** dari departemen **{departemen}**, skor akhir Anda: **{skor_total} Poin**.")
                    st.info("💡 Kompetensi Keselamatan dan Pengelolaan Lingkungan Operasional Anda telah memenuhi standar.")
                else:
                    st.error(f"**STATUS: GAGAL** ❌")
                    st.write(f"Maaf **{nama_peserta}**, skor Anda **{skor_total} Poin** (KKM: 120).")
                    st.warning("Silakan pelajari kembali modul prosedur dan coba lagi.")

# --- FOOTER ---
st.markdown("---")
st.caption("Dikembangkan dan dikelola oleh: **Ananda Wahyu N | SHE & Biodiversity Intern** | 2026")