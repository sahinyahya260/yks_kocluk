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
    bilgi = st.session_state.öğrenci_bilgisi
    tema = BÖLÜM_TEMALARI[bilgi['bölüm_kategori']]
    
    st.markdown(f'<div class="section-header">{tema["icon"]} Derece Öğrencisi Günlük Program</div>', 
                unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        seçilen_gün = st.selectbox("📅 Gün Seçin", 
                                  ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"])
    with col2:
        program_türü = st.selectbox("📋 Program Türü", ["Standart", "Yoğun", "Hafif", "Deneme Günü"])

    # En çok ihtiyaç duyulan konuları bul
    derece_programı = DereceProgramı()
    tüm_konular = {**derece_programı.tyt_konular, **derece_programı.ayt_konular}
    önerilen_konular = []
    
    for ders, konular in tüm_konular.items():
        for konu in konular:
            anahtar = f"TYT-{ders}-{konu}" if ders in derece_programı.tyt_konular else f"AYT-{ders}-{konu}"
            seviye = st.session_state.konu_durumu.get(anahtar, "Hiç Bilmiyor")
            if seviye in ["Hiç Bilmiyor", "Temel Bilgi", "Orta Seviye"]:
                önerilen_konular.append(f"{anahtar.split('-')[0]} - {anahtar.split('-')[1]}: {anahtar.split('-')[2]}")
    
    # Bugünün ana hedefini seç
    st.markdown("---")
    bugünkü_hedef = st.selectbox("🎯 Bugünkü Ana Hedef Konu", ["Seçiniz..."] + önerilen_konular)
    
    program = derece_saatlik_program_oluştur(seçilen_gün, program_türü, bilgi, bugünkü_hedef)
    
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
    
    st.markdown("---")
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
                st.session_state.günlük_çalışma_kayıtları[tarih_str] = {
                'tamamlanan_görevler': tamamlanan_görevler,
                'tamamlanma_oranı': len(tamamlanan_görevler) / max(1, len([a for td in program.values() for a in td.values() if 'Çalışma' in a])) * 100,
                'gün': seçilen_gün
            }
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
                st.success("Günlük performans kaydedildi! 🎉")
            else:
                st.error("Veri kaydetme başarısız.")

def derece_saatlik_program_oluştur(gün, program_türü, bilgi, hedef_konu):
    temel_program = {
        'sabah': {
            '06:00': '🌅 Uyanış + Hafif Egzersiz',
            '06:30': '🥗 Beslenme + Vitamin',
            '07:00': '📚 **Sabah Çalışması**',
            '08:30': '☕ Mola + Nefes Egzersizi',
            '08:45': '📝 **Sabah Çalışması**',
            '10:15': '🥤 Mola + Beyin Oyunları',
            '10:30': '🧪 **Sabah Çalışması**',
            '12:00': '🍽️ Öğle Yemeği'
        },
        'öğle': {
            '13:00': '😴 Kısa Dinlenme (20dk)',
            '13:30': '📖 **Öğle Çalışması**',
            '15:00': '🚶 Mola + Yürüyüş',
            '15:15': '📊 **Öğle Çalışması**',
            '16:45': '☕ Mola + Gevşeme',
            '17:00': '📋 **Öğle Çalışması**',
            '18:00': '🎯 Günlük Değerlendirme'
        },
        'akşam': {
            '19:00': '🍽️ Akşam Yemeği + Aile Zamanı',
            '20:00': '📚 **Akşam Çalışması**',
            '21:30': '📝 **Akşam Çalışması**',
            '22:30': '📖 Hafif Okuma (Genel Kültür)',
            '23:00': '🧘 Meditasyon + Yarın Planı',
            '23:30': '😴 Uyku Hazırlığı'
        }
    }

    # Eğer bir hedef konu seçildiyse, programı ona göre doldur
    if hedef_konu != "Seçiniz...":
        parts = hedef_konu.split(': ')
        ders_konu_str = parts[0]
        konu_adı = parts[1]
        
        # TYT veya AYT dersini ayır
        ders_tyt_ayt = ders_konu_str.split(' - ')[0]
        ders_adı = ders_konu_str.split(' - ')[1]

        # Sahte bir konu dağılımı yapalım
        konu_saatleri = {
            '07:00': f'{hedef_konu} - Konu Anlatımı',
            '08:45': f'{hedef_konu} - Konu Tekrarı + Soru Çözümü',
            '10:30': f'{hedef_konu} - Test Çözümü + Yanlış Analizi',
            '13:30': f'Diğer dersler',
            '15:15': f'Diğer dersler',
            '17:00': f'Deneme Sınavı',
            '20:00': f'Geriye dönük tekrar',
            '21:30': f'Yarınki programın hazırlanması'
        }

        # Programı güncelleyelim
        temel_program['sabah']['07:00'] = f'📚 {hedef_konu} Konu Anlatımı'
        temel_program['sabah']['08:45'] = f'📝 {hedef_konu} Soru Çözümü'
        temel_program['sabah']['10:30'] = f'🧪 {hedef_konu} Konu Tekrarı'
        temel_program['öğle']['13:30'] = f'📖 TYT Genel Tekrar'
        temel_program['öğle']['15:15'] = f'📊 AYT Denemesi (Kısa)'
        temel_program['öğle']['17:00'] = f'📋 Deneme Analizi'
        temel_program['akşam']['20:00'] = f'📚 Zayıf Alan Çalışması (Farklı Konu)'
        temel_program['akşam']['21:30'] = f'📝 Günlük Değerlendirme'

    # Program türüne göre ayarlama
    if program_türü == "Yoğun":
        # Çalışma saatlerini artır, mola sürelerini azalt
        pass
    elif program_türü == "Deneme Günü":
        temel_program['sabah']['07:00'] = '📝 TYT Deneme Sınavı'
        temel_program['sabah']['08:45'] = '⏳ TYT Deneme Sınavı'
        temel_program['sabah']['10:30'] = '📊 TYT Analizi'
        temel_program['öğle']['13:30'] = '📝 AYT Deneme Sınavı'
        temel_program['öğle']['15:15'] = '⏳ AYT Deneme Sınavı'
        temel_program['öğle']['17:00'] = '📊 AYT Analizi'
        temel_program['akşam']['20:00'] = '📚 Deneme yanlışları'
        temel_program['akşam']['21:30'] = '📝 Zayıf konu tespiti'

    return temel_program

def derece_konu_takibi():
    
    
    st.markdown('<div class="section-header">🎯 Konu Masterysi</div>', unsafe_allow_html=True)
    st.markdown('<p style="font-size: 1.1rem;">Eksik olduğun konuları en detaylı şekilde takip et.</p>', unsafe_allow_html=True)
    
    # YKS konularını 4 seviyeli hiyerarşik olarak tanımla
    yks_konulari = {
        "TYT Türkçe": {
            "Anlam Bilgisi": {
                "Sözcükte Anlam": [
                    "Gerçek Anlam",
                    "Mecaz Anlam",
                    "Terim Anlam",
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
                    "Paragrafta Anlatım Teknikleri",
                    "Paragrafta Düşünceyi Geliştirme Yolları",
                    "Paragrafta Yapı",
                    "Paragrafta Konu-Ana Düşünce",
                    "Paragrafta Yardımcı Düşünce"
                ]
            },
            "Dil Bilgisi": {
                "Ses Bilgisi": [
                    "Büyük Ünlü Uyumu",
                    "Ünsüz Benzeşmesi",
                    "Ünsüz Yumuşaması"
                ],
                "Sözcük Türleri": [
                    "İsim",
                    "Sıfat",
                    "Zamir",
                    "Edat"
                ]
            }
        },
        "TYT Matematik": {
            "Temel Kavramlar": {
                "Sayılar": [
                    "Rasyonel Sayılar", 
                    "Gerçek Sayılar", 
                    "Bölünebilme"
                ]
            },
            "Problemler": {
                "Temel Problemler": [
                    "Sayı Problemleri", 
                    "Kesir Problemleri"
                ]
            }
        }
    }
    
    mastery_seviyeleri = ["Hiç Bilmiyor", "Temel Bilgi", "Orta Seviye", "İyi Seviye", "Uzman (Derece) Seviye"]
    
    # 1. Adım: Ders seçimi
    dersler = list(yks_konulari.keys())
    secilen_ders = st.selectbox("Ders Seç", dersler, key="ders_add")
    
    # 2. Adım: Konu alanı seçimi
    if secilen_ders:
        konu_alanlari = list(yks_konulari[secilen_ders].keys())
        secilen_konu_alani = st.selectbox("Konu Alanı Seç", konu_alanlari, key="konu_alani_add")
    
    # 3. Adım: Alt konu seçimi
    alt_konu_anahtarlari = []
    if secilen_konu_alani:
        alt_konu_anahtarlari = list(yks_konulari[secilen_ders][secilen_konu_alani].keys())
        secilen_alt_konu = st.selectbox("Alt Konu Seç", alt_konu_anahtarlari, key="alt_konu_add")
    
    # 4. Adım: Daha alt konu seçimi
    daha_alt_konular = []
    if secilen_alt_konu:
        daha_alt_konular = yks_konulari[secilen_ders][secilen_konu_alani][secilen_alt_konu]
        secilen_daha_alt_konu = st.selectbox("Daha Alt Konu Seç", daha_alt_konular, key="daha_alt_konu_add")
    
    # 5. Adım: Seviye Belirleme
    if secilen_daha_alt_konu:
        konu_key = f"{secilen_ders}>{secilen_konu_alani}>{secilen_alt_konu}>{secilen_daha_alt_konu}"
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

def pomodoro_zamanlayıcısı_sayfası():
    st.markdown('<div class="section-header">⏰ Akıllı Çalışma Zamanlayıcısı</div>', unsafe_allow_html=True)
    
    # Zamanlayıcı durumlarını yönet
    POMODORO_MODES = {
        "Pomodoro (25dk)": {"time": 25 * 60, "label": "Çalışma Modu"},
        "Kısa Mola (5dk)": {"time": 5 * 60, "label": "Kısa Mola"},
        "Uzun Mola (15dk)": {"time": 15 * 60, "label": "Uzun Mola"},
        "Derin Odak (50dk)": {"time": 50 * 60, "label": "Derin Odak"}
    }

    # Ana zamanlayıcı ekranı
    timer_display = st.empty()

    # Butonlar için kolonlar
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("▶️ Başla", use_container_width=True):
            st.session_state.pomodoro_running = True
    with col2:
        if st.button("⏸️ Duraklat", use_container_width=True):
            st.session_state.pomodoro_running = False
    with col3:
        if st.button("🔄 Sıfırla", use_container_width=True):
            st.session_state.pomodoro_running = False
            st.session_state.pomodoro_time = POMODORO_MODES[st.session_state.pomodoro_mode]["time"]
            st.session_state.pomodoro_count = 0

    st.markdown("---")
    
    col4, col5, col6, col7 = st.columns(4)
    with col4:
        if st.button("🍅 Pomodoro (25dk)", use_container_width=True):
            st.session_state.pomodoro_mode = "Pomodoro (25dk)"
            st.session_state.pomodoro_time = POMODORO_MODES["Pomodoro (25dk)"]["time"]
            st.session_state.pomodoro_running = False
    with col5:
        if st.button("☕ Kısa Mola (5dk)", use_container_width=True):
            st.session_state.pomodoro_mode = "Kısa Mola (5dk)"
            st.session_state.pomodoro_time = POMODORO_MODES["Kısa Mola (5dk)"]["time"]
            st.session_state.pomodoro_running = False
    with col6:
        if st.button("🛌 Uzun Mola (15dk)", use_container_width=True):
            st.session_state.pomodoro_mode = "Uzun Mola (15dk)"
            st.session_state.pomodoro_time = POMODORO_MODES["Uzun Mola (15dk)"]["time"]
            st.session_state.pomodoro_running = False
    with col7:
        if st.button("🧠 Derin Odak (50dk)", use_container_width=True):
            st.session_state.pomodoro_mode = "Derin Odak (50dk)"
            st.session_state.pomodoro_time = POMODORO_MODES["Derin Odak (50dk)"]["time"]
            st.session_state.pomodoro_running = False
    
    st.markdown("---")
    
    # Pomodoro sayacı ve ilerleme çubuğu
    pomodoro_progress_bar = st.progress(0)
    pomodoro_progress_text = st.empty()
    pomodoro_progress_text.text(f"Bugünkü Pomodoro: {st.session_state.pomodoro_count}/8")
    
    # Zamanlayıcıyı başlat
    if st.session_state.pomodoro_running:
        while st.session_state.pomodoro_time > 0 and st.session_state.pomodoro_running:
            mins, secs = divmod(st.session_state.pomodoro_time, 60)
            timer_display.markdown(f"""
                <div style="
                    text-align: center; 
                    font-size: 5rem; 
                    font-weight: bold; 
                    background: rgba(255,255,255,0.1); 
                    border-radius: 10px;
                    padding: 2rem;
                ">
                    {mins:02}:{secs:02}
                </div>
                <p style="text-align:center; font-size:1.2rem; color:#ccc;">{POMODORO_MODES[st.session_state.pomodoro_mode]['label']}</p>
            """, unsafe_allow_html=True)
            
            time.sleep(1)
            st.session_state.pomodoro_time -= 1
            st.rerun()
            
        if st.session_state.pomodoro_time <= 0:
            st.session_state.pomodoro_running = False
            
            if st.session_state.pomodoro_mode == "Pomodoro (25dk)":
                st.session_state.pomodoro_count += 1
                pomodoro_progress_bar.progress(min(st.session_state.pomodoro_count / 8, 1.0))
                st.balloons()
                st.success("Pomodoro tamamlandı! Şimdi kısa bir mola ver.")
                st.session_state.pomodoro_mode = "Kısa Mola (5dk)"
                st.session_state.pomodoro_time = POMODORO_MODES["Kısa Mola (5dk)"]["time"]
            
            st.rerun()

    # Zamanlayıcı çalışmıyorsa mevcut durumu göster
    else:
        mins, secs = divmod(st.session_state.pomodoro_time, 60)
        timer_display.markdown(f"""
            <div style="
                text-align: center; 
                font-size: 5rem; 
                font-weight: bold; 
                background: rgba(255,255,255,0.1); 
                border-radius: 10px;
                padding: 2rem;
            ">
                {mins:02}:{secs:02}
            </div>
            <p style="text-align:center; font-size:1.2rem; color:#ccc;">{POMODORO_MODES[st.session_state.pomodoro_mode]['label']}</p>
        """, unsafe_allow_html=True)
        pomodoro_progress_bar.progress(min(st.session_state.pomodoro_count / 8, 1.0))
        pomodoro_progress_text.text(f"Bugünkü Pomodoro: {st.session_state.pomodoro_count}/8")

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
                
                for anahtar, seviye in st.session_state.konu_durumu.items():
                    parcalar = anahtar.split('>') # YENİ ANAHTAR AYRIŞTIRMASI
                    if len(parcalar) >= 4:
                        ders = parcalar[0].strip()
                        konu_adı = " > ".join(parcalar[1:]).strip() # Daha açıklayıcı konu adı oluştur
                    else:
                        continue # Hatalı veya eski formatlı anahtarları atla
                    
                    if ders not in ders_seviye_sayilari:
                        ders_seviye_sayilari[ders] = {s: 0 for s in mastery_seviyeleri.keys()}
                    
                    if ders not in konu_detaylari:
                        konu_detaylari[ders] = []
                    
                    ders_seviye_sayilari[ders][seviye] += 1
                    konu_detaylari[ders].append({"konu": konu_adı, "seviye": seviye})

                for ders, seviye_sayilari in ders_seviye_sayilari.items():
                    toplam_konu = sum(seviye_sayilari.values())
                    
                    if toplam_konu == 0:
                        continue
                        
                    st.markdown(f"### {ders} Genel Durumu")
                    
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