import streamlit as st
import hashlib
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import csv
import os
import json
import random
import firebase_admin
from firebase_admin import credentials, db

# Sayfa yapılandırması
st.set_page_config(
    page_title="YKS Takip Sistemi",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Firebase başlatma
try:
    # Firebase'in zaten başlatılıp başlatılmadığını kontrol et
    if not firebase_admin._apps:
        # Firebase Admin SDK'yı başlat
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL':'https://yks-takip-c26d5-default-rtdb.firebaseio.com/'  # ✅ DOĞRU/'
        })
    
    db_ref = db.reference('users')
    if not hasattr(st.session_state, 'firebase_connected'):
        st.success("🔥 Firebase bağlantısı başarılı!")
        st.session_state.firebase_connected = True
        
except Exception as e:
    st.error(f"❌ Firebase başlatma hatası: {e}")
    st.info("🔧 Lütfen 'firebase_key.json' dosyasının doğru konumda olduğundan ve databaseURL'in doğru olduğundan emin olun.")
    db_ref = None

# === HİBRİT POMODORO SİSTEMİ SABİTLERİ ===

# YKS Odaklı Motivasyon Sözleri - Hibrit Sistem için
MOTIVATION_QUOTES = [
    "Her 50 dakikalık emek, seni rakiplerinden ayırıyor! 💪",
    "Şu anda çözdüğün her soru, YKS'de seni zirveye taşıyacak! 🎯",
    "Büyük hedefler küçük adımlarla başlar - sen doğru yoldasın! ⭐",
    "Her nefes alışın, YKS başarına bir adım daha yaklaştırıyor! 🌬️",
    "Zorluklara direnmek seni güçlendiriyor - YKS'de fark yaratacaksın! 🚀",
    "Bugün kazandığın her kavram, sınavda seni öne çıkaracak! 📚",
    "Konsantrasyon kasların güçleniyor - şampiyonlar böyle yetişir! 🧠",
    "Hedefine odaklan! Her dakika YKS başarın için değerli! 🏆",
    "Mola hakkını akıllıca kullanıyorsun - bu seni daha güçlü yapıyor! 💨",
    "Başarı sabır ister, sen sabırlı bir savaşçısın! ⚔️",
    "Her yeni konu öğrenişin, gelecekteki mesleğinin temeli! 🏗️",
    "Rüyalarının peşinde koşuyorsun - asla vazgeçme! 🌟",
    "YKS sadece bir sınav, sen ise sınırsız potansiyelin! 🌈",
    "Her pomodoro seansı, hedefine bir adım daha yaklaştırıyor! 🎯",
    "Dün yapamadığını bugün yapabiliyorsun - bu gelişim! 📈",
    "Zorlu soruları çözerken beynin güçleniyor! 🧩",
    "Her mola sonrası daha güçlü dönüyorsun! 💪",
    "Bilim insanları da böyle çalıştı - sen de başaracaksın! 🔬",
    "Her nefes, yeni bir başlangıç fırsatı! 🌱",
    "Hayal ettiğin üniversite seni bekliyor! 🏛️"
]

# Mikro ipuçları (ders bazında)
MICRO_TIPS = {
    "TYT Matematik": [
        "📐 Türev sorularında genellikle önce fonksiyonun köklerini bulmak saldırıları hızlandırır.",
        "🔢 İntegral hesaplarken substitüsyon methodunu akılda tut.",
        "📊 Geometri problemlerinde çizim yapmayı unutma.",
        "⚡ Limit sorularında l'hopital kuralını hatırla."
    ],
    "TYT Fizik": [
        "⚡ Newton yasalarını uygularken kuvvet vektörlerini doğru çiz.",
        "🌊 Dalga problemlerinde frekans-dalga boyu ilişkisini unutma.",
        "🔥 Termodinamik sorularında sistem sınırlarını net belirle.",
        "🔬 Elektrik alanı hesaplamalarında işaret dikkatli kontrol et."
    ],
    "TYT Kimya": [
        "🧪 Mol kavramı tüm hesaplamaların temeli - ezberleme!",
        "⚛️ Periyodik cetveldeki eğilimleri görselleştir.",
        "🔄 Denge tepkimelerinde Le Chatelier prensibini uygula.",
        "💧 Asit-baz titrasyonlarında eşdeğer nokta kavramını unutma."
    ],
    "TYT Türkçe": [
        "📖 Paragraf sorularında ana fikri ilk ve son cümlelerde ara.",
        "✍️ Anlam bilgisi sorularında bağlamı dikkate al.",
        "📝 Yazım kurallarında 'de/da' ayrım kuralını hatırla.",
        "🎭 Edebi türlerde karakterizasyon önemli."
    ],
    "TYT Tarih": [
        "📅 Olayları kronolojik sırayla öğren, sebep-sonuç bağla.",
        "🏛️ Siyasi yapılar sosyal yapılarla ilişkisini kur.",
        "🗺️ Haritalarla coğrafi konumları pekiştir.",
        "👑 Dönem özelliklerini başlıca olaylarla örnekle."
    ],
    "TYT Coğrafya": [
        "🌍 İklim türlerini sebepleriyle birlikte öğren.",
        "🏔️ Jeomorfoloji'de süreç-şekil ilişkisini kur.",
        "📊 İstatistiksel veriler harita okuma becerisini geliştir.",
        "🌱 Bitki örtüsü-iklim ilişkisini unutma."
    ],
    "AYT Matematik": [
        "📐 Türev sorularında genellikle önce fonksiyonun köklerini bulmak saldırıları hızlandırır.",
        "🔢 İntegral hesaplarken substitüsyon methodunu akılda tut.",
        "📊 Geometri problemlerinde çizim yapmayı unutma.",
        "⚡ Limit sorularında l'hopital kuralını hatırla."
    ],
    "AYT Fizik": [
        "⚡ Newton yasalarını uygularken kuvvet vektörlerini doğru çiz.",
        "🌊 Dalga problemlerinde frekans-dalga boyu ilişkisini unutma.",
        "🔥 Termodinamik sorularında sistem sınırlarını net belirle.",
        "🔬 Elektrik alanı hesaplamalarında işaret dikkatli kontrol et."
    ],
    "AYT Kimya": [
        "🧪 Mol kavramı tüm hesaplamaların temeli - ezberleme!",
        "⚛️ Periyodik cetveldeki eğilimleri görselleştir.",
        "🔄 Denge tepkimelerinde Le Chatelier prensibini uygula.",
        "💧 Asit-baz titrasyonlarında eşdeğer nokta kavramını unutma."
    ],
    "Genel": [
        "🎯 Zor sorularla karşılaştığında derin nefes al ve sistematik düşün.",
        "⏰ Zaman yönetimini ihmal etme - her dakika değerli.",
        "📚 Kavramları sadece ezberlemek yerine anlayarak öğren.",
        "🔄 Düzenli tekrar yapmak kalıcılığı artırır."
    ]
}

# YKS Odaklı Nefes Egzersizi Talimatları
BREATHING_EXERCISES = [
    {
        "name": "4-4-4-4 Tekniği (Kare Nefes)",
        "instruction": "4 saniye nefes al → 4 saniye tut → 4 saniye ver → 4 saniye bekle",
        "benefit": "Stresi azaltır, odaklanmayı artırır, sınav kaygısını azaltır"
    },
    {
        "name": "Karın Nefesi (Diyafragma Nefesi)",
        "instruction": "Elinizi karnınıza koyun. Nefes alırken karın şişsin, verirken insin",
        "benefit": "Gevşemeyi sağlar, kaygıyı azaltır, zihinsel netliği artırır"
    },
    {
        "name": "4-7-8 Sakinleştirici Nefes",
        "instruction": "4 saniye burun ile nefes al → 7 saniye tut → 8 saniye ağız ile ver",
        "benefit": "Derin rahatlama sağlar, uykuya yardım eder, sınav öncesi sakinleştirir"
    },
    {
        "name": "Yavaş Derin Nefes",
        "instruction": "6 saniye nefes al → 2 saniye tut → 6 saniye yavaşça ver",
        "benefit": "Kalp ritmi düzenlenir, sakinleşir, zihinsel berraklık artar"
    },
    {
        "name": "Alternatif Burun Nefesi",
        "instruction": "Sağ burun deliği ile nefes al, sol ile ver. Sonra tersini yap",
        "benefit": "Beynin her iki yarım küresini dengeler, konsantrasyonu artırır"
    },
    {
        "name": "5-5 Basit Ritim",
        "instruction": "5 saniye nefes al → 5 saniye nefes ver (hiç tutmadan)",
        "benefit": "Basit ve etkili, hızlı sakinleşme, odaklanma öncesi ideal"
    }
]

# Tüm kullanıcı alanlarını tutarlılık için tanımlıyoruz.
FIELDNAMES = ['username', 'password', 'name', 'surname', 'grade', 'field', 'target_department', 'tyt_last_net', 'tyt_avg_net', 'ayt_last_net', 'ayt_avg_net', 'learning_style', 'learning_style_scores', 'created_at',  'detailed_nets', 'deneme_analizleri','study_program', 'topic_progress', 'topic_completion_dates', 'yks_survey_data', 'pomodoro_history'
              ,'is_profile_complete', 
              'is_learning_style_set', 
              'learning_style']

# Bölümlere göre arka plan resimleri
BACKGROUND_STYLES = {
    "Tıp": {
        "image": "https://images.unsplash.com/photo-1551076805-e1869033e561?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%)",
        "icon": "🩺"
    },
    "Mühendislik": {
        "image": "https://images.unsplash.com/photo-1504384308090-c894fdcc538d?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #4ecdc4 0%, #44a08d 100%)",
        "icon": "⚙️"
    },
    "Hukuk": {
        "image": "https://images.unsplash.com/photo-1589391886645-d51941baf7fb?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #556270 0%, #4ecdc4 100%)",
        "icon": "⚖️"
    },
    "Öğretmenlik": {
        "image": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #ffd89b 0%, #19547b 100%)",
        "icon": "👨‍🏫"
    },
    "İktisat": {
        "image": "https://images.unsplash.com/photo-1665686306574-1ace09918530?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #834d9b 0%, #d04ed6 100%)",
        "icon": "📈"
    },
    "Mimarlık": {
        "image": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #5614b0 0%, #dbd65c 100%)",
        "icon": "🏛️"
    },
    "Psikoloji": {
        "image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #654ea3 0%, #eaafc8 100%)",
        "icon": "🧠"
    },
    "Diş Hekimliği": {
        "image": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #ff5e62 0%, #ff9966 100%)",
        "icon": "🦷"
    },
    "Varsayılan": {
        "image": "https://images.unsplash.com/photo-1523240795612-9a054b0db644?ixlib=rb-4.0.3&auto=format&fit=crop&w=2000&q=80",
        "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "icon": "🎯"
    }
}

# Kitap önerileri
BOOK_RECOMMENDATIONS = {
    "Bilim Kurgu": [
        "Isaac Asimov - Foundation Serisi",
        "Douglas Adams - Otostopçunun Galaksi Rehberi", 
        "George Orwell - 1984",
        "Aldous Huxley - Cesur Yeni Dünya"
    ],
    "Klasik Edebiyat": [
        "Victor Hugo - Sefiller",
        "Fyodor Dostoyevski - Suç ve Ceza",
        "Leo Tolstoy - Savaş ve Barış",
        "Charles Dickens - İki Şehrin Hikayesi"
    ],
    "Kişisel Gelişim": [
        "Dale Carnegie - Dost Kazanma ve İnsanları Etkileme Sanatı",
        "Stephen Covey - Etkili İnsanların 7 Alışkanlığı",
        "Carol Dweck - Mindset",
        "Daniel Goleman - Duygusal Zeka"
    ],
    "Tarih": [
        "Yuval Noah Harari - Sapiens",
        "Jared Diamond - Tüfek, Mikrop ve Çelik",
        "Howard Zinn - Amerika Birleşik Devletleri'nin Halkın Gözünden Tarihi",
        "İlber Ortaylı - Osmanlı'yı Yeniden Keşfetmek"
    ],
    "Felsefe": [
        "Jostein Gaarder - Sophie'nin Dünyası",
        "Platon - Devlet",
        "Aristoteles - Nikomakhos'a Etik",
        "Ahmet Cevizci - Felsefe Tarihi"
    ],
    "Psikoloji": [
        "Daniel Kahneman - Hızlı ve Yavaş Düşünme",
        "Viktor Frankl - İnsanın Anlam Arayışı",
        "Carl Jung - İnsan ve Sembolleri",
        "Sigmund Freud - Rüyaların Yorumu"
    ]
}

# Öğrenme Stili Tanımları (basit versiyonlar)
LEARNING_STYLE_DESCRIPTIONS = {
    "Görsel": {
        "title": "Görsel Öğrenme Stili",
        "intro": "Bilgiyi görsel unsurlarla daha iyi işliyorsunuz.",
        "strengths": ["Şemalar ve grafiklerle öğrenme", "Renk kodlama", "Zihin haritaları"],
        "weaknesses": ["Sadece dinleyerek öğrenmede zorluk"],
        "advice": "Ders notlarınızı renkli kalemlerle alın, şemalar çizin."
    },
    "İşitsel": {
        "title": "İşitsel Öğrenme Stili", 
        "intro": "Dinleyerek ve konuşarak daha iyi öğreniyorsunuz.",
        "strengths": ["Ders dinleme", "Sesli okuma", "Tartışma"],
        "weaknesses": ["Görsel materyallerle zorluk"],
        "advice": "Konuları yüksek sesle tekrar edin, ders kayıtları dinleyin."
    },
    "Kinestetik": {
        "title": "Kinestetik Öğrenme Stili",
        "intro": "Yaparak ve deneyimleyerek öğreniyorsunuz.",
        "strengths": ["Pratik yapma", "Hareket halinde öğrenme", "Deney"],
        "weaknesses": ["Uzun süre hareketsiz kalma"],
        "advice": "Çalışırken ara ara hareket edin, el yazısıyla not alın."
    }
}

# === YENİ SİSTEMATİK YKS TAKİP SİSTEMİ ===

# Ders Önem Puanları (1-10 arası)
SUBJECT_IMPORTANCE_SCORES = {
    "TYT Matematik": 10,      # En kritik
    "TYT Türkçe": 9,          # Yüksek soru sayısı
    "TYT Fizik": 8,           # Önemli
    "TYT Kimya": 8,           # Önemli
    "TYT Biyoloji": 7,        # Orta-Yüksek
    "TYT Geometri": 7,        # Orta-Yüksek
    "TYT Tarih": 6,           # Orta
    "TYT Coğrafya": 6,        # Orta
    "TYT Felsefe": 4,         # 2-3. hafta başlangıç
    "TYT Din Kültürü": 4,     # 2-3. hafta başlangıç
    "AYT Matematik": 10,      # En kritik
    "AYT Fizik": 9,           # Yüksek
    "AYT Kimya": 9,           # Yüksek
    "AYT Biyoloji": 8,        # Önemli
    "AYT Edebiyat": 9,        # Sözel için kritik
    "AYT Tarih": 7,           # Sözel için önemli
    "AYT Coğrafya": 7,        # Sözel için önemli
}

# Bilimsel Tekrar Aralıkları (gün)
SPACED_REPETITION_INTERVALS = [3, 7, 14, 30, 90]

# Öncelik Kategorileri - YENİ DİNAMİK SİSTEM (Konu Takip Seviyelerine Göre)
PRIORITY_CATEGORIES = {
    "HIGH": {"icon": "🔥", "name": "Acil - Zayıf Konu", "color": "#dc3545"},
    "MEDIUM": {"icon": "⚡", "name": "Öncelikli - Temel Konu", "color": "#fd7e14"},
    "NORMAL": {"icon": "🎯", "name": "Normal - Orta Konu", "color": "#20c997"},
    "LOW": {"icon": "🟢", "name": "Düşük - İyi Konu", "color": "#28a745"},
    "MINIMAL": {"icon": "⭐", "name": "Minimal - Uzman Konu", "color": "#6c757d"},
    
    # Tekrar kategorileri
    "REPEAT_HIGH": {"icon": "🔄", "name": "Acil Tekrar", "color": "#e74c3c"},
    "REPEAT_MEDIUM": {"icon": "🔄", "name": "Öncelikli Tekrar", "color": "#f39c12"},
    "REPEAT_NORMAL": {"icon": "🔄", "name": "Normal Tekrar", "color": "#3498db"}
}

# Haftalık Konu Sayısı Limitleri (Öneme göre) - 1-5 Arası
WEEKLY_TOPIC_LIMITS = {
    10: 5,  # En önemli dersler: 5 konu/hafta
    9: 4,   # Çok önemli: 4 konu/hafta
    8: 3,   # Önemli: 3 konu/hafta
    7: 2,   # Orta-Yüksek: 2 konu/hafta
    6: 2,   # Orta: 2 konu/hafta
    4: 1,   # Düşük öncelik: 1 konu/hafta (2-3. hafta sonra)
}

# Modern CSS
def get_custom_css(target_department):
    bg_style = BACKGROUND_STYLES.get(target_department, BACKGROUND_STYLES["Varsayılan"])
    
    return f"""
<style>
    .main-header {{
        background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('{bg_style['image']}');
        background-size: cover;
        background-position: center;
        padding: 3rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        position: relative;
        overflow: hidden;
    }}

    .main-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: {bg_style['gradient']};
        opacity: 0.8;
        z-index: -1;
    }}

    .super-minimal-gauge {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.8rem 0;
        margin: 0.3rem 0;
        border-bottom: 1px solid #f0f0f0;
    }}

    .subject-name {{
        font-size: 1rem;
        font-weight: 500;
        color: #333;
    }}

    .subject-percent {{
        font-size: 1.1rem;
        font-weight: bold;
        color: #4CAF50;
        min-width: 50px;
        text-align: right;
    }}

    .gauge-container {{
        margin: 1rem 0;
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    
    .psychology-test {{
        background: linear-gradient(135deg, #654ea3 0%, #eaafc8 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }}
    
    .psychology-card {{
        background: #c0392b;
        color: white;
        padding: 2rem;
        border-radius: 15px;
        border-left: 5px solid #a43a3a;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    
    .stSpinner > div > span {{
        color: #654ea3 !important;
    }}
    
    .stProgress > div > div > div > div {{
        background-color: #654ea3 !important;
    }}
</style>
"""

