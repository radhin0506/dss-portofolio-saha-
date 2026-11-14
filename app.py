import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Konfigurasi halaman web
st.set_page_config(page_title="DSS Portofolio Saham BRIS, CTRA, TLKM", layout="wide")

st.title("📈 Sistem Pendukung Keputusan (DSS) Portofolio Saham")
st.markdown("Aplikasi berbasis Python & Streamlit untuk Analisis Return, Risiko, Kovarians, Korelasi, dan Portofolio Gabungan.")

# Path file Excel
file_path = "Data_Harga_Close_Mingguan_BRIS_CTRA_TLKM.xlsx"

@st.cache_data
def load_excel_data():
    xls = pd.ExcelFile(file_path)
    sheets = xls.sheet_names
    data_dict = {sheet: pd.read_excel(file_path, sheet_name=sheet) for sheet in sheets}
    return xls.sheet_names, data_dict

try:
    sheet_names, data_dict = load_excel_data()

    # Sidebar Menu
    st.sidebar.header("📁 Menu Navigasi Sheet")
    selected_sheet = st.sidebar.selectbox("Pilih Tampilan Sheet:", sheet_names)

    st.subheader(f"📄 Data dari Sheet: {selected_sheet}")
    df_selected = data_dict[selected_sheet]
    st.dataframe(df_selected, use_container_width=True)

    # Visualisasi Tambahan untuk Harga Close Mingguan
    if selected_sheet == 'Harga Close Mingguan':
        st.markdown("---")
        st.subheader("📊 Grafik Pergerakan Harga Close Mingguan")
        fig, ax = plt.subplots(figsize=(10, 4))
        for col in ['Close BRIS', 'Close CTRA', 'Close TLKM']:
            if col in df_selected.columns:
                ax.plot(df_selected['Tanggal'], df_selected[col], label=col, marker='o', markersize=3)
        ax.set_xlabel("Tanggal")
        ax.set_ylabel("Harga Close (Rp)")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)

    # ==========================================
    # SIMULASI & PERHITUNGAN PORTOFOLIO GABUNGAN
    # ==========================================
    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Simulasi Bobot Portofolio")
    st.sidebar.info("Sesuaikan bobot ketiga saham (total harus 100% / 1.0)")
    
    w_bris = st.sidebar.slider("Bobot BRIS", 0.0, 1.0, 0.40, 0.05)
    w_ctra = st.sidebar.slider("Bobot CTRA", 0.0, 1.0, 0.30, 0.05)
    w_tlkm = st.sidebar.slider("Bobot TLKM", 0.0, 1.0, 0.30, 0.05)

    weights = np.array([w_bris, w_ctra, w_tlkm])
    total_bobot = weights.sum()

    st.markdown("---")
    st.subheader("⚖️ Hasil Simulasi Kinerja Portofolio Gabungan")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Bobot BRIS", f"{w_bris*100:.1f}%")
    col2.metric("Bobot CTRA", f"{w_ctra*100:.1f}%")
    col3.metric("Bobot TLKM", f"{w_tlkm*100:.1f}%")
    col4.metric("Total Bobot", f"{total_bobot*100:.1f}%", delta="Valid" if abs(total_bobot - 1.0) < 1e-4 else "⚠️ Harus 100%")

    # Jika sheet Return / Analisis tersedia di Excel, kita tarik untuk simulasi dinamis
    # Asumsi: Kita hitung dari sheet Return atau data Close jika ada
    if 'Return Saham' in data_dict:
        df_ret = data_dict['Return Saham']
    elif 'Harga Close Mingguan' in data_dict:
        df_close = data_dict['Harga Close Mingguan']
        # Hitung return mingguan otomatis jika belum ada di sheet terpisah
        cols = [c for c in ['Close BRIS', 'Close CTRA', 'Close TLKM'] if c in df_close.columns]
        if len(cols) == 3:
            df_ret = df_close[cols].pct_change().dropna()
        else:
            df_ret = None
    else:
        df_ret = None

    if df_ret is not None and abs(total_bobot - 1.0) < 1e-4:
        # Ambil kolom return numerik saja
        numeric_ret = df_ret.select_dtypes(include=[np.number]).iloc[:, :3]
        
        if numeric_ret.shape[1] == 3:
            # Expected Return rata-rata per periode
            mean_returns = numeric_ret.mean().values
            # Kovarians antar saham
            cov_matrix = numeric_ret.cov().values

            # Perhitungan Portofolio Gabungan
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
            portfolio_std = np.sqrt(portfolio_variance)

            st.success("✅ Perhitungan portofolio gabungan berhasil diperbarui berdasarkan bobot slider Anda!")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Expected Return Portofolio", f"{portfolio_return*100:.4f}% per minggu")
            res_col2.metric("Risiko Portofolio (Std Dev)", f"{portfolio_std*100:.4f}%")
            res_col3.metric("Varians Portofolio", f"{portfolio_variance:.6f}")
        else:
            st.warning("⚠️ Kolom data return untuk 3 saham tidak terdeteksi dengan pas di Excel.")
    elif abs(total_bobot - 1.0) >= 1e-4:
        st.warning("⚠️ Total bobot portofolio Anda belum pas 100% (1.0). Harap sesuaikan slider di sidebar.")

