import streamlit as st
import pandas as pd

APP_TITLE = "🎓 YKS Ultra Profesyonel Koç v2.0"
SHOPIER_LINK = "https://www.shopier.com/37499480"  # Shopier ürün linki

st.set_page_config(page_title=APP_TITLE, layout="wide")
st.title(APP_TITLE)

# Kullanıcıları CSV'den oku
try:
    users = pd.read_csv("users.csv")
except FileNotFoundError:
    st.error("⛔ users.csv dosyası bulunamadı! Lütfen kullanıcı listesini ekleyin.")
    st.stop()

# Session state
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# -------------------------------
# GİRİŞ EKRANI
# -------------------------------
if not st.session_state["logged_in"]:
    st.info("Bu sisteme giriş için **kullanıcı adı ve şifre** gereklidir. Şifreyi Shopier ödeme sonrası alabilirsiniz.")

    username = st.text_input("👤 Kullanıcı Adı:")
    password = st.text_input("🔑 Şifre:", type="password")

    if st.button("Giriş Yap"):
        if ((users["username"] == username) & (users["password"] == password)).any():
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.success(f"✅ Hoş geldin {username}!")
            st.rerun()
        else:
            st.error("⛔ Kullanıcı adı veya şifre yanlış!")
            st.markdown(f"[💳 Şifre almak için ödeme yap]({SHOPIER_LINK})")

# -------------------------------
# KOÇLUK PANELİ
# -------------------------------
else:
    st.sidebar.success(f"Giriş yaptınız ✅ ({st.session_state['username']})")
    if st.sidebar.button("Çıkış Yap"):
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

    # 🔥 Buradan sonrası sadece giriş yapan öğrenciye gözükür
    st.subheader("📊 Koçluk Paneli")
    st.write("Burada öğrencinin programı, analizleri, ilerlemesi olacak.")

    st.table({
        "Ders": ["Matematik", "Türkçe", "Fizik", "Biyoloji"],
        "Hedef Soru": [40, 35, 25, 30]
    })
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import json
from typing import Dict, List
import numpy as np
import calendar

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="YKS Derece Öğrencisi Hazırlık Sistemi",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Bölüm bazlı tema renkleri ve arka planları
BÖLÜM_TEMALARI = {
    "Tıp": {
        "renk": "#dc3545",
        "arka_plan": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "icon": "🩺",
        "background_image": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1f?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
    },
    "Hukuk": {
        "renk": "#6f42c1",
        "arka_plan": "linear-gradient(135deg, #2c3e50 0%, #34495e 100%)",
        "icon": "⚖️",
        "background_image": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
    },
    "Mühendislik": {
        "renk": "#fd7e14",
        "arka_plan": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "icon": "⚙️",
        "background_image": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
    },
    "İşletme": {
        "renk": "#20c997",
        "arka_plan": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "icon": "💼",
        "background_image": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
    },
    "Öğretmenlik": {
        "renk": "#198754",
        "arka_plan": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
        "icon": "👩‍🏫",
        "background_image": "https://images.unsplash.com/photo-1427504494785-3a9ca7044f45?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
    },
    "Diğer": {
        "renk": "#6c757d",
        "arka_plan": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "icon": "🎓",
        "background_image": "https://images.unsplash.com/photo-1523050854058-8df90110c9f1?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"
    }
}

# Derece öğrencisi stratejileri
DERECE_STRATEJİLERİ = {
    "9. Sınıf": {
        "öncelik": ["TYT Matematik Temeli", "TYT Türkçe", "Fen Temel", "Sosyal Temel"],
        "haftalık_dağılım": {
            "TYT Matematik": 6, "TYT Türkçe": 4, "TYT Fen": 3, "TYT Sosyal": 2, 
            "AYT": 0, "Deneme": 1, "Tekrar": 4
        },
        "günlük_strateji": "Temel kavram odaklı çalışma, bol tekrar",
        "hedef": "TYT konularında %80 hakimiyet"
    },
    "10. Sınıf": {
        "öncelik": ["TYT Matematik İleri", "AYT Giriş", "TYT Pekiştirme"],
        "haftalık_dağılım": {
            "TYT Matematik": 5, "TYT Türkçe": 3, "TYT Fen": 3, "TYT Sosyal": 2,
            "AYT": 3, "Deneme": 2, "Tekrar": 2
        },
        "günlük_strateji": "TYT pekiştirme + AYT temel başlangıç",
        "hedef": "TYT %85, AYT temel konularda %60 hakimiyet"
    },
    "11. Sınıf": {
        "öncelik": ["AYT Ana Dersler", "TYT Hız", "Deneme Yoğunluğu"],
        "haftalık_dağılım": {
            "TYT Matematik": 3, "TYT Türkçe": 2, "TYT Fen": 2, "TYT Sosyal": 1,
            "AYT": 8, "Deneme": 3, "Tekrar": 1
        },
        "günlük_strateji": "AYT odaklı yoğun çalışma, TYT hız çalışması",
        "hedef": "TYT %90, AYT %75 hakimiyet"
    },
    "12. Sınıf": {
        "öncelik": ["AYT İleri Seviye", "Deneme Maratonu", "Zayıf Alan Kapatma"],
        "haftalık_dağılım": {
            "TYT Matematik": 2, "TYT Türkçe": 2, "TYT Fen": 1, "TYT Sosyal": 1,
            "AYT": 8, "Deneme": 5, "Tekrar": 1
        },
        "günlük_strateji": "Zorlu sorular, hız ve doğruluk, psikolojik hazırlık",
        "hedef": "TYT %95, AYT %85+ hakimiyet"
    },
    "Mezun": {
        "öncelik": ["Eksik Alan Kapatma", "Üst Seviye Problemler", "Mental Hazırlık"],
        "haftalık_dağılım": {
            "TYT Matematik": 2, "TYT Türkçe": 1, "TYT Fen": 1, "TYT Sosyal": 1,
            "AYT": 10, "Deneme": 4, "Tekrar": 1
        },
        "günlük_strateji": "Uzman seviyesi sorular, tam hakimiyet",
        "hedef": "TYT %98, AYT %90+ hakimiyet"
    }
}

