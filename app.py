import streamlit as st
import pandas as pd
import urllib.parse
import time

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. Çoklu Dil Sözlüğü
LANG = {
    "TR": {
        "title": "FİLYOS FAZ-2", "subtitle": "DİJİTAL OFİS", "sicil": "FİORİ PERSONEL NO", "sifre": "DOĞUM YILI (Şifre)", 
        "login_btn": "SİSTEME GİRİŞ YAP", "yukleniyor": "Sisteme Bağlanılıyor...", "hata": "❌ Hatalı Bilgi!",
        "welcome": "Hoş Geldin", "gorev": "Görev", "gun": "GÜN",
        "odenecek": "Ödenecek Gün", "fiziki": "Fiziki Çalışılan", "sgk": "SGK Günü",
        "hesap_baslik": "İnteraktif Maaş Metre", "yevmiye": "Günlük Yevmiyeniz (TL)", "tahmini": "Tahmini Hak Ediş",
        "iletisim_baslik": "İK Destek Merkezi", "iletisim_bilgi": "İtiraz konunuzu seçip destek hattına bağlanın.",
        "konu_sec": "Destek Konusu:", "konular": ["Eksik Gün İtirazı", "Mesai Saati İtirazı", "Maaş/Yevmiye Sorunu", "Diğer Konular"],
        "destek_btn": "FAZ-2 İK DESTEK HATTI"
    },
    "EN": {
        "title": "FILYOS PHASE-2", "subtitle": "DIGITAL OFFICE", "sicil": "FIORI ID", "sifre": "BIRTH YEAR", 
        "login_btn": "LOGIN TO SYSTEM", "yukleniyor": "Connecting...", "hata": "❌ Invalid Info!",
        "welcome": "Welcome", "gorev": "Role", "gun": "DAYS",
        "odenecek": "Payable Days", "fiziki": "Physical Days", "sgk": "SGK Days",
        "hesap_baslik": "Salary Calculator", "yevmiye": "Daily Wage (TL)", "tahmini": "Estimated Pay",
        "iletisim_baslik": "HR Support", "iletisim_bilgi": "Select issue and connect.",
        "konu_sec": "Issue:", "konular": ["Missing Days", "Overtime", "Salary", "Other"],
        "destek_btn": "PHASE-2 HR SUPPORT"
    },
    "UZ": {
        "title": "FILYOS FAZ-2", "subtitle": "RAQAMLI OFIS", "sicil": "FIORI ID", "sifre": "TUG'ILGAN YIL", 
        "login_btn": "KIRISH", "yukleniyor": "Bog'lanmoqda...", "hata": "❌ Xato Ma'lumot!",
        "welcome": "Xush Kelibsiz", "gorev": "Lavozim", "gun": "KUN",
        "odenecek": "To'lanadigan", "fiziki": "Ishlagan", "sgk": "SGK Kunlari",
        "hesap_baslik": "Maosh Hisoblash", "yevmiye": "Kunlik Ish Haqi", "tahmini": "Taxminiy Maosh",
        "iletisim_baslik": "Kadrlar Bo'limi", "iletisim_bilgi": "Muammoni tanlang.",
        "konu_sec": "Muammo:", "konular": ["Kam Kunlar", "Qo'shimcha Ish", "Maosh", "Boshqa"],
        "destek_btn": "KADRLAR DESTEK HATTI"
    }
}

