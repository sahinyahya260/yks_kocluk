import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta, date
import json
from typing import Dict, List
import numpy as np
import calendar
import hashlib
import os

import time
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Veri kaydetme fonksiyonu
def save_user_data(username, data):
    """Kullanıcı verilerini JSON dosyasına kaydeder."""
    filename = f"{username}_data.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        st.error(f"Veri kaydetme hatası: {e}")
        return False

# Veri yükleme fonksiyonu
def load_user_data(username):
    """Kullanıcı verilerini JSON dosyasından yükler."""
    filename = f"{username}_data.json"
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Veri yükleme hatası: {e}")
            return None
    return None

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

def kullanıcı_doğrula(kullanıcı_adı, şifre):
    """CSV dosyasından kullanıcı bilgilerini kontrol eder"""
    try:
        if os.path.exists('users.csv'):
            users_df = pd.read_csv('users.csv', header=None, names=['kullanıcı_adı', 'şifre'])
            for index, row in users_df.iterrows():
                if row['kullanıcı_adı'].strip() == kullanıcı_adı.strip() and row['şifre'].strip() == şifre.strip():
                    return True
        else:
            örnek_data = [['ahmet', '1234'], ['admin', 'admin123']]
            örnek_df = pd.DataFrame(örnek_data, columns=['kullanıcı_adı', 'şifre'])
            örnek_df.to_csv('users.csv', index=False, header=False)
            st.info("users.csv dosyası oluşturuldu. Örnek kullanıcılar: ahmet/1234, admin/admin123")
            
            if kullanıcı_adı == 'ahmet' and şifre == '1234':
                return True
            if kullanıcı_adı == 'admin' and şifre == 'admin123':
                return True
                
        return False
    except Exception as e:
        st.error(f"Kullanıcı doğrulama hatası: {e}")
        return False

