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
    page_title="YKS Derece Ajandası",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema ve CSS
def set_tema_ve_stil():
    st.markdown("""
        <style>
            .main-header {
                font-size: 2.5rem;
                font-weight: 700;
                color: #2c3e50;
                text-align: center;
                margin-bottom: 2rem;
            }
            .section-header {
                font-size: 1.8rem;
                font-weight: 600;
                color: #34495e;
                margin-top: 2rem;
                margin-bottom: 1rem;
                border-bottom: 2px solid #3498db;
                padding-bottom: 0.5rem;
            }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: nowrap;
                background-color: #ecf0f1;
                border-radius: 4px 4px 0 0;
                gap: 10px;
                padding: 10px 20px;
                border: 1px solid #bdc3c7;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e0e6e9;
            }
            .stTabs [aria-selected="true"] {
                background-color: #3498db;
                color: white;
                border-bottom: 3px solid #e74c3c;
            }
            .stMetric h3 {
                color: #2c3e50;
            }
            .metric-card {
                background-color: #f8f9fa;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            .metric-card h3 {
                font-size: 1.2rem;
                color: #7f8c8d;
            }
            .hero-section {
                padding: 4rem 0;
                background: linear-gradient(45deg, #f0f4f7, #e3e9ed);
                border-radius: 15px;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }
            .hero-section .main-header {
                color: #2c3e50;
            }
        </style>
    """, unsafe_allow_html=True)
set_tema_ve_stil()

# Oturum Durumu Başlatma
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.is_logged_in = False
    st.session_state.username = ""
    st.session_state.user_data = {}
    st.session_state.konu_durumu = {}
    st.session_state.deneme_sonuçları = []
    st.session_state.günlük_çalışma_kayıtları = {}
    st.session_state.motivasyon_puanı = 0

# Giriş Sayfası
def login_page():
    st.title("Giriş Yap")
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Şifre", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Giriş Yap", use_container_width=True):
            user_data = load_user_data(username)
            if user_data:
                if user_data['password'] == hashlib.sha256(password.encode()).hexdigest():
                    st.session_state.is_logged_in = True
                    st.session_state.username = username
                    st.session_state.user_data = user_data
                    st.session_state.konu_durumu = user_data.get('konu_durumu', {})
                    st.session_state.deneme_sonuçları = user_data.get('deneme_sonuçları', [])
                    st.session_state.günlük_çalışma_kayıtları = user_data.get('günlük_çalışma_kayıtları', {})
                    st.session_state.motivasyon_puanı = user_data.get('motivasyon_puanı', 0)
                    st.success("Giriş başarılı!")
                    st.experimental_rerun()
                else:
                    st.error("Şifre yanlış.")
            else:
                st.error("Kullanıcı bulunamadı.")
    
    with col2:
        if st.button("Kayıt Ol", use_container_width=True):
            if username and password:
                user_data = {
                    'password': hashlib.sha256(password.encode()).hexdigest(),
                    'konu_durumu': {},
                    'deneme_sonuçları': [],
                    'günlük_çalışma_kayıtları': {},
                    'motivasyon_puanı': random.randint(50, 100),
                }
                save_user_data(username, user_data)
                st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
            else:
                st.error("Kullanıcı adı ve şifre boş bırakılamaz.")
                
    st.info("Kayıt olmak için yeni bir kullanıcı adı ve şifre girip Kayıt Ol butonuna tıklayın.")