def tema_css_oluştur(bölüm_kategori):
    tema = BÖLÜM_TEMALARI[bölüm_kategori]
    
    return f"""
    <style>
        .main-container {{
            background: {tema['arka_plan']};
            min-height: 100vh;
        }}
        
        .hero-section {{
            background: url('{tema['background_image']}') center/cover;
            background-blend-mode: overlay;
            background-color: rgba(0,0,0,0.3);
            padding: 3rem 0;
            border-radius: 15px;
            margin: 1rem 0;
            text-align: center;
            color: white;
        }}
        
        .main-header {{
            font-size: 3rem;
            font-weight: bold;
            color: white;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
            margin-bottom: 1rem;
        }}
        
        .section-header {{
            font-size: 1.8rem;
            font-weight: bold;
            color: {tema['renk']};
            margin: 2rem 0 1rem 0;
            padding: 1rem;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            border-left: 5px solid {tema['renk']};
        }}
        
        .info-card {{
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(10px);
            padding: 1.5rem;
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.2);
            margin: 1rem 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        
        .success-card {{
            background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        }}
        
        .warning-card {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            color: white;
        }}
        
        .metric-card {{
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(15px);
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        
        .program-item {{
            background: rgba(255,255,255,0.1);
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid {tema['renk']};
            backdrop-filter: blur(5px);
        }}
        
        .sidebar .element-container {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 10px;
            padding: 0.5rem;
        }}
    </style>
    """

class DereceProgramı:
    def __init__(self):
        self.tyt_konular = {
            "Matematik": {
                "Temel": ["Temel Kavramlar", "Sayılar", "Bölünebilme"],
                "Orta": ["Cebirsel İfadeler", "1. Dereceden Denklemler", "Eşitsizlikler"],
                "İleri": ["Fonksiyonlar", "Polinomlar", "2. Derece Denklemler"],
                "Uzman": ["Logaritma", "Diziler ve Seriler", "Permütasyon-Kombinasyon"]
            },
            "Türkçe": {
                "Temel": ["Sözcükte Anlam", "Cümlede Anlam"],
                "Orta": ["Paragraf", "Anlatım Biçimleri"],
                "İleri": ["Edebiyat Bilgileri", "Şiir İncelemesi"],
                "Uzman": ["Metin İnceleme", "Dil Bilgisi İleri"]
            },
            "Fen": {
                "Temel": ["Hareket", "Kuvvet ve Hareket", "Madde"],
                "Orta": ["Enerji", "Isı ve Sıcaklık", "Elektrik"],
                "İleri": ["Dalgalar", "Atom ve Periyodik Sistem", "Hücre"],
                "Uzman": ["Modern Fizik", "Organik Bileşikler", "Kalıtım"]
            }
        }
        
        self.ayt_konular = {
            "Matematik": {
                "Temel": ["Trigonometri Temelleri", "Logaritma"],
                "Orta": ["Diziler", "Limit", "Süreklilik"],
                "İleri": ["Türev", "İntegral", "Analitik Geometri"],
                "Uzman": ["Diferansiyel Denklemler", "Çok Değişkenli Fonksiyonlar"]
            }
        }

def bölüm_kategorisi_belirle(hedef_bölüm):
    bölüm_lower = hedef_bölüm.lower()
    if any(word in bölüm_lower for word in ['tıp', 'diş', 'eczacılık', 'veteriner']):
        return "Tıp"
    elif any(word in bölüm_lower for word in ['hukuk', 'adalet']):
        return "Hukuk"
    elif any(word in bölüm_lower for word in ['mühendis', 'bilgisayar', 'elektrik', 'makine', 'inşaat']):
        return "Mühendislik"
    elif any(word in bölüm_lower for word in ['işletme', 'iktisat', 'maliye', 'ekonomi']):
        return "İşletme"
    elif any(word in bölüm_lower for word in ['öğretmen', 'eğitim', 'pdrs']):
        return "Öğretmenlik"
    else:
        return "Diğer"

