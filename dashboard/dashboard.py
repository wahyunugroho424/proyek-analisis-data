import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Fungsi bantu untuk menyiapkan berbagai dataframe
def buat_df_harian(df):
    df_harian = df.resample(rule='D', on='order_delivered_customer_date').agg({
        "order_id": "nunique",
        "price": "sum"
    })
    df_harian = df_harian.reset_index()
    df_harian.rename(columns={
        "order_id": "jumlah_pesanan",
        "price": "pendapatan"
    }, inplace=True)
    
    return df_harian

def buat_df_produk(df):
    df_produk = df.groupby("product_name_lenght").product_photos_qty.sum().sort_values(ascending=False).reset_index()
    return df_produk   

def buat_df_per_provinsi(df):
    df_provinsi = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    df_provinsi.rename(columns={
        "customer_id": "jumlah_pelanggan"
    }, inplace=True)
    
    return df_provinsi

def buat_df_rfm(df):
    df_rfm = df.groupby(by="customer_id", as_index=False).agg({
        "order_delivered_customer_date": "max", # Tanggal terakhir order
        "order_id": "nunique",
        "price": "sum"
    })
    df_rfm.columns = ["customer_id", "tanggal_order_terakhir", "frekuensi", "moneter"]
    
    df_rfm["tanggal_order_terakhir"] = df_rfm["tanggal_order_terakhir"].dt.date
    tanggal_terbaru = df["order_delivered_customer_date"].dt.date.max()
    df_rfm["recency"] = df_rfm["tanggal_order_terakhir"].apply(lambda x: (tanggal_terbaru - x).days)
    df_rfm.drop("tanggal_order_terakhir", axis=1, inplace=True)
    
    return df_rfm

# Memuat data
# Link file Excel yang benar (gunakan `/raw/` dalam URL)
url = "https://github.com/wahyunugroho424/proyek-analisis-data/raw/main/dashboard/all_data.xlsx"

# Membaca file Excel dengan pandas
df = pd.read_excel(url, engine="openpyxl")  # Gunakan engine openpyxl untuk file .xlsx

kolom_tanggal = ["order_delivered_customer_date"]
df.sort_values(by="order_delivered_customer_date", inplace=True)
df.reset_index(inplace=True)

for kolom in kolom_tanggal:
    df[kolom] = pd.to_datetime(df[kolom])

# Filter data
tanggal_min = df["order_delivered_customer_date"].min()
tanggal_max = df["order_delivered_customer_date"].max()

with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    
    start_date, end_date = st.date_input(
        label='Pilih Rentang Waktu', min_value=tanggal_min,
        max_value=tanggal_max, value=[tanggal_min, tanggal_max]
    )

df_main = df[(df["order_delivered_customer_date"] >= str(start_date)) & 
              (df["order_delivered_customer_date"] <= str(end_date))]

# Membuat berbagai dataframe
df_harian = buat_df_harian(df_main)
df_produk = buat_df_produk(df_main)
df_provinsi = buat_df_per_provinsi(df_main)
df_rfm = buat_df_rfm(df_main)

# Tampilan utama dashboard
st.header('Dashboard E-Commerce')
st.subheader('Ringkasan Pesanan Harian')

kol1, kol2 = st.columns(2)

with kol1:
    total_pesanan = df_harian.jumlah_pesanan.sum()
    st.metric("Total Pesanan", value=total_pesanan)

with kol2:
    total_pendapatan = format_currency(df_harian.pendapatan.sum(), "IDR", locale='id_ID') 
    st.metric("Total Pendapatan", value=total_pendapatan)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    df_harian["order_delivered_customer_date"],
    df_harian["jumlah_pesanan"],
    marker='o', linewidth=2, color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)

st.pyplot(fig)

# Performa Produk
st.subheader("Performa Produk")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
warna = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

sns.barplot(x="product_photos_qty", y="product_name_lenght", data=df_produk.head(5), palette=warna, ax=ax[0])
ax[0].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[0].set_title("Produk Terlaris", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="product_photos_qty", y="product_name_lenght", data=df_produk.sort_values(by="product_photos_qty", ascending=True).head(5), palette=warna, ax=ax[1])
ax[1].invert_xaxis()
ax[1].set_xlabel("Jumlah Penjualan", fontsize=30)
ax[1].set_title("Produk Kurang Laku", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)

st.pyplot(fig)

# Pelanggan
st.subheader("Demografi Pelanggan")
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(y="jumlah_pelanggan", x="customer_state", data=df_provinsi, palette="pastel", ax=ax)
ax.set_title("Jumlah Pelanggan per Provinsi", fontsize=30)
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
st.pyplot(fig)

# Pelanggan Terbaik berdasarkan RFM
st.subheader("Pelanggan Terbaik berdasarkan RFM")

kol1, kol2, kol3 = st.columns(3)

with kol1:
    avg_recency = round(df_rfm.recency.mean(), 1)
    st.metric("Rata-rata Recency (hari)", value=avg_recency)

with kol2:
    avg_frekuensi = round(df_rfm.frekuensi.mean(), 2)
    st.metric("Rata-rata Frekuensi", value=avg_frekuensi)

with kol3:
    avg_moneter = format_currency(df_rfm.moneter.mean(), "IDR", locale='id_ID')
    st.metric("Rata-rata Moneter", value=avg_moneter)

st.caption('Coding Camp DBS Foundation © 2025')