# Ana Uygulama
def main_app():
    # Sayfa Başlığı ve Tema
    bilgi = {
        'isim': st.session_state.username.capitalize(),
        'hedef_bölüm': 'Hukuk'
    }
    tema = {
        'icon': '📚',
        'renk': '#e74c3c'
    }

    st.sidebar.markdown(f'''
        <div style="text-align: center; padding: 20px; background-color: #34495e; color: white; border-radius: 10px;">
            <h1 style="color: white; font-size: 2rem;">{tema['icon']} Derece Ajandası</h1>
        </div>
    ''', unsafe_allow_html=True)
    
    menu = st.sidebar.radio("Menü",
        ["🏠 Ana Sayfa", "🎯 Konu Masterysi", "📈 Deneme Analizi", "📅 Günlük Program", "⏰ Pomodoro Zamanlayıcısı", "💡 Derece Önerileri", "📊 Performans İstatistikleri"])

    if st.sidebar.button("💾 Kaydet ve Çıkış Yap"):
        st.session_state.user_data['konu_durumu'] = st.session_state.konu_durumu
        st.session_state.user_data['deneme_sonuçları'] = st.session_state.deneme_sonuçları
        st.session_state.user_data['günlük_çalışma_kayıtları'] = st.session_state.günlük_çalışma_kayıtları
        st.session_state.user_data['motivasyon_puanı'] = st.session_state.motivasyon_puanı
        save_user_data(st.session_state.username, st.session_state.user_data)
        st.session_state.is_logged_in = False
        st.experimental_rerun()
    
    # --- Sayfalar Arası Gezinme ---
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
            "Hiç Bilmiyor": "Bu konuya öncelik ver ve temel kaynaklardan çalışmaya başla. Konunun ana hatlarını anlamaya odaklan.",
            "Temel Bilgi": "Konunun temel kavramlarını pekiştirmek için bol bol basit ve orta düzey soru çöz. Konu anlatımı tekrarı faydalı olabilir.",
            "Orta Seviye": "Farklı kaynaklardan ve zorluk seviyelerinde soru çözerek pratik yap. Yanlış yaptığın soruların çözümünü iyice analiz et.",
            "İyi Seviye": "Bu konuyu uzmanlık seviyesine çıkarmak için çıkmış sorular ve denemelerdeki zorlayıcı sorulara odaklan. Zamanla yarışarak soru çözme egzersizleri yap.",
            "Uzman (Derece) Seviye": "Tebrikler! Bu konuyu pekiştirmek için sadece denemelerde karşısına çıkan sorulara bakman yeterli. Bildiğin konuyu tekrar etme tuzağına düşme."
        }
        
        if 'konu_durumu' in st.session_state and st.session_state.konu_durumu:
            
            ders_seviye_sayilari = {}
            konu_detaylari = {}
            
            for anahtar, seviye in st.session_state.konu_durumu.items():
                parcalar = anahtar.split('-')
                ders = parcalar[1]
                konu = parcalar[2]
                
                if ders not in ders_seviye_sayilari:
                    ders_seviye_sayilari[ders] = {s: 0 for s in mastery_seviyeleri.keys()}
                
                if ders not in konu_detaylari:
                    konu_detaylari[ders] = []
                
                ders_seviye_sayilari[ders][seviye] += 1
                konu_detaylari[ders].append({"konu": konu, "seviye": seviye})

            st.markdown('<div class="section-header">📈 Konu Tamamlama Analizi</div>', unsafe_allow_html=True)

            for ders, seviye_sayilari in ders_seviye_sayilari.items():
                toplam_konu = sum(seviye_sayilari.values())
                
                if toplam_konu == 0:
                    continue
                    
                st.markdown(f"### {ders} Genel Durumu")
                
                yuzdeler = {seviye: (sayi / toplam_konu) * 100 for seviye, sayi in seviye_sayilari.items()}
                
                # Sadece değerleri olan seviyeleri bar chart'a ekle
                yuzdeler_df = pd.DataFrame(yuzdeler.items(), columns=['Seviye', 'Yüzde'])
                st.bar_chart(yuzdeler_df.set_index('Seviye'))
                
                with st.expander(f"**{ders} Konu Detayları ve Öneriler**"):
                    for konu_veri in konu_detaylari[ders]:
                        konu = konu_veri['konu']
                        seviye = konu_veri['seviye']
                        yuzde = mastery_seviyeleri[seviye]
                        
                        st.markdown(f"**{konu}** - *{seviye}* (%{yuzde})")
                        st.progress(yuzde / 100)
                        
                        st.markdown(f"""
                            <div style="background-color: #ecf0f1; border-left: 5px solid #3498db; padding: 10px; margin-top: 10px; border-radius: 5px;">
                                <strong>İpucu:</strong> {oneriler[seviye]}
                            </div>
                        """, unsafe_allow_html=True)
        else:
            st.info("Henüz 'Konu Masterysi' bölümüne veri girmediniz. Lütfen konularınızı tamamlayın.")

        # --- Mevcut Hızlı İstatistikler ---
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
            
            # Scatter plot ile net-sıralama ilişkisi
            if 'Net' in df.columns and 'Sıralama' in df.columns:
                fig = px.scatter(df, x='Net', y='Sıralama', 
                                 title='Net-Sıralama Korelasyonu',
                                 hover_data=['Deneme Adı'],
                                 labels={'Net': 'Net Sayısı', 'Sıralama': 'Sıralama'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Tarih bazlı net değişimleri
            if 'Tarih' in df.columns and 'Net' in df.columns:
                df['Tarih'] = pd.to_datetime(df['Tarih'])
                df = df.sort_values(by='Tarih')
                fig = px.line(df, x='Tarih', y='Net', 
                              title='Zaman İçinde Net Gelişimi',
                              labels={'Tarih': 'Tarih', 'Net': 'Net Sayısı'})
                st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.info("Henüz deneme sonucu girilmedi. Lütfen 'Deneme Analizi' sayfasından yeni sonuçlar ekleyin.")

# Diğer fonksiyonların tanımları (Bu kısımlar mevcut ilk.py dosyanızdan alınmıştır)

def derece_konu_takibi():
    st.markdown('<div class="section-header">🎯 Konu Masterysi</div>', unsafe_allow_html=True)
    st.info("Hangi konuya ne kadar hakim olduğunu burada belirle ve ilerlemeni takip et.")
    
    dersler = ["TYT Matematik", "TYT Türkçe", "TYT Fen", "TYT Sosyal", "AYT Matematik", "AYT Fizik", "AYT Kimya", "AYT Biyoloji", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
    konular = {
        "TYT Matematik": ["Temel Kavramlar", "Sayı Kümeleri", "Rasyonel Sayılar", "Üslü Sayılar", "Köklü Sayılar", "Denklem Çözme", "Oran-Orantı", "Problemler", "Mantık", "Kümeler", "İstatistik", "Olasılık", "Fonksiyonlar", "Polinomlar", "2. Dereceden Denklemler", "Geometri Temelleri"],
        "TYT Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragrafta Anlam", "Ses Bilgisi", "Yazım Kuralları", "Noktalama İşaretleri", "Dil Bilgisi", "Anlatım Bozuklukları"],
        "TYT Fen": ["Fizik: Kuvvet ve Hareket", "Fizik: Enerji", "Fizik: Elektrik", "Kimya: Atom ve Periyodik Cetvel", "Kimya: Kimyasal Türler Arası Etkileşimler", "Biyoloji: Canlıların Ortak Özellikleri", "Biyoloji: Hücre"],
        "TYT Sosyal": ["Tarih: İlk ve Orta Çağda Türk Dünyası", "Coğrafya: Doğa ve İnsan", "Felsefe: Felsefenin Alanı", "Din Kültürü: İslam ve İbadet"],
        "AYT Matematik": ["Türev", "İntegral", "Limit ve Süreklilik", "Trigonometri", "Logaritma"],
        "AYT Fizik": ["Vektörler", "Basit Harmonik Hareket", "Dalga Mekaniği", "Modern Fizik"],
        "AYT Kimya": ["Organik Kimya", "Kimyasal Tepkimelerde Enerji", "Kimyasal Denge"],
        "AYT Biyoloji": ["İnsan Fizyolojisi", "Genetik", "Bitki Biyolojisi"],
        "AYT Edebiyat": ["Divan Edebiyatı", "Tanzimat Edebiyatı", "Cumhuriyet Dönemi Edebiyatı"],
        "AYT Tarih": ["Osmanlı Tarihi", "Atatürk İlke ve İnkılapları"],
        "AYT Coğrafya": ["Ekosistemler", "Nüfus ve Yerleşme"]
    }
    
    mastery_seviyeleri = ["Hiç Bilmiyor", "Temel Bilgi", "Orta Seviye", "İyi Seviye", "Uzman (Derece) Seviye"]
    
    secilen_ders = st.selectbox("Ders Seç", dersler)
    
    with st.form(key='konu_mastery_form'):
        st.subheader(f"{secilen_ders} Konuları")
        
        for konu in konular[secilen_ders]:
            anahtar = f"{secilen_ders}-{konu}"
            if anahtar not in st.session_state.konu_durumu:
                st.session_state.konu_durumu[anahtar] = "Hiç Bilmiyor"
                
            st.session_state.konu_durumu[anahtar] = st.select_slider(
                konu,
                options=mastery_seviyeleri,
                value=st.session_state.konu_durumu[anahtar],
                key=anahtar
            )
            
        submit_button = st.form_submit_button(label='Kaydet')
        if submit_button:
            st.success(f"{secilen_ders} konuları başarıyla kaydedildi!")

def derece_deneme_analizi():
    st.markdown('<div class="section-header">📈 Deneme Analizi</div>', unsafe_allow_html=True)
    st.info("Çözdüğün denemelerin sonuçlarını gir ve gelişimi takip et.")

    with st.form(key='deneme_form'):
        deneme_adi = st.text_input("Deneme Adı")
        tarih = st.date_input("Deneme Tarihi", value=datetime.now())
        tyt_net = st.number_input("TYT Net Sayısı", min_value=0.0, max_value=120.0, step=0.25)
        ayt_net = st.number_input("AYT Net Sayısı", min_value=0.0, max_value=80.0, step=0.25)
        toplam_net = tyt_net + ayt_net
        siralama = st.number_input("Türkiye Sıralaması (varsa)", min_value=1, step=1)
        
        submit_button = st.form_submit_button(label='Deneme Sonucunu Ekle')

        if submit_button:
            if deneme_adi:
                deneme_sonucu = {
                    "Deneme Adı": deneme_adi,
                    "Tarih": tarih.strftime("%Y-%m-%d"),
                    "TYT Net": tyt_net,
                    "AYT Net": ayt_net,
                    "Net": toplam_net,
                    "Sıralama": siralama if siralama > 0 else "N/A"
                }
                st.session_state.deneme_sonuçları.append(deneme_sonucu)
                st.success("Deneme sonucu başarıyla eklendi!")
            else:
                st.error("Deneme adı boş bırakılamaz.")

def derece_günlük_program():
    st.markdown('<div class="section-header">📅 Günlük Program</div>', unsafe_allow_html=True)
    st.info("Bugün neler çalıştığını kaydederek verimliğini artır.")
    
    bugun = date.today().strftime("%Y-%m-%d")
    
    if bugun not in st.session_state.günlük_çalışma_kayıtları:
        st.session_state.günlük_çalışma_kayıtları[bugun] = []

    with st.form(key='gunluk_kayit_form'):
        ders = st.selectbox("Ders", ["Matematik", "Türkçe", "Fen", "Sosyal", "Edebiyat", "Tarih", "Coğrafya", "Felsefe", "Fizik", "Kimya", "Biyoloji"])
        konu = st.text_input("Çalıştığın Konu")
        süre = st.number_input("Çalışma Süresi (dk)", min_value=15, max_value=240, step=15)
        
        submit_button = st.form_submit_button(label='Kaydet')
        
        if submit_button:
            if konu and süre:
                st.session_state.günlük_çalışma_kayıtları[bugun].append({"ders": ders, "konu": konu, "süre": süre})
                st.success("Çalışma kaydı başarıyla eklendi!")
            else:
                st.error("Konu ve süre boş bırakılamaz.")
                
    st.subheader(f"Bugünkü Çalışmaların ({bugun})")
    if st.session_state.günlük_çalışma_kayıtları[bugun]:
        df = pd.DataFrame(st.session_state.günlük_çalışma_kayıtları[bugun])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Henüz bugün için bir çalışma kaydın yok.")

def pomodoro_zamanlayıcısı_sayfası():
    st.markdown('<div class="section-header">⏰ Pomodoro Zamanlayıcısı</div>', unsafe_allow_html=True)
    st.info("25 dakikalık odaklanma seanslarıyla verimliliğini artır.")

    if 'running' not in st.session_state:
        st.session_state.running = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = 0
    if 'mode' not in st.session_state:
        st.session_state.mode = "work" # work, break, long_break
    if 'work_cycles' not in st.session_state:
        st.session_state.work_cycles = 0

    work_duration = 25 * 60
    break_duration = 5 * 60
    long_break_duration = 15 * 60

    if st.session_state.running:
        elapsed_time = time.time() - st.session_state.start_time
        if st.session_state.mode == "work":
            remaining_time = work_duration - elapsed_time
        elif st.session_state.mode == "break":
            remaining_time = break_duration - elapsed_time
        else:
            remaining_time = long_break_duration - elapsed_time
        
        if remaining_time <= 0:
            if st.session_state.mode == "work":
                st.success("Çalışma seansı tamamlandı! Mola zamanı.")
                st.session_state.work_cycles += 1
                if st.session_state.work_cycles % 4 == 0:
                    st.session_state.mode = "long_break"
                else:
                    st.session_state.mode = "break"
            else:
                st.success("Mola bitti! Yeni bir çalışma seansına başla.")
                st.session_state.mode = "work"
            
            st.session_state.running = False
            st.experimental_rerun()
        
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        st.markdown(f"<h1 style='text-align: center; font-size: 4rem;'>{minutes:02}:{seconds:02}</h1>", unsafe_allow_html=True)
        st.progress(1 - (remaining_time / (work_duration if st.session_state.mode == "work" else break_duration if st.session_state.mode == "break" else long_break_duration)))
        
        if st.button("Durdur"):
            st.session_state.running = False
            st.experimental_rerun()
    else:
        st.markdown(f"<h1 style='text-align: center; font-size: 4rem;'>{25:02}:{0:02}</h1>", unsafe_allow_html=True)
        if st.button("Başlat"):
            st.session_state.running = True
            st.session_state.start_time = time.time()
            st.experimental_rerun()
            
def derece_öneriler():
    st.markdown('<div class="section-header">💡 Derece Önerileri</div>', unsafe_allow_html=True)
    st.info("Bu bölümde, YKS'ye hazırlık için genel ipuçları ve motivasyon artırıcı bilgiler bulabilirsin.")
    
    oneriler = {
        "Pomodoro Tekniği": "Çalışma seanslarını 25 dakika çalışıp 5 dakika mola vererek planla. 4 seans sonunda 15-30 dakika uzun mola ver.",
        "Verimli Soru Çözümü": "Yanlış yaptığın veya boş bıraktığın soruları biriktir ve daha sonra tekrar çözmeye çalış. Her yanlış soru bir öğrenme fırsatıdır.",
        "Programlı Çalışma": "Günlük, haftalık ve aylık hedefler belirleyerek çalışmanı daha düzenli hale getir.",
        "Uyku Düzeni": "Sınav başarısı için düzenli uyku çok önemlidir. Her gece ortalama 7-8 saat uyumaya özen göster."
    }
    
    for baslik, icerik in oneriler.items():
        st.markdown(f"### {baslik}")
        st.write(icerik)
        st.markdown("---")

if 'is_logged_in' not in st.session_state:
    st.session_state.is_logged_in = False

if st.session_state.is_logged_in:
    main_app()
else:
    login_page()