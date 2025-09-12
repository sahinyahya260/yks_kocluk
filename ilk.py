import streamlit as st
import pandas as pd

# ================= LOGIN SİSTEMİ ================= #

# Kullanıcıları csv'den yükle
def load_users():
    try:
        df = pd.read_csv("users.csv")
        return {row['username']: row['password'] for _, row in df.iterrows()}
    except:
        return {}

# Login ekranı
def login_screen():
    st.title("🔐 YKS Ultra Profesyonel Koç Giriş")
    st.markdown("Lütfen kullanıcı adı ve şifrenizi giriniz.")

    username = st.text_input("👤 Kullanıcı Adı")
    password = st.text_input("🔑 Şifre", type="password")

    if st.button("Giriş Yap"):
        users = load_users()
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Başarıyla giriş yaptınız!")
            st.rerun()
        else:
            st.error("❌ Kullanıcı adı veya şifre hatalı!")

# Paneli çağıran bölüm
def main_panel():
    st.sidebar.success(f"👋 Hoş geldin, {st.session_state.username}")
    main()

# ================= EKSİK OLAN BAŞLANGIÇ ================= #
def initialize_session_state():
    if "program_oluşturuldu" not in st.session_state:
        st.session_state.program_oluşturuldu = False
    if "öğrenci_bilgisi" not in st.session_state:
        st.session_state.öğrenci_bilgisi = {}
    if "konu_durumu" not in st.session_state:
        st.session_state.konu_durumu = {}
    if "deneme_sonuçları" not in st.session_state:
        st.session_state.deneme_sonuçları = []
    if "günlük_çalışma_kayıtları" not in st.session_state:
        st.session_state.günlük_çalışma_kayıtları = []
    if "motivasyon_puanı" not in st.session_state:
        st.session_state.motivasyon_puanı = 100

# ================= SENİN PANEL KODUN ================= #

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

# ================= GİRİŞ AKIŞI ================= #

def app():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if st.session_state.logged_in:
        main_panel()
    else:
        login_screen()

if __name__ == "__main__":
    app()
