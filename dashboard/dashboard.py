import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='dark')

# Memuat data
url = "https://github.com/wahyunugroho424/proyek-analisis-data/raw/main/dashboard/all_data.xlsx"
df = pd.read_excel(url, engine="openpyxl")

# Pastikan kolom tanggal dalam format datetime
df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])

tanggal_min = df["order_delivered_customer_date"].min().date()
tanggal_max = df["order_delivered_customer_date"].max().date()

# Sidebar untuk memilih rentang tanggal
with st.sidebar:
    st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")
    tanggal_range = st.date_input(
        "Pilih Rentang Waktu", 
        min_value=tanggal_min, 
        max_value=tanggal_max, 
        value=(tanggal_min, tanggal_max)  # Pastikan dalam bentuk tuple
    )
    
    # Jika hanya satu tanggal yang dipilih, gunakan default
    if isinstance(tanggal_range, tuple) and len(tanggal_range) == 2:
        start_date, end_date = tanggal_range
    else:
        start_date, end_date = tanggal_min, tanggal_max

# Filter data berdasarkan rentang waktu
df_main = df[(df["order_delivered_customer_date"] >= pd.Timestamp(start_date)) & 
              (df["order_delivered_customer_date"] <= pd.Timestamp(end_date))]

# Menghitung jumlah pesanan per minggu
df_mingguan = df_main.resample('W', on="order_delivered_customer_date")["order_id"].nunique().reset_index()

# Visualisasi tren jumlah pesanan mingguan
st.header('Dashboard E-Commerce')
st.subheader('Tren Jumlah Pesanan Mingguan')
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df_mingguan["order_delivered_customer_date"], df_mingguan["order_id"], marker='o', linestyle='-', color="blue")
ax.set_xlabel("Tanggal")
ax.set_ylabel("Jumlah Pesanan")
ax.set_title("Tren Jumlah Pesanan Mingguan")
plt.xticks(rotation=45)
st.pyplot(fig)

# Produk Terlaris dan Kurang Laku
df_produk = df_main.groupby("product_id")["order_id"].count().reset_index()
df_produk = df_produk.rename(columns={"order_id": "jumlah_penjualan"})
df_produk = df_produk.merge(df_main[["product_id", "product_category_name"]].drop_duplicates(), on="product_id")

fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(20, 6))

# Produk Terlaris (Top 5)
top5 = df_produk.nlargest(5, "jumlah_penjualan")
sns.barplot(x="product_category_name", y="jumlah_penjualan", data=top5, ax=ax[0], color="blue")
ax[0].set_title("Produk Terlaris")
ax[0].set_xticklabels(ax[0].get_xticklabels(), rotation=45)

# Produk Kurang Laku (Bottom 5)
bottom5 = df_produk.nsmallest(5, "jumlah_penjualan")
sns.barplot(x="product_category_name", y="jumlah_penjualan", data=bottom5, ax=ax[1], color="red")
ax[1].set_title("Produk Kurang Laku")
ax[1].set_xticklabels(ax[1].get_xticklabels(), rotation=45)

st.subheader("Performa Produk")
st.pyplot(fig)

# Distribusi jumlah pelanggan berdasarkan provinsi
df_provinsi = df_main.groupby("customer_state")["customer_id"].nunique().reset_index()

fig, ax = plt.subplots(figsize=(12, 6))
sns.barplot(x="customer_state", y="customer_id", data=df_provinsi, color="#3498db")
ax.set_title("Distribusi Jumlah Pelanggan Berdasarkan Provinsi")
ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
st.subheader("Demografi Pelanggan")
st.pyplot(fig)

st.caption('Coding Camp DBS Foundation © 2025')
