import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import base64
import os

# Sayfa ayarları
st.set_page_config(
    page_title="DF Senin YKS Takip Sistemi",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Kullanıcı doğrulama fonksiyonu
def authenticate(username, password):
    try:
        users_df = pd.read_csv('users.csv')
        user = users_df[(users_df['username'] == username) & (users_df['password'] == password)]
        return not user.empty
    except:
        return False

# Arka plan resmi ayarlama fonksiyonu
def set_bg_by_department(department):
    department_bg = {
        "Sayısal": "https://raw.githubusercontent.com/emrekocak0/dfyks/main/sayisal.jpg",
        "Eşit Ağırlık": "https://raw.githubusercontent.com/emrekocak0/dfyks/main/ea.jpg",
        "Sözel": "https://raw.githubusercontent.com/emrekocak0/dfyks/main/sozel.jpg",
        "Dil": "https://raw.githubusercontent.com/emrekocak0/dfyks/main/dil.jpg"
    }
    
    # Varsayılan olarak Sayısal arka planını kullan
    bg_url = department_bg.get(department, department_bg["Sayısal"])
    
    # Arka plan CSS'i
    bg_css = f"""
    <style>
    .stApp {{
        background-image: url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    .main .block-container {{
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 2rem;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)

# Giriş sayfası
def login_page():
    st.title("DF Senin YKS Takip Sistemi")
    st.subheader("Lütfen giriş yapın")
    
    with st.form("login_form"):
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        department = st.selectbox("Hedeflediğiniz Bölüm", 
                                 ["Sayısal", "Eşit Ağırlık", "Sözel", "Dil"])
        submitted = st.form_submit_button("Giriş Yap")
        
        if submitted:
            if authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.department = department
                st.success("Başarıyla giriş yapıldı!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Kullanıcı adı veya şifre hatalı!")

# Ana sayfa
def main_page():
    set_bg_by_department(st.session_state.department)
    
    st.title(f"Hoş geldin {st.session_state.username}!")
    st.subheader(f"Hedeflenen Bölüm: {st.session_state.department}")
    
    # Sınav tarihi (örnek olarak 2025 Haziran'ın ilk pazarı)
    exam_date = datetime(2025, 6, 1)
    while exam_date.weekday() != 6:  # 6 = Pazar
        exam_date += timedelta(days=1)
    
    days_until_exam = (exam_date - datetime.now()).days
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Sınava Kalan Gün", days_until_exam)
    with col2:
        st.metric("Tamamlanan Konular", "24/120")
    with col3:
        st.metric("Son Deneme Net", "68.5")
    
    st.write("---")
    st.write("### Son Aktivitelerniz")
    
    # Örnek aktivite verileri
    activities = pd.DataFrame({
        "Tarih": ["2024-03-15", "2024-03-14", "2024-03-13", "2024-03-12"],
        "Aktivite": ["Matematik Denemesi", "Geometri Konu Çalışması", "Fizik Problemleri", "Türkçe Paragraf"],
        "Süre": ["45 dk", "120 dk", "90 dk", "60 dk"]
    })
    
    st.dataframe(activities, hide_index=True, use_container_width=True)

# Konu Takip Sistemi
def topic_tracking_page():
    st.header("Konu Detay Takip Sistemi")
    
    # Örnek konu verileri
    topics = {
        "Matematik": ["Temel Kavramlar", "Sayı Basamakları", "Bölme-Bölünebilme", "OBEB-OKEK", 
                     "Rasyonel Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar"],
        "Geometri": ["Doğruda Açılar", "Üçgende Açılar", "Özel Üçgenler", "Üçgende Alan"],
        "Fizik": ["Fizik Bilimine Giriş", "Madde ve Özellikleri", "Hareket ve Kuvvet", "Enerji"],
        "Kimya": ["Kimya Bilimi", "Atom ve Periyodik Sistem", "Kimyasal Türler Arası Etkileşimler"],
        "Biyoloji": ["Biyoloji Bilimi", "Canlıların Yapısı", "Hücre", "Canlıların Çeşitliliği"],
        "Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Ses Bilgisi"],
        "Tarih": ["Tarih Bilimi", "İlk Uygarlıklar", "İslamiyet Öncesi Türk Tarihi"],
        "Coğrafya": ["Doğa ve İnsan", "Coğrafi Konum", "Harita Bilgisi"]
    }
    
    selected_subject = st.selectbox("Ders Seçin", list(topics.keys()))
    
    if selected_subject:
        completed_topics = st.multiselect(
            "Tamamlanan Konular",
            options=topics[selected_subject],
            default=topics[selected_subject][:2]
        )
        
        progress_value = len(completed_topics) / len(topics[selected_subject])
        st.progress(progress_value, text=f"{selected_subject} Tamamlama Oranı: {progress_value:.0%}")
        
        # Konu ilerleme grafiği
        fig = go.Figure(go.Bar(
            x=[len(completed_topics), len(topics[selected_subject]) - len(completed_topics)],
            y=[selected_subject],
            orientation='h',
            marker_color=['#4CAF50', '#e0e0e0'],
            text=[f"Tamamlanan: {len(completed_topics)}", f"Kalan: {len(topics[selected_subject]) - len(completed_topics)}"],
            textposition='auto'
        ))
        fig.update_layout(
            title=f"{selected_subject} Konu İlerlemesi",
            xaxis_title="Konu Sayısı",
            showlegend=False,
            height=200
        )
        st.plotly_chart(fig, use_container_width=True)

# Deneme Analizleri
def exam_analysis_page():
    st.header("Deneme Analizlerim")
    
    # Örnek deneme sonuçları
    exams = pd.DataFrame({
        "Tarih": ["2024-03-15", "2024-03-08", "2024-03-01", "2024-02-22", "2024-02-15"],
        "Türkçe": [35, 32, 30, 28, 25],
        "Matematik": [25, 22, 20, 18, 15],
        "Fen Bilimleri": [30, 28, 25, 22, 20],
        "Sosyal Bilimler": [30, 28, 25, 22, 20],
        "Toplam Net": [120, 110, 100, 90, 80],
        "Sıralama": [12500, 18500, 24500, 32000, 41000]
    })
    
    st.dataframe(exams, hide_index=True, use_container_width=True)
    
    # Net grafiği
    st.subheader("Net Gelişim Grafiği")
    fig = px.line(exams, x="Tarih", y="Toplam Net", title="Toplam Net Gelişimi", markers=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Derslere göre net dağılımı
    st.subheader("Derslere Göre Net Dağılımı")
    fig = go.Figure()
    for col in ["Türkçe", "Matematik", "Fen Bilimleri", "Sosyal Bilimler"]:
        fig.add_trace(go.Scatter(x=exams["Tarih"], y=exams[col], mode='lines+markers', name=col))
    fig.update_layout(title="Derslere Göre Net Gelişimi")
    st.plotly_chart(fig, use_container_width=True)

# Pomodoro Zamanlayıcı
def pomodoro_page():
    st.header("Pomodoro Çalışma Zamanlayıcı")
    
    col1, col2 = st.columns(2)
    
    with col1:
        work_time = st.slider("Çalışma Süresi (dakika)", 5, 60, 25)
        break_time = st.slider("Mola Süresi (dakika)", 1, 30, 5)
    
    with col2:
        st.write("### Pomodoro Tekniği")
        st.write("""
        1. 25 dakika çalışma
        2. 5 dakika mola
        3. 4 pomodoro sonunda 15-30 dakika uzun mola
        
        Bu teknik odaklanmanızı artırır ve verimliliği yükseltir.
        """)
    
    if st.button("Zamanlayıcıyı Başlat"):
        with st.spinner(f"Çalışma zamanı: {work_time} dakika..."):
            time.sleep(work_time * 0.1)  # Gerçek uygulamada 0.1 yerine 60 kullanılmalı
            st.balloons()
            st.success(f"Çalışma süresi tamamlandı! {break_time} dakika mola zamanı.")
            
            with st.spinner(f"Mola zamanı: {break_time} dakika..."):
                time.sleep(break_time * 0.1)  # Gerçek uygulamada 0.1 yerine 60 kullanılmalı
                st.success("Mola süresi tamamlandı. Yeni çalışma seansına hazırsınız!")

# Sınava Kadar Sayfası
def countdown_page():
    st.header("Sınava Kadar")
    
    # Sınav tarihi (örnek olarak 2025 Haziran'ın ilk pazarı)
    exam_date = datetime(2025, 6, 1)
    while exam_date.weekday() != 6:  # 6 = Pazar
        exam_date += timedelta(days=1)
    
    now = datetime.now()
    delta = exam_date - now
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Gün", days)
    col2.metric("Saat", hours)
    col3.metric("Dakika", minutes)
    
    # Çalışma planı önerisi
    st.subheader("Çalışma Planı Önerisi")
    weeks_until_exam = days // 7
    
    if weeks_until_exam > 0:
        st.write(f"Sınava {weeks_until_exam} hafta kaldı. Haftalık plan:")
        
        study_plan = {
            "Pazartesi": ["Matematik", "Fizik"],
            "Salı": ["Türkçe", "Tarih"],
            "Çarşamba": ["Geometri", "Kimya"],
            "Perşembe": ["Coğrafya", "Biyoloji"],
            "Cuma": ["Deneme Çözümü", "Tekrar"],
            "Cumartesi": ["Eksik Konular", "Soru Çözümü"],
            "Pazar": ["Dinlenme", "Hafif Tekrar"]
        }
        
        for day, subjects in study_plan.items():
            with st.expander(day):
                for subject in subjects:
                    st.write(f"- {subject}")
    else:
        st.write("Sınav çok yaklaştı. Son tekrarlarınızı yapın ve bolca deneme çözün.")

# Psikolojim Sayfası
def psychology_page():
    st.header("Psikolojim")
    
    st.subheader("Motivasyon Cümleleri")
    motivations = [
        "Başarı, hazırlık ve fırsatın buluştuğu yerdir.",
        "Pes etmeyen asla yenilmez.",
        "Bugünün işini yarına bırakma.",
        "Zorluklar, başarının değerini artıran süslerdir.",
        "Hedefini yüksek tut, çünkü hedefe ulaşamasan bile yüksekte olacaksın."
    ]
    
    st.info(motivations[datetime.now().day % len(motivations)])
    
    st.subheader("Stres Seviyeniz")
    stress_level = st.slider("Stres seviyenizi belirtin (1 = Çok rahat, 10 = Çok stresli)", 1, 10, 5)
    
    if stress_level >= 7:
        st.warning("Stres seviyeniz yüksek. Derin nefes egzersizleri yapmayı deneyin.")
        st.write("""
        **Rahatlama Önerileri:**
        - 5 dakika derin nefes alın
        - Kısa bir yürüyüş yapın
        - Sevdiğiniz bir şarkıyı dinleyin
        - 10 dakika meditasyon yapın
        """)
    elif stress_level >= 4:
        st.info("Stres seviyeniz orta düzeyde. Molalar vererek çalışmaya devam edebilirsiniz.")
    else:
        st.success("Stres seviyeniz düşük. Mükemmel, çalışmaya devam edin!")
    
    st.subheader("Günlük Duygu Durumu")
    mood = st.select_slider("Bugünkü ruh haliniz", 
                           options=["Çok Kötü", "Kötü", "Normal", "İyi", "Çok İyi"])
    
    if mood in ["Çok Kötü", "Kötü"]:
        st.error("Üzüldüm. Unutma, zor günler geçecek ve başaracaksın!")
    elif mood == "Normal":
        st.info("Günlük rutinine devam edebilirsin. Kendine iyi bak!")
    else:
        st.success("Harika! Bu enerjiyi ders çalışmak için kullan!")

# Ana uygulama akışı
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sekmeler
        tabs = st.tabs(["Ana Sayfa", "Konu Detay Takip Sistemi", "Deneme Analizlerim", 
                       "Pomodoro", "Sınava Kadar", "Psikolojim"])
        
        with tabs[0]:
            main_page()
        with tabs[1]:
            topic_tracking_page()
        with tabs[2]:
            exam_analysis_page()
        with tabs[3]:
            pomodoro_page()
        with tabs[4]:
            countdown_page()
        with tabs[5]:
            psychology_page()
        
        # Çıkış butonu
        if st.sidebar.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()