# 3. Premium CSS (Dünyanın En Sağlam Arka Planı ve Animasyonları)
st.markdown("""
    <style>
    /* Menüleri ve Streamlit'in kendi arka planlarını tamamen yok et */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background: transparent !important;
    }
    .stApp { background: transparent !important; }
    
    /* 🇹🇷 100% ÇALIŞAN GARANTİLİ BAYRAK (Wikipedia Sunucusu) ve SİNEMATİK HAREKET */
    body::before {
        content: "";
        position: fixed;
        top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover;
        background-position: center;
        z-index: -2;
        animation: droneShot 15s ease-in-out infinite alternate;
    }

    /* Koyu Sinematik Filtre (Bayrağın kırmızısını boğmayan jilet gibi geçiş) */
    body::after {
        content: "";
        position: fixed;
        top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(180deg, rgba(15,20,30,0.80) 0%, rgba(5,10,15,0.95) 100%);
        z-index: -1;
    }

    /* Bayrağı ağır ağır hareket ettiren kurgu animasyonu */
    @keyframes droneShot {
        0% { transform: scale(1) translate(0, 0); }
        100% { transform: scale(1.15) translate(-1%, 2%); }
    }

    /* Kartlar ve Aşağıdan Yukarı Kayma Animasyonu */
    .dark-card {
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        opacity: 0;
        transform: translateY(30px);
    }
    
    @keyframes slideUp {
        to { opacity: 1; transform: translateY(0); }
    }

    /* Mekanik Flipper Rakamları (Havalimanı Takvimi) */
    .flipper-text {
        font-family: 'Courier New', Courier, monospace;
        font-size: 34px;
        font-weight: bold;
        color: #e2e8f0;
        background-color: #0f172a;
        padding: 10px 15px;
        border-radius: 8px;
        display: inline-block;
        border: 2px solid #334155;
        box-shadow: inset 0 4px 10px rgba(0,0,0,0.8);
        animation: flipIn 1s cubic-bezier(0.25, 0.8, 0.25, 1) forwards;
    }
    @keyframes flipIn {
        0% { transform: rotateX(-90deg); opacity: 0; }
        100% { transform: rotateX(0deg); opacity: 1; }
    }

    /* Buton Tasarımları */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #1e40af 0%, #1d4ed8 100%);
        color: white;
        height: 50px;
        font-size: 16px;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:active { transform: scale(0.97); }

    .stLinkButton>a { 
        width: 100% !important; 
        border-radius: 8px !important; 
        background: linear-gradient(90deg, #166534 0%, #15803d 100%) !important; 
        color: white !important; 
        height: 50px !important; 
        line-height: 35px !important;
        font-weight: bold !important;
        text-align: center !important;
        text-decoration: none !important;
        display: block !important;
    }
    
    /* Şifre Input Odaklama (Lazer Çizgi Hissiyatı) */
    .stTextInput>div>div>input {
        background-color: rgba(0,0,0,0.5) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        height: 50px !important;
        transition: all 0.3s;
    }
    .stTextInput>div>div>input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 10px rgba(59,130,246,0.5) !important;
    }
    .stSelectbox>div>div>div {
        background-color: rgba(0,0,0,0.5) !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
    }
    
    .main-title {
        text-align: center; font-weight: 900; letter-spacing: 2px; margin-bottom: 0px; color: white;
    }
    .sub-title {
        text-align: center; font-size: 14px; color: #94a3b8; letter-spacing: 4px; margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_data' not in st.session_state:
    st.session_state['user_data'] = None

@st.cache_data
def load_data():
    try:
        # Excel okuma kısmı DÜZELTİLDİ: Sayfa adı ne olursa olsun okur.
        return pd.read_excel("veri.xlsx")
    except:
        return None

df = load_data()

dil_secim = st.selectbox("🌐", ["TR", "EN", "UZ"], label_visibility="collapsed")
t = LANG[dil_secim]

# ----------------- GİRİŞ EKRANI -----------------
if not st.session_state['logged_in']:
    st.markdown(f"<h1 class='main-title'>{t['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{t['subtitle']}</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    sicil_input = st.text_input(t['sicil'], placeholder="Örn: 1100XXX")
    sifre_input = st.text_input(t['sifre'], type="password", placeholder="Örn: 1990")
    st.write(" ")
    giris_basildi = st.button(t['login_btn'])
    st.markdown('</div>', unsafe_allow_html=True)

    if giris_basildi:
        if df is not None:
            sonuc = df[(df['FİORİ PERSONEL NO'].astype(str) == sicil_input) & (df['DOĞUM TARİHİ'].astype(str) == sifre_input)]
            if not sonuc.empty:
                ilerleme = st.progress(0, text=t['yukleniyor'])
                for percent in range(100):
                    time.sleep(0.01)
                    ilerleme.progress(percent + 1, text=t['yukleniyor'])
                
                ilerleme.empty()
                st.session_state['user_data'] = sonuc.iloc[0]
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error(t['hata'])
                
# ----------------- ANA EKRAN -----------------
else:
    kisi = st.session_state['user_data']

    st.markdown('<div class="dark-card" style="animation-delay: 0s;">', unsafe_allow_html=True)
    st.markdown(f"### 👋 {t['welcome']}, {kisi['ADI SOYADI']}")
    st.caption(f"📂 {t['gorev']} | Sicil: {kisi['FİORİ PERSONEL NO']}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dark-card" style="animation-delay: 0.1s;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.caption(t['odenecek'])
        st.markdown(f"<div class='flipper-text'>{kisi['Personele Ödenecek Gün']}</div>", unsafe_allow_html=True)
    with c2:
        st.caption(t['fiziki'])
        st.markdown(f"<div class='flipper-text'>{kisi['Fiziki Çalışılan Gün']}</div>", unsafe_allow_html=True)
    with c3:
        st.caption(t['sgk'])
        st.markdown(f"<div class='flipper-text'>{kisi['SGK Ödenecek Gün']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dark-card" style="animation-delay: 0.2s;">', unsafe_allow_html=True)
    st.markdown(f"#### 🧮 {t['hesap_baslik']}")
    yevmiye = st.number_input(t['yevmiye'], min_value=0, step=100)
    if yevmiye > 0:
        toplam_maas = yevmiye * kisi['Personele Ödenecek Gün']
        st.success(f"💸 **{t['tahmini']}:** {toplam_maas:,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="dark-card" style="animation-delay: 0.3s;">', unsafe_allow_html=True)
    st.markdown(f"#### ☎️ {t['iletisim_baslik']}")
    st.caption(t['iletisim_bilgi'])
    
    itiraz_konusu = st.selectbox(t['konu_sec'], t['konular'])
    
    admin_no = "905459157444" 
    mesaj_metni = f"DİJİTAL OFİS BİLDİRİMİ\nPersonel: {kisi['ADI SOYADI']}\nSicil: {kisi['FİORİ PERSONEL NO']}\nKonu: {itiraz_konusu}\n\nMert Bey merhaba, yukarıda belirttiğim konu hakkında puantaj kayıtlarımla ilgili kontrol talep ediyorum."
    encoded_mesaj = urllib.parse.quote(mesaj_metni)
    wp_link = f"https://wa.me/{admin_no}?text={encoded_mesaj}"
    
    st.link_button(f"📲 {t['destek_btn']}", wp_link)
    st.markdown('</div>', unsafe_allow_html=True)