def login_sayfası():
    """Giriş sayfası"""
    st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem;
        border-radius: 15px;
        margin: 2rem auto;
        max-width: 500px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .login-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .login-form {
        background: rgba(255,255,255,0.1);
        padding: 2rem;
        border-radius: 10px;
        margin-top: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-header">🏆 YKS Derece Sistemi</div>
            <p>Giriş yaparak derece öğrencisi programına erişin</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form"):
            st.markdown("### 🔐 Giriş Bilgileri")
            
            kullanıcı_adı = st.text_input("👤 Kullanıcı Adı", placeholder="Kullanıcı adınızı girin")
            şifre = st.text_input("🔒 Şifre", type="password", placeholder="Şifrenizi girin")
            
            giriş_butonu = st.form_submit_button("🚀 Giriş Yap", use_container_width=True)
            
            if giriş_butonu:
                if kullanıcı_adı and şifre:
                    if kullanıcı_doğrula(kullanıcı_adı, şifre):
                        st.session_state.giriş_yapıldı = True
                        st.session_state.kullanıcı_adı = kullanıcı_adı
                        
                        user_data = load_user_data(kullanıcı_adı)
                        if user_data:
                            st.session_state.update(user_data)
                        else:
                            initialize_session_state()

                        st.success("Giriş başarılı! Programa yönlendiriliyorsunuz...")
                        st.rerun()
                    else:
                        st.error("❌ Kullanıcı adı veya şifre hatalı!")
                        st.info("💡 users.csv dosyasında kayıtlı kullanıcı bilgilerini kontrol edin.")
                else:
                    st.warning("⚠️ Lütfen kullanıcı adı ve şifre giriniz!")

        with st.expander("ℹ️ Sistem Hakkında"):
            st.markdown("""
            **Kullanım:**
            - users.csv dosyasında kayıtlı kullanıcı adı ve şifre ile giriş yapın
            - Dosya formatı: kullanıcı_adı,şifre (her satırda bir kullanıcı)
            - Örnek: ahmet,1234
            
            **Özellikler:**
            - Kişiselleştirilmiş derece öğrencisi programı
            - Detaylı konu takibi ve analizi
            - Deneme sonuçları değerlendirmesi
            - Bölüm özel stratejiler
            """)

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
            "Matematik": [
                "Temel Kavramlar", "Sayılar", "Bölünebilme", "Rasyonel Sayılar", "Birinci Dereceden Denklemler", 
                "Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Çarpanlara Ayırma", "Oran Orantı",
                "Kümeler", "Mantık", "Fonksiyonlar", "Permütasyon-Kombinasyon-Olasılık", "İstatistik", "Problem Çözümü"
            ],
            "Türkçe": [
                "Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Anlatım Bozuklukları", "Yazım Kuralları", 
                "Noktalama İşaretleri", "Dil Bilgisi Temelleri"
            ],
            "Fen": [
                "Fizik: Madde ve Özellikleri", "Fizik: Hareket ve Kuvvet", "Fizik: Enerji", "Fizik: Isı ve Sıcaklık",
                "Kimya: Kimyanın Temel Kanunları", "Kimya: Atom ve Periyodik Sistem", "Kimya: Mol Kavramı",
                "Biyoloji: Canlıların Ortak Özellikleri", "Biyoloji: Hücre ve Organeller", "Biyoloji: Kalıtım"
            ],
            "Sosyal": [
                "Tarih: İlk Çağ Uygarlıkları", "Tarih: Osmanlı Devleti", "Tarih: Kurtuluş Savaşı",
                "Coğrafya: Dünya Haritaları", "Coğrafya: İklim Bilgisi", "Coğrafya: Türkiye Coğrafyası",
                "Felsefe: Felsefenin Alanı", "Din Kültürü: İslam Dini"
            ]
        }
        
        self.ayt_konular = {
            "Matematik": [
                "Fonksiyonlar", "Polinomlar", "Trigonometri", "Logaritma", "Diziler ve Seriler", "Limit ve Süreklilik",
                "Türev", "İntegral", "Analitik Geometri", "Konikler"
            ],
            "Fizik": [
                "Vektörler", "Tork ve Denge", "İtme ve Momentum", "Dalgalar", "Elektrik ve Manyetizma"
            ],
            "Kimya": [
                "Gazlar", "Sıvı Çözeltiler", "Kimyasal Tepkimelerde Hız", "Kimyasal Denge", "Organik Kimya"
            ],
            "Biyoloji": [
                "Hücresel Solunum", "Fotosentez", "Sinir Sistemi", "Endokrin Sistem", "Ekosistem Ekolojisi"
            ]
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
        'giriş_yapıldı': False,
        'kullanıcı_adı': '',
        'öğrenci_bilgisi': {},
        'program_oluşturuldu': False,
        'deneme_sonuçları': [],
        'konu_durumu': {},
        'günlük_çalışma_kayıtları': {},
        'motivasyon_puanı': 100,
        'hedef_sıralama': 1000,
        # Pomodoro için yeni durumlar
        'pomodoro_mode': 'Çalışma Modu',
        'pomodoro_time': 25 * 60, # Saniye cinsinden
        'pomodoro_running': False,
        'pomodoro_count': 0
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

        st.markdown("### 💪 Motivasyon Profili")
        col4, col5 = st.columns(2)
        with col4:
            çalışma_ortamı = st.selectbox("🏠 Çalışma Ortamı", ["Sessiz Oda", "Kütüphane", "Kafe", "Karışık"])
            çalışma_tarzı = st.selectbox("📖 Çalışma Tarzı", ["Yalnız", "Grup", "Karma"])
        with col5:
            hedef_motivasyonu = st.slider("🎯 Hedef Motivasyon Seviyesi", 1, 10, 8)
            stres_yönetimi = st.selectbox("😌 Stres Yönetimi", ["Çok İyi", "İyi", "Orta", "Zayıf"])

        submitted = st.form_submit_button("✅ Derece Öğrencisi Programını Başlat", use_container_width=True)

    if submitted:
        if not isim or not hedef_bölüm:
            st.warning("⚠️ Lütfen adınızı ve hedef bölümünüzü giriniz!")
            return

        bölüm_kategori = bölüm_kategorisi_belirle(hedef_bölüm)
        st.session_state.öğrenci_bilgisi = {
            'isim': isim,
            'sınıf': sınıf,
            'alan': alan,
            'hedef_bölüm': hedef_bölüm,
            'hedef_sıralama': int(hedef_sıralama),
            'seviye': seviye,
            'çalışma_saati': int(çalışma_saati),
            'uyku_saati': int(uyku_saati),
            'beslenme_kalitesi': beslenme_kalitesi,
            'çalışma_ortamı': çalışma_ortamı,
            'çalışma_tarzı': çalışma_tarzı,
            'hedef_motivasyonu': int(hedef_motivasyonu),
            'stres_yönetimi': stres_yönetimi,
            'bölüm_kategori': bölüm_kategori,
            'kayıt_tarihi': str(datetime.now().date())
        }
        st.session_state.program_oluşturuldu = True

        try:
            tema_css = tema_css_oluştur(bölüm_kategori)
            st.markdown(tema_css, unsafe_allow_html=True)
        except Exception:
            pass

        data_to_save = {
            'öğrenci_bilgisi': st.session_state.öğrenci_bilgisi,
            'program_oluşturuldu': st.session_state.program_oluşturuldu,
            'deneme_sonuçları': st.session_state.deneme_sonuçları,
            'konu_durumu': st.session_state.konu_durumu,
            'günlük_çalışma_kayıtları': st.session_state.günlük_çalışma_kayıtları,
            'motivasyon_puanı': st.session_state.motivasyon_puanı,
            'hedef_sıralama': st.session_state.hedef_sıralama,
        }
        if save_user_data(st.session_state.kullanıcı_adı, data_to_save):
            st.success(f"🎉 Hoş geldin {isim}! {bölüm_kategori} temalı derece öğrencisi programın hazırlandı ve kaydedildi!")
        st.rerun()

def derece_günlük_program():
    
    import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time
import calendar


# Sayfa yapılandırması
st.set_page_config(
    page_title="Psikoloji Temelli YKS Programı",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS stilleri
st.markdown("""
<style>
    :root {
        --primary: #1E88E5;
        --primary-dark: #0D47A1;
        --secondary: #64B5F6;
        --accent: #4CAF50;
        --warning: #FF9800;
        --danger: #F44336;
        --light: #E3F2FD;
        --dark: #212121;
        --gray: #F5F5F5;
    }
    
    .main-header {
        font-size: 2.8rem;
        color: var(--primary-dark);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
        padding: 1.5rem;
        background: linear-gradient(135deg, var(--light) 0%, #ffffff 100%);
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        border-left: 5px solid var(--primary);
    }
    
    .section-header {
        font-size: 1.8rem;
        color: var(--primary-dark);
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.8rem;
        border-bottom: 3px solid var(--secondary);
        font-weight: 600;
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1.5rem;
        border-left: 4px solid var(--primary);
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .psych-tip {
        background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        margin: 1.2rem 0;
        border-left: 4px solid var(--primary);
    }
    
    .success-card {
        background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);
        border-left: 4px solid var(--accent);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #FFF3E0 0%, #FFE0B2 100%);
        border-left: 4px solid var(--warning);
    }
    
    .danger-card {
        background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%);
        border-left: 4px solid var(--danger);
    }
    
    .metric-card {
        text-align: center;
        padding: 1.2rem;
        background: white;
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--primary-dark);
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #666;
        font-weight: 500;
    }
    
    .program-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        margin: 1.5rem 0;
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    }
    
    .program-table th {
        background: var(--primary);
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
    }
    
    .program-table td {
        padding: 1rem;
        border-bottom: 1px solid #eee;
    }
    
    .program-table tr:last-child td {
        border-bottom: none;
    }
    
    .program-table tr:nth-child(even) {
        background-color: #f9f9f9;
    }
    
    .program-table tr:hover {
        background-color: #f1f8ff;
    }
    
    .btn-primary {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 0.8rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .btn-primary:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(30, 136, 229, 0.4);
    }
    
    .progress-container {
        width: 100%;
        height: 1.5rem;
        background-color: #e0e0e0;
        border-radius: 1rem;
        margin: 1rem 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        border-radius: 1rem;
        text-align: center;
        color: white;
        line-height: 1.5rem;
        font-weight: 600;
        transition: width 0.5s ease;
    }
    
    .technique-card {
        background: white;
        padding: 1.2rem;
        border-radius: 1rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        border-left: 4px solid var(--secondary);
        transition: all 0.3s ease;
    }
    
    .technique-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        color: var(--primary);
    }
    
    /* Responsive tasarım */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
            padding: 1rem;
        }
        
        .section-header {
            font-size: 1.5rem;
        }
        
        .metric-value {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown('<div class="main-header">🧠 PSİKOLOJİ TEMELLİ YKS HAZIRLIK PROGRAMI</div>', unsafe_allow_html=True)

# YKS konuları (daha detaylı ve yapılandırılmış)
yks_konulari = {
    "TYT Türkçe": {
        "Anlam Bilgisi": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf"],
        "Dil Bilgisi": ["Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Sözcükte Yapı", "Sözcük Türleri"],
        "Anlatım Bozukluğu": ["Anlatım Bozukluğu"],
        "Edebi Türler": ["Sözlü Anlatım", "Yazılı Anlatım"]
    },
    "TYT Matematik": {
        "Temel Kavramlar": ["Sayılar", "Sayı Basamakları", "Bölme-Bölünebilme", "EBOB-EKOK"],
        "Problemler": ["Sayı Problemleri", "Kesir Problemleri", "Yaş Problemleri", "İşçi Problemleri", "Hareket Problemleri"],
        "Cebir": ["Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar"],
        "Geometri": ["Doğruda Açılar", "Üçgende Açılar", "Üçgende Alan", "Çokgenler", "Çember-Daire"]
    },
    # Diğer dersler için benzer yapı...
}

# Oturum durumu başlatma
if 'konu_durumu' not in st.session_state:
    st.session_state.konu_durumu = {}
if 'ogrenme_stili' not in st.session_state:
    st.session_state.ogrenme_stili = ""
if 'verimli_saatler' not in st.session_state:
    st.session_state.verimli_saatler = {"sabah": False, "ogle": False, "aksam": False, "gece": False}
if 'program' not in st.session_state:
    st.session_state.program = {}
if 'motivasyon' not in st.session_state:
    st.session_state.motivasyon = 70
if 'kisisel_veri' not in st.session_state:
    st.session_state.kisisel_veri = {}
if 'hedefler' not in st.session_state:
    st.session_state.hedefler = {}
if 'ilerleme' not in st.session_state:
    st.session_state.ilerleme = {}

# Yan menü
with st.sidebar:
    st.markdown('<div style="text-align: center; margin-bottom: 2rem;">', unsafe_allow_html=True)
    st.image("https://img.icons8.com/dusk/128/000000/mental-health.png", width=80)
    st.markdown('</div>', unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title="🎓 ÖĞRENCİ PROFİLİ",
        options=["Kişisel Bilgiler", "Öğrenme Stili", "Hedefler", "İlerleme", "Ayarlar"],
        icons=["person", "lightbulb", "flag", "graph-up", "gear"],
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f8f9fa"},
            "icon": {"color": "#1E88E5", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#e9ecef"},
            "nav-link-selected": {"background-color": "#1E88E5", "font-weight": "600"},
        }
    )
    
    if selected == "Kişisel Bilgiler":
        st.subheader("👤 Kişisel Bilgiler")
        isim = st.text_input("Adınız Soyadınız", "")
        yas = st.number_input("Yaşınız", min_value=15, max_value=30, value=18)
        hedef = st.text_input("Hedefiniz (Üniversite/Bölüm)", "Psikoloji Fakültesi")
        
        st.subheader("🛌 Uyku Düzeniniz")
        uyku_baslangic = st.time_input("Uyku Saati", datetime.strptime("23:00", "%H:%M").time())
        uyku_bitis = st.time_input("Uyanma Saati", datetime.strptime("06:00", "%H:%M").time())
        
    elif selected == "Öğrenme Stili":
        st.subheader("🎯 Öğrenme Stiliniz")
        ogrenme_stili = st.radio(
            "En iyi nasıl öğreniyorsunuz?",
            ["Görsel", "İşitsel", "Kinestetik", "Okuma/Yazma"],
            horizontal=True
        )
        st.session_state.ogrenme_stili = ogrenme_stili
        
        st.subheader("⏰ Verimli Saatleriniz")
        col1, col2 = st.columns(2)
        with col1:
            sabah = st.checkbox("Sabah (08:00-12:00)", True)
            ogle = st.checkbox("Öğle (12:00-16:00)")
        with col2:
            aksam = st.checkbox("Akşam (16:00-20:00)")
            gece = st.checkbox("Gece (20:00-24:00)")
        
        st.session_state.verimli_saatler = {
            "sabah": sabah, "ogle": ogle, "aksam": aksam, "gece": gece
        }
        
    elif selected == "Hedefler":
        st.subheader("🎯 Aylık Hedefler")
        hedef_aylik = st.slider("Bu Ay Tamamlanacak Konu Sayısı", 5, 50, 20)
        st.session_state.hedefler['aylik_konu'] = hedef_aylik
        
    elif selected == "İlerleme":
        st.subheader("📊 İlerleme Durumu")
        toplam_konu = len(st.session_state.konu_durumu)
        if toplam_konu > 0:
            tamamlanan_konu = sum(1 for v in st.session_state.konu_durumu.values() if v in ["İyi Seviye", "Uzman Seviye"])
            ilerleme_yuzdesi = (tamamlanan_konu / toplam_konu) * 100
            
            st.metric("Tamamlanan Konular", f"{tamamlanan_konu}/{toplam_konu}")
            st.metric("İlerleme Oranı", f"%{ilerleme_yuzdesi:.1f}")
            
            # İlerleme çubuğu
            st.markdown('<div class="progress-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="progress-bar" style="width: {ilerleme_yuzdesi}%; background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%);">{ilerleme_yuzdesi:.1f}%</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
    elif selected == "Ayarlar":
        st.subheader("⚙️ Çalışma Ayarları")
        pomodoro_sure = st.slider("Pomodoro Çalışma Süresi (dakika)", 25, 90, 45)
        mola_sure = st.slider("Mola Süresi (dakika)", 5, 20, 10)
        gunluk_ders_sayisi = st.slider("Günlük Ders Çeşidi", 1, 6, 3)
        gunluk_calisma_saati = st.slider("Günlük Çalışma Saati", 1, 12, 7)
        
        st.session_state.kisisel_veri['calisma_ayarlari'] = {
            'pomodoro': pomodoro_sure,
            'mola': mola_sure,
            'gunluk_ders': gunluk_ders_sayisi,
            'gunluk_saat': gunluk_calisma_saati
        }

# Ana içerik
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏠 Dashboard", "📚 Konu Analizi", "📅 Program", "📊 İlerleme", "💡 Teknikler"])

with tab1:
    st.markdown('<div class="section-header">📊 Kişisel Dashboard</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="feature-icon">📚</div>', unsafe_allow_html=True)
        toplam_konu = len(st.session_state.konu_durumu)
        st.markdown(f'<div class="metric-value">{toplam_konu}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Toplam Konu</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="feature-icon">✅</div>', unsafe_allow_html=True)
        tamamlanan_konu = sum(1 for v in st.session_state.konu_durumu.values() if v in ["İyi Seviye", "Uzman Seviye"])
        st.markdown(f'<div class="metric-value">{tamamlanan_konu}</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">Tamamlanan Konu</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown('<div class="feature-icon">📈</div>', unsafe_allow_html=True)
        ilerleme_yuzdesi = (tamamlanan_konu / toplam_konu * 100) if toplam_konu > 0 else 0
        st.markdown(f'<div class="metric-value">{ilerleme_yuzdesi:.1f}%</div>', unsafe_allow_html=True)
        st.markdown('<div class="metric-label">İlerleme Oranı</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Öneriler ve istatistikler
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('### 🎯 Bugünün Hedefi')
        
        if st.session_state.program:
            bugun = datetime.now().date()
            if bugun in st.session_state.program:
                st.info(f"**{st.session_state.program[bugun]['icerik']}**")
                st.caption(f"⏰ {st.session_state.program[bugun]['sure']} saat | 🍅 {st.session_state.program[bugun]['pomodoro']}")
            else:
                st.warning("Bugün için programlanmış bir aktivite bulunamadı.")
        else:
            st.info("Henüz bir program oluşturulmamış. Program sekmesinden oluşturabilirsiniz.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('### 📊 Haftalık Performans')
        
        # Örnek haftalık veri
        gunler = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
        calisma_saatleri = [6, 7, 5, 8, 6, 4, 3]  # Örnek veri
        
        fig = go.Figure(data=[
            go.Bar(x=gunler, y=calisma_saatleri, marker_color='#1E88E5')
        ])
        
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=False,
            yaxis_title="Saat"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Motivasyon ve öneriler
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('### 💪 Motivasyon ve Öneriler')
    
    if ilerleme_yuzdesi > 70:
        st.markdown('<div class="success-card">', unsafe_allow_html=True)
        st.success("**🎉 Mükemmel Gidiyorsunuz!** Hedefinize doğru emin adımlarla ilerliyorsunuz. Bu tempoyu koruyun.")
        st.markdown('</div>', unsafe_allow_html=True)
    elif ilerleme_yuzdesi > 40:
        st.markdown('<div class="warning-card">', unsafe_allow_html=True)
        st.warning("**👍 İyi Gidiyorsunuz!** Biraz daha çaba ile hedefinize ulaşabilirsiniz. Küçük molalar vererek verimliliğinizi artırabilirsiniz.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="danger-card">', unsafe_allow_html=True)
        st.error("**💪 Başlangıç Seviyesi!** Hedeflerinize ulaşmak için düzenli çalışma programı oluşturmalısınız. Her gün küçük adımlarla başlayın.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="section-header">📚 Konu Analizi ve Seviye Belirleme</div>', unsafe_allow_html=True)
    
    mastery_seviyeleri = ["Hiç Bilmiyorum", "Temel Seviye", "Orta Seviye", "İyi Seviye", "Uzman Seviye"]
    
    # Ders seçimi
    col1, col2 = st.columns([1, 3])
    
    with col1:
        secilen_ders = st.selectbox("Ders Seçin", list(yks_konulari.keys()))
    
    with col2:
        if secilen_ders:
            st.info(f"**{secilen_ders}** dersindeki konuları ve seviyelerinizi belirleyin.")
    
    if secilen_ders:
        # Konu kategorileri
        for kategori, konular in yks_konulari[secilen_ders].items():
            st.markdown(f'### 📖 {kategori}')
            
            for konu in konular:
                konu_key = f"{secilen_ders}>{kategori}>{konu}"
                
                if konu_key not in st.session_state.konu_durumu:
                    st.session_state.konu_durumu[konu_key] = "Hiç Bilmiyorum"
                
                mevcut_seviye = st.session_state.konu_durumu[konu_key]
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{konu}**")
                with col2:
                    yeni_seviye = st.selectbox(
                        f"{konu} seviyeniz:",
                        options=mastery_seviyeleri,
                        index=mastery_seviyeleri.index(mevcut_seviye),
                        key=konu_key,
                        label_visibility="collapsed"
                    )
                
                if yeni_seviye != mevcut_seviye:
                    st.session_state.konu_durumu[konu_key] = yeni_seviye
                    st.success(f"{konu} seviyesi güncellendi: {yeni_seviye}")

with tab3:
    st.markdown('<div class="section-header">📅 Kişiselleştirilmiş Çalışma Programı</div>', unsafe_allow_html=True)
    
    # Program oluşturma
    col1, col2, col3 = st.columns(3)
    
    with col1:
        baslangic_tarihi = st.date_input("Başlangıç Tarihi", datetime.now())
    
    with col2:
        program_suresi = st.slider("Program Süresi (gün)", 7, 90, 30)
    
    with col3:
        zorluk_seviyesi = st.slider("Program Yoğunluğu", 1, 5, 3)
        hedef_gun = baslangic_tarihi + timedelta(days=program_suresi)
        st.caption(f"Hedef Tarih: {hedef_gun.strftime('%d/%m/%Y')}")
    
    # Program oluşturma butonu
    if st.button("🔄 Programı Oluştur", type="primary", use_container_width=True):
        with st.spinner("Psikolojik profilinize uygun program oluşturuluyor..."):
            time.sleep(2)
            
            # Program oluşturma mantığı
            program = {}
            calisma_gunleri = [baslangic_tarihi + timedelta(days=i) for i in range(program_suresi)]
            
            # Basitleştirilmiş program oluşturma
            for i, gun in enumerate(calisma_gunleri):
                if i % 7 == 0:  # Pazartesi - Tekrar günü
                    program[gun] = {
                        "tip": "🔄 Tekrar",
                        "icerik": "Geçmiş haftanın konularının tekrarı ve deneme çözümü",
                        "sure": 6,
                        "pomodoro": "45+15"
                    }
                elif i % 7 == 6:  # Pazar - Hafif program
                    program[gun] = {
                        "tip": "📖 Hafif Çalışma",
                        "icerik": "Genel tekrar ve eksik konuların tamamlanması",
                        "sure": 4,
                        "pomodoro": "30+10"
                    }
                else:
                    # Normal çalışma günleri
                    program[gun] = {
                        "tip": "📚 Yoğun Çalışma",
                        "icerik": "Yeni konu öğrenme ve soru pratiği",
                        "sure": 8,
                        "pomodoro": "50+10"
                    }
            
            st.session_state.program = program
            st.success("✅ Program başarıyla oluşturuldu!")
    
    # Programı göster
    if st.session_state.program:
        st.markdown("### 📅 Haftalık Program")
        
        # Mevcut haftayı göster
        bugun = datetime.now().date()
        baslangic = bugun - timedelta(days=bugun.weekday())  # Haftanın başlangıcı (Pazartesi)
        haftalik_program = {}
        
        for i in range(7):
            gun = baslangic + timedelta(days=i)
            if gun in st.session_state.program:
                haftalik_program[gun] = st.session_state.program[gun]
        
        # Program tablosu
        program_data = []
        for gun, detay in haftalik_program.items():
            program_data.append({
                "Tarih": gun.strftime('%d/%m (%A)'),
                "Tip": detay["tip"],
                "İçerik": detay["icerik"],
                "Süre": f"{detay['sure']} saat",
                "Pomodoro": detay["pomodoro"]
            })
        
        program_df = pd.DataFrame(program_data)
        st.dataframe(program_df, use_container_width=True, hide_index=True)
        
        # Günlük program detayı
        st.markdown("### 📋 Günlük Program Detayı")
        secilen_gun = st.selectbox("Gün Seçin", list(haftalik_program.keys()), format_func=lambda x: x.strftime('%d/%m/%Y - %A'))
        
        if secilen_gun:
            gun_detay = haftalik_program[secilen_gun]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{gun_detay["sure"]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Saat</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                pomodoro = gun_detay["pomodoro"].split('+')
                st.markdown(f'<div class="metric-value">{pomodoro[0]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Dakika Çalışma</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<div class="metric-value">{pomodoro[1]}</div>', unsafe_allow_html=True)
                st.markdown('<div class="metric-label">Dakika Mola</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown(f"**Açıklama:** {gun_detay['icerik']}")

with tab4:
    st.markdown('<div class="section-header">📊 Detaylı İlerleme Analizi</div>', unsafe_allow_html=True)
    
    if not st.session_state.konu_durumu:
        st.info("Henüz konu eklemediniz. Lütfen önce 'Konu Analizi' sekmesinden konularınızı ekleyin.")
    else:
        # İlerleme istatistikleri
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            toplam_konu = len(st.session_state.konu_durumu)
            st.markdown(f'<div class="metric-value">{toplam_konu}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Toplam Konu</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            tamamlanan_konu = sum(1 for v in st.session_state.konu_durumu.values() if v in ["İyi Seviye", "Uzman Seviye"])
            st.markdown(f'<div class="metric-value">{tamamlanan_konu}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Tamamlanan</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            devam_eden_konu = sum(1 for v in st.session_state.konu_durumu.values() if v == "Orta Seviye")
            st.markdown(f'<div class="metric-value">{devam_eden_konu}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Devam Eden</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            baslanacak_konu = sum(1 for v in st.session_state.konu_durumu.values() if v in ["Hiç Bilmiyorum", "Temel Seviye"])
            st.markdown(f'<div class="metric-value">{baslanacak_konu}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Başlanacak</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # İlerleme grafiği
        st.markdown("### 📈 İlerleme Grafiği")
        
        # Derslere göre ilerleme
        ders_ilerleme = {}
        for konu_key, seviye in st.session_state.konu_durumu.items():
            ders = konu_key.split('>')[0]
            if ders not in ders_ilerleme:
                ders_ilerleme[ders] = {'toplam': 0, 'tamamlanan': 0}
            
            ders_ilerleme[ders]['toplam'] += 1
            if seviye in ["İyi Seviye", "Uzman Seviye"]:
                ders_ilerleme[ders]['tamamlanan'] += 1
        
        # Grafik için veri hazırlama
        dersler = list(ders_ilerleme.keys())
        tamamlanan_oranlar = [(ders_ilerleme[d]['tamamlanan'] / ders_ilerleme[d]['toplam'] * 100) for d in dersler]
        
        fig = go.Figure(data=[
            go.Bar(x=dersler, y=tamamlanan_oranlar, marker_color='#1E88E5')
        ])
        
        fig.update_layout(
            title="Derslere Göre Tamamlanma Oranları",
            yaxis_title="Tamamlanma Oranı (%)",
            showlegend=False,
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Aylık hedef takibi
        st.markdown("### 🎯 Aylık Hedef Takibi")
        
        hedef_aylik = st.slider("Bu Ay Tamamlamayı Hedeflediğiniz Konu Sayısı", 5, 50, 20)
        tahmini_tamamlanma = hedef_aylik * (tamamlanan_konu / toplam_konu) if toplam_konu > 0 else 0
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{tahmini_tamamlanma:.1f}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Tahmini Tamamlanma</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown(f'<div class="metric-value">{hedef_aylik}</div>', unsafe_allow_html=True)
            st.markdown('<div class="metric-label">Hedef</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # İlerleme durumu
        if tahmini_tamamlanma >= hedef_aylik * 0.8:
            st.markdown('<div class="success-card">', unsafe_allow_html=True)
            st.success("**🎉 Mükemmel!** Bu hızla hedefinize ulaşacaksınız. Motivasyonunuzu koruyun.")
            st.markdown('</div>', unsafe_allow_html=True)
        elif tahmini_tamamlanma >= hedef_aylik * 0.5:
            st.markdown('<div class="warning-card">', unsafe_allow_html=True)
            st.warning("**👍 İyi Gidiyorsunuz!** Biraz daha çaba ile hedefinize ulaşabilirsiniz. Planınızı gözden geçirin.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="danger-card">', unsafe_allow_html=True)
            st.error("**💪 Daha Fazla Çaba Gerek!** Hedefinize ulaşmak için çalışma tempounuzu artırmanız gerekebilir.")
            st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    st.markdown('<div class="section-header">💡 Kanıtlanmış Öğrenme Teknikleri</div>', unsafe_allow_html=True)
    
    # Öğrenme teknikleri
    teknikler = [
        {
            "isim": "Feynman Tekniği",
            "aciklama": "Konuyu 5 yaşındaki bir çocuğa anlatabilecek kadar basitleştir. Bu, konuyu ne kadar iyi anladığını test eder.",
            "emoji": "🎯",
            "detay": "1. Konuyu öğren\n2. Basitçe açıkla\n3. Eksikleri tespit et\n4. Basitleştir ve analojiler kullan"
        },
        {
            "isim": "Aktif Hatırlama (Active Recall)",
            "aciklama": "Kitaba veya deftere bakmadan konuyu hatırlamaya çalış. Beynini zorlayarak bilgiyi daha derinlemesine işlersin.",
            "emoji": "🔄",
            "detay": "1. Konuyu oku\n2. Kitabı kapat\n3. Hatırlamaya çalış\n4. Kontrol et ve tekrarla"
        },
        {
            "isim": "Interleaving (Karışık Çalışma)",
            "aciklama": "Farklı konuları veya dersleri art arda çalış. Bu yöntem, beynin bilgiyi ayırt etme ve bağlantı kurma yeteneğini güçlendirir.",
            "emoji": "🎨",
            "detay": "1. Farklı konuları karıştır\n2. Benzer konuları ardışık çalışma\n3. Beynin bağlantı kurmasını sağla"
        },
        {
            "isim": "Mind Mapping (Zihin Haritası)",
            "aciklama": "Konuları anahtar kelimeler ve görsellerle bir ağaç gibi organize et. Beyin, bu görsel bağlantıları daha kolay hatırlar.",
            "emoji": "📝",
            "detay": "1. Ana konuyu merkeze yaz\n2. Alt başlıkları dallandır\n3. Görseller ve renkler kullan\n4. İlişkileri göster"
        },
        {
            "isim": "Pomodoro Tekniği",
            "aciklama": "25 dakika çalışma, 5 dakika mola şeklinde çalış. Odaklanmayı artırır ve mental yorgunluğu azaltır.",
            "emoji": "⏰",
            "detay": "1. 25 dakika odaklan\n2. 5 dakika mola\n3. 4 pomodoroda 15-30 dakika mola\n4. Tekrarla"
        },
        {
            "isim": "Blitz Tekrar",
            "aciklama": "Öğrendiğin bir konuyu kısa süre sonra (örneğin 24 saat içinde) hızlıca tekrar et. Bu, bilginin uzun süreli hafızaya geçişini sağlar.",
            "emoji": "🚀",
            "detay": "1. Öğren\n2. 24 saat içinde tekrarla\n3. 1 hafta sonra tekrar tekrarla\n4. 1 ay sonra son tekrar"
        }
    ]
    
    for teknik in teknikler:
        with st.expander(f"{teknik['emoji']} {teknik['isim']}", expanded=False):
            st.markdown(f"**{teknik['aciklama']}**")
            st.markdown(f"*{teknik['detay']}*")
    
    # Öğrenme stiline göre öneriler
    st.markdown("### 👤 Öğrenme Stilinize Özel İpuçları")
    
    if st.session_state.ogrenme_stili == "Görsel":
        st.markdown("""
        <div class="psych-tip">
        <h4>👁️ Görsel Öğrenenler İçin:</h4>
        <ul>
        <li><strong>Renk kodlaması kullanın:</strong> Farklı konular için farklı renklerde kalemler/markerlar kullanın</li>
        <li><strong>Mind map oluşturun:</strong> Konuları görsel haritalarla ilişkilendirin</li>
        <li><strong>Grafik ve diyagramlar çizin:</strong> Soyut kavramları görselleştirin</li>
        <li><strong>Video içerikleri izleyin:</strong> Görsel anlatımları tercih edin</li>
        <li><strong>Flashcard'ları renkli yapın:</strong> Görsel hafızanızı güçlendirin</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.ogrenme_stili == "İşitsel":
        st.markdown("""
        <div class="psych-tip">
        <h4>👂 İşitsel Öğrenenler İçin:</h4>
        <ul>
        <li><strong>Sesli kayıtlar yapın:</strong> Kendi sesinizle konu anlatımlarını kaydedin</li>
        <li><strong>Grupla çalışın:</strong> Konuları başkalarına anlatın veya tartışın</li>
        <li><strong>Ritmik tekrarlar yapın:</strong> Önemli bilgileri ritmik şekilde tekrarlayın</li>
        <li><strong>Arka plan müziği kullanın:</strong> Çalışırken klasik müzik veya doğa sesleri dinleyin</li>
        <li><strong>Konu anlatım videoları izleyin:</strong> Sesli anlatımları tercih edin</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    elif st.session_state.ogrenme_stili == "Kinestetik":
        st.markdown("""
        <div class="psych-tip">
        <h4>🔧 Kinestetik Öğrenenler İçin:</h4>
        <ul>
        <li><strong>Hareket ederek çalışın:</strong> Ayakta durarak veya yürüyerek çalışın</li>
        <li><strong>Modeller oluşturun:</strong> Fiziksel modeller veya el işleriyle öğrenin</li>
        <li><strong>Role-play yapın:</strong> Tarihi olayları veya bilimsel süreçleri canlandırın</li>
        <li><strong>Sık molalar verin:</strong> Uzun süre hareketsiz kalmayın</li>
        <li><strong>Deneyler yapın:</strong> Mümkünse konuları pratik olarak deneyimleyin</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        st.markdown("""
        <div class="psych-tip">
        <h4>📖 Okuyarak/Yazarak Öğrenenler İçin:</h4>
        <ul>
        <li><strong>Detaylı notlar çıkarın:</strong> Okuduklarınızı kendi kelimelerinizle yazın</li>
        <li><strong>Özetler hazırlayın:</strong> Konuları özet kartlarına yazın</li>
        <li><strong>Essay'ler yazın:</strong> Konular hakkında kısa yazılar yazın</li>
        <li><strong>Listeler oluşturun:</strong> Bilgileri maddeler halinde düzenleyin</li>
        <li><strong>Kendi sorularınızı yazın:</strong> Konularla ilgili sorular oluşturun ve cevaplayın</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Motivasyon artırıcı teknikler
    st.markdown("### 💪 Motivasyon Artırıcı Teknikler")
    
    st.markdown("""
    <div class="card">
    <ul>
    <li><strong>Küçük hedefler belirleyin:</strong> Büyük hedefleri küçük parçalara bölün</li>
    <li><strong>Kendini ödüllendirin:</strong> Başarılarınızı küçük ödüllerle kutlayın</li>
    <li><strong>Olumlu iç konuşma:</strong> Kendinize motive edici cümleler söyleyin</li>
    <li><strong>Görselleştirme:</strong> Başarılı olduğunuz anları zihninizde canlandırın</li>
    <li><strong>Sosyal destek:</strong> Aileniz ve arkadaşlarınızdan destek isteyin</li>
    <li><strong>İlerlemeyi takip edin:</strong> Günlük ve haftalık ilerlemenizi kaydedin</li>
    <li><strong>Esneklik:</strong> Programınızda esnek olun, kendinize zaman tanıyın</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 3rem;">
<p><strong>🧠 Bu program psikoloji prensipleri temel alınarak kişiselleştirilmiş öğrenme deneyimi sunar.</strong></p>
<p>Düzenli geri bildirim ve ayarlamalarla maksimum verimlilik hedeflenir. Unutmayın, her öğrenci farklıdır ve kendi hızında ilerler.</p>
<p>Kendinizi başkalarıyla kıyaslamak yerine, kendi ilerlemenize odaklanın.</p>
</div>
""", unsafe_allow_html=True)
def derece_deneme_analizi():
    st.markdown('<div class="section-header">📈 Deneme Sonucu Analizi</div>', unsafe_allow_html=True)
    
    bilgi = st.session_state.öğrenci_bilgisi
    tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
    
    # Deneme sonucu girme formu
    with st.form("deneme_form"):
        st.markdown("### ✍️ Yeni Deneme Sonucu Ekle")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**TYT Netleri**")
            tyt_mat = st.number_input("Matematik", 0, 40, 0, key="tyt_mat")
            tyt_tur = st.number_input("Türkçe", 0, 40, 0, key="tyt_tur")
            tyt_sos = st.number_input("Sosyal", 0, 20, 0, key="tyt_sos")
            tyt_fen = st.number_input("Fen", 0, 20, 0, key="tyt_fen")
        
        with col2:
            st.markdown("**AYT Netleri**")
            if bilgi['alan'] == "Sayısal":
                ayt_mat = st.number_input("AYT Matematik", 0, 40, 0, key="ayt_mat")
                ayt_fiz = st.number_input("Fizik", 0, 14, 0, key="ayt_fiz")
                ayt_kim = st.number_input("Kimya", 0, 13, 0, key="ayt_kim")
                ayt_bio = st.number_input("Biyoloji", 0, 13, 0, key="ayt_bio")
                ayt_edeb = 0
                ayt_tar = 0
                ayt_cog = 0
            elif bilgi['alan'] == "Sözel":
                ayt_edeb = st.number_input("Edebiyat", 0, 24, 0, key="ayt_edeb")
                ayt_tar = st.number_input("Tarih", 0, 10, 0, key="ayt_tar")
                ayt_cog = st.number_input("Coğrafya", 0, 6, 0, key="ayt_cog")
                ayt_mat = 0
                ayt_fiz = 0
                ayt_kim = 0
                ayt_bio = 0
            else:  # Eşit Ağırlık
                ayt_mat = st.number_input("AYT Matematik", 0, 40, 0, key="ayt_mat")
                ayt_edeb = st.number_input("Edebiyat", 0, 24, 0, key="ayt_edeb")
                ayt_tar = st.number_input("Tarih", 0, 10, 0, key="ayt_tar")
                ayt_cog = st.number_input("Coğrafya", 0, 6, 0, key="ayt_cog")
                ayt_fiz = 0
                ayt_kim = 0
                ayt_bio = 0
        
        with col3:
            st.markdown("**Ek Bilgiler**")
            deneme_adı = st.text_input("Deneme Adı", "Genel Deneme")
            deneme_tarihi = st.date_input("Deneme Tarihi", datetime.now().date())
            çözüm_süresi = st.number_input("Çözüm Süresi (dk)", 60, 300, 180)
            notlar = st.text_area("Notlar", placeholder="Zorlandığın sorular, gözlemler...")
        
        deneme_kaydet = st.form_submit_button("📊 Deneme Sonucunu Kaydet")
        
        if deneme_kaydet:
            toplam_tyt = tyt_mat + tyt_tur + tyt_sos + tyt_fen
            toplam_ayt = ayt_mat + ayt_fiz + ayt_kim + ayt_bio + ayt_edeb + ayt_tar + ayt_cog
            
            yeni_deneme = {
                'tarih': str(deneme_tarihi),
                'ad': deneme_adı,
                'tyt_mat': tyt_mat,
                'tyt_tur': tyt_tur,
                'tyt_sos': tyt_sos,
                'tyt_fen': tyt_fen,
                'tyt_net': toplam_tyt,
                'ayt_mat': ayt_mat,
                'ayt_fiz': ayt_fiz,
                'ayt_kim': ayt_kim,
                'ayt_bio': ayt_bio,
                'ayt_edeb': ayt_edeb,
                'ayt_tar': ayt_tar,
                'ayt_cog': ayt_cog,
                'ayt_net': toplam_ayt,
                'toplam_net': toplam_tyt + toplam_ayt,
                'süre': çözüm_süresi,
                'notlar': notlar,
                'alan': bilgi['alan']
            }
            
            if 'deneme_sonuçları' not in st.session_state:
                st.session_state.deneme_sonuçları = []
            
            st.session_state.deneme_sonuçları.append(yeni_deneme)
            
            # Analiz yap
            analiz = derece_performans_analizi(toplam_tyt, toplam_ayt, bilgi)
            
            st.success(f"✅ Deneme kaydedildi! Toplam Net: {toplam_tyt + toplam_ayt}")
            
            # Durum mesajı
            if analiz['durum'] == 'Derece Adayı':
                st.balloons()
                st.markdown(f'''
                <div class="success-card">
                    <h3>🏆 TEBRİKLER! DERECE ADAYISIN!</h3>
                    <p>Bu performansla {bilgi['hedef_bölüm']} çok yakın!</p>
                </div>
                ''', unsafe_allow_html=True)
            elif analiz['durum'] == 'Hedefte':
                st.markdown(f'''
                <div class="info-card">
                    <h3>🎯 HEDEFTESİN!</h3>
                    <p>Çok iyi gidiyorsun, bu tempoyu korumaya odaklan!</p>
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div class="warning-card">
                    <h3>💪 DAHA FAZLA ÇALIŞMAN GEREKİYOR!</h3>
                    <p>{analiz['eksik_net']:.1f} net daha artırman gerekiyor.</p>
                </div>
                ''', unsafe_allow_html=True)
            
            # Verileri kaydet
            data_to_save = {
                'öğrenci_bilgisi': st.session_state.öğrenci_bilgisi,
                'program_oluşturuldu': st.session_state.program_oluşturuldu,
                'deneme_sonuçları': st.session_state.deneme_sonuçları,
                'konu_durumu': st.session_state.konu_durumu,
                'günlük_çalışma_kayıtları': st.session_state.günlük_çalışma_kayıtları,
                'motivasyon_puanı': st.session_state.motivasyon_puanı,
                'hedef_sıralama': st.session_state.hedef_sıralama,
            }
            save_user_data(st.session_state.kullanıcı_adı, data_to_save)
            
            st.rerun()
    
    # Mevcut deneme sonuçlarını göster
    if 'deneme_sonuçları' in st.session_state and st.session_state.deneme_sonuçları:
        st.markdown("### 📊 Deneme Sonuçları Trendi")
        
        df = pd.DataFrame(st.session_state.deneme_sonuçları)
        
        # Grafik oluştur
        fig = px.line(df, x='tarih', y=['tyt_net', 'ayt_net', 'toplam_net'], 
                     title="Net Gelişim Trendi", 
                     labels={'value': 'Net Sayısı', 'tarih': 'Tarih'})
        
        fig.update_traces(mode='markers+lines')
        st.plotly_chart(fig, use_container_width=True)
        
        # Son deneme analizi
        son_deneme = df.iloc[-1]
        st.markdown("### 📋 Son Deneme Detaylı Analizi")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("TYT Net", f"{son_deneme['tyt_net']}", 
                     delta=f"{son_deneme['tyt_net'] - df.iloc[-2]['tyt_net']:.1f}" if len(df) > 1 else None)
        
        with col2:
            st.metric("AYT Net", f"{son_deneme['ayt_net']}", 
                     delta=f"{son_deneme['ayt_net'] - df.iloc[-2]['ayt_net']:.1f}" if len(df) > 1 else None)
        
        with col3:
            st.metric("Toplam Net", f"{son_deneme['toplam_net']}", 
                     delta=f"{son_deneme['toplam_net'] - df.iloc[-2]['toplam_net']:.1f}" if len(df) > 1 else None)
        
        with col4:
            hedef_net = hedef_net_hesapla(bilgi['hedef_sıralama'], bilgi['alan'])
            fark = son_deneme['toplam_net'] - hedef_net
            st.metric("Hedefe Uzaklık", f"{fark:+.1f}")
        
        # Ders bazında analiz
        st.markdown("### 🎯 Ders Bazında Detay Analizi")
        
        if bilgi['alan'] == "Sayısal":
            ders_netleri = {
                'TYT Matematik': son_deneme['tyt_mat'],
                'TYT Türkçe': son_deneme['tyt_tur'],
                'TYT Fen': son_deneme['tyt_fen'],
                'TYT Sosyal': son_deneme['tyt_sos'],
                'AYT Matematik': son_deneme['ayt_mat'],
                'Fizik': son_deneme['ayt_fiz'],
                'Kimya': son_deneme['ayt_kim'],
                'Biyoloji': son_deneme['ayt_bio']
            }
            maksimum_netler = {
                'TYT Matematik': 40, 'TYT Türkçe': 40, 'TYT Fen': 20, 'TYT Sosyal': 20,
                'AYT Matematik': 40, 'Fizik': 14, 'Kimya': 13, 'Biyoloji': 13
            }
        elif bilgi['alan'] == "Sözel":
            ders_netleri = {
                'TYT Matematik': son_deneme['tyt_mat'],
                'TYT Türkçe': son_deneme['tyt_tur'],
                'TYT Fen': son_deneme['tyt_fen'],
                'TYT Sosyal': son_deneme['tyt_sos'],
                'Edebiyat': son_deneme['ayt_edeb'],
                'Tarih': son_deneme['ayt_tar'],
                'Coğrafya': son_deneme['ayt_cog']
            }
            maksimum_netler = {
                'TYT Matematik': 40, 'TYT Türkçe': 40, 'TYT Fen': 20, 'TYT Sosyal': 20,
                'Edebiyat': 24, 'Tarih': 10, 'Coğrafya': 6
            }
        else:  # Eşit Ağırlık
            ders_netleri = {
                'TYT Matematik': son_deneme['tyt_mat'],
                'TYT Türkçe': son_deneme['tyt_tur'],
                'TYT Fen': son_deneme['tyt_fen'],
                'TYT Sosyal': son_deneme['tyt_sos'],
                'AYT Matematik': son_deneme['ayt_mat'],
                'Edebiyat': son_deneme['ayt_edeb'],
                'Tarih': son_deneme['ayt_tar'],
                'Coğrafya': son_deneme['ayt_cog']
            }
            maksimum_netler = {
                'TYT Matematik': 40, 'TYT Türkçe': 40, 'TYT Fen': 20, 'TYT Sosyal': 20,
                'AYT Matematik': 40, 'Edebiyat': 24, 'Tarih': 10, 'Coğrafya': 6
            }
        
        # Her ders için başarı yüzdesi hesapla
        ders_analizi = []
        for ders, net in ders_netleri.items():
            maksimum = maksimum_netler[ders]
            yüzde = (net / maksimum) * 100 if maksimum > 0 else 0
            
            if yüzde >= 80:
                durum = "🟢 Mükemmel"
                öneri = "Bu seviyeyi koru, hız çalış"
            elif yüzde >= 60:
                durum = "🟡 İyi"
                öneri = "Daha zorlu sorulara geç"
            elif yüzde >= 40:
                durum = "🟠 Orta"
                öneri = "Konu eksiklerini tamamla"
            else:
                durum = "🔴 Zayıf"
                öneri = "Temel konuları güçlendir"
            
            ders_analizi.append({
                'Ders': ders,
                'Net': f"{net}/{maksimum}",
                'Yüzde': f"{yüzde:.1f}%",
                'Durum': durum,
                'Öneri': öneri
            })
        
        analiz_df = pd.DataFrame(ders_analizi)
        st.dataframe(analiz_df, use_container_width=True)
        
        # Zayıf alanlar için özel öneriler
        zayıf_dersler = [d for d in ders_analizi if "🔴" in d['Durum']]
        orta_dersler = [d for d in ders_analizi if "🟠" in d['Durum']]
        
        if zayıf_dersler:
            st.markdown("### 🔴 Acil Müdahale Gereken Dersler")
            for ders in zayıf_dersler:
                st.warning(f"**{ders['Ders']}**: {ders['Öneri']}")
        
        if orta_dersler:
            st.markdown("### 🟠 İyileştirilebilir Dersler")
            for ders in orta_dersler:
                st.info(f"**{ders['Ders']}**: {ders['Öneri']}")
        
        # Hedef odaklı analiz
        st.markdown("### 🎯 Hedefe Yönelik Strateji")
        
        analiz = derece_performans_analizi(son_deneme['tyt_net'], son_deneme['ayt_net'], bilgi)
        
        st.markdown(f"**Durum:** {analiz['durum']}")
        
        if analiz['eksik_net'] > 0:
            st.markdown(f"**Kapatman gereken net:** {analiz['eksik_net']:.1f}")
            
            # Net dağılım önerisi
            if bilgi['alan'] == "Sayısal":
                öneri_dağılım = {
                    "TYT Matematik": min(5, analiz['eksik_net'] * 0.3),
                    "AYT Matematik": min(8, analiz['eksik_net'] * 0.4),
                    "Fen Dersleri": min(6, analiz['eksik_net'] * 0.3)
                }
            elif bilgi['alan'] == "Sözel":
                öneri_dağılım = {
                    "TYT Türkçe": min(6, analiz['eksik_net'] * 0.3),
                    "Edebiyat": min(8, analiz['eksik_net'] * 0.4),
                    "Sosyal Dersler": min(4, analiz['eksik_net'] * 0.3)
                }
            else:  # Eşit Ağırlık
                öneri_dağılım = {
                    "TYT Matematik": min(4, analiz['eksik_net'] * 0.25),
                    "TYT Türkçe": min(4, analiz['eksik_net'] * 0.25),
                    "AYT Matematik": min(6, analiz['eksik_net'] * 0.3),
                    "Edebiyat": min(4, analiz['eksik_net'] * 0.2)
                }
            
            st.markdown("**Önerilen Net Artırım Dağılımı:**")
            for ders, artış in öneri_dağılım.items():
                if artış > 0:
                    st.markdown(f"• {ders}: +{artış:.1f} net")
        
        # Zamana göre ilerleme analizi
        if len(df) >= 3:
            st.markdown("### 📈 İlerleme Hız Analizi")
            
            son_3_deneme = df.tail(3)
            ilk_net = son_3_deneme.iloc[0]['toplam_net']
            son_net = son_3_deneme.iloc[-1]['toplam_net']
            
            ilerleme_hızı = (son_net - ilk_net) / 2  # Son 3 deneme arası ortalama artış
            
            if ilerleme_hızı > 2:
                st.success(f"🚀 Harika! Deneme başına ortalama {ilerleme_hızı:.1f} net artırıyorsun!")
            elif ilerleme_hızı > 0:
                st.info(f"📈 İyi gidiyorsun. Deneme başına {ilerleme_hızı:.1f} net artış var.")
            else:
                st.warning("⚠️ Son denemelerde net artışı yavaşladı. Strateji değişikliği gerekebilir.")
            
            # Hedefe ulaşma tahmini
            if ilerleme_hızı > 0 and analiz['eksik_net'] > 0:
                gereken_deneme = int(analiz['eksik_net'] / ilerleme_hızı) + 1
                st.info(f"Bu hızla devam edersen, yaklaşık {gereken_deneme} deneme sonra hedefe ulaşabilirsin.")
    
    else:
        st.info("Henüz deneme sonucu girmediniz. İlk denemenizi ekleyerek analizlere başlayın!")

    
     
def derece_konu_takibi():
    
    
    st.markdown('<div class="section-header">🎯 Konu Masterysi</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.1rem;">Eksik olduğun konuları en detaylı şekilde takip et.</p>', unsafe_allow_html=True)
    
    # YKS konularını 4 seviyeli hiyerarşik olarak tanımla
    yks_konulari = {
        "TYT Türkçe": {
            "Anlam Bilgisi": {
                "Sözcükte Anlam": [
                    "Gerçek, Mecaz, Terim Anlam",
                    "Çok Anlamlılık",
                    "Deyimler ve Atasözleri",
                    "Sözcükler Arası Anlam İlişkileri"
                ],
                "Cümlede Anlam": [
                    "Cümle Yorumlama",
                    "Kesin Yargıya Ulaşma",
                    "Anlatım Biçimleri",
                    "Duygu ve Düşünceleri İfade Etme",
                    "Amaç-Sonuç, Neden-Sonuç, Koşul-Sonuç"
                ],
                "Paragraf": [
                    "Anlatım Teknikleri",
                    "Düşünceyi Geliştirme Yolları",
                    "Paragrafta Yapı",
                    "Paragrafta Konu-Ana Düşünce",
                    "Paragrafta Yardımcı Düşünce"
                ]
            },
            "Dil Bilgisi": {
                "Ses Bilgisi": [
                    "Ünlü-Ünsüz Uyumları",
                    "Ses Olayları"
                ],
                "Yazım Kuralları": [
                    "Büyük Harflerin Kullanımı",
                    "Birleşik Kelimelerin Yazımı",
                    "Sayıların ve Kısaltmaların Yazımı",
                    "Bağlaçların Yazımı"
                ],
                "Noktalama İşaretleri": [
                    "Nokta, Virgül",
                    "Noktalı Virgül, İki Nokta, Üç Nokta",
                    "Soru, Ünlem, Tırnak İşareti",
                    "Yay Ayraç ve Kesme İşareti"
                ],
                "Sözcükte Yapı": [
                    "Kök ve Gövde",
                    "Ekler (Yapım/Çekim)",
                    "Basit, Türemiş, Birleşik Sözcükler"
                ],
                "Sözcük Türleri": [
                    "İsimler ve Zamirler",
                    "Sıfatlar ve Zarflar",
                    "Edat, Bağlaç, Ünlem"
                ],
                "Fiiller": [
                    "Fiilde Anlam",
                    "Ek Fiil",
                    "Fiilimsi",
                    "Fiilde Çatı"
                ],
                "Cümlenin Ögeleri": [
                    "Temel Ögeler (Yüklem, Özne, Nesne)",
                    "Yardımcı Ögeler (Dolaylı, Zarf, Edat Tümleci)"
                ],
                "Cümle Türleri": [
                    "Yüklem ve Yapılarına Göre Cümleler"
                ],
                "Anlatım Bozukluğu": [
                    "Anlamsal ve Yapısal Bozukluklar"
                ]
            }
        },
        "TYT Matematik": {
            "Temel Matematik": {
                "Temel Kavramlar": [
                    "Sayılar",
                    "Sayı Basamakları",
                    "Bölme ve Bölünebilme",
                    "EBOB – EKOK"
                ],
                "Temel İşlemler": [
                    "Rasyonel Sayılar",
                    "Basit Eşitsizlikler",
                    "Mutlak Değer",
                    "Üslü Sayılar",
                    "Köklü Sayılar"
                ],
                "Cebirsel İfadeler": [
                    "Çarpanlara Ayırma",
                    "Oran Orantı",
                    "Denklem Çözme"
                ]
            },
            "Problemler": {
                "Sayı Problemleri": ["Sayı Problemleri Genel"],
                "Kesir Problemleri": ["Kesir Problemleri Genel"],
                "Yaş Problemleri": ["Yaş Problemleri Genel"],
                "Yüzde Problemleri": ["Yüzde Problemleri Genel"],
                "Kar-Zarar Problemleri": ["Kar-Zarar Problemleri Genel"],
                "Karışım Problemleri": ["Karışım Problemleri Genel"],
                "Hareket Problemleri": ["Hareket Problemleri Genel"],
                "İşçi Problemleri": ["İşçi Problemleri Genel"],
                "Tablo-Grafik Problemleri": ["Tablo-Grafik Problemleri Genel"],
                "Rutin Olmayan Problemler": ["Rutin Olmayan Problemler Genel"]
            },
            "Kümeler ve Olasılık": {
                "Fonksiyonlar ve Kümeler": [
                    "Kümeler",
                    "Mantık",
                    "Fonksiyonlar"
                ],
                "İleri Cebir Konuları": [
                    "Polinomlar",
                    "2. Dereceden Denklemler"
                ],
                "Olasılık ve İstatistik": [
                    "Permütasyon",
                    "Kombinasyon",
                    "Olasılık",
                    "Veri – İstatistik"
                ]
            }
        },
        "TYT Geometri": {
            "Temel Geometri": {
                "Temel Kavramlar": ["Geometriye Giriş"],
                "Doğruda Açılar": ["Doğruda Açılar Genel"],
                "Üçgende Açılar": ["Üçgende Açılar Genel"]
            },
            "Özel Üçgenler": {
                "Özel Üçgenler": [
                    "Dik Üçgen",
                    "İkizkenar Üçgen",
                    "Eşkenar Üçgen"
                ],
                "Üçgen Yardımcı Elemanları": [
                    "Açıortay",
                    "Kenarortay",
                    "Eşlik ve Benzerlik",
                    "Üçgende Alan",
                    "Açı Kenar Bağıntıları"
                ]
            },
            "Çokgenler": {
                "Genel Çokgenler": ["Genel Çokgenler Konuları"],
                "Özel Dörtgenler": [
                    "Dörtgenler (Genel)",
                    "Deltoid",
                    "Paralelkenar",
                    "Eşkenar Dörtgen",
                    "Dikdörtgen",
                    "Kare",
                    "Yamuk"
                ]
            },
            "Çember ve Katı Cisimler": {
                "Çember ve Daire": [
                    "Çemberde Açı",
                    "Çemberde Uzunluk",
                    "Dairede Çevre ve Alan"
                ],
                "Katı Cisimler": [
                    "Prizmalar",
                    "Küp",
                    "Silindir",
                    "Piramit",
                    "Koni",
                    "Küre"
                ]
            },
            "Analitik Geometri": {
                "Analitik Geometri": [
                    "Noktanın Analitiği",
                    "Doğrunun Analitiği",
                    "Dönüşüm Geometrisi",
                    "Çemberin Analitiği"
                ]
            }
        },
        "TYT Tarih": {
            "Tarih Bilimine Giriş": {
                "Tarih ve Zaman": [
                    "Tarih Biliminin Tanımı",
                    "Türklerin Kullandığı Takvimler"
                ],
                "İnsanlığın İlk Dönemleri": [
                    "Tarih Öncesi Çağlar",
                    "Yazının İcadı ve Önemi"
                ]
            },
            "Türk ve İslam Tarihi": {
                "İlk ve Orta Çağda Türk Dünyası": [
                    "İlk Türk Devletleri (Asya Hun, Göktürk, Uygur)",
                    "Türklerin İslamiyet'i Kabulü"
                ],
                "İslam Medeniyetinin Doğuşu": [
                    "İslamiyet'in Doğuşu"
                ],
                "Türk-İslam Devletlerinde Kültür ve Medeniyet": [
                    "Karahanlılar, Gazneliler, Büyük Selçuklu",
                    "Devlet Yönetimi ve Ekonomi"
                ],
                "Beylikten Devlete Osmanlı Siyaseti": [
                    "Kuruluş ve Büyüme Nedenleri",
                    "İskan Politikası"
                ]
            },
            "Osmanlı ve Avrupa Tarihi": {
                "Dünya Gücü Osmanlı": [
                    "Yükselme Dönemi (Fatih, Yavuz, Kanuni)",
                    "Siyasi ve Askeri Güç"
                ],
                "Arayış Yılları (Duraklama)": [
                    "Duraklama Dönemi ve Nedenleri",
                    "Osmanlı-Avrupa İlişkileri"
                ],
                "En Uzun Yüzyıl (19. Yüzyıl)": [
                    "Dağılma Dönemi",
                    "Fikir Akımları"
                ],
                "20. Yüzyıl Başlarında Osmanlı": [
                    "I. Dünya Savaşı ve Osmanlı'nın Durumu",
                    "Wilson İlkeleri, Mondros"
                ]
            }
        },
        "TYT Coğrafya": {
            "Doğal Sistemler": {
                "Doğa ve İnsan": ["Doğa ve İnsan Etkileşimi"],
                "Dünya ve Konum": [
                    "Dünya’nın Şekli ve Hareketleri",
                    "Coğrafi Konum",
                    "Harita Bilgisi"
                ],
                "İklim Bilgisi": [
                    "İklim Elemanları (Sıcaklık, Basınç vb.)",
                    "İklim Tipleri"
                ],
                "Yerin Şekillenmesi": [
                    "İç Kuvvetler",
                    "Dış Kuvvetler"
                ],
                "Doğanın Varlıkları": [
                    "Kayaçlar",
                    "Su Kaynakları",
                    "Topraklar",
                    "Bitki Örtüsü"
                ]
            },
            "Beşeri Sistemler": {
                "Nüfus ve Yerleşme": [
                    "Beşeri Yapı ve Yerleşme",
                    "Nüfusun Gelişimi ve Dağılışı",
                    "Göçlerin Nedenleri ve Sonuçları"
                ],
                "Ekonomik Faaliyetler": [
                    "Geçim Tarzları"
                ]
            },
            "Türkiye Coğrafyası": {
                "Türkiye": [
                    "Yeryüzü Şekilleri ve İklimi",
                    "Doğal Varlıkları",
                    "Yerleşme ve Nüfus"
                ]
            },
            "Küresel ve Çevresel Konular": {
                "Bölgeler ve Ülkeler": [
                    "Bölge Türleri",
                    "Konum ve Etkileşim",
                    "Uluslararası Ulaşım"
                ],
                "Çevre ve Toplum": [
                    "Çevre Sorunları",
                    "Doğal Afetler"
                ]
            }
        },
        "TYT Biyoloji": {
            "Yaşam Bilimi": {
                "Canlıların Ortak Özellikleri": ["Canlıların Ortak Özellikleri Genel"],
                "Temel Bileşikler": [
                    "İnorganik Bileşikler",
                    "Organik Bileşikler"
                ]
            },
            "Hücre ve Canlılar": {
                "Hücre Bilgisi": [
                    "Prokaryot ve Ökaryot",
                    "Organellerin Yapı ve Görevleri"
                ],
                "Canlılar Dünyası": [
                    "Canlıların Sınıflandırılması",
                    "Canlı Alemleri ve Özellikleri"
                ]
            },
            "Kalıtım ve Ekoloji": {
                "Hücre Bölünmeleri": [
                    "Mitoz ve Eşeysiz Üreme",
                    "Mayoz ve Eşeyli Üreme"
                ],
                "Kalıtım ve Çeşitlilik": [
                    "Kalıtımın Genel İlkeleri",
                    "Biyolojik Çeşitlilik"
                ],
                "Ekosistem Ekolojisi": [
                    "Besin Zinciri",
                    "Madde Döngüleri",
                    "Güncel Çevre Sorunları"
                ]
            },
            "İnsan ve Diğer Sistemler": {
                "İnsan Fizyolojisi": [
                    "Denetleyici ve Düzenleyici Sistem",
                    "Duyu, Destek ve Hareket Sistemi",
                    "Sindirim, Dolaşım ve Solunum",
                    "Üriner, Üreme ve Gelişim"
                ],
                "Diğer Konular": [
                    "Genden Proteine",
                    "Enerji Dönüşümleri",
                    "Bitki Biyolojisi"
                ]
            }
        },
        "TYT Kimya": {
            "Kimya Bilimi": {
                "Kimya Bilimine Giriş": [
                    "Kimyanın Alt Dalları",
                    "Laboratuvar Güvenlik Kuralları"
                ],
                "Atom ve Periyodik Sistem": [
                    "Atom Modelleri",
                    "Periyodik Sistemin Özellikleri"
                ],
                "Etkileşimler": [
                    "Güçlü Etkileşimler",
                    "Zayıf Etkileşimler"
                ],
                "Maddenin Hâlleri": [
                    "Katı, Sıvı, Gaz, Plazma",
                    "Hal Değişimleri"
                ],
                "Doğa ve Kimya": [
                    "Su ve Hava Kirliliği",
                    "Geri Dönüşüm"
                ]
            },
            "Kimyanın Temel Yasaları": {
                "Kimyanın Temel Kanunları": [
                    "Kütlenin Korunumu",
                    "Sabit ve Katlı Oranlar",
                    "Mol Kavramı"
                ],
                "Karışımlar": [
                    "Homojen ve Heterojen Karışımlar",
                    "Derişim Birimleri"
                ],
                "Asitler, Bazlar ve Tuzlar": [
                    "Asit ve Bazların Özellikleri",
                    "pH Kavramı"
                ],
                "Kimya Her Yerde": [
                    "Polimerler",
                    "Sabun ve Deterjanlar",
                    "İlaçlar, Gıdalar"
                ]
            }
        },
        "TYT Fizik": {
            "Fizik Bilimine Giriş": {
                "Fizik Bilimine Giriş": [
                    "Fiziğin Alt Dalları",
                    "Temel ve Türetilmiş Büyüklükler"
                ],
                "Madde ve Özellikleri": [
                    "Kütle, Hacim, Özkütle",
                    "Adezyon, Kohezyon, Yüzey Gerilimi"
                ]
            },
            "Mekanik ve Enerji": {
                "Hareket ve Kuvvet": [
                    "Konum, Yol, Sürat, Hız",
                    "Newton’ın Hareket Yasaları"
                ],
                "Enerji": [
                    "İş, Güç, Enerji",
                    "Enerjinin Korunumu"
                ]
            },
            "Elektrik ve Basınç": {
                "Isı ve Sıcaklık": [
                    "Sıcaklık ve Isı",
                    "Hal Değişimleri"
                ],
                "Elektrostatik": [
                    "Yük",
                    "Elektriklenme Çeşitleri"
                ],
                "Elektrik ve Manyetizma": [
                    "Elektrik Akımı ve Direnç",
                    "Ohm Yasası",
                    "Manyetizma"
                ],
                "Basınç ve Kaldırma Kuvveti": [
                    "Katı, Sıvı, Gaz Basıncı",
                    "Kaldırma Kuvveti"
                ]
            },
            "Dalga ve Optik": {
                "Dalgalar": [
                    "Dalga Hareketi",
                    "Dalga Çeşitleri",
                    "Yay, Su ve Ses Dalgaları"
                ],
                "Optik": [
                    "Işık ve Gölge",
                    "Yansıma ve Aynalar",
                    "Kırılma ve Mercekler",
                    "Renk"
                ]
            }
        },
        "TYT Felsefe": {
            "Temel Felsefe Konuları": {
                "Felsefe’nin Konusu": [
                    "Tanımı, Alanı, Özellikleri"
                ],
                "Bilgi Felsefesi (Epistemoloji)": [
                    "Bilginin Doğası ve Kaynakları",
                    "Şüphecilik, Rasyonalizm, Empirizm"
                ],
                "Varlık Felsefesi (Ontoloji)": [
                    "Varlığın Ana Maddesi",
                    "İdealizm, Realizm, Materyalizm"
                ],
                "Ahlak Felsefesi (Etik)": [
                    "Ahlaki Eylemin Amacı",
                    "Evrensel Ahlak Yasası",
                    "Hedonizm, Utilitarizm, Egoizm"
                ],
                "Sanat ve Din Felsefesi": [
                    "Sanatın Doğası (Estetik)",
                    "Din Felsefesi"
                ],
                "Siyaset ve Bilim Felsefesi": [
                    "Devletin Amacı (Siyaset Felsefesi)",
                    "Bilimin Doğası (Bilim Felsefesi)"
                ]
            },
            "Felsefe Tarihi Dönemleri": {
                "İlk ve Orta Çağ Felsefesi": [
                    "İlk Çağ Filozofları (Sokrates, Platon)",
                    "Orta Çağ Felsefesi (İslam ve Hristiyan Felsefesi)"
                ],
                "Modern ve Çağdaş Felsefe": [
                    "Rönesans ve Erken Modern Felsefe",
                    "Aydınlanma ve Modern Felsefe",
                    "20. Yüzyıl Felsefesi"
                ]
            }
        },
        "TYT Din Kültürü": {
            "İnanç ve İbadet": {
                "Bilgi ve İnanç": ["İslam’da Bilginin Kaynakları", "İnancın Önemi"],
                "Din ve İslam": ["Din Kavramı", "İslam’ın Temel Özellikleri"],
                "İslam ve İbadet": ["İbadetin Yeri ve Önemi", "Başlıca İbadetler"]
            },
            "Ahlak ve Değerler": {
                "Gençlik ve Değerler": ["Gençlerin Din ve Ahlak Eğitimi"],
                "Ahlaki Tutum ve Davranışlar": ["İslam Ahlakının Temel İlkeleri"]
            },
            "İslam Düşüncesi": {
                "İslam Medeniyeti": ["Gelişimi ve Katkıları"],
                "Allah İnancı": ["Allah’ın Varlığı ve Sıfatları", "Kur’an’da İnsan"],
                "Hz. Muhammed ve Gençlik": ["Bir Genç Olarak Hz. Muhammed", "Genç Sahabiler"],
                "Din ve Toplumsal Hayat": [
                    "Din ve Aile",
                    "Din, Kültür ve Sanat",
                    "Din ve Çevre",
                    "Din ve Sosyal Adalet"
                ],
                "İslam Düşüncesinde Yorumlar": ["Mezhepler (İtikadi, Siyasi, Fıkhi)"]
            }
        },
        "AYT Matematik": {
            "Temel ve İleri Fonksiyonlar": {
                "Fonksiyonlar": ["Fonksiyonlar Genel"],
                "Parabol": ["Parabol Genel"],
                "İkinci Dereceden Fonksiyonlar ve Grafikleri": ["İkinci Dereceden Fonksiyonlar Genel"],
                "Trigonometrik Fonksiyonlar (Trigonometri)": ["Trigonometri Genel"],
                "Üstel Fonksiyonlar – Logaritmik Fonksiyonlar": ["Üstel ve Logaritmik Fonksiyonlar Genel"]
            },
            "Cebir": {
                "Polinomlar": ["Polinomlar Genel"],
                "İkinci Dereceden Denklemler": ["İkinci Dereceden Denklemler Genel"]
            },
            "Kalkülüs (Analiz)": {
                "Limit – Süreklilik": ["Limit ve Süreklilik Genel"],
                "Türev": ["Türev Genel"],
                "Belirsiz İntegral": ["Belirsiz İntegral Genel"],
                "Belirli İntegral": ["Belirli İntegral Genel"]
            },
            "Diğer İleri Konular": {
                "Permütasyon – Kombinasyon – Olasılık": ["Permütasyon, Kombinasyon ve Olasılık Genel"],
                "Diziler": ["Diziler Genel"]
            }
        },
        "AYT Geometri": {
            "Açılar ve Üçgenler": {
                "Açılar ve Üçgenler": [
                    "Doğruda ve Üçgende Açılar",
                    "Dik Üçgen",
                    "Özel Üçgenler (30-60-90, 45-45-90 vb.)",
                    "İkizkenar ve Eşkenar Üçgen",
                    "Açı Kenar Bağıntıları"
                ],
                "Üçgende Yardımcı Elemanlar": [
                    "Üçgende Eşlik ve Benzerlik",
                    "Üçgende Açıortay",
                    "Üçgende Kenarortay",
                    "Üçgende Alan"
                ]
            },
            "Çokgenler ve Dörtgenler": {
                "Çokgenler": ["Çokgenler Genel"],
                "Dörtgenler": [
                    "Dörtgenler",
                    "Yamuk",
                    "Paralelkenar",
                    "Eşkenar Dörtgen",
                    "Deltoid",
                    "Dikdörtgen",
                    "Kare"
                ]
            },
            "Çember ve Analitik Geometri": {
                "Çember ve Daire": ["Çember ve Daire Genel"],
                "Analitik Geometri": [
                    "Doğrunun Analitik İncelenmesi"
                ]
            },
            "Katı Cisimler": {
                "Katı Cisimler": [
                    "Dikdörtgenler Prizması",
                    "Küp",
                    "Silindir",
                    "Piramit",
                    "Koni",
                    "Küre"
                ]
            }
        },
        "AYT Türk Dili ve Edebiyatı": {
            "Temel Edebiyat Bilgisi": {
                "Giriş ve Kavramlar": [
                    "Edebiyatın Tanımı ve Akımlarla İlişkisi"
                ],
                "Edebi Türler": [
                    "Hikaye",
                    "Şiir",
                    "Roman",
                    "Tiyatro",
                    "Biyografi/Otobiyografi",
                    "Mektup/E-posta",
                    "Günlük/Blog",
                    "Masal/Fabl",
                    "Haber Metni",
                    "Gezi Yazısı",
                    "Anı (Hatıra)",
                    "Makale",
                    "Sohbet ve Fıkra",
                    "Eleştiri",
                    "Mülakat/Röportaj",
                    "Deneme",
                    "Söylev (Nutuk)"
                ]
            },
            "Şiir ve Sanat Bilgisi": {
                "Şiir Bilgisi": [
                    "Şiirin Temel Unsurları",
                    "Nazım Birimleri, Ölçü ve Uyak"
                ],
                "Söz Sanatları": [
                    "Teşbih, İstiare, Mecazımürsel, Teşhis vb."
                ]
            },
            "Türk Edebiyatı Dönemleri": {
                "İslamiyet Öncesi ve Geçiş Dönemi": [
                    "Destan, Koşuk, Sagu, Sav",
                    "Geçiş Dönemi Eserleri"
                ],
                "Halk Edebiyatı": [
                    "Anonim, Aşık Tarzı, Dinî-Tasavvufî Halk Edebiyatı"
                ],
                "Divan Edebiyatı": [
                    "Nazım Biçimleri",
                    "Önemli Şair ve Yazarlar"
                ],
                "Tanzimat Edebiyatı": [
                    "Birinci ve İkinci Dönem Tanzimat"
                ],
                "Servet-i Fünun ve Fecr-i Ati": ["Servet-i Fünun ve Fecr-i Ati Genel"],
                "Milli Edebiyat": ["Milli Edebiyat Genel"],
                "Cumhuriyet Dönemi Edebiyatı": [
                    "Cumhuriyet Dönemi Şiir",
                    "Cumhuriyet Dönemi Hikaye ve Roman"
                ]
            },
            "Dünya Edebiyatı ve Akımlar": {
                "Edebi Akımlar": [
                    "Klasisizm, Romantizm, Realizm, Parnasizm vb."
                ],
                "Dünya Edebiyatı": [
                    "Önemli Eserler ve Yazarları"
                ]
            }
        },
        "AYT Tarih": {
            "İlk Çağ ve Türk İslam Tarihi": {
                "Tarih Bilimi": ["Tarih Biliminin Tanımı ve Yardımcı Bilim Dalları"],
                "İlk Uygarlıklar": ["Uygarlığın Doğuşu ve İlk Uygarlıklar"],
                "İlk Türk Devletleri": ["İlk Türk Devletlerinin Siyasi ve Sosyal Yapıları"],
                "İslam Tarihi ve Uygarlığı": ["İslamiyet'in Doğuşu ve Gelişimi"],
                "Türk İslam Devletleri": ["Karahanlılar, Gazneliler, Büyük Selçuklu"],
                "Türkiye Tarihi": ["Anadolu'nun Türkleşmesi ve Anadolu Selçuklu"]
            },
            "Osmanlı ve Dünya Tarihi": {
                "Beylikten Devlete Osmanlı": ["Osmanlı'nın Kuruluşu ve İlk Sultanlar"],
                "Dünya Gücü Osmanlı": ["Yükselme Dönemi ve Fetihler"],
                "Arayış Yılları": ["Duraklama Dönemi ve Islahat Hareketleri"],
                "En Uzun Yüzyıl (19. Yüzyıl)": ["Dağılma Dönemi ve Fikir Akımları"],
                "Değişim Çağında Avrupa ve Osmanlı": ["Avrupa'daki Gelişmelerin Osmanlı'ya Etkileri"]
            },
            "İnkılap Tarihi": {
                "20. Yüzyıl Başlarında Osmanlı ve Dünya": ["I. Dünya Savaşı ve Osmanlı'nın Son Yılları"],
                "Milli Mücadele": ["Mondros, İşgaller, Cemiyetler, Kongreler", "Cepheler ve Lozan"],
                "Atatürkçülük ve Türk İnkılabı": ["Atatürk İlke ve İnkılapları", "Cumhuriyet Dönemi Yenilikleri"]
            },
            "Yakın Dünya Tarihi": {
                "İki Savaş Arası Dönem": ["Atatürk Dönemi Türk Dış Politikası"],
                "II. Dünya Savaşı": ["Nedenleri, Sonuçları ve Türkiye'nin Tutumu"],
                "Soğuk Savaş Dönemi": ["Bloklar ve Türkiye"],
                "Toplumsal Devrim Çağı": ["Küreselleşme ve Teknolojik Gelişmeler"]
            }
        },
        "AYT Coğrafya": {
            "Doğal Sistemler": {
                "Doğa ve İnsan": ["İnsan-Doğa Etkileşimi ve Çevresel Sorunlar"],
                "Dünya ve Konum": ["Dünya’nın Hareketleri", "Coğrafi Konum", "Harita Bilgisi"],
                "İklim Bilgisi": ["İklim Elemanları", "İklim Tipleri"],
                "Yerin Şekillenmesi": ["İç ve Dış Kuvvetler"],
                "Ekosistemler ve Biyomlar": ["Doğanın Varlıkları", "Ekosistemlerin İşleyişi"]
            },
            "Beşeri ve Ekonomik Sistemler": {
                "Nüfus ve Yerleşme": ["Nüfusun Gelişimi, Dağılışı ve Göçler"],
                "Ekonomik Faaliyetler": ["Geçim Tarzları ve Dağılışı"]
            },
            "Türkiye Coğrafyası": {
                "Türkiye": [
                    "Türkiye’nin Yeryüzü Şekilleri ve İklimi",
                    "Doğal Varlıkları",
                    "Yerleşme, Nüfus ve Göç"
                ]
            },
            "Küresel ve Çevresel Konular": {
                "Bölgeler ve Ülkeler": ["Bölge Türleri", "Uluslararası Etkileşimler"],
                "Çevre ve Toplum": ["Çevresel Sorunlar", "Doğal Afetler"]
            }
        },
        "AYT Fizik": {
            "Mekanik ve Dinamik": {
                "Kuvvet ve Hareket": [
                    "Vektörler",
                    "Bağıl Hareket",
                    "Newton'un Hareket Yasaları",
                    "İki Boyutta Hareket"
                ],
                "Enerji ve Momentum": ["İtme ve Çizgisel Momentum", "Tork", "Denge", "Basit Makineler"],
                "Çembersel Hareket": ["Düzgün Çembersel Hareket", "Dönerek Öteleme", "Açısal Momentum"],
                "Kütle Çekim ve Harmonik Hareket": ["Kütle Çekim Kuvveti", "Kepler Kanunları", "Basit Harmonik Hareket"]
            },
            "Elektrik ve Modern Fizik": {
                "Elektrik ve Manyetizma": [
                    "Elektriksel Kuvvet ve Alan",
                    "Elektriksel Potansiyel ve Sığa",
                    "Manyetizma ve Elektromanyetik İndüksiyon"
                ],
                "Dalga Mekaniği": ["Dalgalarda Kırınım, Girişim ve Doppler"],
                "Modern Fizik": [
                    "Atom Fiziğine Giriş ve Radyoaktivite",
                    "Modern Fizik Temel Kavramları",
                    "Modern Fiziğin Uygulamaları"
                ]
            }
        },
        "AYT Kimya": {
            "Kimyanın Temel Kanunları": {
                "Kimya Bilimi": ["Kimyanın Temel Kavramları"],
                "Atom ve Periyodik Sistem": ["Atomun Yapısı ve Periyodik Tablo"],
                "Kimyasal Etkileşimler": ["Türler Arası Etkileşimler"],
                "Maddenin Halleri": ["Maddenin Halleri Genel"]
            },
            "Çözeltiler ve Termodinamik": {
                "Karışımlar": ["Homojen ve Heterojen Karışımlar", "Derişim Birimleri"],
                "Asitler, Bazlar ve Tuzlar": ["Asitler, Bazlar ve Tuzlar Genel"],
                "Kimya Her Yerde": ["Kimya Her Yerde Genel"],
                "Sıvı Çözeltiler ve Çözünürlük": ["Derişim Birimleri", "Koligatif Özellikler"]
            },
            "İleri Kimya": {
                "Modern Atom Teorisi": ["Kuantum Sayıları ve Elektron Dizilimi"],
                "Gazlar": ["Gaz Yasaları ve İdeal Gaz Denklemi"],
                "Kimyasal Tepkimelerde Enerji": ["Entalpi ve Hess Yasası"],
                "Kimyasal Tepkimelerde Hız ve Denge": ["Tepkime Hızı ve Denge"],
                "Kimya ve Elektrik": ["Redoks Tepkimeleri", "Piller", "Elektroliz"]
            },
            "Organik Kimya": {
                "Karbon Kimyasına Giriş": ["Karbonun Özellikleri"],
                "Organik Bileşikler": ["Fonksiyonel Gruplar", "Hidrokarbonlar"],
                "Enerji Kaynakları": ["Alternatif Enerji Kaynakları"]
            }
        }
    }
    
    mastery_seviyeleri = ["Hiç Bilmiyor", "Temel Bilgi", "Orta Seviye", "İyi Seviye", "Uzman (Derece) Seviye"]
    
    # Yeni bir konu ekleme arayüzü
    st.markdown('<div class="section-header">Konu Ekle</div>', unsafe_allow_html=True)
    
    # 1. Adım: Ders seçimi
    dersler = list(yks_konulari.keys())
    secilen_ders = st.selectbox("Ders Seç", dersler, key="ders_add")
    
    # 2. Adım: Konu alanı seçimi
    konu_alanlari = []
    if secilen_ders:
        konu_alanlari = list(yks_konulari[secilen_ders].keys())
        secilen_konu_alani = st.selectbox("Konu Alanı Seç", konu_alanlari, key="konu_alani_add")
    else:
        secilen_konu_alani = None
    
    # 3. Adım: Alt konu seçimi
    alt_konu_anahtarlari = []
    if secilen_konu_alani:
        alt_konu_anahtarlari = list(yks_konulari[secilen_ders][secilen_konu_alani].keys())
        secilen_alt_konu = st.selectbox("Alt Konu Seç", alt_konu_anahtarlari, key="alt_konu_add")
    else:
        secilen_alt_konu = None
    
    # 4. Adım: Daha alt konu seçimi
    daha_alt_konular = []
    if secilen_alt_konu:
        daha_alt_konular = yks_konulari[secilen_ders][secilen_konu_alani][secilen_alt_konu]
        secilen_daha_alt_konu = st.selectbox("Daha Alt Konu Seç", daha_alt_konular, key="daha_alt_konu_add")
    else:
        secilen_daha_alt_konu = None
    
    # 5. Adım: Seviye Belirleme
    if secilen_daha_alt_konu:
        konu_key = f"{secilen_ders}>{secilen_konu_alani}>{secilen_alt_konu}>{secilen_daha_alt_konu}"
        
        # Konu zaten takip listesinde yoksa ekle ve varsayılan seviye ata
        if konu_key not in st.session_state.konu_durumu:
            st.session_state.konu_durumu[konu_key] = "Hiç Bilmiyor"
            st.success(f"**{konu_key}** takibe eklendi. Şimdi seviyesini belirleyebilirsiniz.")
        
        mevcut_seviye = st.session_state.konu_durumu.get(konu_key, "Hiç Bilmiyor")
        
        st.markdown("---")
        st.markdown(f"**{konu_key}** için seviye belirle:")
        
        yeni_seviye = st.select_slider(
            label="",
            options=mastery_seviyeleri,
            value=mevcut_seviye,
            key=f"slider_{konu_key}"
        )
        
        if yeni_seviye != mevcut_seviye:
            st.session_state.konu_durumu[konu_key] = yeni_seviye
            st.success(f"**{konu_key}** seviyesi **{yeni_seviye}** olarak güncellendi!")
    else:
        st.info("Lütfen bir alt konu seçerek seviye belirleme alanını görünür yapın.")
def derece_performans_analizi(tyt_net, ayt_net, bilgi):
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
    hedef_netleri = {
        'Sayısal': {1: 180, 100: 170, 1000: 150, 10000: 120, 50000: 90},
        'Eşit Ağırlık': {1: 175, 100: 165, 1000: 145, 10000: 115, 50000: 85},
        'Sözel': {1: 170, 100: 160, 1000: 140, 10000: 110, 50000: 80}
    }
    
    alan_netleri = hedef_netleri.get(alan, hedef_netleri['Sayısal'])
    
    sıralama_listesi = sorted(alan_netleri.keys())
    for i in range(len(sıralama_listesi)-1):
        if sıralama_listesi[i] <= sıralama <= sıralama_listesi[i+1]:
            x1, x2 = sıralama_listesi[i], sıralama_listesi[i+1]
            y1, y2 = alan_netleri[x1], alan_netleri[x2]
            return y1 + (y2-y1) * (sıralama-x1) / (x2-x1)
    
    return 100

def derece_öneriler():
    st.markdown('<div class="section-header">💡 Derece Öğrencisi Önerileri</div>', unsafe_allow_html=True)
    
    bilgi = st.session_state.öğrenci_bilgisi
    tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
    strateji = DERECE_STRATEJİLERİ[bilgi['sınıf']]
    
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
        motivasyon_mesajları = [
            f"🌟 {bilgi['isim']}, sen {bilgi['hedef_bölüm']} için doğmuşsun!",
            f"🏆 {bilgi['hedef_sıralama']}. sıralama çok yakın!",
            "💪 Her gün biraz daha güçleniyorsun!",
            f"🚀 {tema['icon']} Bu hedef tam sana göre!",
            "⭐ Derece öğrencileri böyle çalışır!"
        ]
        
        günün_motivasyonu = random.choice(motivasyon_mesajları)
        
        st.markdown(f'''
        <div class="warning-card">
            <h3>💝 Günün Derece Motivasyonu</h3>
            <p style="font-size: 1.2rem; font-weight: bold;">{günün_motivasyonu}</p>
            <small>Motivasyon Puanın: {st.session_state.motivasyon_puanı}/100</small>
        </div>
        ''', unsafe_allow_html=True)
        
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
def psikolojik_destek_sayfası():
    st.markdown('<div class="section-header">🧠 Verimli Öğrenme Teknikleri</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.1rem;">Bilgiyi kalıcı hale getirmek ve öğrenme verimini artırmak için bu etkili teknikleri kullanabilirsin.</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Her bir tekniği ayrı bir blokta göster
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<p style='font-size: 3rem;'>🧠</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("### Feynman Tekniği")
        st.markdown("Konuyu 5 yaşındaki bir çocuğa anlatabilecek kadar basitleştir. Bu, konuyu ne kadar iyi anladığını test eder.")
        st.button("Dene →", key="feynman")

    st.markdown("---")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<p style='font-size: 3rem;'>🎯</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("### Aktif Hatırlama (Active Recall)")
        st.markdown("Kitaba veya deftere bakmadan konuyu hatırlamaya çalış. Beynini zorlayarak bilgiyi daha derinlemesine işlersin.")
        st.button("Başla →", key="active_recall")

    st.markdown("---")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<p style='font-size: 3rem;'>🔄</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("### Interleaving (Karışık Çalışma)")
        st.markdown("Farklı konuları veya dersleri art arda çalış. Bu yöntem, beynin bilgiyi ayırt etme ve bağlantı kurma yeteneğini güçlendirir.")
        st.button("Uygula →", key="interleaving")

    st.markdown("---")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<p style='font-size: 3rem;'>🎨</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("### Mind Mapping (Zihin Haritası)")
        st.markdown("Konuları anahtar kelimeler ve görsellerle bir ağaç gibi organize et. Beyin, bu görsel bağlantıları daha kolay hatırlar.")
        st.button("Oluştur →", key="mind_mapping")

    st.markdown("---")

    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<p style='font-size: 3rem;'>📝</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("### Cornell Not Alma Tekniği")
        st.markdown("Sayfayı üç bölüme ayırarak not al. Bu sistematik teknik, hem öğrenmeyi hem de tekrarı kolaylaştırır.")
        st.button("Öğren →", key="cornell")

    st.markdown("---")
    
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("<p style='font-size: 3rem;'>⚡</p>", unsafe_allow_html=True)
    with col2:
        st.markdown("### Blitz Tekrar")
        st.markdown("Öğrendiğin bir konuyu kısa süre sonra (örneğin 24 saat içinde) hızlıca tekrar et. Bu, bilginin uzun süreli hafızaya geçişini sağlar.")
        st.button("Hızlan →", key="blitz")
    st.markdown('<div class="section-header">💡 Psikolojik Destek ve Motivasyon</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.1rem;">Sınav sürecinde psikolojik sağlığını korumak, başarının anahtarlarından biridir. İşte bu zorlu yolda sana destek olacak bazı ipuçları:</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🧠 Zihinsel Hazırlık ve Odaklanma")
    st.write("""
    **Sınav Kaygısıyla Başa Çıkma:**
    Sınav kaygısı, her öğrencinin yaşadığı doğal bir duygudur. Önemli olan bu kaygıyı yönetebilmektir. Nefes egzersizleri yaparak veya kısa molalar vererek zihnini dinlendirebilirsin.
    """)
    st.write("""
    **Olumlu Düşünce Yapısı Geliştirme:**
    Kendine güvenmek, motivasyonunu artırır. "Yapabilirim", "Başaracağım" gibi olumlu ifadeleri sıkça tekrarla. Başarısızlıkları birer öğrenme fırsatı olarak gör.
    """)
    st.write("""
    **Hedef Belirleme:**
    Gerçekçi ve ulaşılabilir hedefler belirlemek, motivasyonunu yüksek tutar. Büyük hedefini küçük parçalara bölerek her başarıda kendini ödüllendir.
    """)
    
    st.markdown("---")

    st.markdown("### 🏃🏻‍♀️ Fiziksel Sağlık ve Dinlenme")
    st.write("""
    **Düzenli Uyku:**
    Uyku, beynin öğrendiklerini pekiştirdiği en önemli zamandır. Günde 7-8 saat uyumaya özen göster. Yorgun bir zihinle çalışmak verimini düşürür.
    """)
    st.write("""
    **Sağlıklı Beslenme:**
    Beyin, doğru yakıtla çalışır. Dengeli ve düzenli beslenerek enerjini yüksek tut. Şekerli ve işlenmiş gıdalardan uzak durmaya çalış.
    """)
    st.write("""
    **Egzersiz Yapma:**
    Düzenli egzersiz, stresi azaltır ve ruh halini iyileştirir. Günde 20-30 dakika yürüyüş yapmak bile zihnini tazeleyebilir.
    """)
    
    st.markdown("---")

    st.markdown("### 🧘🏻‍♀️ Duygusal Destek ve Stratejiler")
    st.write("""
    **Destek Çevresi Oluşturma:**
    Ailen, arkadaşların ve öğretmenlerinle konuşmak, yükünü hafifletebilir. Duygularını paylaşmaktan çekinme.
    """)
    st.write("""
    **Kendine Karşı Nazik Olma:**
    Her zaman mükemmel olmak zorunda değilsin. Hata yaptığında kendine kızmak yerine, bu durumdan ders çıkar. Mola vermek, kendini şımartmak için fırsat yarat.
    """)
    st.write("""
    **Zaman Yönetimi:**
    Etkili bir program oluşturmak, kontrol hissini artırır ve stresi azaltır. Programına dinlenme molalarını ve hobilerini de eklemeyi unutma.
    """)
    
    st.markdown("---")
    st.info("Unutma, bu süreçte yalnız değilsin. Kendine iyi bakmak, en az ders çalışmak kadar önemlidir. Başarılar dileriz!")
def pomodoro_zamanlayıcısı_sayfası():
    
   
    st.markdown('<div class="section-header">⏰ Akıllı Çalışma Zamanlayıcısı</div>', unsafe_allow_html=True)
    
    # Özel CSS ile fotoğraftaki tasarımı oluşturma
    st.markdown("""
    <style>
    .pomodoro-container {
        background: #2c3e50;
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem auto;
        max-width: 400px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .timer-display {
        font-size: 3.5rem;
        font-weight: bold;
        margin: 1rem 0;
        color: #ecf0f1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    .mode-display {
        font-size: 1.2rem;
        margin-bottom: 1.5rem;
        color: #bdc3c7;
    }
    .pomodoro-button {
        background: #34495e;
        border: none;
        border-radius: 50px;
        padding: 10px 20px;
        margin: 0.5rem;
        color: white;
        font-weight: bold;
        cursor: pointer;
        transition: all 0.3s ease;
        width: 120px;
    }
    .pomodoro-button:hover {
        background: #3498db;
        transform: translateY(-2px);
    }
    .mode-selector {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    .mode-option {
        padding: 8px 15px;
        border-radius: 20px;
        background: #34495e;
        cursor: pointer;
        transition: all 0.3s ease;
        border: none;
        color: white;
        font-size: 0.9rem;
    }
    .mode-option.active {
        background: #3498db;
    }
    .stats-display {
        margin-top: 1.5rem;
        padding: 1rem;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # POMODORO modları ve süreleri - Türkçe anahtarlarla
    POMODORO_MODES = {
        'Pomodoro': {'label': 'Pomodoro (25dk)', 'time': 25 * 60, 'color': '#e74c3c'},
        'Kısa Mola': {'label': 'Kısa Mola (5dk)', 'time': 5 * 60, 'color': '#2ecc71'},
        'Uzun Mola': {'label': 'Uzun Mola (15dk)', 'time': 15 * 60, 'color': '#9b59b6'},
        'Derin Odak': {'label': 'Derin Odak (50dk)', 'time': 50 * 60, 'color': '#f39c12'}
    }
    
    # Session state'i başlat - Varsayılan modu kontrol et
    if 'pomodoro_mode' not in st.session_state:
        st.session_state.pomodoro_mode = 'Pomodoro'
    
    # Eğer mevcut mod tanımlı değilse, varsayılan moda dön
    if st.session_state.pomodoro_mode not in POMODORO_MODES:
        st.session_state.pomodoro_mode = 'Pomodoro'
    
    if 'pomodoro_time' not in st.session_state:
        st.session_state.pomodoro_time = POMODORO_MODES[st.session_state.pomodoro_mode]['time']
    
    if 'pomodoro_running' not in st.session_state:
        st.session_state.pomodoro_running = False
    
    if 'pomodoro_count' not in st.session_state:
        st.session_state.pomodoro_count = 0
    
    if 'pomodoro_goal' not in st.session_state:
        st.session_state.pomodoro_goal = 8

    # Zamanlayıcı fonksiyonları
    def start_timer():
        st.session_state.pomodoro_running = True

    def stop_timer():
        st.session_state.pomodoro_running = False

    def reset_timer():
        st.session_state.pomodoro_running = False
        st.session_state.pomodoro_time = POMODORO_MODES[st.session_state.pomodoro_mode]['time']

    def set_mode(mode):
        if mode in POMODORO_MODES:
            st.session_state.pomodoro_mode = mode
            st.session_state.pomodoro_time = POMODORO_MODES[mode]['time']
            st.session_state.pomodoro_running = False
        else:
            st.error("Geçersiz mod seçildi!")

    # Zamanlayıcıyı güncelleme
    if st.session_state.pomodoro_running:
        time.sleep(1)
        st.session_state.pomodoro_time -= 1
        
        # Süre bittiğinde
        if st.session_state.pomodoro_time <= 0:
            st.session_state.pomodoro_running = False
            
            # Pomodoro tamamlandıysa sayacı artır
            if st.session_state.pomodoro_mode == 'Pomodoro':
                st.session_state.pomodoro_count += 1
                st.balloons()
                st.success("Pomodoro tamamlandı! Bir mola zamanı!")
            
            # Otomatik olarak bir sonraki moda geç
            if st.session_state.pomodoro_mode == 'Pomodoro':
                if st.session_state.pomodoro_count % 4 == 0:
                    set_mode('Uzun Mola')
                else:
                    set_mode('Kısa Mola')
            else:
                set_mode('Pomodoro')
            
            st.session_state.pomodoro_running = True
            st.rerun()
    
    # Zamanlayıcı arayüzü
    st.markdown('<div class="pomodoro-container">', unsafe_allow_html=True)
    
    # Zaman gösterimi
    minutes = st.session_state.pomodoro_time // 60
    seconds = st.session_state.pomodoro_time % 60
    time_str = f"{minutes:02d}:{seconds:02d}"
    
    st.markdown(f'<div class="timer-display">{time_str}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="mode-display">{POMODORO_MODES[st.session_state.pomodoro_mode]["label"]}</div>', unsafe_allow_html=True)
    
    # Kontrol butonları
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Başla", use_container_width=True, key="start_button") and not st.session_state.pomodoro_running:
            start_timer()
            st.rerun()
    
    with col2:
        if st.button("⏸️ Durdur", use_container_width=True, key="stop_button") and st.session_state.pomodoro_running:
            stop_timer()
            st.rerun()
    
    with col3:
        if st.button("⏹️ Sıfırla", use_container_width=True, key="reset_button"):
            reset_timer()
            st.rerun()
    
    # Mod seçici - Streamlit butonlarıyla
    st.markdown("**Mod Seçin:**")
    mode_cols = st.columns(4)
    
    modes = list(POMODORO_MODES.keys())
    for i, mode in enumerate(modes):
        with mode_cols[i]:
            if st.button(POMODORO_MODES[mode]["label"], key=f"mode_{mode}", 
                        use_container_width=True,
                        type="primary" if st.session_state.pomodoro_mode == mode else "secondary"):
                set_mode(mode)
                st.rerun()
    
    # İlerleme istatistikleri
    st.markdown('<div class="stats-display">', unsafe_allow_html=True)
    st.markdown(f"**Bugünkü Pomodoro**")
    progress = min(1.0, st.session_state.pomodoro_count / st.session_state.pomodoro_goal)
    st.markdown(f"{st.session_state.pomodoro_count}/{st.session_state.pomodoro_goal}")
    st.progress(progress)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
def main():
    initialize_session_state()
    
    if not st.session_state.giriş_yapıldı:
        login_sayfası()
    else:
        if not st.session_state.program_oluşturuldu:
            öğrenci_bilgi_formu()
            return

        bilgi = st.session_state.öğrenci_bilgisi
        tema_css = tema_css_oluştur(bilgi['bölüm_kategori'])
        st.markdown(tema_css, unsafe_allow_html=True)
        
        tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
        
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
            
            menu = st.selectbox("📋 Derece Menüsü", [
                "🏠 Ana Sayfa",
                "🧠 Psikolojik Taktiklerim",
                "⏰ Pomodoro Zamanlayıcısı",
                "📅 Günlük Program", 
                "🎯 YKS Konuların Burda",
                "📈 Deneme Analizi",
                "💡 Derece Önerileri",
                "📊 Performans İstatistikleri"
            ])
            
            if st.session_state.konu_durumu:
                uzman_konular = sum(1 for seviye in st.session_state.konu_durumu.values() 
                                  if "Uzman" in seviye)
                st.metric("🏆 Uzman Konular", uzman_konular)
            
            if st.session_state.deneme_sonuçları:
                son_net = st.session_state.deneme_sonuçları[-1]['tyt_net']
                st.metric("📈 Son TYT Net", f"{son_net:.1f}")
            
            st.markdown("---")
            if st.button("🔄 Sistemi Sıfırla"):
                for key in st.session_state.keys():
                    del st.session_state[key]
                st.rerun()
        
        if menu == "🏠 Ana Sayfa":
           
            
            st.markdown(f'''
            <div class="hero-section">
                <div class="main-header">{tema['icon']} {bilgi['isim']}'in Derece Yolculuğu</div>
                <p style="font-size: 1.3rem;">"{bilgi['hedef_bölüm']}" hedefine giden yolda!</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Mastery seviyelerini ve önerileri tanımla
            mastery_seviyeleri = {
                "Hiç Bilmiyor": 0,
                "Temel Bilgi": 25,
                "Orta Seviye": 50,
                "İyi Seviye": 75,
                "Uzman (Derece) Seviye": 100
            }

            oneriler = {
                "Hiç Bilmiyor": "Bu konuyu öğrenmeye başlamalısın! Temelini sağlamlaştırmak için 50-75 arası basit soru çözerek konuya giriş yap.",
                "Temel Bilgi": "Konuyu orta seviyeye taşımak için konu anlatımı videoları izle ve en az 100-150 arası orta düzey soru çöz. Yanlışlarını mutlaka not al.",
                "Orta Seviye": "İyi seviyeye çıkmak için farklı kaynaklardan zor sorular çözerek kendini dene. Bu konudan deneme sınavı sorularına ağırlık ver ve 200'den fazla soruyla pekiştir.",
                "İyi Seviye": "Artık bir uzmansın! Bu konuyu tam anlamıyla oturtmak için çıkmış sorular ve efsane zorlayıcı sorularla pratik yap. Sadece denemelerde karşına çıkan sorulara odaklan.",
                "Uzman (Derece) Seviye": "Tebrikler! Bu konu tamamen cebinde. Sadece tekrar amaçlı deneme çözerken karşına çıkan soruları kontrol etmen yeterli. Yeni konulara yönelerek zamanını daha verimli kullan."
            }
            
            # --- Hızlı İstatistikler ---
            st.markdown('<div class="section-header">🚀 Hızlı İstatistikler</div>', unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                konu_sayısı = len(st.session_state.konu_durumu) if 'konu_durumu' in st.session_state else 0
                st.markdown(f'''
                <div class="metric-card">
                    <h3>📚 Toplam Konu</h3>
                    <h2 style="color: {tema['renk']};">{konu_sayısı}</h2>
                </div>
                ''', unsafe_allow_html=True)
            
            with col2:
                deneme_sayısı = len(st.session_state.deneme_sonuçları) if 'deneme_sonuçları' in st.session_state else 0
                st.markdown(f'''
                <div class="metric-card">
                    <h3>📝 Toplam Deneme</h3>
                    <h2 style="color: {tema['renk']};">{deneme_sayısı}</h2>
                </div>
                ''', unsafe_allow_html=True)
            
            with col3:
                çalışma_günü = len(st.session_state.günlük_çalışma_kayıtları) if 'günlük_çalışma_kayıtları' in st.session_state else 0
                st.markdown(f'''
                <div class="metric-card">
                    <h3>📅 Çalışma Günü</h3>
                    <h2 style="color: {tema['renk']};">{çalışma_günü}</h2>
                </div>
                ''', unsafe_allow_html=True)
            
            with col4:
                motivasyon = st.session_state.motivasyon_puanı if 'motivasyon_puanı' in st.session_state else 0
                st.markdown(f'''
                <div class="metric-card">
                    <h3>💪 Motivasyon</h3>
                    <h2 style="color: {tema['renk']};">{motivasyon}%</h2>
                </div>
                ''', unsafe_allow_html=True)

            # --- Konu Tamamlama Analizi ---
            st.markdown('<div class="section-header">📈 Konu Tamamlama Analizi</div>', unsafe_allow_html=True)
            
            if 'konu_durumu' in st.session_state and st.session_state.konu_durumu:
                
                # Verileri ders bazında grupla
                ders_seviye_sayilari = {}
                konu_detaylari = {}
                
                # Ders bazında bitirme yüzdesi için yeni sözlük
                ders_bitirme_yüzdeleri = {}
                
                # Puanlama sistemi
                puanlar = {
                    "Hiç Bilmiyor": 0,
                    "Temel Bilgi": 1,
                    "Orta Seviye": 2,
                    "İyi Seviye": 3,
                    "Uzman (Derece) Seviye": 4
                }

                for anahtar, seviye in st.session_state.konu_durumu.items():
                    parcalar = anahtar.split('>') 
                    if len(parcalar) >= 4:
                        ders = parcalar[0].strip()
                        konu_adı = " > ".join(parcalar[1:]).strip() 
                    else:
                        continue 
                    
                    if ders not in ders_seviye_sayilari:
                        ders_seviye_sayilari[ders] = {s: 0 for s in mastery_seviyeleri.keys()}
                    
                    if ders not in konu_detaylari:
                        konu_detaylari[ders] = []
                    
                    ders_seviye_sayilari[ders][seviye] += 1
                    konu_detaylari[ders].append({"konu": konu_adı, "seviye": seviye})

                    # Ders bazlı puanlama için
                    if ders not in ders_bitirme_yüzdeleri:
                        ders_bitirme_yüzdeleri[ders] = {"toplam_puan": 0, "konu_sayısı": 0}
                    
                    ders_bitirme_yüzdeleri[ders]["toplam_puan"] += puanlar.get(seviye, 0)
                    ders_bitirme_yüzdeleri[ders]["konu_sayısı"] += 1


                for ders, seviye_sayilari in ders_seviye_sayilari.items():
                    toplam_konu = sum(seviye_sayilari.values())
                    
                    if toplam_konu == 0:
                        continue

                    # Genel bitirme yüzdesini hesapla
                    toplam_puan = ders_bitirme_yüzdeleri[ders]["toplam_puan"]
                    maksimum_puan = ders_bitirme_yüzdeleri[ders]["konu_sayısı"] * 4 # Her konu için maksimum puan 4
                    bitirme_yuzdesi = int((toplam_puan / maksimum_puan) * 100) if maksimum_puan > 0 else 0
                        
                    st.markdown(f"### {ders} Genel Durumu")
                    st.markdown(f"**Genel Bitirme Yüzdesi:** `{bitirme_yuzdesi}%`")
                    st.progress(bitirme_yuzdesi / 100)

                    # Yüzdelik dağılımı DataFrame'e dönüştür
                    yuzdeler_df = pd.DataFrame(seviye_sayilari.items(), columns=['Seviye', 'Sayi'])
                    yuzdeler_df['Yüzde'] = yuzdeler_df['Sayi'] / toplam_konu
                    
                    # Genel ders durumu için dairesel (donut) grafik
                    fig_genel = px.pie(yuzdeler_df,
                                 values='Sayi',
                                 names='Seviye',
                                 title=f"{ders} Konu Dağılımı",
                                 hole=0.4,
                                 labels={'Seviye': 'Seviye', 'Sayi': 'Konu Sayısı'},
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                    
                    fig_genel.update_traces(textinfo='percent+label', pull=[0.05] * len(yuzdeler_df))
                    st.plotly_chart(fig_genel, use_container_width=True, key=f"genel_{ders}_chart")
                    
                    # Detaylar için açılır menü
                    with st.expander(f"**{ders} Konu Detayları ve Öneriler**"):
                        for konu_veri in konu_detaylari[ders]:
                            konu = konu_veri['konu']
                            seviye = konu_veri['seviye']
                            yuzde = mastery_seviyeleri[seviye]
                            
                            col_detay1, col_detay2 = st.columns([1, 4])
                            
                            with col_detay1:
                                # Konu için küçük dairesel ilerleme göstergesi
                                fig_konu = go.Figure(go.Pie(
                                    values=[yuzde, 100 - yuzde],
                                    labels=['Tamamlandı', 'Kalan'],
                                    hole=0.8,
                                    marker_colors=['#3498db', '#ecf0f1'],
                                    hoverinfo='none',
                                    textinfo='text',
                                    text=[f'{yuzde}%', ''],
                                    textfont_size=20,
                                    textfont_color='#2c3e50',
                                    showlegend=False
                                ))
                                fig_konu.update_layout(
                                    width=150,
                                    height=150,
                                    margin=dict(t=0, b=0, l=0, r=0),
                                    annotations=[dict(text=f'{yuzde}%', x=0.5, y=0.5, font_size=20, showarrow=False)]
                                )
                                st.plotly_chart(fig_konu, use_container_width=True, key=f"konu_{ders}_{konu}_chart")

                            with col_detay2:
                                st.markdown(f"**{konu}** - *{seviye}*")
                                st.markdown(f"""
                                    <div style="background-color: #ecf0f1; border-left: 5px solid #3498db; padding: 10px; margin-top: 10px; border-radius: 5px;">
                                        <strong>İpucu:</strong> {oneriler[seviye]}
                                    </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("Henüz 'Konu Masterysi' bölümüne veri girmediniz. Lütfen konularınızı tamamlayın.")
        elif menu == "🧠 Psikolojik Taktiklerim":
            psikolojik_destek_sayfası()
            
        elif menu == "⏰ Pomodoro Zamanlayıcısı":
            pomodoro_zamanlayıcısı_sayfası()

        elif menu == "📅 Günlük Program":
            derece_günlük_program()
            
        elif menu == "🎯 YKS Konuların Burda":
            derece_konu_takibi()
            
        elif menu == "📈 Deneme Analizi":
            derece_deneme_analizi()
            
        elif menu == "💡 Derece Önerileri":
            derece_öneriler()
            
        elif menu == "📊 Performans İstatistikleri":
            st.markdown('<div class="section-header">📊 Detaylı Performans Analizi</div>', unsafe_allow_html=True)
            
            if st.session_state.deneme_sonuçları:
                df = pd.DataFrame(st.session_state.deneme_sonuçları)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("Henüz deneme verisi bulunmuyor. İlk denemenizi girin!")
            
if __name__ == "__main__":
    main()