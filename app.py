import streamlit as st
import pandas as pd

# --- 1. SAYFA AYARLARI ---
st.set_page_config(page_title="KSK Puantaj", layout="centered", initial_sidebar_state="collapsed")

# --- 2. KSK ÖZEL KARANLIK TEMA (CSS) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { background-color: #0f172a; color: white; }
    
    .dark-card {
        background: rgba(30, 41, 59, 0.8);
        border-radius: 12px;
        border: 1px solid #334155;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
    }
    
    .stat-box {
        text-align: center;
        background: #1e293b;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #475569;
    }
    .stat-value { font-size: 26px; font-weight: 900; color: #38bdf8; }
    .stat-label { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
    
    .day-row {
        display: flex; justify-content: space-between; align-items: center;
        padding: 12px 5px; border-bottom: 1px solid #334155;
    }
    .day-row:last-child { border-bottom: none; }
    
    .day-date { font-weight: bold; color: #e2e8f0; width: 35%; font-size: 14px; }
    .day-status { font-weight: bold; padding: 4px 8px; border-radius: 6px; font-size: 13px; text-align: center; width: 25%;}
    
    /* Excel Renklerine Göre Otomatik Renklendirme */
    .status-N { background-color: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid #22c55e; }
    .status-HTC { background-color: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
    .status-HC { background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
    .status-B { background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
    
    .day-mesai { color: #facc15; font-weight: bold; font-size: 13px; text-align: right; width: 40%;}
    
    .stTextInput>div>div>input {
        background-color: #1e293b !important; color: white !important;
        border-radius: 8px !important; border: 1px solid #475569 !important; height: 45px !important;
    }
    .stTextInput>div>div>input:focus { border-color: #38bdf8 !important; }
    
    .stButton>button {
        width: 100%; border-radius: 8px; background: linear-gradient(90deg, #0284c7 0%, #0369a1 100%);
        color: white; height: 50px; font-weight: bold; border: none; transition: 0.3s;
    }
    .stButton>button:active { transform: scale(0.97); }
    </style>
""", unsafe_allow_html=True)

# --- 3. OTURUM VE VERİ YÜKLEME ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

@st.cache_data
def load_data():
    try:
        # Excel'i çek ve tarih/saat bozulmalarını engellemek için metin (str) olarak algıla
        df = pd.read_excel("veri.xlsx", dtype=str)
        df.columns = df.columns.str.strip() # Başlıklardaki gizli boşlukları temizle
        return df
    except Exception as e:
        return None

df = load_data()

# --- 4. GİRİŞ EKRANI ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align: center; color: white; letter-spacing: 2px;'>KSK PUANTAJ</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 30px;'>DİJİTAL OFİS GİRİŞİ</p>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="dark-card">', unsafe_allow_html=True)
        sicil = st.text_input("FİORİ NO", placeholder="Örn: 533707")
        sifre = st.text_input("DOĞUM YILI (Şifre)", type="password", placeholder="Örn: 1993")
        st.write("")
        giris = st.button("SİSTEME GİRİŞ YAP")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if giris:
            if df is not None:
                # Şifreleri ve Sicilleri temizle/eşleştir
                user_df = df[(df['FİORİ NO'].astype(str).str.strip() == sicil.strip()) & 
                             (df['DOĞUM YILI'].astype(str).str.strip() == sifre.strip())]
                
                if not user_df.empty:
                    st.session_state['user_data'] = user_df
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("❌ Hatalı Sicil veya Şifre!")
            else:
                st.error("⚠️ Veritabanı (veri.xlsx) bulunamadı veya hatalı yüklendi!")

# --- 5. ANA EKRAN (AKILLI ÇEKMECE SİSTEMİ) ---
else:
    user_df = st.session_state['user_data']
    
    # Kişinin 2 satırını ayır (N=Gün Satırı ve M=SAAT Satırı)
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)]
    row_saat = user_df[user_df['N-M'].astype(str).