# Tüm YKS konuları (GÜNCELLENMİŞ VE TAMAMLANDI)
YKS_TOPICS = {
    "TYT Türkçe": {
        "Anlam Bilgisi": {
            "Sözcükte Anlam": ["Gerçek Anlam", "Mecaz Anlam", "Terim Anlam", "Yan Anlam", "Eş Anlam", "Zıt Anlam", "Eş Sesli"],
            "Cümlede Anlam": ["Cümle Yorumlama", "Kesin Yargı", "Anlatım Biçimleri", "Duygu ve Düşünce", "Amaç-Sonuç", "Neden-Sonuç"],
            "Paragraf": ["Ana Fikir", "Yardımcı Fikir", "Paragraf Yapısı", "Anlatım Teknikleri", "Düşünceyi Geliştirme"]
        },
        "Dil Bilgisi": {
            "Ses Bilgisi": ["Ses Olayları", "Ünlü Uyumları"],
            "Yazım Kuralları": ["Büyük Harf", "Birleşik Kelimeler", "Sayıların Yazımı"],
            "Noktalama İşaretleri": ["Nokta, Virgül", "Noktalı Virgül", "İki Nokta", "Tırnak İşaretleri","Ünlem, Soru","Kesme İşareti","Yay Ayraç"],
            "Sözcükte Yapı":["Kök (isim/fiil)", "gövde,ekler (yapım/çekim) ,basit ,türemiş ve birleşik sözcükler"],       
            "Sözcük Türleri":["İsimler (Adlar)", "Zamirler (Adıllar)", "Sıfatlar (Ön Adlar)", "Zarflar (Belirteçler)", "Edat – Bağlaç Ünlem"],
            "Fiiller": [" Fiilde Anlam (Kip -zaman/tasarlama-, Kişi, Yapı -basit/türemiş/birleşik-)","Ek Fiil (İsimleri yüklem yapma, basit çekimli fiili birleşik çekimli yapma)"," Fiilimsi (İsim fiil, sıfat fiil, zarf fiil)."," Fiilde Çatı (Özne ve nesneye göre fiilin aldığı ekler)."],
            "Cümlenin Ögeleri":["Yüklem, özne, nesne (belirtili/belirtisiz), dolaylı tümleç (yer tamlayıcısı), zarf tümleci, edat tümleci."],
            "Cümle Türleri":["Yüklemin türüne, yerine, anlamına ve yapısına göre cümleler."],   
            "Anlatım Bozukluğu":["Anlamsal ve yapısal anlatım bozuklukları."],      
        }
    },
    "TYT Matematik": {
        "Temel Kavramlar":["Sayılar", "Sayı Basamakları","Bölme ve Bölünebilme", "EBOB – EKOK."],
        "Temel İşlemler": ["Rasyonel Sayılar", "Basit Eşitsizlikler","Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar"],
        "Problemler":[

          "Sayı Problemleri",
          "Kesir Problemleri",
          "Yaş Problemleri",
          "Yüzde Problemleri",
          "Kar-Zarar Problemleri",
          "Karışım Problemleri",
          "Hareket Problemleri",
          "İşçi Problemleri",
          "Tablo-Grafik Problemleri",
          "Rutin Olmayan Problemler (Mantık-muhakeme gerektiren sorular)"],
        "Genel":["Kümeler", "Mantık", "Fonksiyonlar.(temel tyt düzey)"],
        "Olasılık":["Permütasyon","Kombinasyon","Olasılık"]
            
        },
       
    
    "TYT Geometri": {
        "Üçgenler":{
            "Açılar":["Doğruda Açılar","Üçgende Açılar",],
            "Özel Üçgenler":["Dik Üçgen","İkizkenar Üçgen","Eşkenar Üçgen"],
            "Üçgen Özellikleri":["Açıortay","Kenarortay","Eşlik ve Benzerlik","Üçgende Alan","Açı Kenar Bağıntıları"],
        
        "Çokgenler ve Özellikleri":["Çokgenler","Özel Dörtgenler...","Deltoid","Paralel kenar","Eşkenar Dörtgen","Dikdörtgen","Kare","Yamuk"],
        
        "Çember ve Daire":["Çemberde Açı","Çemberde Uzunluk","Dairede Çevre ve Alan"],
        
        "Analitik Geometri":["Noktanın Analitiği","Doğrunun Analitiği"],
        
        "Katı Cisimler":["Prizmalar","Küp","Silindir","Piramit","Koni","Küre"]}
    },
    "TYT Tarih": {
        "Tarih Bilimi":["Tarih ve Zaman","İnsanlığın İlk Dönemleri","Ortaçağ’da Dünya",
                         "İlk ve Orta Çağlarda Türk Dünyası","İslam Medeniyetinin Doğuşu","İlk Türk İslam Devletleri",
                         "Yerleşme ve Devletleşme Sürecinde Selçuklu Türkiyesi","Beylikten Devlete Osmanlı Siyaseti(1300-1453)",
                        "Dünya Gücü Osmanlı Devleti (1453-1600)",
                        "Yeni Çağ Avrupa Tarihi",
                        "Yakın Çağ Avrupa Tarihi",
                        "Osmanlı Devletinde Arayış Yılları(Duraklama Dönemi ve nedenleri)",
                        "Osmanlı-Avrupa ilişkileri","18. Yüzyılda Değişim ve Diplomasi",
                          "En Uzun Yüzyıl",
                          "Osmanlı Kültür ve Medeniyeti","20. Yüzyılda Osmanlı Devleti",
                         "I. Dünya Savaşı",
                         "Mondros Ateşkesi, İşgaller ve Cemiyetler",
                          "Kurtuluş Savaşına Hazırlık Dönemi",
                        "I. TBMM Dönemi",
                         "Kurtuluş Savaşı ve Antlaşmalar",
                        "II. TBMM Dönemi ve Çok Partili Hayata Geçiş",
                        "Türk İnkılabı","Atatürk İlkeleri",
                         "Atatürk Dönemi Türk Dış Politikası"]
    },
    "TYT Coğrafya":{
        "Dünya Haritaları Kampı (Öneri:Coğrafyanın Kodları)": 
            ["Dünya Haritaları"],
        "Konular":["Doğa ve İnsan Etkileşimi",
                   "Dünya’nın Şekli ve Hareketleri (Günlük ve Yıllık Hareketler, Sonuçları)",
                   "Coğrafi Konum (Mutlak ve Göreceli Konum)","Harita Bilgisi"
                   "Atmosfer ve Sıcaklık",
                   "İklimler","Basınç ve Rüzgarlar",
                    "Nem, Yağış ve Buharlaşma",
                      "İç Kuvvetler / Dış Kuvvetler"," Su – Toprak ve Bitkiler","Nüfus",
                       "Göç",
                       "Yerleşme",
                       "Türkiye’nin Yer Şekilleri",
                        "Ekonomik Faaliyetler",
                        "Bölgeler,Uluslararası Ulaşım Hatları,Çevre ve Toplum","Doğal Afetler"]
        
    },
    "TYT Felsefe": {
        "Temel Felsefe Konuları": [
            "Felsefenin Konusu",
            "Bilgi Felsefesi (Epistemoloji)",
            "Varlık Felsefesi (Ontoloji)",
            "Din, Kültür ve Medeniyet",
            "Ahlak Felsefesi",
            "Sanat Felsefesi",
            "Din Felsefesi",
            "Siyaset Felsefesi",
            "Bilim Felsefesi"
        ],
        "Felsefe Tarihi": [
            "İlk Çağ Felsefesi",
            "Sokrates ve Felsefesi",
            "Platon ve Felsefesi", 
            "Aristoteles ve Felsefesi",
            "Orta Çağ Felsefesi",
            "İslam Felsefesi (Farabi, İbn Sina)",
            "Hristiyan Felsefesi (Augustinus, Aquinalı Thomas)"
        ]
    },
    
    "TYT Din Kültürü": {
        "1. İnanç ve Temel Kavramlar": [
            "İnsan ve Din (İnanç)",
            "Vahiy ve Akıl"
        ],
        "2.  İslam ve İbadet: ve  Gençlik ve Değerler:": [
            "İbadet",
            "Hz. Muhammed'in Hayatı ve Örnekliği"
        ],
        "3. İslam Medeniyeti ve Özellikleri ve Allah İnancı ve İnsan:": [
            "Allah’ın Varlığı ve Birliği (Tevhid)",
            "Allah’ın İsim ve Sıfatları (Esma-ül Hüsna)",
            "Kur’an-ı Kerim’de İnsan ve Özellikleri",
            "İnsanın Allah İle İrtibatı (Dua, Tövbe, İbadet)"


        ],
        "4. Hz. Muhammed (S.A.V) ve Gençlik:": [
             "Kur’an-ı Kerim’de Gençler",
            "Bir Genç Olarak Hz. Muhammed",
            "Hz. Muhammed ve Gençler",
            "Bazı Genç Sahabiler"
        ],
        "5.Din ve Toplumsal Hayat":[ 
            "Din ve Aile",
            "Din, Kültür ve Sanat",
            "Din ve Çevre",
            "Din ve Sosyal Değişim",
            "Din ve Ekonomi",
            "Din ve Sosyal Adalet"],
        "6.Ahlaki Tutum ve Davranışlar":[
            "İslam ahlakının temel ilkeleri, iyi ve kötü davranışlar",
            "İslam Düşüncesinde Yorumlar: İslam Düşüncesinde İtikadi, Siyasi ve Fıkhi Yorumlar (Mezhepler)"
        ]
    },
    "TYT Fizik": {
        " Fiziğe Giriş ve Maddenin Özellikleri (9. Sınıf)": {
            "Fizik Bilimine Giriş": [
                "Fizik biliminin doğası, önemi ve diğer bilimlerle ilişkisi",
                "Fiziğin Doğası, Alt Dalları",
                "Temel ve Türetilmiş Büyüklükler"
            ],
            "Madde ve Özellikleri": [
                "Kütle, Hacim, Özkütle, Dayanıklılık",
                "Adezyon, Kohezyon, Yüzey Gerilimi, Kılcallık"
            ],
        },
        " Kuvvet, Hareket ve Enerji (9. Sınıf)": {
            "Hareket ve Kuvvet": [
                "Konum, Yol, Yer Değiştirme, Sürat, Hız, İvme",
                "Düzgün Doğrusal Hareket",
                "Newton'un Hareket Yasaları"
                "Etki-tepki, net kuvvet, dengelenmiş ve dengelenmemiş kuvvetler"
            ],
            "İş, Güç ve Enerji": [
                "İş, Güç, Enerji Çeşitleri (Kinetik, Potansiyel)",
                "Enerji dönüşümleri","Verim",
                "Enerjinin Korunumu",
                ],
                
            
            "Isı ve Sıcaklık":["Isı alışverişi, hal değişimleri, genleşme olayları, Öz Isı, Isı İletimi"]
        
        },
        "Elektrik, Basınç, Dalgalar ve Optik (10. Sınıf)": {
            
            
            "Basınç ve Kaldırma Kuvveti": [
                "Katı, Sıvı ve Gaz Basıncı, Pascal Prensibi, Bernoulli İlkesi",
                "Kaldırma Kuvveti"
            ],

            "Dalgalar": [
                "Su dalgaları, ses dalgaları, dalga boyu, frekans",
                ],
            "Optik":[ "Aynalar, mercekler, ışığın kırılması ve yansıması"],
            
            "Elektrik ve Manyetizma": [
                "Elektrik yükleri, akım, direnç, Ohm kanunu, devre elemanları, manyetik alan"
            ]
        },
    
    },
    "TYT Kimya": {
        "1. Kimya Bilimi, Atom ve Etkileşimler (9. Sınıf)": {
            "Kimya Bilimine Giriş": [
                "Kimyanın Alt Dalları ve Çalışma Alanları",
                "Laboratuvar Güvenlik Kuralları ve Semboller"
            ],
            "Atom ve Periyodik Sistem": [
                "Atom Modelleri, Atomun Yapısı (P, N, E)",
                "İzotop, İzoton, İzobar Tanecikler",
                "Periyodik Sistem Özellikleri ve Sınıflandırma"
            ],
            "Kimyasal Türler Arası Etkileşimler": [
                "Güçlü Etkileşimler (İyonik, Kovalent, Metalik Bağ)",
                "Zayıf Etkileşimler (van der Waals, Hidrojen Bağları)",
                "Fiziksel ve Kimyasal Değişimler"
            ]
        },
        "2. Madde Halleri ve Hesaplamalar (9. ve 10. Sınıf)": {
            "Maddenin Hâlleri ve Çevre Kimyası": [
                "Katı, Sıvı, Gaz, Plazma ve Hâl Değişimleri",
                "Gazların Temel Özellikleri",
                "Doğa ve Kimya (Su, Hava, Toprak Kirliliği, Geri Dönüşüm)"
            ],
            "Kimyanın Temel Kanunları ve Hesaplamalar": [
                "Kütlenin Korunumu, Sabit ve Katlı Oranlar Kanunu",
                "Mol Kavramı",
                "Kimyasal Tepkime Denklemleri, Denkleştirme",
                "Tepkime Türleri, Verim Hesaplamaları (Temel Düzey)"
            ]
        },
        "3. Karışımlar, Asitler/Bazlar ve Kimya Her Yerde (10. Sınıf)": {
            "Karışımlar ve Çözeltiler": [
                "Homojen ve Heterojen Karışımlar",
                "Çözelti Türleri, Çözünme Süreci",
                "Derişim Birimleri (Kütlece/Hacimce Yüzde)"
            ],
            "Asitler, Bazlar ve Tuzlar": [
                "Asit ve Baz Tanımları ve Özellikleri",
                "Asit-Baz Tepkimeleri, pH Kavramı",
                "Tuzlar ve Kullanım Alanları"
            ],
            "Kimya Her Yerde": [
                "Yaygın Polimerler",
                "Sabun ve Deterjanlar",
                "İlaçlar, Gıdalar, Temizlik Maddeleri"
            ]
        }
    },
    "TYT Biyoloji": {
        "1. Yaşam Bilimi ve Temel Bileşikler (9. Sınıf)": [
            "Canlıların Ortak Özellikleri",
            "Canlıların Yapısında Bulunan İnorganik Bileşikler",
            "Canlıların Yapısında Bulunan Organik Bileşikler"
        ],
        "2. Hücre, Sınıflandırma ve Âlemler (9. Sınıf)": [
            "Hücresel Yapılar ve Görevleri",
            "Hücre Zarından Madde Geçişleri",
            "Canlıların Sınıflandırılması",
            "Canlı Âlemleri"
        ],
        "3. Üreme, Kalıtım ve Genetik (10. Sınıf)": [
            "Hücre Döngüsü ve Mitoz",
            "Eşeysiz Üreme",
            "Mayoz",
            "Eşeyli Üreme",
            
            "Kalıtım Konusu",
            "Genetik Varyasyonlar"
        ],  
         
        "4. Ekoloji ve Çevre (10. Sınıf)": [
            "Ekosistem Ekolojisi",
            "Güncel Çevre Sorunları",
            "Doğal Kaynakların Sürdürülebilirliği",
            "Biyolojik Çeşitliliğin Korunması"
        ]
    },
    "AYT Matematik": {
        "Cebir, Fonksiyonlar,Sayı Sistemleri": [
            "Fonksiyonlar (İleri Düzey)",
            "Polinomlar",
            "2. Dereceden Denklemler",
            "Karmaşık Sayılar",
            "2. Dereceden Eşitsizlikler",
            "Parabol"
        
            "Trigonometri",
            "Logaritma",
            "Diziler",
            "Limit",
            "Türev",
            "İntegral"
        ],
        "Olasılık ": [
            "Permütasyon ve Kombinasyon",
            "Binom ve Olasılık",
            "İstatistik"
        ]
    },
    "AYT Edebiyat": {
        "1. Temel Edebiyat Bilgisi ve Kuramsal Yaklaşım": [
            "Güzel Sanatlar ve Edebiyat İlişkisi",
            "Metinlerin Sınıflandırılması",
            "Edebi Sanatlar (Söz ve Anlam Sanatları)",
            "Edebiyat Akımları (Batı ve Türk Edebiyatındaki Etkisi)",
            "Dünya Edebiyatı (Önemli Temsilciler ve Eserler)"
        ],
        "2. Anlam, Dil Bilgisi ve Şiir Yapısı": [
            "Anlam Bilgisi (Sözcük, Cümle, Paragraf Düzeyinde)",
            "Dil Bilgisi (Ses, Yapı, Cümle Öğeleri, Anlatım Bozuklukları)",
            "Şiir Bilgisi (Nazım Birimi, Ölçü, Uyak, Redif, Tema, İmge)"
        ],
        "3. Türk Edebiyatının Dönemleri (İslamiyet Öncesi ve Sonrası)": [
            "Türk Edebiyatı Dönemleri (Genel Özellikler)",
            "İslamiyet Öncesi Türk Edebiyatı (Sözlü ve Yazılı)",
            "İslamiyet Etkisindeki Geçiş Dönemi Edebiyatı",
            "Halk Edebiyatı (Anonim, Âşık, Tekke/Dini-Tasavvufi)",
            "Divan Edebiyatı (Nazım Biçimleri ve Türleri)"
        ],
        "4. Batı Etkisindeki Edebiyat (Tanzimat'tan Cumhuriyete)": [
            "Tanzimat Dönemi Edebiyatı (1. ve 2. Kuşak)",
            "Servet-i Fünun Edebiyatı (Edebiyat-ı Cedide)",
            "Fecr-i Ati Edebiyatı",
            "Milli Edebiyat Dönemi",
            "Cumhuriyet Dönemi Edebiyatı (Şiir, Hikaye, Roman, Tiyatro)"
        ],"5.Edebi Akımlar":[
            "Klasisizm",

            "Romantizm (Coşumculuk)",

            "Realizm (Gerçekçilik)",

            "Natüralizm (Doğalcılık)",

            "Parnasizm",

            "Sembolizm",

            "Empresyonizm (İzlenimcilik)",

            "Ekspresyonizm (Dışavurumculuk)",

            "Fütürizm (Gelecekçilik)",

            "Kübizm",

            "Dadaizm",

            "Sürrealizm (Gerçeküstücülük)",

            "Egzistansiyalizm (Varoluşçuluk)",

            "Ek:Dünya Edebiyatı"
        ]
    },
    "AYT Tarih": {
        "1. Tarih Bilimi ve İlk Çağlar": [
            "Tarih ve Zaman (Temel Kavramlar)", "İnsanlığın İlk Dönemleri", "Orta Çağ'da Dünya"
        ],
        "2. Türk-İslam Devletleri Dönemi": [
            "İlk ve Orta Çağlarda Türk Dünyası", "İslam Medeniyetinin Doğuşu",
            "Türklerin İslamiyet'i Kabulü ve İlk Türk İslam Devletleri", "Yerleşme ve Devletleşme Sürecinde Selçuklu Türkiyesi"
        ],
        "3. Klasik Çağ Osmanlı Tarihi (Kuruluş ve Yükselme)": [
            "Beylikten Devlete Osmanlı Siyaseti", "Devletleşme Sürecinde Savaşçılar ve Askerler",
            "Beylikten Devlete Osmanlı Medeniyeti", "Dünya Gücü Osmanlı",
            "Sultan ve Osmanlı Merkez Teşkilatı", "Klasik Çağda Osmanlı Toplum Düzeni"
        ],
        "4. Avrupa ve Osmanlı'da Değişim Süreci (Gerileme ve Dağılma)": [
            "Değişen Dünya Dengeleri Karşısında Osmanlı Siyaseti", "Değişim Çağında Avrupa ve Osmanlı",
            "Uluslararası İlişkilerde Denge Stratejisi (1774-1914)", "Devrimler Çağında Değişen Devlet-Toplum İlişkileri",
            "Sermaye ve Emek", "XIX. ve XX. Yüzyılda Değişen Gündelik Hayat"
        ],
        "5. Türkiye Cumhuriyeti Tarihi": [
            "XX. Yüzyıl Başlarında Osmanlı Devleti ve Dünya", "Milli Mücadele", "Atatürkçülük ve Türk İnkılabı"
        ],
        "6. Yakın Çağda Dünya ve Türkiye": [
            "İki Savaş Arasındaki Dönemde Türkiye ve Dünya", "II. Dünya Savaşı Sürecinde Türkiye ve Dünda",
            "II. Dünya Savaşı Sonrasında Türkiye ve Dünya", "Toplumsal Devrim Çağında Dünya ve Türkiye",
            "XXI. Yüzyılın Eşiğinde Türkiye ve Dünya"
        ]
    },
    "AYT Coğrafya": {
        "1. Doğal Sistemler ve Biyocoğrafya": [
            "Ekosistem", "Biyoçeşitlilik", "Biyomlar", "Ekosistemin Unsurları", "Enerji Akışı ve Madde Döngüsü"
        ],
        "2. Beşeri Coğrafya ve Demografi": [
            "Nüfus Politikaları", "Türkiye'de Nüfus ve Yerleşme", "Göç ve Şehirleşme"
        ],
        "3. Ekonomik Coğrafya ve Türkiye Ekonomisi": [
            "Ekonomik Faaliyetler ve Doğal Kaynaklar", "Türkiye Ekonomisi",
            "Türkiye'nin Ekonomi Politikaları", "Türkiye Ekonomisinin Sektörel Dağılımı",
            "Türkiye'de Tarım", "Türkiye'de Hayvancılık", "Türkiye'de Madenler ve Enerji Kaynakları", "Türkiye'de Sanayi", "Türkiye'de Ulaşım", "Türkiye'de Ticaret ve Turizm", "Geçmişten Geleceğe Şehir ve Ekonomi", "Türkiye'nin İşlevsel Bölgeleri ve Kalkınma Projeleri", "Hizmet Sektörünün Ekonomideki Yeri"
        ],
        "4. Küresel Bağlantılar ve Jeopolitik": [
            "Küresel Ticaret", "Bölgeler ve Ülkeler", "İlk Uygarlıklar", "Kültür Bölgeleri ve Türk Kültürü", "Sanayileşme Süreci: Almanya", "Tarım ve Ekonomi İlişkisi Fransa - Somali", "Ülkeler Arası Etkileşim", "Jeopolitik Konum", "Çatışma Bölgeleri", "Küresel ve Bölgesel Örgütler"
        ],
        "5. Çevre, İklim ve Sürdürülebilirlik": [
            "Ekstrem Doğa Olayları", "Küresel İklim Değişimi", "Çevre ve Toplum", "Çevre Sorunları ve Türleri", "Madenler ve Enerji Kaynaklarının Çevreye Etkisi", "Doğal Kaynakların Sürdürülebilir Kullanımı", "Ekolojik Ayak İzi", "Doğal Çevrenin Sınırlılığı", "Çevre Politikaları", "Çevresel Örgütler", "Çevre Anlaşmaları", "Doğal Afetler"
        ]
    },
    "AYT Fizik": {
        "1. Mekanik ve Enerji": [
            "Kuvvet ve Hareket (Vektörler, Bağıl, Newton Yasaları)", "İş - Güç - Enerji (Korunum, Verim)", "Atışlar (Yatay, Eğik, Düşey)", "Basit Makineler", "Kütle Merkezi - Tork - Denge"
        ],
        "2. Elektrik ve Manyetizma": [
            "Elektrostatik (Alan, Potansiyel)", "Elektrik ve Manyetizma (Akım, Direnç, Manyetik Alan, Kuvvet, İndüksiyon)"
        ],
        "3. Basınç, Maddenin Halleri ve Termodinamik": [
            "Madde ve Özellikleri (Katı, Sıvı, Gaz)", "Basınç - Kaldırma Kuvveti", "Isı - Sıcaklık - Genleşme (Termodinamik Yasaları Temelleri)"
        ],
        "4. Titreşim ve Dalgalar": [
            "Dalgalar (Yay, Su, Ses, Deprem)", "Optik (Yansıma, Kırılma, Ayna, Mercek)", "Düzgün Çembersel Hareket", "Basit Harmonik Hareket"
        ],
        "5. Modern Fizik ve Uygulamaları": [
            "Fizik Bilimine Giriş (Temeller)", "Atom Fiziğine Giriş ve Radyoaktivite", "Modern Fizik (Özel Görelilik, Kuantum, Fotoelektrik Olay)"
        ]
    },
    "AYT Kimya": {
        "Giriş Konular":
                ["Modern Atom Teorisi","Gazlar","Sıvı Çözeltiler ve Çözünürlük",
                "Kimyasal Tepkimelerde Enerji","Kimyasal Tepkimelerde Hız", ],
               
     "Kimyasal Tepkimelerde Denge":["Denge Sabiti", "Etkileyen Faktörler)", "Asit-Baz Dengesi (pH, pOH, Titrasyon)", "Çözünürlük Dengesi (Çözünürlük Çarpımı - Kçç"],
                
    "Kimya ve Elektrik":["(Redoks,Elektrot, Pil Potansiyeli)", "Elektroliz ve Korozyon", "Enerji Kaynakları ve Bilimsel Gelişmeler"],
        
                                                                                                                           

    "Organik Kimya": [
            "Organik Kimyaya Giriş (Temel Kavramlar, Hibritleşme)","Karbon Kimyasına Giriş", "Organik Kimya (Fonksiyonel Gruplar, Alkan, Alken, Alkin, Aromatikler)"
        ]
    },
    "AYT Biyoloji": {
        "1. İnsan Fizyolojisi (Sistemler)": [
            "Sinir Sistemi", "Endokrin Sistem ve Hormonlar", "Duyu Organları", "Destek ve Hareket Sistemi", "Sindirim Sistemi", "Dolaşım ve Bağışıklık Sistemi", "Solunum Sistemi", "Üriner Sistem (Boşaltım Sistemi)", "Üreme Sistemi ve Embriyonik Gelişim"
        ],
        "2. Moleküler Biyoloji ve Genetik": [
            "Nükleik Asitler", "Genden Proteine", "Genetik Şifre ve Protein Sentezi"
        ],
        "3. Canlılarda Enerji Dönüşümleri": [
            "Canlılık ve Enerji", "Canlılarda Enerji Dönüşümleri (ATP, Enzim)", "Fotosentez", "Kemosentez", "Hücresel Solunum"
        ],
        "4. Bitki Biyolojisi ve Ekoloji": [
            "Bitki Biyolojisi (Yapı, Taşıma, Beslenme)",
            "Bitkisel Hormonlar ve Hareketler",
            "Ekoloji ve Çevre "
        ]
    },
    "AYT Felsefe":{
        "Felsefe’nin Konusu":["Bilgi Felsefesi",
    "Varlık Felsefesi",
    "Ahlak Felsefesi",
    "Sanat Felsefesi",
    "Din Felsefesi",
    "Siyaset Felsefesi",
    "Bilim Felsefesi",
    "İlk Çağ Felsefesi",
    "MÖ 6. Yüzyıl – MS 2. Yüzyıl Felsefesi",
    "MS 2. Yüzyıl – MS 15. Yüzyıl Felsefesi",
    "15. Yüzyıl – 17. Yüzyıl Felsefesi",
    "18. Yüzyıl – 19. Yüzyıl Felsefesi",
    "20. Yüzyıl Felsefesi"],
        
        "Mantık Konuları":["Mantığa Giriş",
    "Klasik Mantık",
    "Mantık ve Dil",
    "Sembolik Mantık"
    ],
        "Psikoloji Bilimini Tanıyalım":[ 
        "Psikolojinin Temel Süreçleri",
        "Öğrenme Bellek Düşünme",
        "Ruh Sağlığının Temelleri"
        ],
        "Sosyolojiye Giriş":[
        "Birey ve Toplum",
        "Toplumsal Yapı",
       "Toplumsal Değişme ve Gelişme",
        "Toplum ve Kültür",
        "Toplumsal Kurumlar"] },

"AYT Din Kültürü ve Ahlak Bilgisi":{
    "Konular":["Dünya ve Ahiret",
              "Kur’an’a Göre Hz. Muhammed",
               "Kur’an’da Bazı Kavramlar",
               "Kur’an’dan Mesajlar]",
               "İnançla İlgili Meseleler",
               "İslam ve Bilim",
               "Anadolu'da İslam",
               "İslam Düşüncesinde Tasavvufi Yorumlar ve Mezhepler",
               "Güncel Dini Meseleler",
               "Yaşayan Dinler"]}

}

# ------------------------------------------------------------------------------------------------------
# --- DÜZELTME: KONU YAPISI AYRIŞTIRICI FONKSİYON ---
def get_topic_list(subject):
    """Belirli bir dersin tüm alt konularını düz bir liste olarak döndürür."""
    if subject not in YKS_TOPICS:
        return []

    topic_list = []
    subject_content = YKS_TOPICS[subject]

    for category, content in subject_content.items():
        if isinstance(content, dict):
            # Yapı A: Üç seviyeli (Alt Kategori kullanıldı)
            for sub_category, topics in content.items():
                for topic in topics:
                    topic_list.append(f"{subject} | {category} | {sub_category} | {topic}")
        elif isinstance(content, list):
            # Yapı B: İki seviyeli (Alt Kategori kullanılmadı)
            for topic in content:
                topic_list.append(f"{subject} | {category} | None | {topic}")
        
    return topic_list

def count_total_topics():
    """Toplam konu sayısını hesaplar"""
    total = 0
    for subject, content in YKS_TOPICS.items():
        if isinstance(content, dict):
            # content dict ise, normal işlemi yap
            for category, sub_content in content.items():
                if isinstance(sub_content, dict):
                    for sub_category, topics in sub_content.items():
                        total += len(topics)
                elif isinstance(sub_content, list):
                    total += len(sub_content)
        elif isinstance(content, list):
            # content liste ise, doğrudan sayısını ekle
            total += len(content)
    return total
# --- DÜZELTME BİTİŞİ ---

# Psikolojik çalışma teknikleri
STUDY_TECHNIQUES = {
    "Feynman Tekniği": {
        "icon": "🎓",
        "description": "Karmaşık konuları basit terimlerle açıklayarak öğrenme.",
        "steps": [
            "1. Konuyu basitleştirin: Tıpkı 5 yaşındaki bir çocuğa anlatırmış gibi, konuyu en temel kavramlara indirgeyin.",
            "2. Açıklayın: Konuyu kendi cümlelerinizle bir kağıda veya sesli olarak anlatın.", 
            "3. Anlamadığınız yerleri belirleyin: Açıklama sırasında takıldığınız, emin olamadığınız noktaları not alın.",
            "4. Geri dönün ve tekrar çalışın: Bu zayıf noktaları tekrar gözden geçirin, basitleştirin ve süreci tekrarlayın."
        ],
        "benefits": "Aktif hatırlamayı teşvik eder ve konuyu ezberlemek yerine gerçekten anlamanıza yardımcı olur.",
        "learning_style": ["Görsel", "Sosyal", "İşitsel", "Yazısal"]
    },
    "Cornell Not Alma Sistemi": {
        "icon": "📝",
        "description": "Ders notlarını organize etme ve etkili tekrar yapma sistemi.",
        "steps": [
            "1. Sayfayı 3 bölüme ayırın: Ana notlar, anahtar kelimeler ve özet.",
            "2. Notlarınızı alın: Ders sırasında ana notlar bölümüne notlarınızı tutun.", 
            "3. Anahtar kelimeler belirleyin: Notlarınızı gözden geçirerek önemli kavramları ve soruları yan bölüme yazın.",
            "4. Özet çıkarın: Sayfanın altındaki bölüme konuyu 1-2 cümleyle özetleyin."
        ],
        "benefits": "Notları düzenleyerek bilgiyi sindirir ve tekrar sürecini hızlandırır.",
        "learning_style": ["Yazısal", "Görsel"]
    },
    "Aktif Hatırlama & Aralıklı Tekrar": {
        "icon": "🎯",
        "description": "Bilgiyi pasif okumak yerine beyini zorlayarak öğrenme.",
        "steps": [
            "1. Kitabı kapatın: Bir konuyu okuduktan sonra, kitaba bakmadan hatırlamaya çalışın.",
            "2. Zorlayıcı sorular sorun: 'Bu konunun temel amacı neydi?', 'Hangi formüller vardı?' gibi sorularla beyninizi zorlayın.", 
            "3. Hatalarınızı düzeltin: Hatırlayamadığınız yerleri tekrar kitaptan kontrol edin.",
            "4. Aralıklı tekrar planı oluşturun: Konuları 1 gün, 3 gün, 1 hafta, 1 ay gibi aralıklarla tekrar edin."
        ],
        "benefits": "Bilgiyi uzun süreli hafızaya daha kalıcı bir şekilde yerleştirir.",
        "learning_style": ["Kinestetik", "Bireysel", "Yazısal"]
    },
    "Pomodoro Tekniği": {
        "icon": "🍅",
        "description": "Zamanı verimli kullanarak odaklanmayı artıran bir teknik.",
        "steps": [
            "1. 25 dakikalık bir zamanlayıcı kurun.",
            "2. Sadece belirlediğiniz konuya odaklanarak çalışın.", 
            "3. Zaman dolduğunda 5 dakikalık kısa bir mola verin.",
            "4. 4. Pomodoro'dan sonra 15-30 dakikalık uzun bir mola verin."
        ],
        "benefits": "Zaman yönetimi becerisini geliştirir, tükenmişliği önler ve motivasyonu korur.",
        "learning_style": ["Odaklanma"]
    }
}

LEARNING_STYLE_DESCRIPTIONS = {
    "Görsel": {
        "title": "👁️ Görsel Öğrenme Stili",
        "intro": "Sen bilgiyi en iyi gözlerinle algılayan bir öğrencisin. Zihninde canlandırdığın resimler, grafikler ve renkler, öğrenme sürecini çok daha kolay ve kalıcı hale getirir.",
        "strengths": [
            "Harita, grafik ve şemaları kolay anlarsın.",
            "Renkli notlar ve görsellerle daha hızlı öğrenirsin.",
            "Karmaşık bilgileri zihninde görselleştirme yeteneğin güçlüdür."
        ],
        "weaknesses": [
            "Sadece dinleyerek öğrenmekte zorlanabilirsin.",
            "Ders notları dağınık olduğunda odaklanman zorlaşır."
        ],
        "advice": "Bol bol zihin haritaları (mind maps) oluştur. Konuları akış şemalarıyla özetle. Önemli yerlerin altını farklı renk kalemlerle çiz."
    },
    "İşitsel": {
        "title": "👂 İşitsel Öğrenme Stili",
        "intro": "Sen bilgiyi en iyi kulaklarınla işleyen bir öğrencisin. Sesler, ritimler ve tonlamalar öğrenme sürecinde en büyük yardımcın. Bir şeyi sesli tekrar ederek veya dinleyerek öğrenmek sana daha kolay gelir.",
        "strengths": [
            "Dersleri dinleyerek anlama yeteneğin yüksektir.",
            "Tartışmalardan ve sohbetlerden çok şey öğrenirsin.",
            "Sesli tekrar yaparak ezberleme becerin güçlüdür."
        ],
        "weaknesses": [
            "Uzun sessiz çalışma ortamları seni sıkabilir.",
            "Gürültülü ortamlarda konsantre olmakta zorlanabilirsin."
        ],
        "advice": "Konuları sesli tekrar et veya kendi kendine anlat. Dersleri ses kaydına alıp tekrar dinle. Arkadaşlarınla konuları tartış ve birbirinize anlatın."
    },
    "Yazısal": {
        "title": "✍️ Yazısal Öğrenme Stili",
        "intro": "Senin için en önemli olan şey kelimeler ve notlardır. Bir konuyu anlamak için mutlaka okumalı, not almalı ve kendi cümlelerinle yazmalısın. Yazdıkça bilgiyi sindirir ve kalıcı hale getirirsin.",
        "strengths": [
            "Not tutma, özet çıkarma ve listeleme yeteneğin güçlüdür.",
            "Okuma ve yazma aktivitelerinde verimliliğin yüksektir.",
            "Yapısal ve sıralı bilgileri daha iyi kavrarsın."
        ],
        "weaknesses": [
            "Sadece dinlemeye dayalı derslerde zorlanabilirsin.",
            "Görsel veya kinestetik öğrenenlere göre daha az yaratıcı yöntemler tercih edebilirsin."
        ],
        "advice": "Ders notlarını temize çek ve özetlerini çıkar. Her konudan sonra konuyla ilgili kısa makaleler yaz. Notlarını kartlara yazarak ezber yap."
    },
    "Kinestetik": {
        "title": "🤸 Kinestetik Öğrenme Stili",
        "intro": "Senin için öğrenme, bir hareket ve deneyim işidir. Bir şeyi en iyi yaparak, dokunarak ve tecrübe ederek öğrenirsin. Yerinde duramayan, aktif bir öğrenme tarzın vardır.",
        "strengths": [
            "Uygulamalı derslerde (laboratuvar, atölye) çok başarılı olursun.",
            "Hareket halindeyken (yürüyüş gibi) düşünme ve öğrenme becerin yüksektir.",
            "Problem çözme ve deneme yanılma yoluyla öğrenmeye yatkınsın."
        ],
        "weaknesses": [
            "Uzun süre hareketsiz oturmak seni yorar ve dikkatini dağıtır.",
            "Teorik ve soyut konuları kavramakta zorlanabilirsin."
        ],
        "advice": "Ders çalışırken ara sıra ayağa kalkıp yürü. Mola vererek kısa fiziksel aktiviteler yap. Konuları somutlaştırmak için maketler veya modeller yap. 'Aktif Hatırlama' tekniğini bolca kullan."
    }
}

