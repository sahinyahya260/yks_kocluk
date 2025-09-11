import streamlit as st
import pandas as pd

APP_TITLE = "🎓 YKS Ultra Profesyonel Koç v2.0"
SHOPIER_LINK = "https://www.shopier.com/37499480"  # Shopier ürün linkini buraya ekle

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# Kullanıcıları CSV'den oku
try:
    users = pd.read_csv("users.csv")
except FileNotFoundError:
    st.error("⛔ users.csv dosyası bulunamadı! Lütfen kullanıcı listesini ekleyin.")
    st.stop()

# -------------------------------
# GİRİŞ EKRANI
# -------------------------------
st.info("Bu sisteme giriş için **kullanıcı adı ve şifre** gereklidir. Şifreyi Shopier ödeme sonrası alabilirsiniz.")

username = st.text_input("👤 Kullanıcı Adı:")
password = st.text_input("🔑 Şifre:", type="password")

if st.button("Giriş Yap"):
    if ((users["username"] == username) & (users["password"] == password)).any():
        st.success(f"✅ Hoş geldin {username}!")

        # -------------------------------
        # ANA UYGULAMA BURAYA GELECEK
        # -------------------------------
        st.subheader("📊 Koçluk Paneli")
        st.write("Burada öğrencinin programı, analizleri, ilerlemesi olacak.")

        st.table({
            "Ders": ["Matematik", "Türkçe", "Fizik", "Biyoloji"],
            "Hedef Soru": [40, 35, 25, 30]
        })

    else:
        st.error("⛔ Kullanıcı adı veya şifre yanlış!")
        st.markdown(f"[💳 Şifre almak için ödeme yap]({SHOPIER_LINK})")