def initialize_session_state():
    defaults = {
        'öğrenci_bilgisi': {},
        'program_oluşturuldu': False,
        'deneme_sonuçları': [],
        'konu_durumu': {},
        'günlük_çalışma_kayıtları': {},
        'motivasyon_puanı': 100,
        'hedef_sıralama': 1000
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def öğrenci_bilgi_formu():
    st.markdown("""
    <div class="hero-section">
        <div class="main-header">🏆 YKS Derece Öğrencisi Sistemi</div>
        <p style="font-size: 1.2rem;">Türkiye'nin En Başarılı Öğrencilerinin Stratejileri ile Hazırlan!</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("öğrenci_bilgi_form", clear_on_submit=False):
        st.markdown('<div class="section-header">📝 Kişisel Bilgiler</div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            isim = st.text_input("👤 Adın Soyadın", placeholder="Örn: Ahmet Yılmaz")
            sınıf = st.selectbox("🏫 Sınıf", ["9. Sınıf", "10. Sınıf", "11. Sınıf", "12. Sınıf", "Mezun"])
            alan = st.selectbox("📚 Alan", ["Sayısal", "Eşit Ağırlık", "Sözel"])
        
        with col2:
            hedef_bölüm = st.text_input("🎯 Hedef Bölüm", placeholder="Örn: Tıp - İstanbul Üniversitesi")
            hedef_sıralama = st.number_input("🏅 Hedef Sıralama", min_value=1, max_value=100000, value=1000)
            çalışma_saati = st.slider("⏰ Günlük Çalışma Saati", 4, 16, 10)
        
        with col3:
            seviye = st.selectbox("📊 Şu Anki Seviye", 
                                ["Başlangıç (Net: 0-30)", "Temel (Net: 30-60)", 
                                 "Orta (Net: 60-90)", "İyi (Net: 90-120)", "Çok İyi (Net: 120+)"])
            uyku_saati = st.slider("😴 Günlük Uyku Saati", 6, 10, 8)
            beslenme_kalitesi = st.selectbox("🍎 Beslenme Kalitesi", ["Düzenli", "Orta", "Düzensiz"])
        
        # Gelişmiş motivasyon faktörleri
        st.markdown("### 💪 Motivasyon Profili")
        col4, col5 = st.columns(2)
        
        with col4:
            çalışma_ortamı = st.selectbox("🏠 Çalışma Ortamı", ["Sessiz Oda", "Kütüphane", "Kafe", "Karışık"])
            çalışma_tarzı = st.selectbox("📖 Çalışma Tarzı", ["Yalnız", "Grup", "Karma"])
        
        with col5:
            hedef_motivasyonu = st.slider("🎯 Hedef Motivasyon Seviyesi", 1, 10, 8)
            stres_yönetimi = st.selectbox("😌 Stres Yönetimi", ["Çok İyi", "İyi", "Orta", "Zayıf"])
        
        submitted = st.form_submit_button("✅ Derece Öğrencisi Programını Başlat", use_container_width=True)
        
        if submitted and isim and hedef_bölüm:
            bölüm_kategori = bölüm_kategorisi_belirle(hedef_bölüm)
            
            st.session_state.öğrenci_bilgisi = {
                'isim': isim, 'sınıf': sınıf, 'alan': alan, 'hedef_bölüm': hedef_bölüm,
                'hedef_sıralama': hedef_sıralama, 'seviye': seviye, 'çalışma_saati': çalışma_saati,
                'uyku_saati': uyku_saati, 'beslenme_kalitesi': beslenme_kalitesi,
                'çalışma_ortamı': çalışma_ortamı, 'çalışma_tarzı': çalışma_tarzı,
                'hedef_motivasyonu': hedef_motivasyonu, 'stres_yönetimi': stres_yönetimi,
                'bölüm_kategori': bölüm_kategori, 'kayıt_tarihi': str(datetime.now().date())
            }
            st.session_state.program_oluşturuldu = True
            
            # Tema CSS'ini uygula
            tema_css = tema_css_oluştur(bölüm_kategori)
            st.markdown(tema_css, unsafe_allow_html=True)
            
            st.success(f"🎉 Hoş geldin {isim}! {bölüm_kategori} temalı derece öğrencisi programın hazırlandı!")
            st.rerun()

def derece_günlük_program():
    bilgi = st.session_state.öğrenci_bilgisi
    strateji = DERECE_STRATEJİLERİ[bilgi['sınıf']]
    tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
    
    st.markdown(f'<div class="section-header">{tema["icon"]} Derece Öğrencisi Günlük Program</div>', 
                unsafe_allow_html=True)
    
    # Gün seçimi
    col1, col2, col3 = st.columns(3)
    with col1:
        seçilen_gün = st.selectbox("📅 Gün Seçin", 
                                  ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
    with col2:
        program_türü = st.selectbox("📋 Program Türü", ["Standart", "Yoğun", "Hafif", "Deneme Günü"])
    with col3:
        bugünkü_hedef = st.selectbox("🎯 Bugünkü Ana Hedef", strateji['öncelik'])
    
    # Derece öğrencisi saatlik program
    program = derece_saatlik_program_oluştur(seçilen_gün, program_türü, bilgi, strateji)
    
    col_sabah, col_ogle, col_aksam = st.columns(3)
    
    with col_sabah:
        st.markdown("### 🌅 Sabah Programı (06:00-12:00)")
        for saat, aktivite in program['sabah'].items():
            renk = tema['renk'] if 'Çalışma' in aktivite else '#6c757d'
            st.markdown(f'''
                <div class="program-item" style="border-left-color: {renk};">
                    <strong>{saat}</strong><br>
                    {aktivite}
                </div>
            ''', unsafe_allow_html=True)
    
    with col_ogle:
        st.markdown("### ☀️ Öğle Programı (12:00-18:00)")
        for saat, aktivite in program['öğle'].items():
            renk = tema['renk'] if 'Çalışma' in aktivite else '#6c757d'
            st.markdown(f'''
                <div class="program-item" style="border-left-color: {renk};">
                    <strong>{saat}</strong><br>
                    {aktivite}
                </div>
            ''', unsafe_allow_html=True)
    
    with col_aksam:
        st.markdown("### 🌙 Akşam Programı (18:00-24:00)")
        for saat, aktivite in program['akşam'].items():
            renk = tema['renk'] if 'Çalışma' in aktivite else '#6c757d'
            st.markdown(f'''
                <div class="program-item" style="border-left-color: {renk};">
                    <strong>{saat}</strong><br>
                    {aktivite}
                </div>
            ''', unsafe_allow_html=True)
    
    # Günlük performans takibi
    st.markdown("### 📊 Bugün Tamamlanan Görevler")
    
    with st.expander("✅ Görev Tamamla"):
        tamamlanan_görevler = st.multiselect(
            "Tamamladığın görevleri seç:",
            [f"{saat}: {aktivite}" for zaman_dilimi in program.values() 
             for saat, aktivite in zaman_dilimi.items() if 'Çalışma' in aktivite]
        )
        
        if st.button("Günlük Performansı Kaydet"):
            tarih_str = str(date.today())
            if tarih_str not in st.session_state.günlük_çalışma_kayıtları:
                st.session_state.günlük_çalışma_kayıtları[tarih_str] = {}
            
            st.session_state.günlük_çalışma_kayıtları[tarih_str] = {
                'tamamlanan_görevler': tamamlanan_görevler,
                'tamamlanma_oranı': len(tamamlanan_görevler) / max(1, len([a for td in program.values() for a in td.values() if 'Çalışma' in a])) * 100,
                'gün': seçilen_gün
            }
            st.success("Günlük performans kaydedildi! 🎉")

def derece_saatlik_program_oluştur(gün, program_türü, bilgi, strateji):
    # Derece öğrencisi için detaylı saatlik program
    temel_program = {
        'sabah': {
            '06:00': '🌅 Uyanış + Hafif Egzersiz',
            '06:30': '🥗 Beslenme + Vitamin',
            '07:00': '📚 TYT Matematik (Zor Konular)',
            '08:30': '☕ Mola + Nefes Egzersizi',
            '08:45': '📝 TYT Türkçe (Paragraf)',
            '10:15': '🥤 Mola + Beyin Oyunları',
            '10:30': '🧪 TYT Fen (Problem Çözümü)',
            '12:00': '🍽️ Öğle Yemeği'
        },
        'öğle': {
            '13:00': '😴 Kısa Dinlenme (20dk)',
            '13:30': '📖 AYT Ana Ders (Teorik)',
            '15:00': '🚶 Mola + Yürüyüş',
            '15:15': '📊 AYT Problem Çözümü',
            '16:45': '☕ Mola + Gevşeme',
            '17:00': '📋 Deneme Sınavı / Soru Bankası',
            '18:00': '🎯 Günlük Değerlendirme'
        },
        'akşam': {
            '19:00': '🍽️ Akşam Yemeği + Aile Zamanı',
            '20:00': '📚 Zayıf Alan Çalışması',
            '21:30': '📝 Konu Tekrarı + Not Çıkarma',
            '22:30': '📖 Hafif Okuma (Genel Kültür)',
            '23:00': '🧘 Meditasyon + Yarın Planı',
            '23:30': '😴 Uyku Hazırlığı'
        }
    }
    
    # Program türüne göre ayarlama
    if program_türü == "Yoğun":
        # Çalışma saatlerini artır, mola sürelerini azalt
        pass
    elif program_türü == "Deneme Günü":
        temel_program['sabah']['07:00'] = '📝 TYT Deneme Sınavı'
        temel_program['sabah']['10:30'] = '📊 TYT Analizi'
        temel_program['öğle']['13:30'] = '📝 AYT Deneme Sınavı'
        temel_program['öğle']['17:00'] = '📊 AYT Analizi'
    
    return temel_program

def derece_konu_takibi():
    st.markdown('<div class="section-header">🎯 Derece Öğrencisi Konu Masterysi</div>', unsafe_allow_html=True)
    
    bilgi = st.session_state.öğrenci_bilgisi
    tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
    program = DereceProgramı()
    
    # Mastery seviyeleri
    mastery_seviyeleri = {
        "Hiç Bilmiyor": 0,
        "Temel Bilgi": 25,
        "Orta Seviye": 50,
        "İyi Seviye": 75,
        "Uzman (Derece) Seviye": 100
    }
    
    # Konu seçimi ve durum güncelleme
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📚 TYT Konu Masterysi")
        for ders, seviyeler in program.tyt_konular.items():
            with st.expander(f"{ders}"):
                for seviye, konular in seviyeler.items():
                    st.write(f"**{seviye} Seviye:**")
                    for konu in konular:
                        anahtar = f"TYT-{ders}-{konu}"
                        mevcut_seviye = st.session_state.konu_durumu.get(anahtar, "Hiç Bilmiyor")
                        
                        yeni_seviye = st.selectbox(
                            f"{konu}",
                            list(mastery_seviyeleri.keys()),
                            index=list(mastery_seviyeleri.keys()).index(mevcut_seviye),
                            key=anahtar
                        )
                        
                        if yeni_seviye != mevcut_seviye:
                            st.session_state.konu_durumu[anahtar] = yeni_seviye
    
    with col2:
        st.markdown("### 🚀 AYT Konu Masterysi")
        for ders, seviyeler in program.ayt_konular.items():
            with st.expander(f"{ders}"):
                for seviye, konular in seviyeler.items():
                    st.write(f"**{seviye} Seviye:**")
                    for konu in konular:
                        anahtar = f"AYT-{ders}-{konu}"
                        mevcut_seviye = st.session_state.konu_durumu.get(anahtar, "Hiç Bilmiyor")
                        
                        yeni_seviye = st.selectbox(
                            f"{konu}",
                            list(mastery_seviyeleri.keys()),
                            index=list(mastery_seviyeleri.keys()).index(mevcut_seviye),
                            key=anahtar
                        )
                        
                        if yeni_seviye != mevcut_seviye:
                            st.session_state.konu_durumu[anahtar] = yeni_seviye
    
    # Mastery istatistikleri
    if st.session_state.konu_durumu:
        st.markdown("### 📊 Genel Mastery İstatistikleri")
        
        toplam_mastery = []
        for anahtar, seviye in st.session_state.konu_durumu.items():
            toplam_mastery.append(mastery_seviyeleri[seviye])
        
        ortalama_mastery = np.mean(toplam_mastery)
        
        col3, col4, col5 = st.columns(3)
        
        with col3:
            st.markdown(f'''
                <div class="metric-card">
                    <h3>📈 Ortalama Mastery</h3>
                    <h2 style="color: {tema['renk']};">{ortalama_mastery:.1f}%</h2>
                </div>
            ''', unsafe_allow_html=True)
        
        with col4:
            uzman_konular = sum(1 for seviye in st.session_state.konu_durumu.values() 
                               if seviye == "Uzman (Derece) Seviye")
            st.markdown(f'''
                <div class="metric-card">
                    <h3>🏆 Uzman Konular</h3>
                    <h2 style="color: {tema['renk']};">{uzman_konular}</h2>
                </div>
            ''', unsafe_allow_html=True)
        
        with col5:
            zayif_konular = sum(1 for seviye in st.session_state.konu_durumu.values() 
                               if mastery_seviyeleri[seviye] < 50)
            st.markdown(f'''
                <div class="metric-card">
                    <h3>⚠️ Zayıf Konular</h3>
                    <h2 style="color: {tema['renk']};">{zayif_konular}</h2>
                </div>
            ''', unsafe_allow_html=True)

def derece_deneme_analizi():
    st.markdown('<div class="section-header">📈 Derece Öğrencisi Deneme Analizi</div>', unsafe_allow_html=True)
    
    bilgi = st.session_state.öğrenci_bilgisi
    tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
    
    # Gelişmiş deneme girişi
    with st.expander("➕ Detaylı Deneme Sonucu Ekle"):
        with st.form("deneme_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                deneme_tarihi = st.date_input("📅 Deneme Tarihi")
                deneme_adı = st.text_input("📝 Deneme Adı", placeholder="Örn: YKS Denemesi 15")
                deneme_türü = st.selectbox("📋 Tür", ["TYT", "AYT", "TYT+AYT", "Konu Taraması"])
            
            with col2:
                # TYT detaylı giriş
                st.markdown("**TYT Sonuçları**")
                tyt_turkce_d = st.number_input("Türkçe Doğru", 0, 40, 0)
                tyt_turkce_y = st.number_input("Türkçe Yanlış", 0, 40, 0)
                tyt_mat_d = st.number_input("Matematik Doğru", 0, 40, 0)
                tyt_mat_y = st.number_input("Matematik Yanlış", 0, 40, 0)
                tyt_fen_d = st.number_input("Fen Doğru", 0, 20, 0)
                tyt_fen_y = st.number_input("Fen Yanlış", 0, 20, 0)
                tyt_sosyal_d = st.number_input("Sosyal Doğru", 0, 20, 0)
                tyt_sosyal_y = st.number_input("Sosyal Yanlış", 0, 20, 0)
            
            with col3:
                # AYT detaylı giriş
                st.markdown("**AYT Sonuçları**")
                if bilgi['alan'] == "Sayısal":
                    ayt_mat_d = st.number_input("AYT Mat Doğru", 0, 40, 0)
                    ayt_mat_y = st.number_input("AYT Mat Yanlış", 0, 40, 0)
                    ayt_fizik_d = st.number_input("Fizik Doğru", 0, 14, 0)
                    ayt_fizik_y = st.number_input("Fizik Yanlış", 0, 14, 0)
                    ayt_kimya_d = st.number_input("Kimya Doğru", 0, 13, 0)
                    ayt_kimya_y = st.number_input("Kimya Yanlış", 0, 13, 0)
                    ayt_biyoloji_d = st.number_input("Biyoloji Doğru", 0, 13, 0)
                    ayt_biyoloji_y = st.number_input("Biyoloji Yanlış", 0, 13, 0)
            
            # Psikolojik durum
            st.markdown("### 🧠 Psikolojik Durum (Derece Öğrencisi Takibi)")
            col4, col5 = st.columns(2)
            
            with col4:
                sinav_oncesi_durum = st.selectbox("Sınav Öncesi", 
                    ["Çok Sakin", "Sakin", "Heyecanlı", "Çok Heyecanlı", "Stresli"])
                konsantrasyon = st.slider("Konsantrasyon", 1, 10, 8)
            
            with col5:
                zaman_yonetimi = st.selectbox("Zaman Yönetimi", 
                    ["Mükemmel", "İyi", "Orta", "Zayıf", "Çok Zayıf"])
                genel_memnuniyet = st.slider("Genel Memnuniyet", 1, 10, 7)
            
            if st.form_submit_button("📊 Derece Analizi Yap"):
                # Net hesaplamaları
                tyt_net = (tyt_turkce_d + tyt_mat_d + tyt_fen_d + tyt_sosyal_d) - \
                         (tyt_turkce_y + tyt_mat_y + tyt_fen_y + tyt_sosyal_y) / 4
                
                if bilgi['alan'] == "Sayısal":
                    ayt_net = (ayt_mat_d + ayt_fizik_d + ayt_kimya_d + ayt_biyoloji_d) - \
                             (ayt_mat_y + ayt_fizik_y + ayt_kimya_y + ayt_biyoloji_y) / 4
                else:
                    ayt_net = 0
                
                # Derece öğrencisi analizi
                derece_analizi = derece_performans_analizi(tyt_net, ayt_net, bilgi)
                
                sonuç = {
                    'tarih': str(deneme_tarihi),
                    'deneme_adı': deneme_adı,
                    'tür': deneme_türü,
                    'tyt_net': tyt_net,
                    'ayt_net': ayt_net,
                    'tyt_detay': {
                        'turkce': tyt_turkce_d - tyt_turkce_y/4,
                        'matematik': tyt_mat_d - tyt_mat_y/4,
                        'fen': tyt_fen_d - tyt_fen_y/4,
                        'sosyal': tyt_sosyal_d - tyt_sosyal_y/4
                    },
                    'psikolojik': {
                        'sinav_oncesi': sinav_oncesi_durum,
                        'konsantrasyon': konsantrasyon,
                        'zaman_yonetimi': zaman_yonetimi,
                        'memnuniyet': genel_memnuniyet
                    },
                    'derece_analizi': derece_analizi
                }
                
                st.session_state.deneme_sonuçları.append(sonuç)
                st.success("Derece öğrencisi analizi tamamlandı! 📊")
    
    # Derece öğrencisi grafikleri
    if st.session_state.deneme_sonuçları:
        df = pd.DataFrame(st.session_state.deneme_sonuçları)
        
        # Çoklu grafik gösterimi
        tab1, tab2, tab3 = st.tabs(["📈 Net Analizi", "🎯 Alan Analizi", "🧠 Psikoloji"])
        
        with tab1:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['tarih'], y=df['tyt_net'], 
                                    mode='lines+markers', name='TYT Net',
                                    line=dict(color=tema['renk'])))
            if 'ayt_net' in df.columns:
                fig.add_trace(go.Scatter(x=df['tarih'], y=df['ayt_net'], 
                                        mode='lines+markers', name='AYT Net'))
            
            # Derece hedef çizgisi
            derece_hedefi = hedef_net_hesapla(bilgi['hedef_sıralama'], bilgi['alan'])
            fig.add_hline(y=derece_hedefi, line_dash="dash", 
                         annotation_text="Derece Hedefi")
            
            fig.update_layout(title="Derece Öğrencisi Net İlerleme", 
                            xaxis_title="Tarih", yaxis_title="Net")
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Alan bazlı radar chart
            if len(df) > 0:
                son_deneme = df.iloc[-1]
                if 'tyt_detay' in son_deneme:
                    detay = son_deneme['tyt_detay']
                    
                    fig = go.Figure(data=go.Scatterpolar(
                        r=list(detay.values()),
                        theta=list(detay.keys()),
                        fill='toself',
                        name='Son Deneme'
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, max(detay.values()) + 5]
                            )),
                        showlegend=True,
                        title="Alan Bazlı Performans Analizi"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Psikolojik durum analizi
            if 'psikolojik' in df.columns:
                psiko_df = pd.json_normalize(df['psikolojik'])
                
                col6, col7 = st.columns(2)
                
                with col6:
                    fig = px.line(df, x='tarih', y=psiko_df['konsantrasyon'], 
                                 title='Konsantrasyon Değişimi')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col7:
                    fig = px.line(df, x='tarih', y=psiko_df['memnuniyet'], 
                                 title='Genel Memnuniyet')
                    st.plotly_chart(fig, use_container_width=True)

def derece_performans_analizi(tyt_net, ayt_net, bilgi):
    # Derece öğrencisi için performans analizi
    hedef_net = hedef_net_hesapla(bilgi['hedef_sıralama'], bilgi['alan'])
    
    analiz = {
        'durum': 'Hedefin Altında',
        'eksik_net': max(0, hedef_net - (tyt_net + ayt_net)),
        'öneriler': [],
        'güçlü_yanlar': [],
        'zayıf_yanlar': []
    }
    
    toplam_net = tyt_net + ayt_net
    
    if toplam_net >= hedef_net * 1.1:
        analiz['durum'] = 'Derece Adayı'
        analiz['öneriler'] = ['Mükemmel! Bu performansı koru', 'Zor sorulara odaklan']
    elif toplam_net >= hedef_net:
        analiz['durum'] = 'Hedefte'
        analiz['öneriler'] = ['Çok yakın! Son sprint zamanı', 'Hız çalışması yap']
    else:
        analiz['öneriler'] = [f'{analiz["eksik_net"]:.1f} net artırman gerekiyor', 
                             'Zayıf alanlarına odaklan']
    
    return analiz

def hedef_net_hesapla(sıralama, alan):
    # Sıralamaya göre yaklaşık net hesabı
    hedef_netleri = {
        'Sayısal': {1: 180, 100: 170, 1000: 150, 10000: 120, 50000: 90},
        'Eşit Ağırlık': {1: 175, 100: 165, 1000: 145, 10000: 115, 50000: 85},
        'Sözel': {1: 170, 100: 160, 1000: 140, 10000: 110, 50000: 80}
    }
    
    alan_netleri = hedef_netleri.get(alan, hedef_netleri['Sayısal'])
    
    # Lineer interpolasyon
    sıralama_listesi = sorted(alan_netleri.keys())
    for i in range(len(sıralama_listesi)-1):
        if sıralama_listesi[i] <= sıralama <= sıralama_listesi[i+1]:
            x1, x2 = sıralama_listesi[i], sıralama_listesi[i+1]
            y1, y2 = alan_netleri[x1], alan_netleri[x2]
            return y1 + (y2-y1) * (sıralama-x1) / (x2-x1)
    
    return 100  # Varsayılan

def derece_öneriler():
    st.markdown('<div class="section-header">💡 Derece Öğrencisi Önerileri</div>', unsafe_allow_html=True)
    
    bilgi = st.session_state.öğrenci_bilgisi
    tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
    strateji = DERECE_STRATEJİLERİ[bilgi['sınıf']]
    
    # Kişiselleştirilmiş öneriler
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'''
        <div class="success-card">
            <h3>{tema['icon']} {bilgi['bölüm_kategori']} Özel Stratejileri</h3>
            <p><strong>Hedef Bölüm:</strong> {bilgi['hedef_bölüm']}</p>
            <p><strong>Günlük Strateji:</strong> {strateji['günlük_strateji']}</p>
            <p><strong>Ana Hedef:</strong> {strateji['hedef']}</p>
        </div>
        ''', unsafe_allow_html=True)
        
        # Bölüm özel tavsiyeleri
        bölüm_tavsiyeleri = {
            "Tıp": ["🩺 Biyoloji ve Kimya'ya extra odaklan", "🧠 Problem çözme hızını artır", 
                   "📚 Tıp terminolojisi öğren", "💪 Fiziksel dayanıklılık çalış"],
            "Hukuk": ["⚖️ Türkçe ve mantık güçlendir", "📖 Hukuk felsefesi oku", 
                     "🗣️ Tartışma becerilerini geliştir", "📝 Yazma becerisini artır"],
            "Mühendislik": ["⚙️ Matematik ve Fizik'te uzmanlaş", "🔧 Pratik problem çözme", 
                          "💻 Temel programlama öğren", "🎯 Sistem düşüncesi geliştir"]
        }
        
        if bilgi['bölüm_kategori'] in bölüm_tavsiyeleri:
            st.markdown("### 🎯 Bölüm Özel Tavsiyeleri")
            for tavsiye in bölüm_tavsiyeleri[bilgi['bölüm_kategori']]:
                st.markdown(f"• {tavsiye}")
    
    with col2:
        # Motivasyon sistemi
        motivasyon_mesajları = [
            f"🌟 {bilgi['isim']}, sen {bilgi['hedef_bölüm']} için doğmuşsun!",
            f"🏆 {bilgi['hedef_sıralama']}. sıralama çok yakın!",
            "💪 Her gün biraz daha güçleniyorsun!",
            f"🚀 {tema['icon']} Bu hedef tam sana göre!",
            "⭐ Derece öğrencileri böyle çalışır!"
        ]
        
        import random
        günün_motivasyonu = random.choice(motivasyon_mesajları)
        
        st.markdown(f'''
        <div class="warning-card">
            <h3>💝 Günün Derece Motivasyonu</h3>
            <p style="font-size: 1.2rem; font-weight: bold;">{günün_motivasyonu}</p>
            <small>Motivasyon Puanın: {st.session_state.motivasyon_puanı}/100</small>
        </div>
        ''', unsafe_allow_html=True)
        
        # Derece öğrencisi alışkanlıkları
        st.markdown("### 🏅 Derece Öğrencisi Alışkanlıkları")
        alışkanlıklar = [
            "🌅 Erken kalkma (6:00)",
            "🧘 Günlük meditasyon (15dk)",
            "📚 Pomodoro tekniği kullanma",
            "💧 Bol su içme (2-3L)",
            "🏃 Düzenli egzersiz",
            "📱 Sosyal medya detoksu",
            "📝 Günlük planlama",
            "😴 Kaliteli uyku (7-8 saat)"
        ]
        
        for alışkanlık in alışkanlıklar:
            st.markdown(f"• {alışkanlık}")

def main():
    initialize_session_state()
    
    # Tema CSS'ini uygula
    if st.session_state.program_oluşturuldu:
        bölüm_kategori = st.session_state.öğrenci_bilgisi['bölüm_kategori']
        tema_css = tema_css_oluştur(bölüm_kategori)
        st.markdown(tema_css, unsafe_allow_html=True)
    
    if not st.session_state.program_oluşturuldu:
        öğrenci_bilgi_formu()
    else:
        bilgi = st.session_state.öğrenci_bilgisi
        tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
        
        # Sidebar
        with st.sidebar:
            st.markdown(f'''
            <div style="text-align: center; padding: 1rem; background: rgba(255,255,255,0.1); border-radius: 10px; margin-bottom: 1rem;">
                <h2>{tema['icon']} Derece Sistemi</h2>
                <p><strong>{bilgi['isim']}</strong></p>
                <p>{bilgi['sınıf']} - {bilgi['alan']}</p>
                <p>🎯 {bilgi['hedef_bölüm']}</p>
                <p>🏅 Hedef: {bilgi['hedef_sıralama']}. sıra</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Menü
            menu = st.selectbox("📋 Derece Menüsü", [
                "🏠 Ana Dashboard",
                "📅 Günlük Program", 
                "🎯 Konu Masterysi",
                "📈 Deneme Analizi",
                "💡 Derece Önerileri",
                "📊 Performans İstatistikleri"
            ])
            
            # Hızlı istatistikler
            if st.session_state.konu_durumu:
                uzman_konular = sum(1 for seviye in st.session_state.konu_durumu.values() 
                                  if "Uzman" in seviye)
                st.metric("🏆 Uzman Konular", uzman_konular)
            
            if st.session_state.deneme_sonuçları:
                son_net = st.session_state.deneme_sonuçları[-1]['tyt_net']
                st.metric("📈 Son TYT Net", f"{son_net:.1f}")
            
            # Sıfırlama
            st.markdown("---")
            if st.button("🔄 Sistemi Sıfırla"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()
        
        # Ana içerik
        if menu == "🏠 Ana Dashboard":
            st.markdown(f'''
            <div class="hero-section">
                <div class="main-header">{tema['icon']} {bilgi['isim']}'in Derece Yolculuğu</div>
                <p style="font-size: 1.3rem;">"{bilgi['hedef_bölüm']}" hedefine giden yolda!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Performans kartları
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                konu_sayısı = len(st.session_state.konu_durumu)
                st.markdown(f'''
                <div class="metric-card">
                    <h3>📚 Toplam Konu</h3>
                    <h2 style="color: {tema['renk']};">{konu_sayısı}</h2>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                deneme_sayısı = len(st.session_state.deneme_sonuçları)
                st.markdown(f'''
                <div class="metric-card">
                    <h3>📝 Toplam Deneme</h3>
                    <h2 style="color: {tema['renk']};">{deneme_sayısı}</h2>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                çalışma_günü = len(st.session_state.günlük_çalışma_kayıtları)
                st.markdown(f'''
                <div class="metric-card">
                    <h3>📅 Çalışma Günü</h3>
                    <h2 style="color: {tema['renk']};">{çalışma_günü}</h2>
                </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                motivasyon = st.session_state.motivasyon_puanı
                st.markdown(f'''
                <div class="metric-card">
                    <h3>💪 Motivasyon</h3>
                    <h2 style="color: {tema['renk']};">{motivasyon}%</h2>
                </div>
                ''', unsafe_allow_html=True)
            
        elif menu == "📅 Günlük Program":
            derece_günlük_program()
            
        elif menu == "🎯 Konu Masterysi":
            derece_konu_takibi()
            
        elif menu == "📈 Deneme Analizi":
            derece_deneme_analizi()
            
        elif menu == "💡 Derece Önerileri":
            derece_öneriler()
            
        elif menu == "📊 Performans İstatistikleri":
            st.markdown('<div class="section-header">📊 Detaylı Performans Analizi</div>', unsafe_allow_html=True)
            
            # Burada detaylı istatistikler olacak
            if st.session_state.deneme_sonuçları:
                df = pd.DataFrame(st.session_state.deneme_sonuçları)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Henüz deneme verisi bulunmuyor. İlk denemenizi girin!")

if __name__ == "__main__":
    main()