# Gelişmiş Öğrenme Stili Testi
LEARNING_STYLE_TEST = [
    {
        "question": "Yeni bir konuyu öğrenmeye başlarken en çok neye dikkat edersiniz?",
        "options": {
            "A": {"text": "Diyagramlara, grafiklere ve resimlere bakarım.", "style": "Görsel"},
            "B": {"text": "Öğretmenin veya bir başkasının konuyu anlatmasını dinlerim.", "style": "İşitsel"},
            "C": {"text": "Konuyla ilgili notlar alır ve metinleri okurum.", "style": "Yazısal"},
            "D": {"text": "Konuyla ilgili uygulamalar yapar, deneyerek öğrenirim.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Sınavda bir soruyu çözerken genellikle ne yaparsınız?",
        "options": {
            "A": {"text": "Soruyu kafamda canlandırır, adımları görselleştiririm.", "style": "Görsel"},
            "B": {"text": "Soruyu veya önemli kısımlarını kendi kendime sesli olarak okurum.", "style": "İşitsel"},
            "C": {"text": "Anahtar kelimeleri ve formülleri kağıda yazarım.", "style": "Yazısal"},
            "D": {"text": "Kalemimi oynatır, el hareketleriyle problemi anlamaya çalışırım.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Bir şeyi hatırlamak için en etkili yol hangisidir?",
        "options": {
            "A": {"text": "Renkli notlar, haritalar veya şemalar oluşturmak.", "style": "Görsel"},
            "B": {"text": "Konuyu başkasına anlatmak veya sesli tekrar etmek.", "style": "İşitsel"},
            "C": {"text": "Önemli noktaların listesini yapmak veya özetini çıkarmak.", "style": "Yazısal"},
            "D": {"text": "Uygulamalı bir örnek çözmek veya bir prototip yapmak.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Ders çalışırken en çok hangi aktivite sizi motive eder?",
        "options": {
            "A": {"text": "Videonun veya animasyonun içeriğini izlemek.", "style": "Görsel"},
            "B": {"text": "Podcast veya sesli kitap dinlemek.", "style": "İşitsel"},
            "C": {"text": "Kitap veya makale okumak, alıştırma soruları çözmek.", "style": "Yazısal"},
            "D": {"text": "Laboratuvar çalışması yapmak veya bir maket hazırlamak.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Bir yol tarifini nasıl almayı tercih edersiniz?",
        "options": {
            "A": {"text": "Bir harita veya çizim görmek.", "style": "Görsel"},
            "B": {"text": "Sesli olarak adım adım dinlemek.", "style": "İşitsel"},
            "C": {"text": "Yazılı bir listeyle takip etmek.", "style": "Yazısal"},
            "D": {"text": "Birinin önümden gitmesi veya bir kere denemek.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Arkadaşınızla konuşurken neye en çok dikkat edersiniz?",
        "options": {
            "A": {"text": "Vücut diline ve yüz ifadelerine.", "style": "Görsel"},
            "B": {"text": "Ses tonuna, vurgusuna ve kelime seçimlerine.", "style": "İşitsel"},
            "C": {"text": "Ne söylediğine, kelimelerin anlamına.", "style": "Yazısal"},
            "D": {"text": "Konuşurken yaptığı jest ve mimiklere.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Sınıfta dersi takip ederken en çok ne sizi rahatsız eder?",
        "options": {
            "A": {"text": "Tahtada dağınık bir yazı veya görselin olmaması.", "style": "Görsel"},
            "B": {"text": "Sınıfın gürültülü olması veya öğretmenin sesinin duyulmaması.", "style": "İşitsel"},
            "C": {"text": "Not almamak veya kitabın elimde olmaması.", "style": "Yazısal"},
            "D": {"text": "Uzun süre yerimde oturup hareket edememek.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Yeni bir kavramı anlamak için ne yaparsınız?",
        "options": {
            "A": {"text": "O kavramla ilgili bir resim, grafik veya şema çizerim.", "style": "Görsel"},
            "B": {"text": "O kavramı sesli olarak tekrar eder veya bir şarkıyla bağdaştırırım.", "style": "İşitsel"},
            "C": {"text": "Tanımını yazar ve farklı cümlelerle ifade etmeye çalışırım.", "style": "Yazısal"},
            "D": {"text": "O kavramı somutlaştıran bir model yapmaya veya canlandırmaya çalışırım.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Boş zamanlarınızda ne yapmaktan hoşlanırsınız?",
        "options": {
            "A": {"text": "Film izlemek veya fotoğraf çekmek.", "style": "Görsel"},
            "B": {"text": "Müzik dinlemek veya arkadaşlarımla sohbet etmek.", "style": "İşitsel"},
            "C": {"text": "Kitap okumak veya blog yazmak.", "style": "Yazısal"},
            "D": {"text": "Spor yapmak veya bir enstrüman çalmak.", "style": "Kinestetik"}
        }
    },
    {
        "question": "Bir şeyi en iyi nasıl hatırlarsınız?",
        "options": {
            "A": {"text": "Zihnimde o anın resmini canlandırarak.", "style": "Görsel"},
            "B": {"text": "O anda çalan müziği veya konuşulanları hatırlayarak.", "style": "İşitsel"},
            "C": {"text": "O konu hakkında yazdığım bir notu veya metni hatırlayarak.", "style": "Yazısal"},
            "D": {"text": "O anki fiziksel hissi veya yaptığım hareketi hatırlayarak.", "style": "Kinestetik"}
        }
    }
]

# Yeni eklenen kısım - "Benim Programım" sekmesi için gerekli fonksiyonlar ve veriler
STUDY_PROGRAMS = {
    "TYT Hızlandırma Programı (30 Gün)": {
        "description": "TYT konularını hızlıca tamamlamak için yoğun program",
        "duration": 30,
        "target": "TYT",
        "daily_hours": "4-6",
        "weekly_structure": {
            "Pazartesi": ["TYT Matematik", "TYT Türkçe"],
            "Salı": ["TYT Fen Bilimleri", "TYT Sosyal Bilimler"],
            "Çarşamba": ["TYT Matematik", "TYT Türkçe"],
            "Perşembe": ["TYT Fen Bilimleri", "TYT Sosyal Bilimler"],
            "Cuma": ["Genel Tekrar", "Deneme Çözümü"],
            "Cumartesi": ["Eksik Konu Tamamlama"],
            "Pazar": ["Dinlenme", "Hafif Tekrar"]
        }
    },
    "AYT Geçiş Programı (45 Gün)": {
        "description": "TYT'si tamamlanmış öğrenciler için AYT'ye geçiş programı",
        "duration": 45,
        "target": "AYT",
        "daily_hours": "5-7",
        "prerequisite": "TYT konularının %70'ini tamamlamış olmak"
    },
    "Derece Hedefli Program (90 Gün)": {
        "description": "İlk 10k hedefleyen öğrenciler için ileri seviye program",
        "duration": 90,
        "target": "TYT+AYT",
        "daily_hours": "6-8",
        "focus": "İleri düzey soru çözümü ve zaman yönetimi"
    }
}

DAILY_PLAN_TEMPLATES = {
    "Sabah Programı": {
        "06:00-07:00": "Uyanma, kahvaltı, hazırlık",
        "07:00-09:00": "Zor ders (Matematik/Fen)",
        "09:00-09:15": "Mola",
        "09:15-11:15": "İkinci zor ders",
        "11:15-12:00": "Hafif tekrar/okuma"
    },
    "Öğlen Programı": {
        "13:00-15:00": "Yeni konu öğrenme",
        "15:00-15:30": "Öğle arası",
        "15:30-17:30": "Soru çözümü",
        "17:30-18:00": "Mola",
        "18:00-19:30": "Tekrar ve not düzenleme"
    },
    "Akşam Programı": {
        "19:30-20:30": "Araştırma/okuma",
        "20:30-22:00": "Eksik tamamlama",
        "22:00-22:30": "Gün değerlendirme",
        "22:30-23:00": "Planlama (yarınki hedefler)"
    }
}

def calculate_study_schedule(user_data, selected_program):
    """Kullanıcının mevcut durumuna göre kişiselleştirilmiş çalışma programı oluşturur"""
    program = STUDY_PROGRAMS[selected_program]
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    
    # Eksik konuları tespit et
    incomplete_topics = {}
    for subject in YKS_TOPICS.keys():
        subject_topics = get_topic_list(subject)
        completed = 0
        for topic in subject_topics:
            net_str = topic_progress.get(topic, '0')
            try:
                net = int(float(net_str))
                if net >= 14:  # Uzman seviye
                    completed += 1
            except (ValueError, TypeError):
                continue
        
        total = len(subject_topics)
        if total > 0 and completed < total:
            incomplete_topics[subject] = {
                'completed': completed,
                'total': total,
                'percent': (completed / total) * 100
            }
    
    return {
        'program': program,
        'incomplete_topics': incomplete_topics,
        'start_date': datetime.now().strftime("%Y-%m-%d"),
        'daily_plans': generate_daily_plans(incomplete_topics, program)
    }

def generate_daily_plans(incomplete_topics, program):
    """Eksik konulara göre günlük planlar oluşturur"""
    daily_plans = {}
    
    # Öncelikli dersleri belirle (kullanıcının alanına göre)
    user_field = st.session_state.users_db[st.session_state.current_user].get('field', 'Sayısal')
    
    if user_field == "Sayısal":
        priority_subjects = ["TYT Matematik", "TYT Fizik", "TYT Kimya", "TYT Biyoloji", "AYT Matematik", "AYT Fizik", "AYT Kimya", "AYT Biyoloji"]
    elif user_field == "Eşit Ağırlık":
        priority_subjects = ["TYT Matematik", "TYT Türkçe", "AYT Matematik", "AYT Edebiyat", "AYT Coğrafya"]
    else:  # Sözel
        priority_subjects = ["TYT Türkçe", "TYT Tarih", "TYT Coğrafya", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
    
    # Program süresince günlük plan oluştur
    for day in range(program['duration']):
        daily_plans[day + 1] = {
            'focus_subjects': [],
            'daily_goals': [],
            'completion_status': False
        }
    
    return daily_plans

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()
    

def load_users_from_firebase():
    """Firebase'den kullanıcıları yükler ve tutarlılık için tüm alanları normalize eder."""
    if db_ref is None:
        return {}
    
    try:
        users_data = db_ref.get()
        if not users_data:
            return {}
        
        # Normalize edilmiş kullanıcı verilerini döndür
        users = {}
        for username, user_data in users_data.items():
            normalized_row = {field: user_data.get(field, '') for field in FIELDNAMES}
            users[username] = normalized_row
        
        return users
    except Exception as e:
        st.error(f"Firebase'den kullanıcı verileri yüklenirken hata oluştu: {e}")
        return {}

def update_user_in_firebase(username, data_to_update):
    """Firebase'deki bir kullanıcının bilgilerini güncelle"""
    if db_ref is None:
        st.error("Firebase bağlantısı yok!")
        return
    
    try:
        # Kullanıcının Firebase'deki verisini güncelle
        user_ref = db_ref.child(username)
        user_ref.update(data_to_update)
    except Exception as e:
        st.error(f"Firebase'de kullanıcı verileri güncellenirken hata oluştu: {e}")
def login_user(username, password):
    """Kullanıcı girişi"""
    users_db = load_users_from_firebase()
    user_data = users_db.get(username)
    if user_data and user_data["password"] == password:
        st.session_state.current_user = username
        st.session_state.users_db = users_db
        return True
    return False

def get_user_data():
    """Giriş yapan kullanıcının verilerini getir"""
    if st.session_state.current_user:
        return st.session_state.users_db.get(st.session_state.current_user, {})
    return None

def calculate_level(net):
    """Net sayısına göre seviye hesapla"""
    if net <= 5: return "🔴 Zayıf Seviye (0-5 net)"
    elif net <= 8: return "🟠 Temel Seviye (5-8 net)"
    elif net <= 14: return "🟡 Orta Seviye (8-14 net)"
    elif net <= 18: return "🟢 İyi Seviye (14-18 net)"
    else: return "🔵 Uzman Seviye (18-20 net)"

def calculate_subject_progress(user_data):
    """Ders bazında ilerlemeyi hesapla"""
    progress_data = {}
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    
    for subject, topics in YKS_TOPICS.items():
        total_topics = 0
        completed_topics = 0
        
        # topics'in türünü kontrol et
        if isinstance(topics, dict):
            # topics bir dict ise, normal işlemi yap
            for main_topic, sub_topics_dict in topics.items():
                if isinstance(sub_topics_dict, dict):
                    for sub_topic, details in sub_topics_dict.items():
                        total_topics += len(details)
                        for detail in details:
                            topic_key = f"{subject} | {main_topic} | {sub_topic} | {detail}"
                            net_str = topic_progress.get(topic_key, '0')
                            try:
                                net = int(float(net_str))
                                if net >= 14:
                                    completed_topics += 1
                            except (ValueError, TypeError):
                                continue
                elif isinstance(sub_topics_dict, list):
                    total_topics += len(sub_topics_dict)
                    for detail in sub_topics_dict:
                        topic_key = f"{subject} | {main_topic} | None | {detail}"
                        net_str = topic_progress.get(topic_key, '0')
                        try:
                            net = int(float(net_str))
                            if net >= 14:
                                completed_topics += 1
                        except (ValueError, TypeError):
                            continue
        elif isinstance(topics, list):
            # topics bir list ise, doğrudan liste üzerinde işlem yap
            total_topics = len(topics)
            for detail in topics:
                topic_key = f"{subject} | None | None | {detail}"
                net_str = topic_progress.get(topic_key, '0')
                try:
                    net = int(float(net_str))
                    if net >= 14:
                        completed_topics += 1
                except (ValueError, TypeError):
                    continue
                        
        if total_topics > 0:
            progress_percent = (completed_topics / total_topics * 100)
            progress_data[subject] = {
                'completed': completed_topics,
                'total': total_topics,
                'percent': round(progress_percent, 1)
            }
        else:
            progress_data[subject] = {'completed': 0, 'total': 0, 'percent': 0}
            
    return progress_data

def determine_learning_style(answers):
    """Öğrenme stilini belirle ve yüzdelik puanları hesapla"""
    style_scores = {"Görsel": 0, "İşitsel": 0, "Yazısal": 0, "Kinestetik": 0}
    for i, answer in enumerate(answers):
        selected_style = LEARNING_STYLE_TEST[i]["options"][answer]["style"]
        style_scores[selected_style] += 1
        
    total_score = sum(style_scores.values())
    if total_score == 0:
        return {}, ""
        
    style_percentages = {style: round((score / total_score) * 100, 1) for style, score in style_scores.items()}
    dominant_style = max(style_percentages, key=style_percentages.get)
    
    return style_percentages, dominant_style

def get_recommended_techniques(style_scores):
    """Öğrenme stillerine göre en uygun çalışma tekniklerini önerir"""
    dominant_styles = [style for style, score in style_scores.items() if score > 5]
    
    recommended_techniques = {}
    for technique_name, info in STUDY_TECHNIQUES.items():
        match_count = sum(1 for style in info['learning_style'] if style in dominant_styles)
        if match_count > 0:
            recommended_techniques[technique_name] = match_count
            
    sorted_techniques = sorted(recommended_techniques.keys(), key=lambda k: recommended_techniques[k], reverse=True)
    
    return sorted_techniques[:4]

def display_progress_summary(user_data, progress_data):
    """Ana sayfada ilerleme özeti gösterir"""
    
    overall_progress = calculate_subject_progress(user_data)
    total_completed = sum(data['completed'] for data in overall_progress.values())
    total_topics = count_total_topics()
    overall_percent = (total_completed / total_topics * 100) if total_topics > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("✅ Tamamlanan Konular", f"{total_completed}/{total_topics}")
    
    with col2:
        st.metric("📚 Toplam Ders", len(progress_data))
    
    with col3:
        avg_per_subject = sum(data['percent'] for data in progress_data.values()) / len(progress_data) if progress_data else 0
        st.metric("📈 Ders Ortalaması", f"%{avg_per_subject:.1f}")
    with col4:
        st.metric("🎯 Hedef Bölüm", user_data.get('target_department', 'Belirlenmedi'), delta_color="off")      
    
    st.markdown("---")
    
    st.subheader("📈 Ders Bazında İlerleme")
    
    if progress_data:
        for subject, data in progress_data.items():
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.write(f"**{subject}**")
                st.progress(data['percent'] / 100)
            with col_b:
                st.write(f"{data['completed']}/{data['total']} konu")
                st.write(f"%{data['percent']:.1f}")
        
        st.markdown("---")
    
    else:
        st.info("Henüz ilerleme verisi bulunmuyor. Konu Takip sekmesinden ilerlemenizi kaydedin.")

# YKS Takip fonksiyonları
def yks_takip_page(user_data):
    st.markdown(f'<div class="main-header"><h1>🎯 YKS Takip & Planlama Sistemi</h1><p>Haftalık hedeflerinizi belirleyin ve takip edin</p></div>', unsafe_allow_html=True)
    
    # Ana panelden bilgileri al
    student_grade = user_data.get('grade', '')
    student_field = user_data.get('field', '')
    learning_style = user_data.get('learning_style', '')
    
    st.subheader("📋 Öğrenci Bilgileri")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🎓 Sınıf", student_grade)
    with col2:
        st.metric("📚 Alan", student_field)
    with col3:
        st.metric("🧠 Öğrenme Stili", learning_style)
    
    st.markdown("---")
    
    # İlk kez giriş için anket sistemi
    if not has_completed_yks_survey(user_data):
        show_yks_survey(user_data)
    else:
        show_weekly_planner(user_data)

def has_completed_yks_survey(user_data):
    """Kullanıcının YKS anketini tamamlayıp tamamlamadığını kontrol eder"""
    survey_data = user_data.get('yks_survey_data', '')
    if survey_data:
        try:
            data = json.loads(survey_data)
            return all(key in data for key in ['program_type', 'daily_subjects', 'study_style', 
                                              'difficult_subjects', 'sleep_time', 'disliked_subjects', 
                                              'book_type', 'rest_day'])
        except:
            return False
    return False

def show_yks_survey(user_data):
    """YKS anketi gösterir"""
    st.subheader("📝 İlk Kurulum: Size Özel Program İçin Bilgilerinizi Alalım")
    
    student_field = user_data.get('field', '')
    
    with st.form("yks_survey_form"):
        # Program türü
        st.markdown("### 🎛️ Haftalık Programınızı Nasıl Oluşturalım?")
        program_type = st.radio(
            "Program türünü seçin:",
            ["🎛️ Kişiselleştirilmiş Program (Kendi gün/saatlerimi belirleyeyim)",
             "📋 Hazır Bilimsel Program (Bana otomatik program hazırlansın)"]
        )
        
        # Günlük ders sayısı
        st.markdown("### 📚 Günlük Ders Dağılımı")
        st.write("Günde kaç farklı ders çalışmayı istersiniz?")
        daily_subjects = st.selectbox("Ders sayısı:", [2, 3, 4, 5], index=1)
        if daily_subjects in [2, 3, 4]:
            st.success("✅ Bilimsel Öneri: 2-4 ders seçiminiz optimal aralıkta! (İdeal olan ise 3'tür)")
        
        # Çalışma stili
        st.markdown("### 🍽️ Çalışma Stilinizi Keşfedin")
        study_style = st.radio(
            "Hangi çalışma stilini tercih edersiniz?",
            ["🍰 En güzel kısmı sona saklarım (Zor dersleri sona saklama)",
             "🍽️ Her şeyi karışık paylaşırım (Dengeli dağılım)", 
             "🔥 En güzelinden başlarım (Zor dersler ön alma)"]
        )
        
        # Dersler alan bazında belirlenir
        all_subjects = get_subjects_by_field_yks(student_field)
        
        # Zorluk analizi
        st.markdown("### 🎯 Zorluk Analizi")
        difficult_subjects = st.multiselect(
            "En zorlandığınız 3 dersi seçin (en zordan başlayarak):",
            all_subjects, max_selections=3
        )
        
        # Uyku saati
        st.markdown("### 😴 Uyku Düzeni")
        st.info("🧠 Bilimsel olarak ideal uyku süresi 7 saattir. Tavsiye edilen uyku saatleri: 23:00 - 06:00 arası")
        sleep_option = st.selectbox(
            "Uyku saatinizi seçin:",
            ["23:00 - 06:00 (7 saat) - Önerilen", "22:00 - 05:00 (7 saat)",
             "00:00 - 07:00 (7 saat)", "01:00 - 08:00 (7 saat)", "Diğer"]
        )
        
        # En az sevilen dersler
        st.markdown("### 😕 Motivasyon Analizi")
        disliked_subjects = st.multiselect(
            "En az sevdiğiniz 3 dersi seçin:", all_subjects, max_selections=3
        )
        
        # Kitap tercihleri
        st.markdown("### 📖 Kitap Önerileri")
        book_type = st.selectbox(
            "Hangi tür kitapları okumayı seversiniz?",
            list(BOOK_RECOMMENDATIONS.keys())
        )
        
        # Tatil günü
        st.markdown("### 🌴 Dinlenme Günü")
        rest_day = st.selectbox(
            "Haftanın hangi günü tamamen dinlenmek istersiniz?",
            ["Pazar", "Cumartesi", "Cuma", "Pazartesi", "Salı", "Çarşamba", "Perşembe"]
        )
        
        # Form submit
        if st.form_submit_button("💾 Bilgilerimi Kaydet ve Planlama Sistemine Geç", type="primary"):
            survey_data = {
                'program_type': program_type,
                'daily_subjects': daily_subjects,
                'study_style': study_style,
                'difficult_subjects': difficult_subjects,
                'sleep_time': sleep_option,
                'disliked_subjects': disliked_subjects,
                'book_type': book_type,
                'rest_day': rest_day,
                'created_at': datetime.now().isoformat()
            }
            
            # Kullanıcı verisini güncelle
            update_user_in_firebase(st.session_state.current_user, 
                              {'yks_survey_data': json.dumps(survey_data)})
            st.session_state.users_db = load_users_from_firebase()
            
            # Kitap önerilerini göster
            st.success("✅ Bilgileriniz kaydedildi!")
            st.markdown("### 📚 Size Özel Kitap Önerileri")
            for book in BOOK_RECOMMENDATIONS[book_type]:
                st.write(f"📖 {book}")
            
            st.rerun()

def show_weekly_planner(user_data):
    """YENİ SİSTEMATİK HAFTALİK PLANLAMA SİSTEMİ"""
    # Anket verilerini yükle
    survey_data = json.loads(user_data.get('yks_survey_data', '{}'))
    student_field = user_data.get('field', '')
    
    # Sistematik haftalık plan al
    weekly_plan = get_weekly_topics_from_topic_tracking(user_data, student_field, survey_data)
    
    # Üst dashboard
    show_progress_dashboard(weekly_plan, user_data)
    
    st.markdown("---")
    
    # Ana haftalık plan
    st.markdown("### 📅 Bu Haftanın Sistematik Planı")
    
    # İki kolon: Yeni Konular ve Tekrarlar
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### 🎯 YENİ KONULAR (Sıralı İlerleme)")
        show_new_topics_section(weekly_plan.get('new_topics', []), user_data)
    
    with col2:
        st.markdown("#### 🔄 TEKRAR EDİLECEK KONULAR")
        show_review_topics_section(weekly_plan.get('review_topics', []), user_data)
    
    st.markdown("---")
    
    # Interaktif planlayıcı
    show_interactive_systematic_planner(weekly_plan, survey_data)
    
    st.markdown("---")
    
    # Akıllı öneriler
    show_systematic_recommendations(weekly_plan, survey_data, student_field)

def show_progress_dashboard(weekly_plan, user_data):
    """İlerleme dashboard'u"""
    projections = weekly_plan.get('projections', {})
    
    st.markdown("### 📊 GENEL İLERLEME DURUMU")
    
    # Ana metrikler
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        overall_progress = projections.get('overall_progress', 0)
        st.metric(
            "🎯 Genel İlerleme",
            f"%{overall_progress:.1f}",
            f"Hedef: %100"
        )
    
    with col2:
        tyt_progress = projections.get('tyt_progress', 0)
        st.metric(
            "📚 TYT İlerleme", 
            f"%{tyt_progress:.1f}",
            f"Tahmini: Mart 2025" if tyt_progress < 80 else "Yakında!"
        )
    
    with col3:
        ayt_progress = projections.get('ayt_progress', 0)
        st.metric(
            "📖 AYT İlerleme",
            f"%{ayt_progress:.1f}", 
            f"Tahmini: Mayıs 2025" if ayt_progress < 70 else "Yakında!"
        )
    
    with col4:
        weekly_target = weekly_plan.get('week_target', 0)
        success_rate = weekly_plan.get('success_target', 0.8)
        st.metric(
            "📅 Bu Hafta",
            f"{weekly_target} konu",
            f"Hedef: %{success_rate*100:.0f} başarı"
        )
    
    # İlerleme çubukları
    st.markdown("#### 📈 Detaylı İlerleme")
    
    progress_col1, progress_col2 = st.columns(2)
    
    with progress_col1:
        st.write("**TYT İlerleme**")
        st.progress(tyt_progress / 100)
        
    with progress_col2:
        st.write("**AYT İlerleme**") 
        st.progress(ayt_progress / 100)
    
    # Tahmini tamamlanma
    estimated_completion = projections.get('estimated_completion')
    if estimated_completion:
        st.info(f"📅 **Tahmini Genel Tamamlanma:** {estimated_completion}")

def show_new_topics_section(new_topics, user_data):
    """Yeni konular bölümü"""
    if not new_topics:
        st.warning("📊 Yeni konu bulunamadı. Konu Takip sekmesinden değerlendirmelerinizi yapın.")
        return
    
    # Öncelik gruplarına ayır (YENİ 5'Lİ SİSTEM)
    high_priority = [t for t in new_topics if t.get('priority') == 'HIGH']
    medium_priority = [t for t in new_topics if t.get('priority') == 'MEDIUM'] 
    normal_priority = [t for t in new_topics if t.get('priority') == 'NORMAL']
    low_priority = [t for t in new_topics if t.get('priority') == 'LOW']
    minimal_priority = [t for t in new_topics if t.get('priority') == 'MINIMAL']
    
    # Acil - Zayıf konular
    if high_priority:
        st.markdown("##### 🔥 Acil - Zayıf Konular")
        for topic in high_priority:
            show_topic_card(topic, "HIGH")
    
    # Öncelikli - Temel konular
    if medium_priority:
        st.markdown("##### ⚡ Öncelikli - Temel Konular")
        for topic in medium_priority:
            show_topic_card(topic, "MEDIUM")
    
    # Normal - Orta konular
    if normal_priority:
        st.markdown("##### 🎯 Normal - Orta Konular")
        for topic in normal_priority:
            show_topic_card(topic, "NORMAL")
    
    # Düşük - İyi konular
    if low_priority:
        st.markdown("##### 🟢 Düşük - İyi Konular")
        for topic in low_priority:
            show_topic_card(topic, "LOW")
    
    # Minimal - Uzman konular
    if minimal_priority:
        st.markdown("##### ⭐ Minimal - Uzman Konular")
        for topic in minimal_priority:
            show_topic_card(topic, "MINIMAL")

def show_review_topics_section(review_topics, user_data):
    """Tekrar konuları bölümü"""
    if not review_topics:
        st.info("🎉 Bu hafta tekrar edilecek konu yok!")
        return
    
    # Öncelik gruplarına ayır
    high_reviews = [t for t in review_topics if t.get('priority') == 'REPEAT_HIGH']
    medium_reviews = [t for t in review_topics if t.get('priority') == 'REPEAT_MEDIUM']
    normal_reviews = [t for t in review_topics if t.get('priority') == 'REPEAT_NORMAL']
    
    # Yüksek öncelikli tekrarlar
    if high_reviews:
        st.markdown("##### 🔄 Yüksek Öncelikli Tekrar")
        for topic in high_reviews:
            show_review_card(topic, "REPEAT_HIGH")
    
    # Öncelikli tekrarlar
    if medium_reviews:
        st.markdown("##### 🔄 Öncelikli Tekrar")
        for topic in medium_reviews:
            show_review_card(topic, "REPEAT_MEDIUM")
    
    # Normal tekrarlar
    if normal_reviews:
        st.markdown("##### 🔄 Normal Tekrar")
        for topic in normal_reviews:
            show_review_card(topic, "REPEAT_NORMAL")

def show_topic_card(topic, priority_type):
    """Konu kartı gösterici"""
    priority_info = PRIORITY_CATEGORIES[priority_type]
    
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {priority_info['color']}22 0%, {priority_info['color']}11 100%); 
                    border-left: 4px solid {priority_info['color']}; 
                    padding: 12px; border-radius: 8px; margin-bottom: 8px;'>
            <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                <span style='font-size: 18px; margin-right: 8px;'>{priority_info['icon']}</span>
                <strong style='color: {priority_info['color']};'>{topic['subject']}</strong>
            </div>
            <div style='margin-left: 26px;'>
                <div><strong>📖 {topic['topic']}</strong></div>
                <div style='font-size: 14px; color: #666; margin-top: 4px;'>
                    └ {topic['detail']} 
                    <span style='background: #f0f0f0; padding: 2px 6px; border-radius: 10px; margin-left: 8px;'>
                        Mevcut: {topic['net']} net
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_review_card(topic, priority_type):
    """Tekrar konu kartı"""
    priority_info = PRIORITY_CATEGORIES[priority_type]
    
    with st.container():
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {priority_info['color']}22 0%, {priority_info['color']}11 100%); 
                    border-left: 4px solid {priority_info['color']}; 
                    padding: 12px; border-radius: 8px; margin-bottom: 8px;'>
            <div style='display: flex; align-items: center; margin-bottom: 8px;'>
                <span style='font-size: 16px; margin-right: 8px;'>{priority_info['icon']}</span>
                <strong style='color: {priority_info['color']};'>{topic['subject']}</strong>
            </div>
            <div style='margin-left: 24px;'>
                <div><strong>📖 {topic['topic']}</strong></div>
                <div style='font-size: 14px; color: #666; margin-top: 4px;'>
                    └ {topic['detail']} 
                    <span style='background: #e8f5e8; padding: 2px 6px; border-radius: 10px; margin-left: 8px;'>
                        {topic['net']} net • {topic['days_passed']} gün önce
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_interactive_systematic_planner(weekly_plan, survey_data):
    """Basit ve etkili haftalık planlayıcı"""
    
    # Güncel hafta tarih aralığını hesapla
    from datetime import datetime, timedelta
    import locale
    
    today = datetime.now()
    
    # Türkçe ay isimleri
    turkish_months = {
        1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
        7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
    }
    
    # Bu haftanın pazartesini bul
    days_since_monday = today.weekday()  # 0=Pazartesi, 6=Pazar
    monday_this_week = today - timedelta(days=days_since_monday)
    sunday_this_week = monday_this_week + timedelta(days=6)
    
    # Tarih aralığı formatla (Türkçe ay isimleri ile)
    monday_str = f"{monday_this_week.day} {turkish_months[monday_this_week.month]}"
    sunday_str = f"{sunday_this_week.day} {turkish_months[sunday_this_week.month]} {sunday_this_week.year}"
    week_range = f"{monday_str} - {sunday_str}"
    
    # Haftalık planlama tablosu
    st.markdown(f"#### 📅 Bu Haftanın Programı ({week_range})")
    
    # Günler
    days = ["PAZARTESİ", "SALI", "ÇARŞAMBA", "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"]
    rest_day = survey_data.get('rest_day', 'Pazar')
    
    # Session state'te planları tut
    if 'day_plans' not in st.session_state:
        st.session_state.day_plans = {day: [] for day in days}
    
    # Günleri göster
    cols = st.columns(7)
    
    for i, day in enumerate(days):
        with cols[i]:
            # Gün başlığı
            if day.title() == rest_day:
                st.markdown(f"**{day}** 🌴")
                st.info("🌴 Dinlenme Günü")
            else:
                st.markdown(f"**{day}**")
                
                # Bu günde planlanmış konuları göster
                day_plan = st.session_state.day_plans.get(day, [])
                if day_plan:
                    for j, plan_item in enumerate(day_plan):
                        with st.container():
                            priority = plan_item.get('priority', 'NORMAL')
                            priority_info = PRIORITY_CATEGORIES.get(priority, PRIORITY_CATEGORIES['NORMAL'])
                            
                            st.markdown(f"<div style='background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); padding: 8px; border-radius: 5px; margin-bottom: 5px; color: white; font-size: 12px;'>"
                                      f"<strong>{priority_info['icon']} {plan_item['subject']}</strong><br>"
                                      f"{plan_item['topic']}<br>"
                                      f"<small>🕰️ {plan_item['time']}</small>"
                                      f"</div>", unsafe_allow_html=True)
                            
                            # Kaldırma butonu
                            if st.button(f"❌", key=f"remove_{day}_{j}", help="Bu konuyu kaldır"):
                                st.session_state.day_plans[day].pop(j)
                                st.rerun()
                
                # Boş alan göstergesi
                if not day_plan:
                    st.markdown("<div style='border: 2px dashed #e0e0e0; padding: 20px; text-align: center; color: #999; border-radius: 5px;'>Konu yok</div>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Konuları göster ve ekleme sistemi
    st.markdown("#### 📋 Bu Haftanın Konuları")
    
    # Tüm konuları birleştir
    all_topics = weekly_plan.get('new_topics', []) + weekly_plan.get('review_topics', [])
    
    if all_topics:
        # Konuları kutu olarak göster
        topic_cols = st.columns(3)  # 3'lü gruplar halinde
        
        for i, topic in enumerate(all_topics):
            with topic_cols[i % 3]:
                # Konu kutusu
                with st.container():
                    priority = topic.get('priority', 'NORMAL')
                    priority_info = PRIORITY_CATEGORIES.get(priority, PRIORITY_CATEGORIES['NORMAL'])
                    
                    st.markdown(f"<div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 15px; border-radius: 8px; margin-bottom: 5px; color: white;'>"
                              f"<strong>📚 {topic['subject']}</strong><br>"
                              f"{topic['topic']}<br>"
                              f"<small>{topic['detail']}</small><br>"
                              f"<small>🎯 {topic['net']} net</small>"
                              f"</div>", unsafe_allow_html=True)
                    
                    # Öncelik bilgisi kutunun altında
                    st.markdown(f"<div style='text-align: center; color: {priority_info['color']}; font-weight: bold; font-size: 12px; margin-bottom: 10px;'>"
                              f"{priority_info['icon']} {priority_info['name']}"
                              f"</div>", unsafe_allow_html=True)
                    
                    # Ekleme formu - sadeleştirilmiş
                    with st.expander(f"📅 Programa Ekle", expanded=False):
                        selected_day = st.selectbox(
                            "Gün seçin:", 
                            [d for d in days if d.title() != rest_day],
                            key=f"day_select_{i}"
                        )
                        
                        time_slot = st.text_input(
                            "Saat aralığı:",
                            placeholder="17:00-18:30",
                            key=f"time_input_{i}"
                        )
                        
                        if st.button("➕ Ekle", key=f"add_topic_{i}", type="primary"):
                            if time_slot:
                                # Konuyu programa ekle
                                new_plan_item = {
                                    'subject': topic['subject'],
                                    'topic': topic['topic'],
                                    'detail': topic['detail'],
                                    'time': time_slot,
                                    'priority': topic.get('priority', 'NORMAL')
                                }
                                
                                if selected_day not in st.session_state.day_plans:
                                    st.session_state.day_plans[selected_day] = []
                                
                                st.session_state.day_plans[selected_day].append(new_plan_item)
                                st.success(f"✅ {topic['topic']} eklendi!")
                                st.rerun()
                            else:
                                st.warning("🕰️ Saat aralığı gerekli!")
    
    else:
        st.info("📊 Bu hafta için otomatik konu bulunamadı. Konu Takip sekmesinden konularınızı değerlendirin.")
    
    st.markdown("---")
    st.markdown("#### 📊 Bu Haftanın Programı")
    
    total_planned = sum(len(plans) for plans in st.session_state.day_plans.values())
    
    if total_planned > 0:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📅 Planlanmış Konu", total_planned)
        with col2:
            active_days = len([day for day, plans in st.session_state.day_plans.items() if plans])
            st.metric("📆 Aktif Gün", active_days)
        
        # Temizleme butonu
        if st.button("🗑️ Programı Temizle", type="secondary"):
            st.session_state.day_plans = {day: [] for day in days}
            st.success("✅ Program temizlendi!")
            st.rerun()
    else:
        st.info("📅 Henüz konu planlanmamış. Yukarıdaki konulardan seçip günlere ekleyin.")
    
    st.markdown("---")
    
    # TYT/AYT durumu bilgilendirmesi
    if 'tyt_progress' in weekly_plan and 'ayt_enabled' in weekly_plan:
        tyt_progress = weekly_plan.get('tyt_progress', 0)
        ayt_enabled = weekly_plan.get('ayt_enabled', False)
        tyt_math_completed = weekly_plan.get('tyt_math_completed', 0)
        
        st.markdown("#### 📋 Öğrenim Durumu")
        
        if not ayt_enabled:
            st.info(f"""
            🎯 **TYT Aşaması** - AYT henüz başlamadı
            
            • TYT İlerleme: **%{tyt_progress:.1f}** (Hedef: %60)
            • TYT Matematik: **{tyt_math_completed}** konu tamamlandı (Hedef: 12)
            
            🔒 **AYT Başlatma Koşulları:** TYT %60 + TYT Matematik 12 konu tamamlanınca AYT konuları eklenecek.
            """)
        else:
            st.success(f"""
            ✅ **TYT + AYT Aşaması** - Tüm konular aktif!
            
            • TYT: **%{tyt_progress:.1f}** tamamlandı
            • TYT Matematik: **{tyt_math_completed}** konu tamamlandı
            
            🎯 Artık hem TYT hem AYT konuları haftalık programınızda görünüyor.
            """)
    
    # Program özeti kaldırıldı - tekrar olmaması için

def show_weekly_summary(weekly_plan):
    """Haftalık program özeti"""
    st.markdown("---")
    st.markdown("#### 📊 Haftalık Program Özeti")
    
    new_topics_count = len(weekly_plan.get('new_topics', []))
    review_topics_count = len(weekly_plan.get('review_topics', []))
    total_topics = new_topics_count + review_topics_count
    success_target = weekly_plan.get('success_target', 0.8)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎯 Yeni Konular", new_topics_count)
    
    with col2:
        st.metric("🔄 Tekrar Konuları", review_topics_count)
    
    with col3:
        st.metric("📅 Toplam Hedef", total_topics)
    
    with col4:
        target_completion = int(total_topics * success_target)
        st.metric("🏆 Başarı Hedefi", f"{target_completion}/{total_topics}")
    
    if total_topics > 0:
        st.info(f"💡 **Bu Hafta Hedefiniz:** {total_topics} konunun %{success_target*100:.0f}'ini (%{target_completion} konu) iyi seviyeye çıkarmak!")
        
        # İlerleme simülasyonu
        if st.button("🗑️ Haftalık Planı Temizle", type="secondary"):
            st.session_state.systematic_day_plans = {day: [] for day in ["PAZARTESİ", "SALI", "ÇARŞAMBA", "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"]}
            st.success("✅ Haftalık plan temizlendi!")
            st.rerun()

def show_systematic_recommendations(weekly_plan, survey_data, student_field):
    """Sistematik akıllı öneriler"""
    st.markdown("### 💡 Size Özel Sistematik Öneriler")
    
    new_topics = weekly_plan.get('new_topics', [])
    review_topics = weekly_plan.get('review_topics', [])
    projections = weekly_plan.get('projections', {})
    
    recommendations = []
    
    # İlerleme durumu analizi
    overall_progress = projections.get('overall_progress', 0)
    if overall_progress < 30:
        recommendations.append({
            'type': '⚡ Hızlandırma Önerileri',
            'items': [
                "Günlük çalışma sürenizi artırın (6-8 saat ideal)",
                "Pomodoro tekniği ile odaklanmanızı artırın",
                "Zayıf konulara daha fazla zaman ayırın"
            ]
        })
    elif overall_progress > 70:
        recommendations.append({
            'type': '🎯 Son Dönem Stratejileri',
            'items': [
                "Deneme sınavlarına ağırlık verin",
                "Tekrar sıklığını artırın",
                "Zaman yönetimi pratiği yapın"
            ]
        })
    
    # Öncelik analizi
    high_priority_count = len([t for t in new_topics if t.get('priority') == 'HIGH'])
    if high_priority_count > 8:
        recommendations.append({
            'type': '🔥 Acil Durum Planı',
            'items': [
                f"{high_priority_count} acil konu var - günlük 2-3 konuya odaklanın",
                "Kolay konuları geçici olarak erteleyin",
                "Ek destekse alarak hızlıca ilerleyin"
            ]
        })
    
    # Tekrar yükü analizi
    repeat_high_count = len([t for t in review_topics if t.get('priority') == 'REPEAT_HIGH'])
    if repeat_high_count > 5:
        recommendations.append({
            'type': '🔄 Tekrar Optimizasyonu',
            'items': [
                f"{repeat_high_count} kritik tekrar var - unutma riski yüksek",
                "Sabah saatlerinde tekrarları yapın",
                "Aktif hatırlama teknikleri kullanın"
            ]
        })
    
    # Çalışma stili önerileri
    study_style = survey_data.get('study_style', '')
    if '🔥' in study_style:  # Zor dersler önce
        recommendations.append({
            'type': '🔥 Zor Konular Önce Stratejisi',
            'items': [
                "Sabah saatlerinde en zor konuları çalışın",
                "Enerji seviyeniz yüksekken zorlu konulara başlayın",
                "Başarıdan sonra kendini ödüllendirin"
            ]
        })
    elif '🍰' in study_style:  # Kolay dersler önce
        recommendations.append({
            'type': '🍰 Kolay Başlangıç Stratejisi',
            'items': [
                "Motivasyonu yüksek tutmak için kolay konularla başlayın",
                "Zor konular için daha fazla zaman ayırın",
                "Günün son kısmında en zorlu konuları planlayın"
            ]
        })
    
    # Alan bazında öneriler
    if student_field == "Sayısal":
        recommendations.append({
            'type': '🔬 Sayısal Alan Önerileri',
            'items': [
                "Matematik her gün mutlaka çalışın",
                "Fizik formüllerini günlük tekrar edin",
                "Kimya denklemleri için görsel yöntemler kullanın"
            ]
        })
    elif student_field == "Sözel":
        recommendations.append({
            'type': '📚 Sözel Alan Önerileri',
            'items': [
                "Türkçe paragraf sorularında strateji geliştirin",
                "Tarih konularını kronolojik sırayla öğrenin",
                "Coğrafya için harita çalışmaları yapın"
            ]
        })
    
    # Önerileri göster
    for rec in recommendations:
        with st.expander(f"💡 {rec['type']}", expanded=False):
            for item in rec['items']:
                st.write(f"• {item}")
    
    # Haftalık motivasyon
    st.markdown("### 🚀 Bu Hafta Motivasyon")
    motivation_quote = random.choice(MOTIVATION_QUOTES)
    st.success(f"💫 {motivation_quote}")
    
    # Öğrenme tarzına göre ipucu
    learning_style = survey_data.get('book_type', 'Genel')
    if learning_style in LEARNING_STYLE_DESCRIPTIONS:
        style_info = LEARNING_STYLE_DESCRIPTIONS[learning_style]
        st.info(f"🎨 **Öğrenme Tarzınız İçin:** {style_info.get('advice', 'Kendi tarzınızı geliştirin.')}")

def update_topic_completion_date(username, topic_key):
    """Konu tamamlandığında tarihi kaydet"""
    if db_ref is None:
        return
    
    try:
        user_data = get_user_data()
        if user_data:
            completion_dates = json.loads(user_data.get('topic_completion_dates', '{}') or '{}')
            completion_dates[topic_key] = datetime.now().isoformat()
            
            update_user_in_firebase(username, {
                'topic_completion_dates': json.dumps(completion_dates)
            })
    except Exception as e:
        st.error(f"Tamamlama tarihi kaydedilemedi: {e}")

# Konu takip sistemine entegrasyon için yardımcı fonksiyon
def check_and_update_completion_dates():
    """Konu takip sisteminden iyi seviyeye çıkan konuları takip et"""
    if not st.session_state.get('current_user'):
        return
    
    user_data = get_user_data()
    if not user_data:
        return
    
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    completion_dates = json.loads(user_data.get('topic_completion_dates', '{}') or '{}')
    
    # Yeni tamamlanan konuları bul
    for topic_key, net_str in topic_progress.items():
        try:
            net_value = int(float(net_str))
            if net_value >= 14 and topic_key not in completion_dates:
                # Yeni tamamlanan konu
                update_topic_completion_date(st.session_state.current_user, topic_key)
        except:
            continue



def pomodoro_timer_page(user_data):
    """🍅 Hibrit Pomodoro Timer - Akıllı Nefes Sistemi ile"""
    st.markdown(f'<div class="main-header"><h1>🍅 Hibrit Pomodoro Timer</h1><p>Akıllı nefes sistemi ile verimli çalışma - Sıkıldığında "Nefes Al" butonuna bas!</p></div>', unsafe_allow_html=True)
    
    # Session state başlat
    init_pomodoro_session_state()
    
    # Ana pomodoro arayüzü
    show_pomodoro_interface(user_data)
    
    # Bugünkü istatistikler
    show_daily_pomodoro_stats(user_data)
    
    # Çalışma geçmişi
    show_pomodoro_history(user_data)

def init_pomodoro_session_state():
    """Pomodoro session state'ini başlat ve eski değerleri yeni preset'lere migrate et"""
    
    # Mevcut preset isimleri
    valid_presets = ['Kısa Odak (25dk+5dk)', 'Standart Odak (35dk+10dk)', 
                     'Derin Odak (50dk+15dk)', 'Tam Konsantrasyon (90dk+25dk)']
    
    # Eski preset isimlerinden yeni preset isimlerine migration map
    preset_migration = {
        'Pomodoro (25dk)': 'Kısa Odak (25dk+5dk)',
        'Kısa Mola (5dk)': 'Kısa Odak (25dk+5dk)',
        'Uzun Mola (15dk)': 'Derin Odak (50dk+15dk)',
        'Derin Odak (50dk)': 'Derin Odak (50dk+15dk)'
    }
    
    if 'pomodoro_active' not in st.session_state:
        st.session_state.pomodoro_active = False
        
    # Pomodoro türü kontrolü ve migration
    if 'pomodoro_type' not in st.session_state:
        st.session_state.pomodoro_type = 'Kısa Odak (25dk+5dk)'
    else:
        # Eğer mevcut preset geçersizse, migrate et veya varsayılana dön
        if st.session_state.pomodoro_type not in valid_presets:
            if st.session_state.pomodoro_type in preset_migration:
                st.session_state.pomodoro_type = preset_migration[st.session_state.pomodoro_type]
                st.info(f"🔄 Pomodoro ayarınız yeni sisteme güncellendi: {st.session_state.pomodoro_type}")
            else:
                st.session_state.pomodoro_type = 'Kısa Odak (25dk+5dk)'
                st.warning("⚠️ Eski Pomodoro ayarı tespit edildi, varsayılan preset seçildi.")
    
    if 'time_remaining' not in st.session_state:
        st.session_state.time_remaining = 25 * 60  # 25 dakika
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'current_subject' not in st.session_state:
        st.session_state.current_subject = ''
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ''
    if 'daily_pomodoros' not in st.session_state:
        st.session_state.daily_pomodoros = []
    # Eski günlük hedef sistemi kaldırıldı - artık haftalık hedef konular kullanılıyor
    
    # === HİBRİT POMODORO SİSTEMİ İÇİN YENİ SESSION STATES ===
    if 'breathing_active' not in st.session_state:
        st.session_state.breathing_active = False
    if 'breathing_paused_time' not in st.session_state:
        st.session_state.breathing_paused_time = 0
    if 'breath_time_remaining' not in st.session_state:
        st.session_state.breath_time_remaining = 60
    if 'breath_start_time' not in st.session_state:
        st.session_state.breath_start_time = None
    if 'current_motivation_type' not in st.session_state:
        st.session_state.current_motivation_type = 'quote'
    if 'current_motivation_content' not in st.session_state:
        st.session_state.current_motivation_content = ''
    if 'breathing_usage_log' not in st.session_state:
        st.session_state.breathing_usage_log = []

def show_pomodoro_interface(user_data):
    """Ana pomodoro arayüzünü gösterir - Hibrit Pomodoro Sistemi ile"""
    
    # === HİBRİT SİSTEM GÜNCELLEMELERİ ===
    
    # Nefes egzersizi aktifse önce onu kontrol et
    if st.session_state.breathing_active and st.session_state.breath_start_time:
        elapsed = time.time() - st.session_state.breath_start_time
        st.session_state.breath_time_remaining = max(0, 60 - elapsed)
        
        # Süre bittiyse otomatik durdur ve Pomodoro'yu devam ettir
        if st.session_state.breath_time_remaining <= 0:
            complete_breathing_exercise()
    
    # Normal Pomodoro timer güncellemesi (nefes sırasında duraklatılmış olabilir)
    if st.session_state.pomodoro_active and st.session_state.start_time and not st.session_state.breathing_active:
        elapsed = time.time() - st.session_state.start_time
        st.session_state.time_remaining = max(0, st.session_state.time_remaining - elapsed)
        st.session_state.start_time = time.time()
        
        # Süre bittiyse otomatik durdur
        if st.session_state.time_remaining <= 0:
            complete_pomodoro(user_data)
    
    # Pomodoro türleri
    # Bilimsel Temelli Pomodoro Preset Seçenekleri
    pomodoro_types = {
        'Kısa Odak (25dk+5dk)': {
            'duration': 25, 
            'break_duration': 5, 
            'color': '#ff6b6b', 
            'icon': '🍅',
            'description': 'Standart Pomodoro - Çoğu öğrenci için ideal başlangıç',
            'scientific_info': 'Beynin dikkat süresi ortalama 20-25 dk. Kısa molalar hafızayı güçlendirir.'
        },
        'Standart Odak (35dk+10dk)': {
            'duration': 35, 
            'break_duration': 10, 
            'color': '#4ecdc4', 
            'icon': '📚',
            'description': 'Orta seviye konsantrasyon - Alışkanlık kazandıktan sonra',
            'scientific_info': 'Uzun odaklanma süresi derin öğrenmeyi destekler. 10dk mola beynin dinlenmesi için yeterli.'
        },
        'Derin Odak (50dk+15dk)': {
            'duration': 50, 
            'break_duration': 15, 
            'color': '#3742fa', 
            'icon': '🧘',
            'description': 'İleri seviye - Zor konular için önerilen süre',
            'scientific_info': 'Beynin maksimum odaklanma eşiği 45-60dk. Bu süre karmaşık problemler için idealdir.'
        },
        'Tam Konsantrasyon (90dk+25dk)': {
            'duration': 90, 
            'break_duration': 25, 
            'color': '#a55eea', 
            'icon': '🚀',
            'description': 'Uzman seviye - Çok zorlu konular ve sınav hazırlığı',
            'scientific_info': 'Ultradian ritim döngüsü ~90dk. Uzun molalar beyni tamamen yeniler.'
        }
    }
    
    # Timer gösterimi
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Nefes egzersizi aktifse özel arayüzü göster
        if st.session_state.breathing_active:
            show_breathing_exercise()
        else:
            # Normal timer görünümü
            minutes = int(st.session_state.time_remaining // 60)
            seconds = int(st.session_state.time_remaining % 60)
            
            # Güvenlik kontrolü: Eğer session'daki pomodoro_type geçersizse varsayılana dön
            if st.session_state.pomodoro_type not in pomodoro_types:
                st.session_state.pomodoro_type = 'Kısa Odak (25dk+5dk)'
                st.warning("⚠️ Geçersiz Pomodoro türü tespit edildi, varsayılan ayar yüklendi.")
                st.rerun()
            
            timer_color = pomodoro_types[st.session_state.pomodoro_type]['color']
            
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {timer_color}22 0%, {timer_color}44 100%);
                border: 4px solid {timer_color};
                border-radius: 50%;
                width: 250px;
                height: 250px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                margin: 20px auto;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            ">
                <div style="
                    font-size: 48px;
                    font-weight: bold;
                    color: {timer_color};
                    margin-bottom: 10px;
                ">{minutes:02d}:{seconds:02d}</div>
                <div style="
                    font-size: 16px;
                    color: {timer_color};
                    opacity: 0.8;
                ">{st.session_state.pomodoro_type.split('(')[0].strip()}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # === HİBRİT SİSTEM KONTROL BUTONLARI ===
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            if not st.session_state.pomodoro_active:
                if st.button("🟢 Başla", type="primary", use_container_width=True):
                    start_pomodoro()
            else:
                if st.button("🟠 Duraklat", type="secondary", use_container_width=True):
                    pause_pomodoro()
        
        with col_btn2:
            if st.button("🔴 Sıfırla", use_container_width=True):
                reset_pomodoro()
        
        with col_btn3:
            # ⭐ HİBRİT SİSTEMİN KALBI: NEFES AL BUTONU
            if st.session_state.pomodoro_active and not st.session_state.breathing_active:
                if st.button("💨 Nefes Al", type="primary", use_container_width=True):
                    start_hibrit_breathing()
            elif st.session_state.breathing_active:
                if st.button("⏭️ Atla", type="secondary", use_container_width=True):
                    complete_breathing_exercise()
            else:
                st.button("💨 Nefes Al", disabled=True, use_container_width=True, 
                         help="Önce Pomodoro'yu başlatın")
        
        with col_btn4:
            if st.session_state.pomodoro_active and not st.session_state.breathing_active:
                if st.button("✅ Tamamla", type="primary", use_container_width=True):
                    complete_pomodoro(user_data)
    
    st.markdown("---")
    
    # Pomodoro türü seçimi - Bilimsel temelli yaklaşım
    st.markdown("### 🧪 Pomodoro Preset'i Seçin")
    
    cols = st.columns(2)
    for i, (pom_type, info) in enumerate(pomodoro_types.items()):
        with cols[i % 2]:
            # Aktif türü vurgula
            is_active = st.session_state.pomodoro_type == pom_type
            
            # Mola süresi sınırlandırması kontrolü
            can_select = True
            warning_msg = ""
            
            if pom_type == 'Tam Konsantrasyon (90dk+25dk)' and not is_active:
                # 90 dakika çalışma yapan herkes 25 dk mola alabilir
                warning_msg = "⚠️ 90dk yoğun çalışma sonrası uzun mola gerekli!"
            elif pom_type == 'Derin Odak (50dk+15dk)' and not is_active:
                # 50dk çalışma yapan 15dk mola alabilir
                warning_msg = "🧪 50dk derin odaklanma için 15dk mola önerilir!"
            elif pom_type in ['Standart Odak (35dk+10dk)', 'Kısa Odak (25dk+5dk)'] and not is_active:
                # 25dk ve 35dk çalışanlar uzun mola alamaz
                if st.session_state.pomodoro_type in ['Tam Konsantrasyon (90dk+25dk)', 'Derin Odak (50dk+15dk)']:
                    can_select = True  # Daha uzun süreden kısa süreye geçebilir
                warning_msg = f"🚨 {pom_type.split('(')[1].split(')')[0]} çalışanlar uzun mola yapamaz!"
            
            # Preset butonu ve açıklaması
            container = st.container()
            with container:
                if st.button(
                    f"{info['icon']} **{pom_type}**\n{info['description']}", 
                    key=f"pom_type_{i}",
                    use_container_width=True,
                    disabled=st.session_state.pomodoro_active or not can_select,
                    type="primary" if is_active else "secondary"
                ):
                    st.session_state.pomodoro_type = pom_type
                    st.session_state.time_remaining = info['duration'] * 60
                    st.success(f"🎉 {pom_type} seçildi! Çalışma süresi: {info['duration']}dk, Mola süresi: {info['break_duration']}dk")
                    st.rerun()
                
                # Bilimsel açıklama
                with st.expander(f"🔬 Bilimsel Temeli - {pom_type.split('(')[0].strip()}", expanded=False):
                    st.info(f"🧪 **Bilimsel Açıklama:**\n{info['scientific_info']}")
                    
                    if warning_msg:
                        st.warning(warning_msg)
                        
                st.markdown("---")
    
    st.markdown("---")
    
    # Çalışma konusu seçimi
    st.markdown("### 📚 Çalışma Konusu")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Ders seçimi
        student_field = user_data.get('field', '')
        available_subjects = get_subjects_by_field_yks(student_field)
        
        # Özel kategoriler ekle
        special_categories = ["📝 Deneme Sınavı", "📂 Diğer"]
        all_subject_options = ["Seçiniz..."] + available_subjects + special_categories
        
        selected_subject = st.selectbox(
            "Ders:",
            all_subject_options,
            index=0 if not st.session_state.current_subject else (
                all_subject_options.index(st.session_state.current_subject) 
                if st.session_state.current_subject in all_subject_options else 0
            ),
            disabled=st.session_state.pomodoro_active
        )
        
        if selected_subject != "Seçiniz...":
            st.session_state.current_subject = selected_subject

    with col2:
        # Konu seçimi - Eğer normal ders seçildiyse konu takipten konuları getir
        if (st.session_state.current_subject and 
            st.session_state.current_subject not in ["Seçiniz...", "📝 Deneme Sınavı", "📂 Diğer"]):
            
            # Konu takipten konuları getir
            available_topics = get_topic_list(st.session_state.current_subject)
            topic_options = ["Manuel Konu Girişi..."] + available_topics
            
            selected_topic = st.selectbox(
                "Konu:",
                topic_options,
                index=0 if not st.session_state.current_topic else (
                    topic_options.index(st.session_state.current_topic) 
                    if st.session_state.current_topic in topic_options else 0
                ),
                disabled=st.session_state.pomodoro_active,
                help="Konu Takip'ten otomatik olarak konular getirildi. Manuel giriş için 'Manuel Konu Girişi...' seçin."
            )
            
            if selected_topic == "Manuel Konu Girişi...":
                # Manuel konu girişi
                manual_topic = st.text_input(
                    "Manuel Konu:",
                    value=st.session_state.current_topic if st.session_state.current_topic not in topic_options else "",
                    placeholder="örn: Temel Kavramlar - Basamak",
                    disabled=st.session_state.pomodoro_active
                )
                if manual_topic:
                    st.session_state.current_topic = manual_topic
            else:
                if selected_topic and selected_topic != "Manuel Konu Girişi...":
                    # Konu takipten seçilen konuyu kısalt (sadece konu adını göster)
                    if " | " in selected_topic:
                        topic_parts = selected_topic.split(" | ")
                        display_topic = topic_parts[-1]  # Son kısmı (gerçek konu adı)
                    else:
                        display_topic = selected_topic
                    st.session_state.current_topic = display_topic
        else:
            # Deneme sınavı, Diğer veya seçim yapılmamışsa manuel giriş
            topic_placeholder = {
                "📝 Deneme Sınavı": "örn: TYT Deneme 5, AYT Mat Deneme 3",
                "📂 Diğer": "örn: Özet Çıkarma, Formül Tekrarı"
            }.get(st.session_state.current_subject, "örn: Temel Kavramlar - Basamak")
            
            topic_input = st.text_input(
                "Konu/Açıklama:",
                value=st.session_state.current_topic,
                placeholder=topic_placeholder,
                disabled=st.session_state.pomodoro_active
            )
            
            if topic_input:
                st.session_state.current_topic = topic_input
    
    # Bu haftanın hedef konuları
    st.markdown("### 🎯 Bu Haftanın Hedef Konularım")
    
    # Kullanıcı verilerini al
    student_field = user_data.get('field', '')
    survey_data = json.loads(user_data.get('survey_data', '{}')) if user_data.get('survey_data') else {}
    
    # Haftalık hedef konuları çek
    weekly_plan = get_weekly_topics_from_topic_tracking(user_data, student_field, survey_data)
    weekly_target_topics = weekly_plan.get('new_topics', []) + weekly_plan.get('review_topics', [])
    
    if weekly_target_topics:
        # Haftalık hedef konularını görüntüle
        st.markdown("#### 📋 YKS Canlı Takip'ten Hedef Konular")
        
        # Bu haftaki pomodorolardan konu bazında ilerleme hesapla
        topic_progress_in_pomodoros = {}
        
        # Kullanıcının tüm pomodoro geçmişini al
        try:
            pomodoro_history_str = user_data.get('pomodoro_history', '[]')
            all_pomodoros = json.loads(pomodoro_history_str) if pomodoro_history_str else []
            
            # Bu haftanın başlangıcını hesapla (Pazartesi)
            today = datetime.now().date()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            
            # Bu haftaki pomodorolardan konuları say
            this_week_pomodoros = [
                p for p in all_pomodoros 
                if datetime.fromisoformat(p['timestamp']).date() >= week_start
            ]
            
            for p in this_week_pomodoros:
                topic = p.get('topic', '')
                if topic and topic != 'Belirtilmemiş':
                    topic_progress_in_pomodoros[topic] = topic_progress_in_pomodoros.get(topic, 0) + 1
                    
        except Exception as e:
            st.warning("Haftalık ilerleme hesaplanırken hata oluştu.")
            topic_progress_in_pomodoros = {}
        
        # Hedef konuları tabloda göster
        cols = st.columns([3, 1, 1, 1])
        
        with cols[0]:
            st.markdown("**📚 Hedef Konu**")
        with cols[1]:
            st.markdown("**🎯 Net**")
        with cols[2]:
            st.markdown("**🍅 Bu Hafta**")
        with cols[3]:
            st.markdown("**📊 Durum**")
        
        st.markdown("---")
        
        for i, topic in enumerate(weekly_target_topics[:8]):  # Max 8 konu göster
            cols = st.columns([3, 1, 1, 1])
            
            # Konu adını kısalt
            topic_display = f"{topic['subject']} - {topic['detail']}"
            if len(topic_display) > 40:
                topic_display = topic_display[:37] + "..."
            
            # Bu konuda bu hafta kaç pomodoro yapıldı
            pomodoros_this_week = topic_progress_in_pomodoros.get(topic['detail'], 0)
            
            # Net değerine göre renk
            if topic['net'] < 5:
                status_color = "🔴"
                status_text = "Zayıf"
            elif topic['net'] < 10:
                status_color = "🟡"
                status_text = "Orta"
            elif topic['net'] < 14:
                status_color = "🟠"
                status_text = "İyi"
            else:
                status_color = "🟢"
                status_text = "Çok İyi"
            
            with cols[0]:
                st.write(f"**{topic_display}**")
            with cols[1]:
                st.write(f"{topic['net']}")
            with cols[2]:
                if pomodoros_this_week > 0:
                    st.write(f"**{pomodoros_this_week}** 🍅")
                else:
                    st.write("-")
            with cols[3]:
                st.write(f"{status_color} {status_text}")
        
        # Haftalık özet
        st.markdown("---")
        
        total_weekly_pomodoros = sum(topic_progress_in_pomodoros.values())
        completed_today = len(st.session_state.daily_pomodoros)
        
        summary_col1, summary_col2, summary_col3 = st.columns(3)
        
        with summary_col1:
            st.metric("🍅 Bugün", completed_today)
        with summary_col2:
            st.metric("📅 Bu Hafta", total_weekly_pomodoros)
        with summary_col3:
            topics_worked_this_week = len([k for k, v in topic_progress_in_pomodoros.items() if v > 0])
            st.metric("📚 Çalışılan Konu", f"{topics_worked_this_week}/{len(weekly_target_topics)}")
        
        # Motivasyon mesajı
        if topics_worked_this_week >= len(weekly_target_topics) // 2:
            st.success("🎉 Harika gidiyorsun! Haftalık hedeflerinin yarısından fazlasında çalıştın!")
        elif topics_worked_this_week > 0:
            st.info("💪 İyi başlangıç! Hedef konularında çalışmaya devam et!")
        else:
            st.warning("🎯 Bu hafta henüz hedef konularında çalışmadın. Başlamak için şimdi güzel bir zaman!")
            
    else:
        # Hedef konu bulunamadıysa alternatif göster
        completed_today = len(st.session_state.daily_pomodoros)
        
        st.info("📋 Bu hafta için hedef konu bulunamadı. **YKS Canlı Takip** sekmesinde konularınızı değerlendirin ve haftalık programınızı oluşturun.")
        
        # Basit günlük metrik
        summary_col1, summary_col2 = st.columns(2)
        
        with summary_col1:
            st.metric("🍅 Bugün Tamamlanan", completed_today)
        with summary_col2:
            # Son 7 günlük pomodoro sayısı
            try:
                pomodoro_history_str = user_data.get('pomodoro_history', '[]')
                all_pomodoros = json.loads(pomodoro_history_str) if pomodoro_history_str else []
                
                week_ago = datetime.now().date() - timedelta(days=7)
                weekly_count = len([
                    p for p in all_pomodoros 
                    if datetime.fromisoformat(p['timestamp']).date() >= week_ago
                ])
                
                st.metric("📅 Son 7 Gün", weekly_count)
            except:
                st.metric("📅 Son 7 Gün", "?")
    
    # Auto-refresh aktif timer için
    if st.session_state.pomodoro_active:
        time.sleep(1)
        st.rerun()

def start_pomodoro():
    """Pomodoro'yu başlat"""
    if not st.session_state.current_subject or not st.session_state.current_topic:
        st.error("😱 Lütfen ders ve konu seçin!")
        return
    
    st.session_state.pomodoro_active = True
    st.session_state.start_time = time.time()
    st.success(f"✅ {st.session_state.pomodoro_type} başlatıldı!")

def pause_pomodoro():
    """Pomodoro'yu duraklat"""
    st.session_state.pomodoro_active = False
    st.session_state.start_time = None
    st.warning("⏸️ Pomodoro duraklatıldı")

def reset_pomodoro():
    """Pomodoro'yu sıfırla"""
    st.session_state.pomodoro_active = False
    st.session_state.start_time = None
    
    # Süreyi türe göre sıfırla
    duration_map = {
        'Kısa Odak (25dk+5dk)': 25,
        'Standart Odak (35dk+10dk)': 35,
        'Derin Odak (50dk+15dk)': 50,
        'Tam Konsantrasyon (90dk+25dk)': 90
    }
    
    # Güvenlik kontrolü ile süre ayarla
    if st.session_state.pomodoro_type in duration_map:
        st.session_state.time_remaining = duration_map[st.session_state.pomodoro_type] * 60
    else:
        # Eğer preset bulunamazsa varsayılana dön
        st.session_state.pomodoro_type = 'Kısa Odak (25dk+5dk)'
        st.session_state.time_remaining = 25 * 60
        st.warning("⚠️ Geçersiz preset tespit edildi, varsayılan ayarlara dönüldü.")
    
    st.info("🔄 Pomodoro sıfırlandı")

def complete_pomodoro(user_data):
    """Pomodoro'yu tamamla ve kaydet"""
    # Pomodoro'yu durdur
    st.session_state.pomodoro_active = False
    st.session_state.start_time = None
    
    # Kayıt oluştur
    pomodoro_record = {
        'timestamp': datetime.now().isoformat(),
        'type': st.session_state.pomodoro_type,
        'subject': st.session_state.current_subject,
        'topic': st.session_state.current_topic,
        'completed': True
    }
    
    # Günlük listeye ekle
    st.session_state.daily_pomodoros.append(pomodoro_record)
    
    # Kullanıcı verisine kaydet
    save_pomodoro_to_user_data(user_data, pomodoro_record)
    
    # Timer'i sıfırla
    duration_map = {
        'Kısa Odak (25dk+5dk)': 25,
        'Standart Odak (35dk+10dk)': 35,
        'Derin Odak (50dk+15dk)': 50,
        'Tam Konsantrasyon (90dk+25dk)': 90
    }
    
    # Güvenlik kontrolü ile süre ayarla
    if st.session_state.pomodoro_type in duration_map:
        st.session_state.time_remaining = duration_map[st.session_state.pomodoro_type] * 60
    else:
        # Eğer preset bulunamazsa varsayılana dön
        st.session_state.pomodoro_type = 'Kısa Odak (25dk+5dk)'
        st.session_state.time_remaining = 25 * 60
    
    # Başarı mesajı
    st.success(f"🎉 {st.session_state.pomodoro_type} tamamlandı! Harika iş!")
    st.balloons()

def save_pomodoro_to_user_data(user_data, pomodoro_record):
    """Pomodoro kaydını kullanıcı verisine kaydet"""
    try:
        # Mevcut pomodoro verilerini yükle
        pomodoro_data_str = user_data.get('pomodoro_history', '[]')
        pomodoro_history = json.loads(pomodoro_data_str) if pomodoro_data_str else []
        
        # Yeni kaydı ekle
        pomodoro_history.append(pomodoro_record)
        
        # Son 100 kaydı tut (performans için)
        if len(pomodoro_history) > 100:
            pomodoro_history = pomodoro_history[-100:]
        
        # Kullanıcı verisini güncelle
        update_user_in_firebase(st.session_state.current_user, 
                          {'pomodoro_history': json.dumps(pomodoro_history)})
        
        # Session state'teki kullanıcı verisini güncelle
        st.session_state.users_db = load_users_from_firebase()
        
    except Exception as e:
        st.error(f"Pomodoro kaydı kaydedilirken hata: {e}")

def show_daily_pomodoro_stats(user_data):
    """Hibrit Pomodoro istatistiklerini göster"""
    st.markdown("### 📊 Bugünkü Hibrit Pomodoro İstatistikleri")
    
    completed_today = len(st.session_state.daily_pomodoros)
    breathing_used_today = len([log for log in st.session_state.breathing_usage_log 
                              if log['timestamp'][:10] == datetime.now().date().isoformat()])
    
    if st.session_state.daily_pomodoros or breathing_used_today > 0:
        # İstatistik metrikleri
        col1, col2, col3, col4 = st.columns(4)
        
        # Pomodoro türlerine göre süre hesaplama
        duration_map = {
            'Kısa Odak (25dk+5dk)': 25,
            'Standart Odak (35dk+10dk)': 35,
            'Derin Odak (50dk+15dk)': 50,
            'Tam Konsantrasyon (90dk+25dk)': 90
        }
        
        # Ders bazında çalışma sürelerini hesapla
        subject_times = {}
        topic_counts = {}
        total_minutes = 0
        
        for p in st.session_state.daily_pomodoros:
            subject = p['subject']
            topic = p.get('topic', 'Belirtilmemiş')
            pomodoro_type = p.get('type', 'Kısa Odak (25dk+5dk)')
            
            # Süreyi hesapla
            duration = duration_map.get(pomodoro_type, 25)
            total_minutes += duration
            
            # Ders bazında topla
            if subject not in subject_times:
                subject_times[subject] = 0
            subject_times[subject] += duration
            
            # Konu sayısını topla
            if subject not in topic_counts:
                topic_counts[subject] = {}
            if topic not in topic_counts[subject]:
                topic_counts[subject][topic] = 0
            topic_counts[subject][topic] += 1
        
        hours = total_minutes // 60
        minutes = total_minutes % 60
        
        with col1:
            st.metric("🍅 Tamamlanan", completed_today)
        with col2:
            st.metric("💨 Nefes Molası", breathing_used_today)
        with col3:
            st.metric("⏰ Toplam Süre", f"{hours}s {minutes}dk")
        with col4:
            # Haftalık hedef konular bazında ilerleme hesapla
            try:
                student_field = user_data.get('field', '')
                survey_data = json.loads(user_data.get('survey_data', '{}')) if user_data.get('survey_data') else {}
                weekly_plan = get_weekly_topics_from_topic_tracking(user_data, student_field, survey_data)
                weekly_target_topics = weekly_plan.get('new_topics', []) + weekly_plan.get('review_topics', [])
                
                if weekly_target_topics:
                    # Bu haftaki pomodorolardan konu bazlı ilerleme
                    pomodoro_history_str = user_data.get('pomodoro_history', '[]')
                    all_pomodoros = json.loads(pomodoro_history_str) if pomodoro_history_str else []
                    
                    today = datetime.now().date()
                    days_since_monday = today.weekday()
                    week_start = today - timedelta(days=days_since_monday)
                    
                    this_week_pomodoros = [
                        p for p in all_pomodoros 
                        if datetime.fromisoformat(p['timestamp']).date() >= week_start
                    ]
                    
                    topic_progress_in_pomodoros = {}
                    for p in this_week_pomodoros:
                        topic = p.get('topic', '')
                        if topic and topic != 'Belirtilmemiş':
                            topic_progress_in_pomodoros[topic] = topic_progress_in_pomodoros.get(topic, 0) + 1
                    
                    topics_worked = len([k for k, v in topic_progress_in_pomodoros.items() if v > 0])
                    weekly_progress = (topics_worked / len(weekly_target_topics)) * 100 if weekly_target_topics else 0
                    
                    st.metric("🎯 Haftalık İlerleme", f"%{weekly_progress:.1f}")
                else:
                    st.metric("🎯 Haftalık İlerleme", "Hedef yok")
            except:
                st.metric("🎯 Haftalık İlerleme", "?")
        
        
        # === DERS BAZINDA DETAYLAR ===
        st.markdown("#### 📚 Bugünkü Ders Detayları")
        
        if subject_times:
            # Ders tablosu
            col_table, col_chart = st.columns([1, 1])
            
            with col_table:
                st.markdown("**Ders Bazında Çalışma Süreleri:**")
                
                for subject in sorted(subject_times.keys()):
                    minutes_studied = subject_times[subject]
                    hours_studied = minutes_studied // 60
                    mins_studied = minutes_studied % 60
                    
                    time_str = f"{hours_studied}s {mins_studied}dk" if hours_studied > 0 else f"{mins_studied}dk"
                    
                    # Emoji seçimi
                    if subject.startswith("📝"):
                        emoji = "📝"
                    elif subject.startswith("📂"):
                        emoji = "📂"
                    elif "Matematik" in subject:
                        emoji = "🔢"
                    elif "Fizik" in subject:
                        emoji = "⚛️"
                    elif "Kimya" in subject:
                        emoji = "🧪"
                    elif "Biyoloji" in subject:
                        emoji = "🧬"
                    elif "Türkçe" in subject or "Edebiyat" in subject:
                        emoji = "📖"
                    else:
                        emoji = "📚"
                    
                    st.write(f"{emoji} **{subject}**: {time_str}")
                    
                    # Konu detayları
                    if subject in topic_counts:
                        for topic, count in topic_counts[subject].items():
                            if topic and topic != "Belirtilmemiş":
                                st.write(f"    • {topic}: {count} pomodoro")
            
            with col_chart:
                # Pasta grafik
                if len(subject_times) > 1:
                    subject_df = pd.DataFrame([
                        {'Ders': subject, 'Dakika': minutes} 
                        for subject, minutes in subject_times.items()
                    ])
                    fig = px.pie(subject_df, values='Dakika', names='Ders', 
                                title='Bugünkü Çalışma Süresi Dağılımı')
                    st.plotly_chart(fig, use_container_width=True, height=400)
        
        # === TOPLAM İSTATİSTİKLER (TÜM ZAMANLAR) ===
        st.markdown("#### 🏆 Toplam İstatistikler")
        
        # Kullanıcı verisinden geçmiş pomodoro'ları yükle
        try:
            pomodoro_history_str = user_data.get('pomodoro_history', '[]')
            all_pomodoros = json.loads(pomodoro_history_str) if pomodoro_history_str else []
            
            if all_pomodoros:
                # Toplam hesaplamalar
                total_all_time = 0
                subject_totals = {}
                total_count = len(all_pomodoros)
                
                for p in all_pomodoros:
                    pomodoro_type = p.get('type', 'Kısa Odak (25dk+5dk)')
                    subject = p.get('subject', 'Belirtilmemiş')
                    duration = duration_map.get(pomodoro_type, 25)
                    total_all_time += duration
                    
                    if subject not in subject_totals:
                        subject_totals[subject] = 0
                    subject_totals[subject] += duration
                
                total_hours = total_all_time // 60
                total_mins = total_all_time % 60
                
                col_total1, col_total2, col_total3 = st.columns(3)
                
                with col_total1:
                    st.metric("🎯 Toplam Pomodoro", total_count)
                with col_total2:
                    st.metric("⏰ Toplam Çalışma", f"{total_hours}s {total_mins}dk")
                with col_total3:
                    # En çok çalışılan ders
                    if subject_totals:
                        top_subject = max(subject_totals, key=subject_totals.get)
                        st.metric("🏅 En Çok Çalışılan", top_subject.split()[0] + "...")
                
                # Son 7 günün istatistikleri
                today = datetime.now().date()
                last_week_pomodoros = [
                    p for p in all_pomodoros 
                    if (today - datetime.fromisoformat(p['timestamp']).date()).days <= 7
                ]
                
                if last_week_pomodoros:
                    week_total = sum(duration_map.get(p.get('type', 'Kısa Odak (25dk+5dk)'), 25) 
                                   for p in last_week_pomodoros)
                    week_hours = week_total // 60
                    week_mins = week_total % 60
                    avg_daily = week_total / 7
                    
                    st.markdown("**📅 Son 7 Gün:**")
                    st.write(f"• Toplam: {len(last_week_pomodoros)} pomodoro ({week_hours}s {week_mins}dk)")
                    st.write(f"• Günlük ortalama: {avg_daily:.1f} dk")
                    
        except Exception as e:
            st.warning("Toplam istatistikler yüklenirken bir hata oluştu.")
        
        # === HİBRİT SİSTEM ANALİZİ ===
        if breathing_used_today > 0:
            st.markdown("#### 🧠 Hibrit Sistem Analizi")
            
            # Hangi derslerde daha çok nefes molası kullanıldı
            today_breathing_logs = [log for log in st.session_state.breathing_usage_log 
                                   if log['timestamp'][:10] == datetime.now().date().isoformat()]
            
            subject_breathing = {}
            motivation_type_count = {'quote': 0, 'tip': 0, 'breathing': 0}
            
            for log in today_breathing_logs:
                subject = log['subject']
                subject_breathing[subject] = subject_breathing.get(subject, 0) + 1
                motivation_type_count[log['motivation_type']] += 1
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**📚 Derslerde Nefes Kullanımı:**")
                for subject, count in subject_breathing.items():
                    st.write(f"• {subject}: {count} kez")
            
            with col_b:
                st.markdown("**💭 Motivasyon Türü Dağılımı:**")
                st.write(f"• Motivasyon Sözleri: {motivation_type_count['quote']}")
                st.write(f"• Mikro İpuçları: {motivation_type_count['tip']}")
                st.write(f"• Nefes Egzersizleri: {motivation_type_count['breathing']}")
            
            # Akıllı öneriler
            avg_breathing_per_pomodoro = breathing_used_today / completed_today if completed_today > 0 else 0
            
            if breathing_used_today > 4:
                st.warning("💡 **Hibrit Analiz:** Bugün nefes sistemini sıkça kullandınız. Bu, odaklanma zorluğu yaşadığınızı gösterebilir. Bu normal ve sağlıklı bir yaklaşım! Belki çalışma ortamınızı kontrol etmek ya da ara verme sıklığını artırmak faydalı olabilir.")
            elif breathing_used_today > 0 and avg_breathing_per_pomodoro < 1:
                st.info("🎯 **Hibrit Analiz:** Nefes sistemini dengeli şekilde kullanıyorsunuz. Bu, öz-farkındalığınızın yüksek olduğunu gösteriyor!")
            elif breathing_used_today == 0 and completed_today > 3:
                st.success("🏆 **Hibrit Analiz:** Bugün hibrit sistemi kullanmadan harika bir performans sergiledinin! Odaklanma beceriniz gelişiyor.")

    else:
        st.info("📊 Bugün henüz hibrit pomodoro tamamlanmamış. İlk pomodoro'nuzu başlatın!")

def show_pomodoro_history(user_data):
    """Pomodoro geçmişini göster"""
    st.markdown("### 📅 Çalışma Geçmişi")
    
    try:
        pomodoro_data_str = user_data.get('pomodoro_history', '[]')
        pomodoro_history = json.loads(pomodoro_data_str) if pomodoro_data_str else []
        
        if pomodoro_history:
            # Son 10 kaydı göster
            recent_history = pomodoro_history[-10:]
            
            for i, record in enumerate(reversed(recent_history)):
                with st.expander(f"🍅 {record['subject']} - {record['topic'][:30]}... ({record['timestamp'][:10]})"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Tür:** {record['type']}")
                    with col2:
                        st.write(f"**Ders:** {record['subject']}")
                    with col3:
                        st.write(f"**Durum:** {'✅ Tamamlandı' if record['completed'] else '❌ Yarım'}")
                    
                    st.write(f"**Konu:** {record['topic']}")
                    st.write(f"**Tarih:** {record['timestamp']}")
        else:
            st.info("📅 Henüz pomodoro geçmişi bulunmuyor.")
            
    except Exception as e:
        st.error(f"Geçmiş yüklenirken hata: {e}")
# === HİBRİT POMODORO SİSTEMİ FONKSİYONLARI ===

# YKS Odaklı Motivasyon Sözleri - Hibrit Sistem için
MOTIVATION_QUOTES = [
    "Her 50 dakikalık emek, seni rakiplerinden ayırıyor! 💪",
    "Şu anda çözdüğün her soru, YKS'de seni zirveye taşıyacak! 🎯",
    "Büyük hedefler küçük adımlarla başlar - sen doğru yoldasın! ⭐",
    "Her nefes alışın, YKS başarına bir adım daha yaklaştırıyor! 🌬️",
    "Zorluklara direnmek seni güçlendiriyor - YKS'de fark yaratacaksın! 🚀",
    "Bugün kazandığın her kavram, sınavda seni öne çıkaracak! 📚",
    "Konsantrasyon kasların güçleniyor - şampiyonlar böyle yetişir! 🧠",
    "Hedefine odaklan! Her dakika YKS başarın için değerli! 🏆",
    "Mola hakkını akıllıca kullanıyorsun - bu seni daha güçlü yapıyor! 💨",
    "Başarı sabır ister, sen sabırlı bir savaşçısın! ⚔️",
    "Her yeni konu öğrenişin, gelecekteki mesleğinin temeli! 🏗️",
    "Rüyalarının peşinde koşuyorsun - asla vazgeçme! 🌟",
    "YKS sadece bir sınav, sen ise sınırsız potansiyelin! 🌈",
    "Her pomodoro seansı, hedefine bir adım daha yaklaştırıyor! 🎯",
    "Dün yapamadığını bugün yapabiliyorsun - bu gelişim! 📈",
    "Zorlu soruları çözerken beynin güçleniyor! 🧩",
    "Her mola sonrası daha güçlü dönüyorsun! 💪",
    "Bilim insanları da böyle çalıştı - sen de başaracaksın! 🔬",
    "Her nefes, yeni bir başlangıç fırsatı! 🌱",
    "Hayal ettiğin üniversite seni bekliyor! 🏛️"
]

# Mikro ipuçları (ders bazında)
MICRO_TIPS = {
    "TYT Matematik": [
        "📐 Türev sorularında genellikle önce fonksiyonun köklerini bulmak saldırıları hızlandırır.",
        "🔢 İntegral hesaplarken substitüsyon methodunu akılda tut.",
        "📊 Geometri problemlerinde çizim yapmayı unutma.",
        "⚡ Limit sorularında l'hopital kuralını hatırla."
    ],
    "TYT Fizik": [
        "⚡ Newton yasalarını uygularken kuvvet vektörlerini doğru çiz.",
        "🌊 Dalga problemlerinde frekans-dalga boyu ilişkisini unutma.",
        "🔥 Termodinamik sorularında sistem sınırlarını net belirle.",
        "🔬 Elektrik alanı hesaplamalarında işaret dikkatli kontrol et."
    ],
    "TYT Kimya": [
        "🧪 Mol kavramı tüm hesaplamaların temeli - ezberleme!",
        "⚛️ Periyodik cetveldeki eğilimleri görselleştir.",
        "🔄 Denge tepkimelerinde Le Chatelier prensibini uygula.",
        "💧 Asit-baz titrasyonlarında eşdeğer nokta kavramını unutma."
    ],
    "TYT Türkçe": [
        "📖 Paragraf sorularında ana fikri ilk ve son cümlelerde ara.",
        "✍️ Anlam bilgisi sorularında bağlamı dikkate al.",
        "📝 Yazım kurallarında 'de/da' ayrım kuralını hatırla.",
        "🎭 Edebi türlerde karakterizasyon önemli."
    ],
    "TYT Tarih": [
        "📅 Olayları kronolojik sırayla öğren, sebep-sonuç bağla.",
        "🏛️ Siyasi yapılar sosyal yapılarla ilişkisini kur.",
        "🗺️ Haritalarla coğrafi konumları pekiştir.",
        "👑 Dönem özelliklerini başlıca olaylarla örnekle."
    ],
    "TYT Coğrafya": [
        "🌍 İklim türlerini sebepleriyle birlikte öğren.",
        "🏔️ Jeomorfoloji'de süreç-şekil ilişkisini kur.",
        "📊 İstatistiksel veriler harita okuma becerisini geliştir.",
        "🌱 Bitki örtüsü-iklim ilişkisini unutma."
    ],
    "Genel": [
        "🎯 Zor sorularla karşılaştığında derin nefes al ve sistematik düşün.",
        "⏰ Zaman yönetimini ihmal etme - her dakika değerli.",
        "📚 Kavramları sadece ezberlemek yerine anlayarak öğren.",
        "🔄 Düzenli tekrar yapmak kalıcılığı artırır."
    ]
}

# YKS Odaklı Nefes Egzersizi Talimatları
BREATHING_EXERCISES = [
    {
        "name": "4-4-4-4 Tekniği (Kare Nefes)",
        "instruction": "4 saniye nefes al → 4 saniye tut → 4 saniye ver → 4 saniye bekle",
        "benefit": "Stresi azaltır, odaklanmayı artırır, sınav kaygısını azaltır"
    },
    {
        "name": "Karın Nefesi (Diyafragma Nefesi)",
        "instruction": "Elinizi karnınıza koyun. Nefes alırken karın şişsin, verirken insin",
        "benefit": "Gevşemeyi sağlar, kaygıyı azaltır, zihinsel netliği artırır"
    },
    {
        "name": "4-7-8 Sakinleştirici Nefes",
        "instruction": "4 saniye burun ile nefes al → 7 saniye tut → 8 saniye ağız ile ver",
        "benefit": "Derin rahatlama sağlar, uykuya yardım eder, sınav öncesi sakinleştirir"
    },
    {
        "name": "Yavaş Derin Nefes",
        "instruction": "6 saniye nefes al → 2 saniye tut → 6 saniye yavaşça ver",
        "benefit": "Kalp ritmi düzenlenir, sakinleşir, zihinsel berraklık artar"
    },
    {
        "name": "Alternatif Burun Nefesi",
        "instruction": "Sağ burun deliği ile nefes al, sol ile ver. Sonra tersini yap",
        "benefit": "Beynin her iki yarım küresini dengeler, konsantrasyonu artırır"
    },
    {
        "name": "5-5 Basit Ritim",
        "instruction": "5 saniye nefes al → 5 saniye nefes ver (hiç tutmadan)",
        "benefit": "Basit ve etkili, hızlı sakinleşme, odaklanma öncesi ideal"
    }
]

def start_hibrit_breathing():
    """Hibrit nefes sistemini başlat - Pomodoro'yu duraklat"""
    # Pomodoro'yu duraklat
    if st.session_state.pomodoro_active:
        st.session_state.breathing_paused_time = st.session_state.time_remaining
    
    # Nefes sistemini başlat
    st.session_state.breathing_active = True
    st.session_state.breath_time_remaining = 60
    st.session_state.breath_start_time = time.time()
    
    # Rastgele bir motivasyon türü seç
    motivation_types = ['quote', 'tip', 'breathing']
    st.session_state.current_motivation_type = random.choice(motivation_types)
    
    if st.session_state.current_motivation_type == 'quote':
        st.session_state.current_motivation_content = random.choice(MOTIVATION_QUOTES)
    elif st.session_state.current_motivation_type == 'tip':
        subject = st.session_state.current_subject
        if subject in MICRO_TIPS:
            st.session_state.current_motivation_content = random.choice(MICRO_TIPS[subject])
        else:
            st.session_state.current_motivation_content = random.choice(MICRO_TIPS['Genel'])
    else:  # breathing
        exercise = random.choice(BREATHING_EXERCISES)
        st.session_state.current_motivation_content = f"""
🫁 **{exercise['name']}**

📋 {exercise['instruction']}

✨ **Faydası:** {exercise['benefit']}
        """
    
    # Kullanım loguna kaydet
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'subject': st.session_state.current_subject,
        'motivation_type': st.session_state.current_motivation_type,
        'remaining_time_when_used': st.session_state.breathing_paused_time
    }
    st.session_state.breathing_usage_log.append(log_entry)
    
    st.success("💨 Hibrit nefes molası başladı! Pomodoro timer duraklatıldı.")

def complete_breathing_exercise():
    """Nefes egzersizini tamamla ve Pomodoro'ya dön"""
    st.session_state.breathing_active = False
    st.session_state.breath_time_remaining = 60
    st.session_state.breath_start_time = None
    
    # Pomodoro'yu kaldığı yerden devam ettir
    if st.session_state.pomodoro_active:
        st.session_state.time_remaining = st.session_state.breathing_paused_time
        st.session_state.start_time = time.time()
    
    st.success("🎉 Hibrit nefes molası tamamlandı! Pomodoro kaldığı yerden devam ediyor.")
    st.balloons()

def show_breathing_exercise():
    """Hibrit nefes egzersizini göster - 5 saniyede bir değişen motivasyon ile"""
    breath_seconds = int(st.session_state.breath_time_remaining)
    
    # 5 saniyede bir motivasyon içeriğini değiştir
    current_time = int(time.time())
    
    # Her 5 saniyede bir yeni içerik seç
    if not hasattr(st.session_state, 'last_motivation_change'):
        st.session_state.last_motivation_change = current_time
        st.session_state.motivation_index = 0
    
    if current_time - st.session_state.last_motivation_change >= 5:
        st.session_state.last_motivation_change = current_time
        st.session_state.motivation_index = (st.session_state.motivation_index + 1) % len(MOTIVATION_QUOTES)
        
        # Yeni motivasyon türü ve içerik seç
        motivation_types = ['quote', 'tip', 'breathing']
        st.session_state.current_motivation_type = random.choice(motivation_types)
        
        if st.session_state.current_motivation_type == 'quote':
            st.session_state.current_motivation_content = MOTIVATION_QUOTES[st.session_state.motivation_index]
        elif st.session_state.current_motivation_type == 'tip':
            subject = st.session_state.current_subject or 'Genel'
            if subject in MICRO_TIPS:
                st.session_state.current_motivation_content = random.choice(MICRO_TIPS[subject])
            else:
                st.session_state.current_motivation_content = random.choice(MICRO_TIPS['Genel'])
        else:  # breathing
            exercise = random.choice(BREATHING_EXERCISES)
            st.session_state.current_motivation_content = f"🫁 **{exercise['name']}**\n\n📋 {exercise['instruction']}\n\n✨ **Faydası:** {exercise['benefit']}"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
    ">
        <h2 style="color: white; margin-bottom: 20px;">🌬️ Hibrit Nefes Molası</h2>
        <div style="font-size: 72px; font-weight: bold; margin: 20px 0;">
            {breath_seconds}s
        </div>
        <div style="
            font-size: 18px; 
            font-style: italic; 
            margin: 20px 0; 
            min-height: 120px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border-left: 4px solid #ffd700;
            transition: all 0.5s ease-in-out;
        ">
            {st.session_state.current_motivation_content}
        </div>
        <div style="font-size: 12px; opacity: 0.8; margin-top: 10px;">
            💡 İçerik her 5 saniyede değişir
        </div>
        <div style="font-size: 14px; opacity: 0.9; margin-top: 15px;">
            🍅 Pomodoro timer duraklatıldı • Kaldığı yerden devam edecek
        </div>
    </div>
    
    <style>
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
        100% {{ transform: scale(1); }}
    }}
    </style>
    """, unsafe_allow_html=True)



def get_subjects_by_field_yks(field):
    """Alan bazında dersleri döndürür"""
    if field == "Sayısal":
        return ["TYT Matematik", "TYT Geometri", "TYT Fizik", "TYT Kimya", "TYT Biyoloji", 
                "AYT Matematik", "AYT Fizik", "AYT Kimya", "AYT Biyoloji"]
    elif field == "Sözel":
        return ["TYT Türkçe", "TYT Tarih", "TYT Coğrafya", "TYT Felsefe", "TYT Din Kültürü",
                "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
    elif field == "Eşit Ağırlık":
        return ["TYT Matematik", "TYT Geometri", "TYT Türkçe", "TYT Tarih", "TYT Coğrafya",
                "AYT Matematik", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
    else:
        return list(YKS_TOPICS.keys())

def determine_topic_priority_by_performance(topic, user_data):
    """Konunun öğrenci performansına göre öncelik seviyesini belirler"""
    # Konu takip verisinden mevcut net değerini al
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    topic_key = f"{topic['subject']} | {topic['topic']} | {topic.get('main_topic', 'None')} | {topic['detail']}"
    
    # Deneme analizinden de kontrol et
    deneme_weakness_boost = check_topic_weakness_in_exams(topic, user_data)
    
    # Net değerini al
    net_str = topic_progress.get(topic_key, '0')
    try:
        net_value = int(float(net_str))
    except:
        net_value = 0
    
    # Net seviyesine göre öncelik belirle
    base_priority = get_priority_by_net_level(net_value)
    
    # Deneme analizinde zayıf çıkanları bir seviye yükselt
    if deneme_weakness_boost:
        if base_priority == "MINIMAL":
            base_priority = "LOW"
        elif base_priority == "LOW":
            base_priority = "NORMAL"
        elif base_priority == "NORMAL":
            base_priority = "MEDIUM"
        elif base_priority == "MEDIUM":
            base_priority = "HIGH"
        # HIGH zaten en yüksek, değişmez
    
    return base_priority

def get_priority_by_net_level(net_value):
    """Net değerine göre öncelik seviyesi döndürür"""
    if net_value <= 5:
        return "HIGH"        # 🔴 Zayıf Seviye → Acil
    elif net_value <= 8:
        return "MEDIUM"      # 🟠 Temel Seviye → Öncelikli
    elif net_value <= 14:
        return "NORMAL"      # 🟡 Orta Seviye → Normal
    elif net_value <= 18:
        return "LOW"         # 🟢 İyi Seviye → Düşük
    else:
        return "MINIMAL"     # 🔵 Uzman Seviye → Minimal

def check_topic_weakness_in_exams(topic, user_data):
    """Deneme analizinde bu konunun zayıf olup olmadığını kontrol eder"""
    try:
        deneme_data_str = user_data.get('deneme_analizleri', '[]')
        deneme_kayitlari = json.loads(deneme_data_str) if deneme_data_str else []
        
        # Son 3 denemede bu konunun durumunu kontrol et
        recent_exams = deneme_kayitlari[-3:] if len(deneme_kayitlari) >= 3 else deneme_kayitlari
        
        for deneme in recent_exams:
            # Deneme detaylarında bu konu/ders zayıf kategorideyse
            if 'ders_netleri' in deneme:
                subject = topic['subject']
                if subject in deneme['ders_netleri']:
                    net_info = deneme['ders_netleri'][subject]
                    # Net oranı %50'nin altındaysa zayıf
                    if isinstance(net_info, dict) and 'net' in net_info and 'total' in net_info:
                        try:
                            oran = net_info['net'] / net_info['total'] if net_info['total'] > 0 else 0
                            if oran < 0.5:  # %50'nin altında başarı
                                return True
                        except:
                            continue
            
            # Tavsiyelerde bu ders geçiyorsa
            if 'tavsiyeler' in deneme:
                for tavsiye in deneme['tavsiyeler']:
                    if topic['subject'] in tavsiye and any(word in tavsiye.lower() for word in ['zayıf', 'tekrar', 'çalış', 'boşluk']):
                        return True
        
        return False
    except:
        return False

def calculate_subject_priority_new(subject, user_data, survey_data):
    """YENİ SİSTEM: Ders önceliğini konu takip seviyelerine göre hesaplar"""
    # Dersin genel performansını hesapla
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    subject_avg_net = calculate_subject_average_net(subject, topic_progress)
    
    # Net seviyesine göre temel öncelik
    base_priority_score = get_subject_priority_score_by_net(subject_avg_net)
    
    # Deneme analizinde bu ders zayıfsa boost ver
    deneme_weakness_boost = check_subject_weakness_in_exams(subject, user_data)
    if deneme_weakness_boost:
        base_priority_score += 20
    
    # Survey'den zorluk bilgisi (hafif etki)
    if subject in survey_data.get('difficult_subjects', []):
        base_priority_score += 10
    
    # Maksimum 100 puan
    return min(100, base_priority_score)

def get_subject_priority_score_by_net(avg_net):
    """Ders ortalama netine göre öncelik puanı"""
    if avg_net <= 5:
        return 85       # Acil - Çok zayıf
    elif avg_net <= 8:
        return 70       # Öncelikli - Temel seviye
    elif avg_net <= 14:
        return 50       # Normal - Orta seviye
    elif avg_net <= 18:
        return 30       # Düşük - İyi seviye
    else:
        return 15       # Minimal - Uzman seviye

def check_subject_weakness_in_exams(subject, user_data):
    """Deneme analizinde bu dersin zayıf olup olmadığını kontrol eder"""
    try:
        deneme_data_str = user_data.get('deneme_analizleri', '[]')
        deneme_kayitlari = json.loads(deneme_data_str) if deneme_data_str else []
        
        # Son 3 denemede bu dersin durumunu kontrol et
        recent_exams = deneme_kayitlari[-3:] if len(deneme_kayitlari) >= 3 else deneme_kayitlari
        weakness_count = 0
        
        for deneme in recent_exams:
            if 'ders_netleri' in deneme and subject in deneme['ders_netleri']:
                net_info = deneme['ders_netleri'][subject]
                try:
                    # Net oranını kontrol et
                    if isinstance(net_info, dict) and 'net' in net_info and 'total' in net_info:
                        oran = net_info['net'] / net_info['total'] if net_info['total'] > 0 else 0
                        if oran < 0.6:  # %60'ın altında başarı
                            weakness_count += 1
                except:
                    continue
        
        # 3 denemeden 2'sinde zayıfsa boost ver
        return weakness_count >= 2
    except:
        return False

def calculate_subject_average_net(subject, topic_progress):
    """Bir dersin ortalama net performansını hesaplar"""
    if subject not in YKS_TOPICS:
        return 0
        
    total_net = 0
    topic_count = 0
    
    for main_topic, sub_topics in YKS_TOPICS[subject].items():
        if isinstance(sub_topics, dict):
            for sub_topic, details in sub_topics.items():
                for detail in details:
                    topic_key = f"{subject} | {main_topic} | {sub_topic} | {detail}"
                    net_str = topic_progress.get(topic_key, '0')
                    try:
                        net_value = int(float(net_str))
                        total_net += net_value
                        topic_count += 1
                    except:
                        continue
        elif isinstance(sub_topics, list):
            for detail in sub_topics:
                topic_key = f"{subject} | {main_topic} | None | {detail}"
                net_str = topic_progress.get(topic_key, '0')
                try:
                    net_value = int(float(net_str))
                    total_net += net_value
                    topic_count += 1
                except:
                    continue
    
    return total_net / topic_count if topic_count > 0 else 0

def get_sequential_topics(subject, topic_progress, limit=5):
    """Bir dersten sıralı olarak bir sonraki konuları getirir"""
    if subject not in YKS_TOPICS:
        return []
        
    topics = []
    subject_content = YKS_TOPICS[subject]
    
    # İçerik tipini kontrol et
    if isinstance(subject_content, dict):
        # Sözlük formatındaysa
        for main_topic, sub_topics in subject_content.items():
            if isinstance(sub_topics, dict):
                # Alt konular da sözlük
                for sub_topic, details in sub_topics.items():
                    for detail in details:
                        topic_key = f"{subject} | {main_topic} | {sub_topic} | {detail}"
                        net_str = topic_progress.get(topic_key, '0')
                        try:
                            net_value = int(float(net_str))
                            if net_value < 14:  # İyi seviyenin altında
                                topics.append({
                                    'subject': subject,
                                    'main_topic': main_topic,
                                    'topic': sub_topic,
                                    'detail': detail,
                                    'key': topic_key,
                                    'net': net_value,
                                    'order': len(topics)  # Sıralı index
                                })
                                if len(topics) >= limit:
                                    return topics
                        except:
                            # Net bilgisi yoksa 0 kabul et
                            topics.append({
                                'subject': subject,
                                'main_topic': main_topic,
                                'topic': sub_topic,
                                'detail': detail,
                                'key': topic_key,
                                'net': 0,
                                'order': len(topics)
                            })
                            if len(topics) >= limit:
                                return topics
            elif isinstance(sub_topics, list):
                # Alt konular liste
                for detail in sub_topics:
                    topic_key = f"{subject} | {main_topic} | None | {detail}"
                    net_str = topic_progress.get(topic_key, '0')
                    try:
                        net_value = int(float(net_str))
                        if net_value < 14:
                            topics.append({
                                'subject': subject,
                                'main_topic': main_topic,
                                'topic': main_topic,
                                'detail': detail,
                                'key': topic_key,
                                'net': net_value,
                                'order': len(topics)
                            })
                            if len(topics) >= limit:
                                return topics
                    except:
                        topics.append({
                            'subject': subject,
                            'main_topic': main_topic,
                            'topic': main_topic,
                            'detail': detail,
                            'key': topic_key,
                            'net': 0,
                            'order': len(topics)
                        })
                        if len(topics) >= limit:
                            return topics
    elif isinstance(subject_content, list):
        # Ana içerik liste formatındaysa
        for detail in subject_content:
            topic_key = f"{subject} | None | None | {detail}"
            net_str = topic_progress.get(topic_key, '0')
            try:
                net_value = int(float(net_str))
                if net_value < 14:
                    topics.append({
                        'subject': subject,
                        'main_topic': "Genel",
                        'topic': "Genel",
                        'detail': detail,
                        'key': topic_key,
                        'net': net_value,
                        'order': len(topics)
                    })
                    if len(topics) >= limit:
                        return topics
            except:
                topics.append({
                    'subject': subject,
                    'main_topic': "Genel",
                    'topic': "Genel",
                    'detail': detail,
                    'key': topic_key,
                    'net': 0,
                    'order': len(topics)
                })
                if len(topics) >= limit:
                    return topics
    
    return topics

def calculate_spaced_repetition_topics(user_data):
    """Tekrar edilmesi gereken konuları bilimsel aralıklarla hesaplar"""
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    completion_dates = json.loads(user_data.get('topic_completion_dates', '{}') or '{}')
    
    current_date = datetime.now()
    review_topics = []
    
    for topic_key, net_str in topic_progress.items():
        try:
            net_value = int(float(net_str))
            if net_value >= 14:  # İyi seviye ve üzeri
                completion_date_str = completion_dates.get(topic_key)
                if completion_date_str:
                    completion_date = datetime.fromisoformat(completion_date_str)
                    days_passed = (current_date - completion_date).days
                    
                    # Hangi tekrar aralığında olduğunu bul
                    review_interval = None
                    priority = "REPEAT_NORMAL"
                    
                    for i, interval in enumerate(SPACED_REPETITION_INTERVALS):
                        if days_passed >= interval - 1 and days_passed <= interval + 1:
                            review_interval = interval
                            # Kritiklik seviyesi
                            if i == 0:  # 3 gün
                                priority = "REPEAT_HIGH"
                            elif i <= 2:  # 7, 14 gün
                                priority = "REPEAT_MEDIUM"
                            else:  # 30, 90 gün
                                priority = "REPEAT_NORMAL"
                            break
                    
                    if review_interval:
                        # Topic key'den subject ve diğer bilgileri çıkar
                        parts = topic_key.split(' | ')
                        if len(parts) >= 4:
                            review_topics.append({
                                'subject': parts[0],
                                'main_topic': parts[1],
                                'topic': parts[2] if parts[2] != 'None' else parts[1],
                                'detail': parts[3],
                                'key': topic_key,
                                'net': net_value,
                                'days_passed': days_passed,
                                'interval': review_interval,
                                'priority': priority,
                                'completion_date': completion_date_str
                            })
        except:
            continue
    
    # Öncelik sırasına göre sırala
    priority_order = {"REPEAT_HIGH": 0, "REPEAT_MEDIUM": 1, "REPEAT_NORMAL": 2}
    review_topics.sort(key=lambda x: (priority_order.get(x['priority'], 3), x['days_passed']))
    
    return review_topics

def get_weekly_topics_from_topic_tracking(user_data, student_field, survey_data):
    """YENİ SİSTEMATİK HAFTALİK PLAN ÜRETİCİSİ - TYT/AYT AKILLI GEÇİŞ SİSTEMİ"""
    # TYT ve AYT ilerlemesini hesapla
    tyt_progress = calculate_tyt_progress(user_data)
    tyt_math_topics_completed = count_tyt_math_completed_topics(user_data)
    
    # Alan bazında dersleri al
    available_subjects = get_subjects_by_field_yks(student_field)
    
    # AYT başlatma koşullarını kontrol et
    include_ayt = should_include_ayt(tyt_progress, tyt_math_topics_completed)
    
    # Konuların TYT/AYT durumuna göre filtrele
    filtered_subjects = []
    for subject in available_subjects:
        if subject.startswith('AYT') and not include_ayt:
            continue  # AYT henüz başlamadı
        filtered_subjects.append(subject)
    
    # Her dersin öncelik puanını hesapla (YENİ SİSTEM)
    subject_priorities = {}
    for subject in filtered_subjects:
        priority_score = calculate_subject_priority_new(subject, user_data, survey_data)
        subject_priorities[subject] = priority_score
    
    # Öncelik sırasına göre sırala
    sorted_subjects = sorted(subject_priorities.items(), key=lambda x: x[1], reverse=True)
    
    # Haftalık plan oluştur
    weekly_new_topics = []
    weekly_review_topics = []
    
    # 1. YENİ KONULAR (Sıralı İlerleme)
    for subject, priority_score in sorted_subjects:
        # Ders önem puanına göre haftalık limit
        importance = SUBJECT_IMPORTANCE_SCORES.get(subject, 5)
        weekly_limit = WEEKLY_TOPIC_LIMITS.get(importance, 1)
        
        # Düşük öncelikli dersleri 2-3. hafta sonra başlat
        if importance <= 4:
            # Sistem kullanım süresini kontrol et (basit yaklaşım)
            user_creation = user_data.get('created_at', '')
            if user_creation:
                try:
                    creation_date = datetime.fromisoformat(user_creation)
                    weeks_passed = (datetime.now() - creation_date).days // 7
                    if weeks_passed < 2:  # İlk 2 hafta atla
                        continue
                except:
                    continue
        
        # Sıralı konuları al
        sequential_topics = get_sequential_topics(subject, 
            json.loads(user_data.get('topic_progress', '{}') or '{}'), 
            limit=weekly_limit)
        
        # YENİ SİSTEM: Her konunun bireysel önceliğini performansa göre belirle
        for topic in sequential_topics:
            topic['priority'] = determine_topic_priority_by_performance(topic, user_data)
        
        weekly_new_topics.extend(sequential_topics)
    
    # 2. TEKRAR KONULARI (Bilimsel Aralıklarla)
    review_topics = calculate_spaced_repetition_topics(user_data)
    weekly_review_topics = review_topics[:8]  # Max 8 tekrar konusu/hafta
    
    # 3. TOPLAM PLAN
    total_plan = {
        'new_topics': weekly_new_topics[:15],  # Max 15 yeni konu
        'review_topics': weekly_review_topics,
        'week_target': len(weekly_new_topics[:15]) + len(weekly_review_topics),
        'success_target': 0.8,  # %80 başarı hedefi
        'projections': calculate_completion_projections(user_data, student_field),
        'tyt_progress': tyt_progress,
        'ayt_enabled': include_ayt,
        'tyt_math_completed': tyt_math_topics_completed
    }
    
    return total_plan

def calculate_tyt_progress(user_data):
    """TYT ilerlemesini yüzde olarak hesaplar"""
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    
    tyt_total = 0
    tyt_completed = 0
    
    # Sadece TYT dersleri
    for subject in YKS_TOPICS.keys():
        if not subject.startswith('TYT'):
            continue
        
        subject_content = YKS_TOPICS[subject]
        
        # İçerik tipini kontrol et
        if isinstance(subject_content, dict):
            # Sözlük formatındaysa
            for main_topic, sub_topics in subject_content.items():
                if isinstance(sub_topics, dict):
                    # Alt konular da sözlük
                    for sub_topic, details in sub_topics.items():
                        for detail in details:
                            topic_key = f"{subject} | {main_topic} | {sub_topic} | {detail}"
                            tyt_total += 1
                            try:
                                net_value = int(float(topic_progress.get(topic_key, '0')))
                                if net_value >= 14:  # İyi seviye
                                    tyt_completed += 1
                            except:
                                continue
                elif isinstance(sub_topics, list):
                    # Alt konular liste
                    for detail in sub_topics:
                        topic_key = f"{subject} | {main_topic} | None | {detail}"
                        tyt_total += 1
                        try:
                            net_value = int(float(topic_progress.get(topic_key, '0')))
                            if net_value >= 14:  # İyi seviye
                                tyt_completed += 1
                        except:
                            continue
        elif isinstance(subject_content, list):
            # Ana içerik liste formatındaysa
            for detail in subject_content:
                topic_key = f"{subject} | None | None | {detail}"
                tyt_total += 1
                try:
                    net_value = int(float(topic_progress.get(topic_key, '0')))
                    if net_value >= 14:  # İyi seviye
                        tyt_completed += 1
                except:
                    continue
    
    if tyt_total > 0:
        return (tyt_completed / tyt_total) * 100
    return 0

def count_tyt_math_completed_topics(user_data):
    """TYT Matematik'te tamamlanan konu sayısını hesaplar"""
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    
    if "TYT Matematik" not in YKS_TOPICS:
        return 0
    
    completed_count = 0
    subject_content = YKS_TOPICS["TYT Matematik"]
    
    # İçerik tipini kontrol et
    if isinstance(subject_content, dict):
        # Sözlük formatındaysa
        for main_topic, sub_topics in subject_content.items():
            if isinstance(sub_topics, dict):
                # Alt konular da sözlük
                for sub_topic, details in sub_topics.items():
                    for detail in details:
                        topic_key = f"TYT Matematik | {main_topic} | {sub_topic} | {detail}"
                        try:
                            net_value = int(float(topic_progress.get(topic_key, '0')))
                            if net_value >= 14:  # İyi seviye
                                completed_count += 1
                        except:
                            continue
            elif isinstance(sub_topics, list):
                # Alt konular liste
                for detail in sub_topics:
                    topic_key = f"TYT Matematik | {main_topic} | None | {detail}"
                    try:
                        net_value = int(float(topic_progress.get(topic_key, '0')))
                        if net_value >= 14:  # İyi seviye
                            completed_count += 1
                    except:
                        continue
    elif isinstance(subject_content, list):
        # Ana içerik liste formatındaysa
        for detail in subject_content:
            topic_key = f"TYT Matematik | None | None | {detail}"
            try:
                net_value = int(float(topic_progress.get(topic_key, '0')))
                if net_value >= 14:  # İyi seviye
                    completed_count += 1
            except:
                continue
    
    return completed_count

def should_include_ayt(tyt_progress, tyt_math_completed):
    """AYT konularının dahil edilip edilmeyeceğini belirler"""
    # Koşul 1: TYT'nin %60'ı tamamlanmış olmalı
    condition1 = tyt_progress >= 60.0
    
    # Koşul 2: TYT Matematik'te en az 12 konu tamamlanmış olmalı
    condition2 = tyt_math_completed >= 12
    
    # Her iki koşul da sağlanmalı
    return condition1 and condition2

def calculate_completion_projections(user_data, student_field):
    """Uzun vadeli tamamlanma tahminleri"""
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    available_subjects = get_subjects_by_field_yks(student_field)
    
    projections = {
        'overall_progress': 0,
        'tyt_progress': 0,
        'ayt_progress': 0,
        'estimated_completion': None,
        'monthly_targets': [],
        'weekly_average': 0
    }
    
    total_topics = 0
    completed_topics = 0
    tyt_total = 0
    tyt_completed = 0
    ayt_total = 0
    ayt_completed = 0
    
    # Her dersin ilerlemesini hesapla
    for subject in available_subjects:
        if subject not in YKS_TOPICS:
            continue
            
        subject_total = 0
        subject_completed = 0
        subject_content = YKS_TOPICS[subject]
        
        # İçerik tipini kontrol et
        if isinstance(subject_content, dict):
            # Sözlük formatındaysa
            for main_topic, sub_topics in subject_content.items():
                if isinstance(sub_topics, dict):
                    # Alt konular da sözlük
                    for sub_topic, details in sub_topics.items():
                        for detail in details:
                            topic_key = f"{subject} | {main_topic} | {sub_topic} | {detail}"
                            subject_total += 1
                            try:
                                net_value = int(float(topic_progress.get(topic_key, '0')))
                                if net_value >= 14:
                                    subject_completed += 1
                            except:
                                continue
                elif isinstance(sub_topics, list):
                    # Alt konular liste
                    for detail in sub_topics:
                        topic_key = f"{subject} | {main_topic} | None | {detail}"
                        subject_total += 1
                        try:
                            net_value = int(float(topic_progress.get(topic_key, '0')))
                            if net_value >= 14:
                                subject_completed += 1
                        except:
                            continue
        elif isinstance(subject_content, list):
            # Ana içerik liste formatındaysa
            for detail in subject_content:
                topic_key = f"{subject} | None | None | {detail}"
                subject_total += 1
                try:
                    net_value = int(float(topic_progress.get(topic_key, '0')))
                    if net_value >= 14:
                        subject_completed += 1
                except:
                    continue
        
        total_topics += subject_total
        completed_topics += subject_completed
        
        # TYT/AYT ayrımı
        if subject.startswith('TYT'):
            tyt_total += subject_total
            tyt_completed += subject_completed
        elif subject.startswith('AYT'):
            ayt_total += subject_total
            ayt_completed += subject_completed
    
    # İlerleme yüzdelerini hesapla
    if total_topics > 0:
        projections['overall_progress'] = (completed_topics / total_topics) * 100
    if tyt_total > 0:
        projections['tyt_progress'] = (tyt_completed / tyt_total) * 100
    if ayt_total > 0:
        projections['ayt_progress'] = (ayt_completed / ayt_total) * 100
    
    # Haftalık ortalama hesapla (son 4 hafta simülasyonu)
    weekly_avg = 12  # Varsayılan haftalık tamamlama
    projections['weekly_average'] = weekly_avg
    
    # Tahmini bitiş tarihi
    remaining_topics = total_topics - completed_topics
    if remaining_topics > 0 and weekly_avg > 0:
        weeks_needed = remaining_topics / (weekly_avg * 0.8)  # %80 başarı faktörü
        completion_date = datetime.now() + timedelta(weeks=weeks_needed)
        projections['estimated_completion'] = completion_date.strftime("%d %B %Y")
    
    return projections


def get_topic_level_from_tracking(topic, user_data):
    """Bir konunun mevcut seviyesini Konu Takip'ten alır"""
    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
    current_net = topic_progress.get(topic['key'], '0')
    
    try:
        net_value = int(float(current_net))
        level_display = calculate_level(net_value)
        return {
            'net': net_value,
            'level': net_value,
            'display': level_display
        }
    except:
        return {
            'net': 0,
            'level': 0,
            'display': "🔴 Zayıf Seviye (0-5 net)"
        }

def get_level_icon_yks(level):
    """Seviyeye göre ikon döndürür"""
    if level <= 5:
        return "🔴"
    elif level <= 8:
        return "🟠"
    elif level <= 14:
        return "🟡"
    elif level <= 18:
        return "🟢"
    else:
        return "🔵"

def count_completed_topics(weekly_plan, user_data):
    """Haftalık plandaki tamamlanan konu sayısını hesaplar"""
    if not weekly_plan:
        return 0
        
    new_topics = weekly_plan.get('new_topics', [])
    review_topics = weekly_plan.get('review_topics', [])
    all_topics = new_topics + review_topics
    
    completed = 0
    for topic in all_topics:
        if topic.get('net', 0) >= 14:  # İyi seviye
            completed += 1
    return completed

def main():
    if 'users_db' not in st.session_state:
        st.session_state.users_db = load_users_from_firebase()
    
    if 'current_user' not in st.session_state:
        st.session_state.current_user = None
    
    if st.session_state.current_user is None:
        st.markdown(get_custom_css("Varsayılan"), unsafe_allow_html=True)
        st.markdown('<div class="main-header"><h1>🎯 YKS Takip Sistemi</h1><p>Hedefine Bilimsel Yaklaşım</p></div>', unsafe_allow_html=True)
        
        st.subheader("🔐 Giriş Yap")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        
        if st.button("Giriş Yap", type="primary", use_container_width=True):
            if login_user(username, password):
                st.success("Giriş başarılı!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Hatalı kullanıcı adı veya şifre!")
    
    else:
        user_data = get_user_data()
        
        profile_complete = user_data.get('name') and user_data.get('tyt_avg_net')
        learning_style_complete = user_data.get('learning_style')
        
        if not profile_complete:
            st.markdown(get_custom_css("Varsayılan"), unsafe_allow_html=True)
            st.markdown('<div class="main-header"><h1>📝 Profil Bilgilerinizi Tamamlayın</h1><p>Sistemi size özel hale getirmek için bu bilgileri doldurmalısınız</p></div>', unsafe_allow_html=True)
            
            st.subheader("Öğrenci Bilgileri")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Adınız", key="name_input")
                surname = st.text_input("Soyadınız", key="surname_input")
                grade = st.selectbox("Sınıfınız", ["11. Sınıf", "12. Sınıf", "Mezun"], key="grade_input")
                field = st.selectbox("Alanınız", ["Sayısal", "Sözel", "Eşit Ağırlık"], key="field_input")
                target = st.selectbox("Hedef Bölümünüz", list(BACKGROUND_STYLES.keys())[:-1], key="target_input")
            
            with col2:
                st.subheader("📊 Net Bilgileri")
                st.write("**TYT Netler**")
                tyt_last = st.number_input("Son TYT Neti", min_value=0.0, max_value=120.0, step=0.25, key="tyt_last_input")
                tyt_avg = st.number_input("Genel TYT Ortalaması", min_value=0.0, max_value=120.0, step=0.25, key="tyt_avg_input")
                
                st.write("**AYT Netler**")
                ayt_last = st.number_input("Son AYT Neti", min_value=0.0, max_value=80.0, step=0.25, key="ayt_last_input")
                ayt_avg = st.number_input("Genel AYT Ortalaması", min_value=0.0, max_value=80.0, step=0.25, key="ayt_avg_input")
            
            if st.button("💾 Bilgileri Kaydet", type="primary", use_container_width=True):
                if name and surname and target and tyt_last is not None and tyt_avg is not None and ayt_last is not None and ayt_avg is not None:
                    update_user_in_firebase(st.session_state.current_user, {
                        'name': name,
                        'surname': surname,
                        'grade': grade,
                        'field': field,
                        'target_department': target,
                        'tyt_last_net': str(tyt_last),
                        'tyt_avg_net': str(tyt_avg),
                        'ayt_last_net': str(ayt_last),
                        'ayt_avg_net': str(ayt_avg),
                        'is_profile_complete': 'True' 
                           
                    })
                    
                    st.session_state.users_db = load_users_from_firebase()
                    st.session_state.is_profile_complete = True 
                    st.success("🎉 Bilgileriniz başarıyla kaydedildi! Şimdi öğrenme stilinizi belirleyelim.")
                    
                    st.rerun()
                else:
                    st.error("⚠️ Lütfen tüm alanları doldurun!")
        
        elif not learning_style_complete:
            st.markdown(get_custom_css("Varsayılan"), unsafe_allow_html=True)
            st.markdown('<div class="main-header"><h1>🧠 Öğrenme Stili Testi</h1><p>Sana özel çalışma programı için son adım!</p></div>', unsafe_allow_html=True)
            
            st.markdown('<div class="psychology-test">', unsafe_allow_html=True)
            st.subheader("🎯 Öğrenme Stilinizi Keşfedin")
            st.write("Aşağıdaki soruları cevaplayarak öğrenme stilinizi belirleyelim:")
            
            answers = []
            for i, question_data in enumerate(LEARNING_STYLE_TEST, 1):
                st.write(f"**{i}. {question_data['question']}**")
                answer = st.radio(
                    f"Soru {i}",
                    list(question_data['options'].keys()),
                    format_func=lambda x: f"{x}: {question_data['options'][x]['text']}",
                    key=f"q_{i}"
                )
                answers.append(answer)
            
            if st.button("🪄 Sonucu Gör ve Devam Et", type="primary"):
                style_percentages, dominant_style = determine_learning_style(answers)
                
                update_user_in_firebase(st.session_state.current_user, {
                    'learning_style': dominant_style,
                    'learning_style_scores': json.dumps(style_percentages)
                })
                st.session_state.users_db = load_users_from_firebase() 
                
                st.success(f"🎉 Öğrenme Stiliniz: **{dominant_style}** (%{style_percentages[dominant_style]})")
                st.info("Profiliniz artık tamamlandı! Uygulamaya yönlendiriliyorsunuz.")
                
                st.balloons()
                time.sleep(3)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            target_dept = user_data.get('target_department', 'Varsayılan')
            
            st.markdown(get_custom_css(target_dept), unsafe_allow_html=True)
            
            progress_data = calculate_subject_progress(user_data)
            
            with st.sidebar:
                bg_style = BACKGROUND_STYLES.get(target_dept, BACKGROUND_STYLES["Varsayılan"])
                st.markdown(f"### {bg_style['icon']} Hoş geldin, {user_data.get('name', 'Öğrenci')}!")
                st.markdown(f"**🎯 Hedef:** {user_data.get('target_department', 'Belirlenmedi')}")
                st.markdown(f"**📊 Alan:** {user_data.get('field', 'Belirlenmedi')}")
                st.markdown(f"**🏫 Sınıf:** {user_data.get('grade', 'Belirlenmedi')}")
                st.markdown("---")
                st.markdown("**📈 Net Durumu**")
                st.markdown(f"TYT Son: {user_data.get('tyt_last_net', 'Belirlenmedi')}")
                st.markdown(f"TYT Ort: {user_data.get('tyt_avg_net', 'Belirlenmedi')}")
                st.markdown(f"AYT Son: {user_data.get('ayt_last_net', 'Belirlenmedi')}")
                st.markdown(f"AYT Ort: {user_data.get('ayt_avg_net', 'Belirlenmedi')}")
                
                st.markdown("---")
                st.markdown("**🧠 Öğrenme Stili Dağılımı**")
                style_scores_str = user_data.get('learning_style_scores', None)
                if style_scores_str:
                    try:
                        style_scores = json.loads(style_scores_str.replace("'", "\""))
                        sorted_styles = sorted(style_scores.items(), key=lambda item: item[1], reverse=True)
                        for style, score in sorted_styles:
                            if score > 0:
                                st.write(f"- {style}: %{score:.1f}")
                    except json.JSONDecodeError:
                        st.write("Veri Hatası")
                else:
                    st.write("Henüz belirlenmedi.")
                
                total_completed = sum(data['completed'] for data in progress_data.values())
                total_topics = count_total_topics()
                genel_ilerleme = (total_completed / total_topics * 100) if total_topics > 0 else 0
                    
                st.markdown("---")
                st.metric("📈 Genel İlerleme", f"%{genel_ilerleme:.1f}")
                st.metric("✅ Tamamlanan", f"{total_completed}/{total_topics}")
                
                if st.button("🚪 Çıkış Yap", use_container_width=True):
                    st.session_state.current_user = None
                    st.rerun()
            
            page = st.sidebar.selectbox("🌐 Sayfa Seçin", 
                                      ["🏠 Ana Sayfa", "📚 Konu Takip", "⚙️ Benim Programım","🧠 Çalışma Teknikleri","🎯 YKS Canlı Takip", "🍅 Pomodoro Timer", "🧠 Psikolojim","🔬Detaylı Deneme Analiz Takibi","📊 İstatistikler"])
            
            if page == "🏠 Ana Sayfa":
                bg_style = BACKGROUND_STYLES.get(target_dept, BACKGROUND_STYLES["Varsayılan"])
                st.markdown(f'<div class="main-header"><h1>{bg_style["icon"]} {user_data["target_department"]} Yolculuğunuz</h1><p>Hedefinize doğru emin adımlarla ilerleyin</p></div>', unsafe_allow_html=True)
                
                display_progress_summary(user_data, progress_data)
                
                st.subheader("📈 Hız Göstergesi İlerleme")
                
                important_subjects = []
                if user_data.get('field') == "Sayısal":
                    important_subjects = ["TYT Türkçe", "TYT Matematik", "TYT Geometri", "TYT Fizik", "TYT Kimya", "TYT Biyoloji", "AYT Matematik", "AYT Fizik", "AYT Kimya", "AYT Biyoloji"]
                elif user_data.get('field') == "Eşit Ağırlık":
                    important_subjects = ["TYT Türkçe", "TYT Matematik", "TYT Geometri", "TYT Tarih", "TYT Coğrafya", "AYT Matematik", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
                elif user_data.get('field') == "Sözel":
                    important_subjects = ["TYT Türkçe", "TYT Tarih", "TYT Coğrafya", "TYT Felsefe", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
                
                display_subjects = [s for s in important_subjects if s in progress_data]

                subject_icons = {
                    "TYT Türkçe": "📚", "TYT Matematik": "🔢", "TYT Geometri": "📐",
                    "TYT Tarih": "🏛️", "TYT Coğrafya": "🌍", "TYT Felsefe": "💭", "TYT Din Kültürü": "🕌",
                    "TYT Fizik": "⚡", "TYT Kimya": "🧪", "TYT Biyoloji": "🧬",
                    "AYT Matematik": "🧮", "AYT Fizik": "⚛️", "AYT Kimya": "🔬", "AYT Biyoloji": "🔭",
                    "AYT Edebiyat": "📜", "AYT Tarih": "📖", "AYT Coğrafya": "🗺️"
                }
                
                if display_subjects:
                    cols = st.columns(min(len(display_subjects), 4))  # Maksimum 4 sütun
                    for i, subject in enumerate(display_subjects):
                        if subject in progress_data:
                            percent = progress_data[subject]["percent"]
                            subject_name_short = subject.replace("TYT ", "").replace("AYT ", "")
                            with cols[i % len(cols)]:
                                fig = go.Figure(go.Indicator(
                                    mode = "gauge+number",
                                    value = percent,
                                    domain = {'x': [0, 1], 'y': [0, 1]},
                                    title = {'text': f"{subject_icons.get(subject, '📖')} {subject_name_short}"},
                                    gauge = {
                                        'axis': {'range': [None, 100]},
                                        'bar': {'color': "#654ea3"},
                                        'steps': [
                                            {'range': [0, 33], 'color': "#ff6b6b"},
                                            {'range': [33, 66], 'color': "#ffd166"},
                                            {'range': [66, 100], 'color': "#06d6a0"}
                                        ]
                                    }
                                ))
                                fig.update_layout(height=200, margin=dict(l=10, r=10, t=50, b=10))
                                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                st.subheader("📋 Son Aktivite Özeti")
                recent_activities = [
                    {"ders": "TYT Matematik", "konu": "Problemler", "tarih": "Bugün", "durum": "Tamamlandı"},
                    {"ders": "AYT Fizik", "konu": "Elektrik", "tarih": "Dün", "durum": "Devam Ediyor"},
                    {"ders": "TYT Türkçe", "konu": "Paragraf", "tarih": "2 gün önce", "durum": "Tamamlandı"}
                ]
                for activity in recent_activities:
                    with st.container():
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.write(f"**{activity['ders']}** - {activity['konu']}")
                        with col2:
                            st.write(activity['tarih'])
                        with col3:
                            if activity['durum'] == "Tamamlandı": st.success("✅")
                            else: st.info("⏳")

            elif page == "📚 Konu Takip":
                st.markdown(f'<div class="main-header"><h1>📚 Konu Takip Sistemi</h1><p>Her konuda ustalaşın</p></div>', unsafe_allow_html=True)
                
                user_field = user_data.get('field', 'Belirlenmedi')
                
                if user_field == "Sayısal":
                    available_subjects = ["TYT Türkçe", "TYT Matematik", "TYT Geometri", "TYT Fizik", "TYT Kimya", "TYT Biyoloji", "AYT Matematik", "AYT Fizik", "AYT Kimya", "AYT Biyoloji"]
                elif user_field == "Eşit Ağırlık":
                    available_subjects = ["TYT Türkçe", "TYT Matematik", "TYT Geometri", "TYT Tarih", "TYT Coğrafya", "AYT Matematik", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
                elif user_field == "Sözel":
                    available_subjects = ["TYT Türkçe", "TYT Tarih", "TYT Coğrafya", "TYT Felsefe", "TYT Din Kültürü", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya", "AYT Felsefe", "AYT Din Kültürü ve Ahlak Bilgisi"]
                else:
                    available_subjects = list(YKS_TOPICS.keys())
                
                selected_subject = st.selectbox("📖 Ders Seçin", available_subjects)

                if selected_subject and selected_subject in YKS_TOPICS:
                    st.subheader(f"{selected_subject} Konuları")
                    
                    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
                    subject_content = YKS_TOPICS[selected_subject]
                    
                    # İçerik tipini kontrol et
                    if isinstance(subject_content, dict):
                        # Sözlük formatındaysa
                        for main_topic, sub_topics in subject_content.items():
                            with st.expander(f"📂 {main_topic}", expanded=False):
                                if isinstance(sub_topics, dict):
                                    # Alt konular da sözlük
                                    for sub_topic, details in sub_topics.items():
                                        st.write(f"**📋 {sub_topic}**")
                                        for detail in details:
                                            topic_key = f"{selected_subject} | {main_topic} | {sub_topic} | {detail}"
                                            col1, col2, col3 = st.columns([3, 2, 1])
                                            with col1:
                                                st.write(f"• {detail}")
                                            with col2:
                                                current_net = topic_progress.get(topic_key, '0')
                                                try:
                                                    current_net_int = int(float(current_net))
                                                except (ValueError, TypeError):
                                                    current_net_int = 0
                                                new_net = st.slider(f"Net ({detail})", 0, 20, current_net_int, key=topic_key, label_visibility="collapsed")
                                            with col3:
                                                st.write(calculate_level(new_net))
                                            
                                            # Güncelleme
                                            if str(new_net) != current_net:
                                                topic_progress[topic_key] = str(new_net)
                                elif isinstance(sub_topics, list):
                                    # Alt konular liste
                                    for detail in sub_topics:
                                        topic_key = f"{selected_subject} | {main_topic} | None | {detail}"
                                        col1, col2, col3 = st.columns([3, 2, 1])
                                        with col1:
                                            st.write(f"• {detail}")
                                        with col2:
                                            current_net = topic_progress.get(topic_key, '0')
                                            try:
                                                current_net_int = int(float(current_net))
                                            except (ValueError, TypeError):
                                                current_net_int = 0
                                            new_net = st.slider(f"Net ({detail})", 0, 20, current_net_int, key=topic_key, label_visibility="collapsed")
                                        with col3:
                                            st.write(calculate_level(new_net))
                                        
                                        # Güncelleme
                                        if str(new_net) != current_net:
                                            topic_progress[topic_key] = str(new_net)
                    elif isinstance(subject_content, list):
                        # Ana içerik liste formatındaysa
                        with st.expander(f"📂 {selected_subject} Konuları", expanded=True):
                            for detail in subject_content:
                                topic_key = f"{selected_subject} | None | None | {detail}"
                                col1, col2, col3 = st.columns([3, 2, 1])
                                with col1:
                                    st.write(f"• {detail}")
                                with col2:
                                    current_net = topic_progress.get(topic_key, '0')
                                    try:
                                        current_net_int = int(float(current_net))
                                    except (ValueError, TypeError):
                                        current_net_int = 0
                                    new_net = st.slider(f"Net ({detail})", 0, 20, current_net_int, key=topic_key, label_visibility="collapsed")
                                with col3:
                                    st.write(calculate_level(new_net))
                                
                                # Güncelleme
                                if str(new_net) != current_net:
                                    topic_progress[topic_key] = str(new_net)
                                    update_user_in_firebase(st.session_state.current_user, {'topic_progress': json.dumps(topic_progress)})
                                    st.session_state.users_db = load_users_from_firebase()
                                    st.success(f"✅ {detail} neti güncellendi: {new_net}")
                    
                    # Toplu kaydetme seçeneği
                    if st.button("💾 Tüm Değişiklikleri Kaydet", type="primary"):
                        update_user_in_firebase(st.session_state.current_user, {'topic_progress': json.dumps(topic_progress)})
                        st.session_state.users_db = load_users_from_firebase()
                        st.success("✅ Tüm net değerleri başarıyla kaydedildi!")

            elif page == "⚙️ Benim Programım":
                st.markdown(f'<div class="main-header"><h1>⚙️ Benim Programım</h1><p>Derece öğrencisi disipliniyle çalışın</p></div>', unsafe_allow_html=True)
                
                user_data = get_user_data()
                
                # Program seçimi
                st.subheader("🎯 Çalışma Programını Seçin")
                selected_program = st.selectbox(
                    "Size uygun programı seçin:",
                    list(STUDY_PROGRAMS.keys()),
                    format_func=lambda x: f"{x} - {STUDY_PROGRAMS[x]['description']}"
                )
                
                program_info = STUDY_PROGRAMS[selected_program]
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📅 Program Süresi", f"{program_info['duration']} gün")
                with col2:
                    st.metric("⏰ Günlük Çalışma", f"{program_info['daily_hours']} saat")
                with col3:
                    st.metric("🎯 Hedef", program_info['target'])
                
                if st.button("🚀 Programı Başlat", type="primary", use_container_width=True):
                    study_plan = calculate_study_schedule(user_data, selected_program)
                    st.session_state.current_study_plan = study_plan
                    st.success(f"🎉 {selected_program} başlatıldı! {program_info['duration']} gün boyunca bu programı takip edeceksiniz.")
                
                # Günlük planlama
                st.markdown("---")
                st.subheader("📝 Günlük Çalışma Planı")
                
                # Günlük zaman çizelgesi
                st.write("**⏰ Örnek Günlük Zaman Çizelgesi**")
                selected_schedule = st.selectbox("Program tipi seçin:", list(DAILY_PLAN_TEMPLATES.keys()))
                
                for time_slot, activity in DAILY_PLAN_TEMPLATES[selected_schedule].items():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.write(f"**{time_slot}**")
                    with col2:
                        st.write(activity)
                
                # Haftalık hedef belirleme
                st.markdown("---")
                st.subheader("🎯 Haftalık Hedefler")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    weekly_goal_subjects = st.number_input("Haftalık ders sayısı", min_value=1, max_value=10, value=4)
                with col2:
                    weekly_goal_topics = st.number_input("Haftalık konu sayısı", min_value=1, max_value=20, value=8)
                with col3:
                    weekly_goal_hours = st.number_input("Haftalık çalışma saati", min_value=10, max_value=50, value=25)
                
                if st.button("💾 Haftalık Hedefleri Kaydet", use_container_width=True):
                    st.success("Hedefler kaydedildi! Bu hafta bu hedeflere ulaşmaya odaklanın.")
                
                # Aylık ilerleme takibi
                st.markdown("---")
                st.subheader("📈 Aylık İlerleme Takibi")
                
                # Basit bir ilerleme grafiği
                months = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran"]
                progress_data = {
                    'Ay': months,
                    'Tamamlanan Konu': [15, 28, 42, 35, 50, 65],
                    'Çalışılan Saat': [120, 135, 150, 140, 160, 180],
                    'Deneme Net Ort.': [45.2, 48.7, 52.1, 55.3, 58.9, 62.4]
                }
                
                progress_df = pd.DataFrame(progress_data)
                fig = px.line(progress_df, x='Ay', y=['Tamamlanan Konu', 'Çalışılan Saat', 'Deneme Net Ort.'], 
                             title='Aylık İlerleme Grafiği', markers=True)
                st.plotly_chart(fig, use_container_width=True)
                
                # Motivasyon ve hatırlatıcılar
                st.markdown("---")
                st.subheader("💫 Motivasyon ve Hatırlatıcılar")
                
                fmotivation_tips = [
                    "🔹 Her gün aynı saatte çalışmaya başlayarak rutin oluşturun",
                    "🔹 Büyük hedefleri küçük parçalara bölün",
                    "🔹 Her tamamlanan konu için kendinizi ödüllendirin",
                    "🔹 Düzenli molalar vererek zihninizi taze tutun",
                    "🔹 Haftada bir genel tekrar yapın",
                    "🔹 Uyku düzeninize dikkat edin",
                    "🔹 Spor yaparak stres atın"
                ]
                
                for tip in fmotivation_tips:
                    st.write(tip)
                
                # Çalışma istatistikleri
                st.markdown("---")
                st.subheader("📊 Çalışma İstatistikleri")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("🔥 Bugünkü Çalışma", "3.5 saat")
                with col2:
                    st.metric("✅ Bu Hafta Tamamlanan", "12 konu")
                with col3:
                    st.metric("🎯 Bu Ayki Hedef", "45 konu")
                with col4:
                    st.metric("📈 İlerleme Oranı", "%68")
                
                # Anlık geri bildirim
                st.markdown("---")
                st.subheader("💡 Anlık Geri Bildirim")
                
                feedback_options = {
                    "Çok verimli geçti": "🟢",
                    "Normal verimlilikte": "🟡", 
                    "Düşük verimlilik": "🔴",
                    "Planı revize etmem gerek": "🔵"
                }
                
                st.write("Bugünkü çalışmanızı nasıl değerlendiriyorsunuz?")
                selected_feedback = st.radio("Geri bildirim:", list(feedback_options.keys()))
                
                if st.button("📤 Geri Bildirimi Gönder", use_container_width=True):
                    st.success("Geri bildiriminiz kaydedildi! Programınız bu geri bildirime göre optimize edilecek.")

            elif page == "🧠 Çalışma Teknikleri":
                st.markdown(f'<div class="main-header"><h1>🧠 Çalışma Teknikleri</h1><p>Öğrenme stilinize uygun yöntemler</p></div>', unsafe_allow_html=True)
                
                st.subheader("📚 Tüm Çalışma Teknikleri")
                
                cols = st.columns(2)
                technique_list = list(STUDY_TECHNIQUES.items())
                
                for i, (technique, info) in enumerate(technique_list):
                    with cols[i % 2]:
                        with st.container():
                            st.markdown(f"### {info['icon']} {technique}")
                            st.write(info['description'])
                            st.write("**Uygun Stiller:** " + ", ".join(info['learning_style']))
                            
                            with st.expander("Detaylı İncele"):
                                st.write("**Adımlar:**")
                                for j, step in enumerate(info['steps'], 1):
                                    st.write(f"- {step}")
            
            elif page == "🎯 YKS Canlı Takip":
                yks_takip_page(user_data)
            
            elif page == "🍅 Pomodoro Timer":
                pomodoro_timer_page(user_data)
            
            
              
            
            elif page == "🧠 Psikolojim":
                st.markdown(f'<div class="main-header"><h1>🧠 Kişisel Gelişim ve Çalışma Bilimi</h1><p>Kendini tanıyarak hedefine ilerle</p></div>', unsafe_allow_html=True)
                style_scores_str = user_data.get('learning_style_scores', None)
                if style_scores_str:
                    try:
                        style_scores = json.loads(style_scores_str.replace("'", "\""))
                        dominant_style = user_data.get('learning_style')
                        
                        st.subheader("📊 Öğrenme Stili Analizi")
                        st.write("Aşağıdaki grafik, öğrenme stillerinizin yüzdelik dağılımını göstermektedir:")
                        
                        styles_df = pd.DataFrame(list(style_scores.items()), columns=['Öğrenme Stili', 'Yüzde'])
                        fig = px.pie(styles_df, values='Yüzde', names='Öğrenme Stili', title='Öğrenme Stili Dağılımınız')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown("---")
                        
                        st.subheader(f"✨ Öğrenme Psikoloğundan Tavsiyeler")
                        st.write("Test sonuçlarına göre en baskın öğrenme stilin **" + dominant_style + "** olarak belirlendi.")
                        st.markdown(f'<div class="psychology-card"><h3>{LEARNING_STYLE_DESCRIPTIONS[dominant_style]["title"]}</h3>'
                                    f'<p>{LEARNING_STYLE_DESCRIPTIONS[dominant_style]["intro"]}</p>'
                                    '<h4>Güçlü Yönlerin:</h4>'
                                    f'<ul>{"".join([f"<li>{s}</li>" for s in LEARNING_STYLE_DESCRIPTIONS[dominant_style]["strengths"]])}</ul>'
                                    '<h4>Zayıf Yönlerin:</h4>'
                                    f'<ul>{"".join([f"<li>{s}</li>" for s in LEARNING_STYLE_DESCRIPTIONS[dominant_style]["weaknesses"]])}</ul>'
                                    '<h4>Akademik Gelişim Önerileri:</h4>'
                                    f'<p>{LEARNING_STYLE_DESCRIPTIONS[dominant_style]["advice"]}</p>'
                                    '</div>', unsafe_allow_html=True)
                        
                        st.markdown("---")
                        st.subheader("💡 Size Özel Çalışma Teknikleri")
                        st.write("Bu teknikler, baskın öğrenme stilinizi en verimli şekilde kullanmanıza yardımcı olacaktır. Bu teknikleri rutininizin bir parçası haline getirmeyi deneyin.")
                        
                        recommended_techniques = get_recommended_techniques(style_scores)
                        
                        for technique_name in recommended_techniques:
                            info = STUDY_TECHNIQUES[technique_name]
                            with st.expander(f"✨ {technique_name}", expanded=True):
                                st.write(f"**{info['description']}**")
                                st.write("**Nasıl Uygulanır?**")
                                for step in info['steps']:
                                    st.write(f"{info['icon']} {step}")
                                st.write(f"**Faydaları:** {info['benefits']}")
                    except json.JSONDecodeError:
                        st.error("Öğrenme stili verisi okunurken bir hata oluştu. Lütfen testi yeniden yapmayı deneyin.")
                else:
                    st.info("Bu sayfaya erişim için önce **'Öğrenme Stili Testi'** sayfasından testi tamamlamanız gerekmektedir.")
                    
            elif page == "🔬Detaylı Deneme Analiz Takibi":
                st.markdown(f'<div class="main-header"><h1>🔬Detaylı Deneme Analiz Takibi</h1><p>Sınav performansınızı bilimsel analiz edin</p></div>', unsafe_allow_html=True)

                # Eğer global olarak daha önce tanımlanmadıysa ders soru sayılarını tanımla
                if 'SUBJECT_MAX_QUESTIONS' not in globals():
                    SUBJECT_MAX_QUESTIONS = {
                        "TYT Türkçe": 40, "TYT Matematik": 40, "TYT Geometri": 40,
                        "TYT Tarih": 5, "TYT Coğrafya": 5, "TYT Felsefe": 5, "TYT Din Kültürü": 5,
                        "TYT Fizik": 7, "TYT Kimya": 7, "TYT Biyoloji": 6,
                        "AYT Matematik": 40, "AYT Fizik": 14, "AYT Kimya": 13, "AYT Biyoloji": 13,
                        "AYT Edebiyat": 40, "AYT Tarih": 40, "AYT Coğrafya": 40
                    }

                # Kullanıcının deneme verilerini yükle
                deneme_data_str = user_data.get('deneme_analizleri', '[]')
                try:
                    deneme_kayitlari = json.loads(deneme_data_str) if deneme_data_str else []
                except Exception:
                    deneme_kayitlari = []

                # Yeni deneme ekleme (manuel toplam_net alanını koruyoruz)
                with st.expander("➕ Yeni Deneme Ekle", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        deneme_adi = st.text_input("Deneme Adı", placeholder="Örn: 2024 TYT Denemesi #1", key="deneme_adi")
                        deneme_tarihi = st.date_input("Deneme Tarihi", key="deneme_tarihi")
                    with col2:
                        deneme_turu = st.selectbox("Deneme Türü", ["TYT", "AYT", "TYT-AYT"], key="deneme_turu")
                        # Eski arayüzde olan toplam_net alanını bırakıyoruz (kullanıcı manuel girebilir)
                        toplam_net_input = st.number_input("Toplam Net (manuel, istersen bırak)", min_value=0.0, max_value=200.0, step=0.25, key="toplam_net")
                    with col3:
                        toplam_dogru = st.number_input("Toplam Doğru", min_value=0, max_value=200, step=1, key="toplam_dogru")
                        toplam_yanlis = st.number_input("Toplam Yanlış", min_value=0, max_value=200, step=1, key="toplam_yanlis")

                # Ders bazlı net bilgileri (her dersin max'ını SUBJECT_MAX_QUESTIONS ile kontrol et)
                st.subheader("📝 Ders Bazlı Net Dağılımı")
                ders_netleri = {}

                if deneme_turu in ("TYT", "TYT-AYT"):
                    tyt_dersler = ["TYT Türkçe", "TYT Matematik", "TYT Geometri",
                                   "TYT Fizik", "TYT Kimya", "TYT Biyoloji",
                                   "TYT Tarih", "TYT Coğrafya", "TYT Felsefe", "TYT Din Kültürü"]
                    cols = st.columns(2)
                    for i, ders in enumerate(tyt_dersler):
                        with cols[i % 2]:
                            max_val = SUBJECT_MAX_QUESTIONS.get(ders, 20)
                            ders_netleri[ders] = st.number_input(
                                f"{ders} Net",
                                min_value=0.0,
                                max_value=float(max_val),
                                step=0.25,
                                key=f"tyt_{ders}"
                            )

                if deneme_turu in ("AYT", "TYT-AYT"):
                    ayt_dersler = ["AYT Matematik", "AYT Fizik", "AYT Kimya", "AYT Biyoloji", "AYT Edebiyat", "AYT Tarih", "AYT Coğrafya"]
                    cols = st.columns(2)
                    for i, ders in enumerate(ayt_dersler):
                        with cols[i % 2]:
                            max_val = SUBJECT_MAX_QUESTIONS.get(ders, 20)
                            ders_netleri[ders] = st.number_input(
                                f"{ders} Net",
                                min_value=0.0,
                                max_value=float(max_val),
                                step=0.25,
                                key=f"ayt_{ders}"
                            )

                # Yanlış analizi (eski key'leri koruyoruz: f"{ders}_{neden}" -> böylece önceki kayıtlara bağlılık bozulmaz)
                st.subheader("🔍 Yanlış Analizi")
                yanlis_nedenleri = {
                    "Bilgi Eksikliği": "Konuyu tam olarak öğrenmemiş olmak",
                    "Dikkatsizlik": "Soruyu yanlış okuma veya işlem hatası",
                    "Zaman Yetmedi": "Süreyi iyi kullanamama",
                    "Yorum Hatası": "Sorunun mantığını anlayamama",
                    "Şans Eseri Doğru": "Tahminle doğru cevabı bulma",
                    "Kodlama Hatası": "İşaretleme hatası"
                }

                yanlis_analiz = {}
                for ders, net in ders_netleri.items():
                    subject_max = SUBJECT_MAX_QUESTIONS.get(ders, 20)
                    if float(net) < float(subject_max) * 0.75:
                        with st.expander(f"❌ {ders} - Yanlış Analizi"):
                            st.write(f"Bu derste {float(subject_max) - float(net):.1f} net kaybınız var. Sebepleri:")
                            for neden, aciklama in yanlis_nedenleri.items():
                                # Burada eski key formatını koruyoruz: key=f"{ders}_{neden}"
                                yanlis_sayisi = st.number_input(
                                    f"{ders} - {neden}",
                                    min_value=0,
                                    max_value=int(subject_max),
                                    value=0,
                                    step=1,
                                    key=f"{ders}_{neden}"
                                )
                                if yanlis_sayisi > 0:
                                    if ders not in yanlis_analiz:
                                        yanlis_analiz[ders] = {}
                                    yanlis_analiz[ders][neden] = int(yanlis_sayisi)

                # Eksik konu tespiti (aynı mantık korunuyor)
                st.subheader("📌 Eksik Konu Tespiti")
                eksik_konular = {}
                for ders, net in ders_netleri.items():
                    subject_max = SUBJECT_MAX_QUESTIONS.get(ders, 20)
                    if float(net) < float(subject_max) * 0.6:
                        st.write(f"**{ders}** - Eksik konularınızı işaretleyin:")
                        ders_konulari = get_topic_list(ders)
                        if ders_konulari:
                            secilen_konular = st.multiselect(f"{ders} eksik konular", ders_konulari, key=f"eksik_{ders}")
                            if secilen_konular:
                                eksik_konular[ders] = secilen_konular

                # Kaydet butonu: manuel toplam_net_input varsa onu kullan, yoksa ders_netleri toplamını kullan
                if st.button("💾 Deneme Analizini Kaydet", type="primary", use_container_width=True, key="kaydet_deneme"):
                    if deneme_adi and deneme_tarihi:
                        # Derslerden otomatik toplam
                        computed_total = sum([float(v) for v in ders_netleri.values()]) if ders_netleri else 0.0
                        # Eğer kullanıcı manuel toplam girmişse (manuel > 0) onu öncelikle kullan, değilse computed_total
                        toplam_net_to_save = float(toplam_net_input) if float(toplam_net_input) > 0.0 else float(computed_total)

                        yeni_deneme = {
                            "id": len(deneme_kayitlari) + 1,
                            "adi": deneme_adi,
                            "tarih": str(deneme_tarihi),
                            "tur": deneme_turu,
                            "toplam_net": float(toplam_net_to_save),
                            "toplam_dogru": int(toplam_dogru),
                            "toplam_yanlis": int(toplam_yanlis),
                            "ders_netleri": ders_netleri,
                            "yanlis_analiz": yanlis_analiz,
                            "eksik_konular": eksik_konular,
                            "tavsiyeler": []
                        }

                        # Basit otomatik tavsiyeler (ders oranlarına göre)
                        tavsiyeler = []
                        if float(toplam_net_to_save) < 50.0:
                            tavsiyeler.append("🔴 Netiniz düşük: Öncelik temel konu tekrarları olmalı.")
                        elif float(toplam_net_to_save) < 80.0:
                            tavsiyeler.append("🟡 Orta seviye: Eksik konulara ve hız çalışmasına odaklanın.")
                        else:
                            tavsiyeler.append("🟢 İyi seviyedesiniz: Deneme pratiğini sürdürün, süre yönetimini geliştirin.")

                        for ders, net in ders_netleri.items():
                            subject_max = SUBJECT_MAX_QUESTIONS.get(ders, 20)
                            oran = float(net) / subject_max if subject_max > 0 else 0
                            if oran < 0.3:
                                tavsiyeler.append(f"📚 **{ders}**: Temel konu anlatımlarını tekrar et; kısa notlar çıkar.")
                            elif oran < 0.6:
                                tavsiyeler.append(f"📖 **{ders}**: Konu sonrası çıkmış sorular ve hedefli test çöz.")
                            elif oran < 0.8:
                                tavsiyeler.append(f"✍️ **{ders}**: Hız/şablon çalışması ile deneme başarısını arttır.")

                        yeni_deneme["tavsiyeler"] = tavsiyeler
                        deneme_kayitlari.append(yeni_deneme)

                        # Kullanıcı verilerine kaydet (mevcut fonksiyonları kullan)
                        update_user_in_firebase(st.session_state.current_user, {'deneme_analizleri': json.dumps(deneme_kayitlari)})
                        st.session_state.users_db = load_users_from_firebase()

                        st.success("✅ Deneme analizi başarıyla kaydedildi!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error("⚠️ Lütfen deneme adı ve tarihini giriniz")

                # Geçmiş denemeleri gösterme + seçilen deneme detayları
                if deneme_kayitlari:
                    st.markdown("---")
                    st.subheader("📈 Geçmiş Denemeler")

                    deneme_listesi = [f"{d['adi']} - {d['tarih']} ({d['tur']})" for d in deneme_kayitlari]
                    secilen_deneme = st.selectbox("Analizini görüntülemek istediğiniz denemeyi seçin:", deneme_listesi, key="deneme_secim")

                    if secilen_deneme:
                        deneme_index = deneme_listesi.index(secilen_deneme)
                        deneme = deneme_kayitlari[deneme_index]

                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("📊 Toplam Net", f"{float(deneme.get('toplam_net', 0)):.1f}")
                        with col2:
                            st.metric("✅ Doğru Sayısı", deneme.get('toplam_dogru', 0))
                        with col3:
                            st.metric("❌ Yanlış Sayısı", deneme.get('toplam_yanlis', 0))
                        with col4:
                            st.metric("🎯 Deneme Türü", deneme.get('tur', '—'))

                        # Net dağılım grafiği
                        st.subheader("📊 Net Dağılımı")
                        dersler = [d for d, v in (deneme.get('ders_netleri') or {}).items() if v > 0]
                        netler = [deneme.get('ders_netleri', {}).get(d, 0) for d in dersler]
                        if dersler:
                            fig = px.bar(x=dersler, y=netler, title="Derslere Göre Net Dağılımı",
                                         labels={'x': 'Dersler', 'y': 'Net'}, color=netler,
                                         color_continuous_scale="Viridis")
                            st.plotly_chart(fig, use_container_width=True)

                        # Öneriler (kaydedilmiş öneriler gösterilsin)
                        st.subheader("💡 Kayıtlı Gelişim Tavsiyeleri")
                        for tavsiye in deneme.get('tavsiyeler', []):
                            st.write(tavsiye)

                    # ----- EN ALTA: Tüm denemelerin gidişat grafiği -----
                    st.markdown("---")
                    st.subheader("📈 Zaman İçinde Gelişim (Tüm Denemeler)")
                    tarihler = [d.get('tarih') for d in deneme_kayitlari]
                    netler = [float(d.get('toplam_net', 0)) for d in deneme_kayitlari]
                    if tarihler and any(netlers := netler):
                        gelisim_df = pd.DataFrame({"Tarih": tarihler, "Toplam Net": netler})
                        fig_line = px.line(gelisim_df, x="Tarih", y="Toplam Net", markers=True,
                                           title="Denemelerde Net Gelişimi")
                        st.plotly_chart(fig_line, use_container_width=True)

                        # Son denemeye özel ders bazlı öneriler (kısa, eyleme dönük)
                        son_deneme = deneme_kayitlari[-1]
                        low_subjects = []
                        for ders, net in (son_deneme.get('ders_netleri') or {}).items():
                            max_val = SUBJECT_MAX_QUESTIONS.get(ders, 20)
                            try:
                                oran = float(net) / float(max_val) if float(max_val) > 0 else 0
                            except Exception:
                                oran = 0
                            if oran < 0.5:
                                low_subjects.append((ders, oran))

                        st.subheader("📌 Son Denemeye Göre Öncelikli Öneriler")
                        if low_subjects:
                            for ders, oran in low_subjects:
                                st.write(f"- **{ders}** (%{oran*100:.0f}): {('Konu tekrarı ve çıkmış soru çözümü; eksik konuları parça parça kapatın.' )}")
                        else:
                            st.write("Tebrikler — son denemede ders bazında kayda değer düşük alan bulunmadı.")

                        # Genel çalışma önerileri (kaynaklı, kısa)
                        st.markdown("---")
                        st.subheader("🔎 Güvenilir Kaynaklardan Derlenen Kısa Çalışma Önerileri")
                        st.write("- Okuduğunu anlama için günlük okuma alışkanlığı (gazete/deneme/uzun paragraflar).")

            elif page == "📊 İstatistikler":
                st.markdown(f'<div class="main-header"><h1>📊 Detaylı İstatistikler</h1><p>İlerlemenizi analiz edin</p></div>', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    total_completed = sum(data['completed'] for data in progress_data.values())
                    total_topics = count_total_topics()
                    st.metric("📊 Toplam Konu", f"{total_completed}/{total_topics}")
                with col2:
                    completion_rate = (total_completed / total_topics * 100) if total_topics > 0 else 0
                    st.metric("🎯 Tamamlanma Oranı", f"%{completion_rate:.1f}")
                with col3:
                    avg_net = 0; net_count = 0
                    topic_progress = json.loads(user_data.get('topic_progress', '{}') or '{}')
                    for topic_data in topic_progress.values():
                        try:
                            avg_net += float(topic_data)
                            net_count += 1
                        except ValueError:
                            continue
                    avg_net = (avg_net / net_count) if net_count > 0 else 0
                    st.metric("⭐ Ortalama Net", f"{avg_net:.1f}")
                
                st.subheader("📈 Ders Bazında İlerleme")
                if progress_data:
                    subjects = list(progress_data.keys())
                    percents = [data['percent'] for data in progress_data.values()]
                    fig = px.bar(x=subjects, y=percents, title="Derslere Göre Tamamlanma Oranları", labels={'x': 'Dersler', 'y': 'Tamamlanma (%)'}, color=percents, color_continuous_scale="Viridis")
                    st.plotly_chart(fig, use_container_width=True)
                    st.subheader("📋 Detaylı İlerleme Tablosu")
                    progress_df = pd.DataFrame([{'Ders': s, 'Tamamlanan': d['completed'], 'Toplam': d['total'], 'Oran (%)': d['percent']} for s, d in progress_data.items()])
                    st.dataframe(progress_df, use_container_width=True)
                else:
                    st.info("📊 Henüz yeterli veri bulunmuyor. Konu takip sayfasından ilerlemenizi kaydedin.")

# === HİBRİT POMODORO SİSTEMİ FONKSİYONLARI ===

def start_hibrit_breathing():
    """Hibrit nefes sistemini başlat - Pomodoro'yu duraklat"""
    # Pomodoro'yu duraklat
    if st.session_state.pomodoro_active:
        st.session_state.breathing_paused_time = st.session_state.time_remaining
    
    # Nefes sistemini başlat
    st.session_state.breathing_active = True
    st.session_state.breath_time_remaining = 60
    st.session_state.breath_start_time = time.time()
    
    # Rastgele bir motivasyon türü seç
    motivation_types = ['quote', 'tip', 'breathing']
    st.session_state.current_motivation_type = random.choice(motivation_types)
    
    if st.session_state.current_motivation_type == 'quote':
        st.session_state.current_motivation_content = random.choice(MOTIVATION_QUOTES)
    elif st.session_state.current_motivation_type == 'tip':
        subject = st.session_state.current_subject
        if subject in MICRO_TIPS:
            st.session_state.current_motivation_content = random.choice(MICRO_TIPS[subject])
        else:
            st.session_state.current_motivation_content = random.choice(MICRO_TIPS['Genel'])
    else:  # breathing
        exercise = random.choice(BREATHING_EXERCISES)
        st.session_state.current_motivation_content = f"""
🫁 **{exercise['name']}**

📋 {exercise['instruction']}

✨ **Faydası:** {exercise['benefit']}
        """
    
    # Kullanım loguna kaydet
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'subject': st.session_state.current_subject,
        'motivation_type': st.session_state.current_motivation_type,
        'remaining_time_when_used': st.session_state.breathing_paused_time
    }
    st.session_state.breathing_usage_log.append(log_entry)
    
    st.success("💨 Hibrit nefes molası başladı! Pomodoro timer duraklatıldı.")

def complete_breathing_exercise():
    """Nefes egzersizini tamamla ve Pomodoro'ya dön"""
    st.session_state.breathing_active = False
    st.session_state.breath_time_remaining = 60
    st.session_state.breath_start_time = None
    
    # Pomodoro'yu kaldığı yerden devam ettir
    if st.session_state.pomodoro_active:
        st.session_state.time_remaining = st.session_state.breathing_paused_time
        st.session_state.start_time = time.time()
    
    st.success("🎉 Hibrit nefes molası tamamlandı! Pomodoro kaldığı yerden devam ediyor.")
    st.balloons()

def show_breathing_exercise():
    """Hibrit nefes egzersizini göster"""
    breath_seconds = int(st.session_state.breath_time_remaining)
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        animation: pulse 2s infinite;
    ">
        <h2 style="color: white; margin-bottom: 20px;">🌬️ Hibrit Nefes Molası</h2>
        <div style="font-size: 72px; font-weight: bold; margin: 20px 0;">
            {breath_seconds}s
        </div>
        <div style="
            font-size: 18px; 
            font-style: italic; 
            margin: 20px 0; 
            min-height: 100px;
            padding: 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            border-left: 4px solid #ffd700;
            white-space: pre-line;
        ">
            {st.session_state.current_motivation_content}
        </div>
        <div style="font-size: 14px; opacity: 0.9; margin-top: 15px;">
            🍅 Pomodoro timer duraklatıldı • Kaldığı yerden devam edecek
        </div>
    </div>
    
    <style>
    @keyframes pulse {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.02); }}
        100% {{ transform: scale(1); }}
    }}
    </style>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()