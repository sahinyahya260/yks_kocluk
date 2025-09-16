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
import json
import os
import random
import time
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
    st.markdown('<div class="section-header">📅 Mükemmel Ders Programı Asistanı</div>', unsafe_allow_html=True)
    
    # Renkli ve modern arayüz için CSS stilleri
    st.markdown("""
        <style>
        .program-card {
            background-color: #34495e;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
            border-left: 5px solid #f39c12;
        }
        .program-card h3 {
            color: #ecf0f1;
            font-size: 1.5rem;
            margin-bottom: 15px;
        }
        .program-topic {
            display: flex;
            align-items: center;
            padding: 10px 15px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 8px;
            margin-bottom: 8px;
            transition: all 0.2s;
        }
        .program-topic:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .topic-icon {
            font-size: 1.8rem;
            margin-right: 15px;
            line-height: 1;
        }
        .topic-details {
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }
        .topic-details strong {
            color: #fff;
            font-size: 1.1rem;
        }
        .topic-details span {
            font-size: 0.9rem;
            color: #bdc3c7;
        }
        .tyt-tag {
            background-color: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 5px;
            font-size: 0.8rem;
            font-weight: bold;
            text-align: center;
        }
        .ayt-tag {
            background-color: #e74c3c;
            color: white;
            padding: 4px 8px;
            border-radius: 5px;
            font-size: 0.8rem;
            font-weight: bold;
            text-align: center;
        }
        .stButton>button {
            width: 100%;
            border-radius: 10px;
            padding: 10px;
            font-weight: bold;
            background-color: #f39c12;
            color: white;
            border: none;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Konu veri tabanı (Örnek TYT/AYT konuları)
    KONULAR = {
        'TYT': {
            'Türkçe': ['Sözcükte Anlam', 'Cümlede Anlam', 'Paragraf', 'Sözcük Türleri'],
            'Matematik': ['Temel Kavramlar', 'Sayı Kümeleri', 'Bölme-Bölünebilme', 'Rasyonel Sayılar'],
            'Coğrafya': ['Coğrafyanın Konusu', 'Dünya’nın Şekli ve Hareketleri', 'İklim Bilgisi'],
            'Tarih': ['Tarih Bilimi', 'İlk Çağ Uygarlıkları', 'İslam Tarihi'],
            'Kimya': ['Kimya Bilimi', 'Atom ve Yapısı', 'Periyodik Sistem'],
            'Biyoloji': ['Canlıların Ortak Özellikleri', 'Hücre', 'Canlılar Dünyası'],
            'Fizik': ['Fizik Bilimi', 'Madde ve Özellikleri', 'Isı ve Sıcaklık'],
            'Felsefe': ['Felsefenin Alanı', 'Bilgi Felsefesi'],
            'Din Kültürü': ['Din ve İslam', 'İslam ve İbadetler']
        },
        'AYT': {
            'Matematik': ['Polinomlar', 'İkinci Dereceden Denklemler', 'Parabol', 'Fonksiyonlar', 'Trigonometri'],
            'Edebiyat': ['Şiir Bilgisi', 'Türk Şiiri', 'Tanzimat Edebiyatı', 'Servet-i Fünun Edebiyatı'],
            'Tarih': ['İlk Türk Devletleri', 'Osmanlı Kuruluş', 'Kurtuluş Savaşı'],
            'Coğrafya': ['Ekosistem', 'Nüfus Politikaları', 'Sanayi ve Ulaşım'],
            'Fizik': ['Vektörler', 'Newton’ın Hareket Yasaları', 'Elektrik'],
            'Kimya': ['Modern Atom Teorisi', 'Gazlar', 'Sıvı Çözeltiler']
        }
    }
    
    # Session state'i başlat
    if 'program_detaylari' not in st.session_state:
        st.session_state.program_detaylari = None

    if st.session_state.program_detaylari is None:
        st.info("🎯 Lütfen güncel durumunu girerek sana özel profesyonel programını oluşturalım.")
        
        with st.form("program_giriş_formu"):
            st.subheader("Haftalık Hedefler ve Durum Analizi")
            
            # Öğrencinin güçlü ve zayıf derslerini belirleme
            zayif_dersler = st.multiselect(
                'Bu hafta en çok odaklanmak istediğin, zorlandığın dersler neler?',
                options=list(KONULAR['TYT'].keys()) + list(KONULAR['AYT'].keys()),
                help="Buraya eklediğin derslere programında daha çok yer verilecektir."
            )
            
            tyt_ayt_orani = st.slider(
                'Bu hafta TYT-AYT çalışma dengen nasıl olsun?',
                min_value=0, max_value=100, value=70, format="%d%% TYT"
            )
            
            # Programı oluşturan ana fonksiyon
            submitted = st.form_submit_button("Programımı Oluştur")
            
            if submitted:
                # Verimlilik sırasına göre konuları belirle
                tyt_konu_sayisi = int((len(KONULAR['TYT']) + len(KONULAR['AYT'])) * (tyt_ayt_orani / 100))
                ayt_konu_sayisi = (len(KONULAR['TYT']) + len(KONULAR['AYT'])) - tyt_konu_sayisi
                
                # Zayıf dersleri önceliklendirerek konuya göre program oluşturma mantığı
                haftalik_plan = []
                tyt_dersleri = list(KONULAR['TYT'].keys())
                ayt_dersleri = list(KONULAR['AYT'].keys())
                
                # Zayıf dersleri en başa al
                for ders in zayif_dersler:
                    if ders in tyt_dersleri:
                        if len(KONULAR['TYT'][ders]) > 0:
                            haftalik_plan.append({'ders': ders, 'konu': KONULAR['TYT'][ders][0], 'tur': 'TYT'})
                            KONULAR['TYT'][ders].pop(0)
                            
                    elif ders in ayt_dersleri:
                         if len(KONULAR['AYT'][ders]) > 0:
                            haftalik_plan.append({'ders': ders, 'konu': KONULAR['AYT'][ders][0], 'tur': 'AYT'})
                            KONULAR['AYT'][ders].pop(0)

                # Kalan konuları ekle
                tum_dersler = tyt_dersleri + ayt_dersleri
                random.shuffle(tum_dersler)
                
                for ders in tum_dersler:
                    if ders in KONULAR['TYT'] and KONULAR['TYT'][ders]:
                        haftalik_plan.append({'ders': ders, 'konu': KONULAR['TYT'][ders][0], 'tur': 'TYT'})
                    elif ders in KONULAR['AYT'] and KONULAR['AYT'][ders]:
                        haftalik_plan.append({'ders': ders, 'konu': KONULAR['AYT'][ders][0], 'tur': 'AYT'})
                
                st.session_state.program_detaylari = haftalik_plan
                st.rerun()

    else:
        st.markdown(f"""
            <div class="program-card">
                <h3>Bu Haftaki Sınav Stratejin</h3>
                <p style="color:#bdc3c7;">İşte senin için özel olarak hazırlanmış haftalık konu planın. Bu plana sadık kalarak eksiklerini hızla tamamlayabilirsin.</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Her bir konuyu ayrı bir kartta göster
        for konu in st.session_state.program_detaylari:
            tur_tag = 'tyt-tag' if konu['tur'] == 'TYT' else 'ayt-tag'
            
            st.markdown(f"""
                <div class="program-topic">
                    <span class="topic-icon" style="color: {'#3498db' if konu['tur'] == 'TYT' else '#e74c3c'};">📚</span>
                    <div class="topic-details">
                        <strong>{konu['ders']} - {konu['konu']}</strong>
                        <span class="{tur_tag}">{konu['tur']}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        
        st.warning("⚠️ Not: Bu program, eksik konularına ve girmiş olduğun verilere göre otomatik oluşturulmuştur. Daha detaylı bir program için her gün tamamladığın konuları işaretlemeyi unutma.")
        
        if st.button("Programı Sıfırla ve Yeni Haftaya Başla", key="reset_program"):
            st.session_state.program_detaylari = None
            st.rerun()
            
def pomodoro_zamanlayıcısı_sayfası():
    st.markdown('<div class="section-header">⏰ Pomodoro Zamanlayıcısı</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Mod Seçimi")
        mode = st.radio(
            "Çalışma modunuzu seçin:",
            ('Çalışma Modu', 'Kısa Mola', 'Uzun Mola')
        )

    with col2:
        st.subheader("Zaman Ayarı")
        if mode == 'Çalışma Modu':
            st.session_state.pomodoro_time = st.number_input("Çalışma süresi (dakika)", min_value=1, value=25) * 60
        elif mode == 'Kısa Mola':
            st.session_state.pomodoro_time = st.number_input("Kısa mola süresi (dakika)", min_value=1, value=5) * 60
        elif mode == 'Uzun Mola':
            st.session_state.pomodoro_time = st.number_input("Uzun mola süresi (dakika)", min_value=1, value=15) * 60

    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0; padding: 1.5rem; background-color: #2c3e50; border-radius: 15px;">
        <h1 style="color: #ecf0f1; font-size: 4rem;">
            {str(timedelta(seconds=st.session_state.pomodoro_time))[2:]}
        </h1>
        <p style="color: #bdc3c7;">{mode}</p>
    </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn1:
        if st.button("▶️ Başlat"):
            st.session_state.pomodoro_running = True
    with col_btn2:
        if st.button("⏸️ Duraklat"):
            st.session_state.pomodoro_running = False
    with col_btn3:
        if st.button("⏹️ Sıfırla"):
            st.session_state.pomodoro_running = False
            st.session_state.pomodoro_time = 25 * 60

    if st.session_state.pomodoro_running and st.session_state.pomodoro_time > 0:
        time.sleep(1)
        st.session_state.pomodoro_time -= 1
        st.rerun()
    elif st.session_state.pomodoro_time <= 0 and st.session_state.pomodoro_running:
        st.balloons()
        st.success("Pomodoro tamamlandı! Hadi bir sonraki adıma geçelim.")
        st.session_state.pomodoro_running = False
        st.rerun()

def derece_konu_takibi():
    st.markdown('<div class="section-header">🎯 Konu Masterysi</div>', unsafe_allow_html=True)
    
    konu_veri_tabanı = DereceProgramı()
    
    st.info("Her konuyu çalıştıktan sonra seviyeni belirle. Bu, programını daha da kişiselleştirmemizi sağlayacak!")
    
    tyt_mat_konular = konu_veri_tabanı.tyt_konular["Matematik"]
    ayt_mat_konular = konu_veri_tabanı.ayt_konular["Matematik"]

    # Session state'i başlat
    if 'konu_durumu' not in st.session_state:
        st.session_state.konu_durumu = {}

    seviyeler = ["Hiç Bilmiyor", "Temel Bilgi", "Orta Seviye", "Konu Tamam", "Usta Seviyesi"]

    st.subheader("Matematik Konuları")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### TYT Matematik")
        for konu in tyt_mat_konular:
            konu_key = f"TYT Matematik > {konu}"
            seviye = st.selectbox(
                f"{konu}",
                seviyeler,
                index=seviyeler.index(st.session_state.konu_durumu.get(konu_key, "Hiç Bilmiyor")),
                key=konu_key
            )
            st.session_state.konu_durumu[konu_key] = seviye
    
    with col2:
        st.markdown("### AYT Matematik")
        for konu in ayt_mat_konular:
            konu_key = f"AYT Matematik > {konu}"
            seviye = st.selectbox(
                f"{konu}",
                seviyeler,
                index=seviyeler.index(st.session_state.konu_durumu.get(konu_key, "Hiç Bilmiyor")),
                key=konu_key
            )
            st.session_state.konu_durumu[konu_key] = seviye
    
    # Diğer dersler için de bu yapıyı çoğaltabilirsiniz.

    st.markdown("---")
    st.info("Değişiklikler otomatik olarak kaydediliyor.")

def derece_deneme_analizi():
    st.markdown('<div class="section-header">📈 Deneme Analizi</div>', unsafe_allow_html=True)
    
    st.subheader("Yeni Deneme Sonucu Ekle")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        deneme_adı = st.text_input("Deneme Adı/Numarası", placeholder="Örn: 3D Yayınları 1")
    with col2:
        tarih = st.date_input("Deneme Tarihi", value=datetime.now().date())
    with col3:
        toplam_net = st.number_input("Toplam Net", min_value=0.0, max_value=120.0, step=0.25, format="%.2f")

    ders_netleri = {}
    with st.expander("Ders Bazlı Net Girişi"):
        dersler = ["Türkçe", "Sosyal", "Matematik", "Fen"]
        cols = st.columns(len(dersler))
        for i, ders in enumerate(dersler):
            with cols[i]:
                ders_netleri[ders] = st.number_input(f"{ders} Neti", min_value=0.0, max_value=40.0, step=0.25, format="%.2f", key=f"net_{ders}")

    ekle_butonu = st.button("✅ Deneme Sonucunu Kaydet", use_container_width=True)

    if ekle_butonu:
        if deneme_adı and toplam_net is not None:
            st.session_state.deneme_sonuçları.append({
                "deneme": deneme_adı,
                "tarih": str(tarih),
                "toplam_net": toplam_net,
                **ders_netleri
            })
            st.success("Deneme sonucunuz başarıyla kaydedildi!")
            st.rerun()

    if st.session_state.deneme_sonuçları:
        st.subheader("Deneme Sonuçları Tablosu")
        df = pd.DataFrame(st.session_state.deneme_sonuçları)
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Performans Grafiği")
        fig = px.line(df, x="tarih", y="toplam_net", markers=True, title="Toplam Net Gelişimi")
        fig.update_layout(
            xaxis_title="Tarih",
            yaxis_title="Toplam Net",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white'
        )
        st.plotly_chart(fig, use_container_width=True)

def derece_öneriler():
    st.markdown('<div class="section-header">💡 Derece Öğrencisi Önerileri</div>', unsafe_allow_html=True)
    
    öneriler = {
        "pomodoro": "25 dakika çalışma, 5 dakika mola kuralına sadık kal. Beynin daha verimli çalışacaktır.",
        "konu_takibi": "Çalıştığın konuları işaretlemek, ilerlemeni somut olarak görmeni sağlar. Motivasyonunu yüksek tut!",
        "deneme_analizi": "Sadece deneme çözmek yetmez. Yanlışlarını ve boş bıraktığın soruları analiz ederek eksiklerini belirle.",
        "sağlık": "Düzenli uyku ve dengeli beslenme, beynin en iyi dostudur. Sınav maratonunda enerjini koru."
    }
    
    for başlık, öneri in öneriler.items():
        st.info(f"**{başlık.replace('_', ' ').title()}:** {öneri}")

def main():
    if 'giriş_yapıldı' not in st.session_state:
        st.session_state['giriş_yapıldı'] = False
    
    if st.session_state['giriş_yapıldı']:
        st.sidebar.title(f"Merhaba, {st.session_state.kullanıcı_adı} 👋")
        
        if 'öğrenci_bilgisi' in st.session_state and st.session_state.öğrenci_bilgisi:
            bilgi = st.session_state.öğrenci_bilgisi
            tema_kategori = bilgi['bölüm_kategori']
            tema_css = tema_css_oluştur(tema_kategori)
            st.markdown(tema_css, unsafe_allow_html=True)
            
            st.sidebar.markdown(f"""
            <div style="background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; margin-bottom: 20px;">
                <p style="font-size: 1.2rem; color: #fff;">
                    <b>Hedef:</b> {bilgi['hedef_bölüm']} ({bilgi['hedef_sıralama']}. sıra)
                </p>
                <p style="font-size: 1.2rem; color: #fff;">
                    <b>Sınıf:</b> {bilgi['sınıf']}
                </p>
            </div>
            """, unsafe_allow_html=True)

        menu = st.sidebar.selectbox("Menü", [
            "🏠 Ana Sayfa", 
            "📅 Günlük Program", 
            "🎯 Konu Masterysi",
            "📈 Deneme Analizi",
            "⏰ Pomodoro Zamanlayıcısı",
            "💡 Derece Önerileri",
            "📊 Performans İstatistikleri"
        ])

        if menu == "🏠 Ana Sayfa":
            if not st.session_state.program_oluşturuldu:
                öğrenci_bilgi_formu()
            else:
                st.markdown('<div class="section-header">✨ Koçluk Paneliniz</div>', unsafe_allow_html=True)
                bilgi = st.session_state.öğrenci_bilgisi
                tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
                
                st.markdown(f"""
                <div class="info-card">
                    <h2 style="color:{tema['renk']};">{bilgi['isim']}, Hoş Geldin!</h2>
                    <p>Sisteminize en son **{bilgi['kayıt_tarihi']}** tarihinde giriş yaptınız.</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown('<div class="section-header">🚀 Bu Haftanın Hedefleri</div>', unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    hedef_sıra = bilgi['hedef_sıralama']
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>🎯 Hedef Sıralama</h3>
                        <h2 style="color: {tema['renk']};">{hedef_sıra}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    deneme_sayısı = len(st.session_state.deneme_sonuçları)
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>🧪 Çözülen Deneme</h3>
                        <h2 style="color: {tema['renk']};">{deneme_sayısı}</h2>
                    </div>
                    ''', unsafe_allow_html=True)
                
                with col3:
                    çalışma_günü = (date.today() - datetime.strptime(bilgi['kayıt_tarihi'], '%Y-%m-%d').date()).days
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3>🗓️ Çalışma Günleri</h3>
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
                
        elif menu == "⏰ Pomodoro Zamanlayıcısı":
            pomodoro_zamanlayıcısı_sayfası()

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
            
            if st.session_state.deneme_sonuçları:
                df = pd.DataFrame(st.session_state.deneme_sonuçları)
                st.dataframe(df, use_container_width=True)
                
                fig_net = px.line(df, x='deneme', y='toplam_net', title='Deneme Net Gelişimi', markers=True)
                st.plotly_chart(fig_net, use_container_width=True)
            else:
                st.info("Henüz deneme sonucu eklemediniz. Lütfen deneme analizi sayfasından sonuçlarınızı girin.")

    else:
        login_sayfası()

if __name__ == "__main__":
    main()