except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
    st.info("Pastikan file Excel Anda berada di folder yang sama dengan file `app.py` di VS Code.")
    # --- BAGIAN DESKRIPSI & KEPUTUSAN OTOMATIS ---
st.subheader("💡 Analisis & Deskripsi Keputusan Portofolio")

# Logika untuk memberikan deskripsi yang beragam berdasarkan hasil perhitungan
# (Sesuaikan variabel 'portfolio_std' dengan nama variabel risiko/standar deviasi di kode Anda)

if portfolio_std < 0.01:
    kategori_risiko = "Rendah (Konservatif) 🛡️"
    deskripsi_keputusan = (
        "**Rekomendasi Keputusan:** Layak Dipertimbangkan untuk Jangka Panjang.\n\n"
        "**Analisis:** Portofolio ini menunjukkan tingkat fluktuasi harga yang relatif stabil dan aman "
        "dari gejolak pasar ekstrem. Mayoritas aset didominasi oleh saham defensif (seperti TLKM). "
        "Sangat cocok bagi investor atau pengambil keputusan yang mengutamakan keamanan modal, "
        "meskipun tingkat keuntungan (*return*) yang dihasilkan cenderung moderat."
    )
elif portfolio_std <= 0.05:
    kategori_risiko = "Sedang (Moderat) ⚖️"
    deskripsi_keputusan = (
        "**Rekomendasi Keputusan:** Seimbang & Layak Dieksekusi.\n\n"
        "**Analisis:** Portofolio berada pada titik keseimbangan yang baik antara tingkat pertumbuhan modal "
        "dan risiko fluktuasi. Kombinasi bobot aset yang dipilih mampu meredam risiko kerugian besar "
        "sekaligus memberikan peluang keuntungan yang kompetitif. "
        "Keputusan ini sangat ideal untuk profil investor dengan horizon waktu menengah."
    )
else:
    kategori_risiko = "Tinggi (Agresif) 🚀"
    deskripsi_keputusan = (
        "**Rekomendasi Keputusan:** Perlu Pengawasan Ketat / Opsional.\n\n"
        "**Analisis:** Portofolio memiliki potensi keuntungan yang sangat tinggi, namun "
        "diiringi oleh tingkat risiko fluktuasi harga (*volatilitas*) yang sangat besar. "
        "Keputusan investasi dengan profil ini hanya disarankan bagi investor yang siap "
        "menghadapi risiko penurunan nilai portofolio dalam jangka pendek demi memburu *return* maksimal."
    )

# Menampilkan hasil ke web Streamlit
st.info(f"**Profil Portofolio:** {kategori_risiko}")
st.markdown(deskripsi_keputusan)
