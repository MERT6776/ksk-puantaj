import streamlit as st
import pandas as pd
import urllib.parse
import time
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. Premium CSS (Jilet gibi bir görünüm için)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent !important; }
    body::before {
        content: ""; position: fixed; top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover; background-position: center; z-index: -2; opacity: 0.3;
    }
    body::after {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(180deg, rgba(15,20,30,0.9) 0%, rgba(5,10,15,1) 100%);
        z-index: -1;
    }
    .dark-card {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px; margin-bottom: 10px;
    }
    .day-box {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 8px; margin-bottom: 5px;
        font-weight: bold; font-size: 14px; color: white;
    }
    .status-n { background: #166534; border: 1px solid #22c55e; } 
    .status-htc { background: #92400e; border: 1px solid #f59e0b; }
    .status-hc { background: #1e40af; border: 1px solid #3b82f6; }
    .status-b { background: #450a0a; border: 1px solid #ef4444; }
    .mesai-tag { background: #facc15; color: black; padding: 2px 4px; border-radius: 4px; font-size: 10px; margin-top: 2px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        # Excel'i oku ve sütunlardaki gizli boşlukları temizle
        df = pd.read_excel("veri.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- GİRİŞ EKRANI ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align:center; color:white;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    sicil = st.text_input("FİORİ NO")
    sifre = st.text_input("DOĞUM YILI", type="password")
    if st.button("SİSTEME GİRİŞ YAP"):
        if df is not None:
            # Sütun isimlerini garantiye alalım
            res = df[(df['FİORİ NO'].astype(str) == sicil) & (df['DOĞUM YILI'].astype(str) == sifre)]
            if not res.empty:
                st.session_state['user_data'] = res
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("❌ Bilgiler Hatalı!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    user_df = st.session_state['user_data']
    # Gün ve Saat satırlarını ayır (N-M sütununa göre)
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    st.markdown(f'<div class="dark-card"><h3>👋 Hoş Geldin, {row_gun["AD SOYAD"]}</h3><small>{row_gun["GÖREVİ"]} | Sicil: {row_gun["FİORİ NO"]}</small></div>', unsafe_allow_html=True)

    # Özet Veriler
    c1, c2, c3 = st.columns(3)
    c1.metric("Ödenecek Gün", row_gun.get('Personele Ödenecek Gün', 0))
    c2.metric("Fiziki Gün", row_gun.get('Fiziki Çalışılan Gün', 0))
    c3.metric("SGK Gün", row_gun.get('SGK Ödenecek Gün', 0))

    st.write("### 🗓️ Haftalık Puantaj Çekmeceleri")
    
    # Tarih Sütunlarını Tespit Et (Excel'in tarih objelerini yakalar)
    tarih_sutunlari = []
    for col in df.columns:
        # Eğer sütun adı bir datetime objesiyse veya içinde tarih geçiyorsa
        if isinstance(col, datetime) or (isinstance(col, str) and any(x in col for x in ['.', '/', '202'])):
            tarih_sutunlari.append(col)

    if not tarih_sutunlari:
        st.warning("⚠️ Tarih sütunları bulunamadı. Lütfen Excel başlıklarını kontrol edin.")
    else:
        # Haftalık grupla (7 gün)
        for i in range(0, len(tarih_sutunlari), 7):
            hafta = tarih_sutunlari[i:i+7]
            # Başlık için tarihi güzelleştir (23.02 gibi)
            h_start = hafta[0].strftime('%d.%m') if hasattr(hafta[0], 'strftime') else str(hafta[0])[:5]
            h_end = hafta[-1].strftime('%d.%m') if hasattr(hafta[-1], 'strftime') else str(hafta[-1])[:5]
            
            with st.expander(f"📅 {h_start} - {h_end} Tarihleri Arası Detaylar"):
                cols = st.columns(len(hafta))
                for idx, t_col in enumerate(hafta):
                    with cols[idx]:
                        durum = str(row_gun[t_col]).strip().upper()
                        mesai = str(row_saat[t_col]).strip()
                        
                        # Renk belirleme
                        cls = "status-b"
                        if "N" in durum: cls = "status-n"
                        elif "HTÇ" in durum: cls = "status-htc"
                        elif "HÇ" in durum: cls = "status-hc"
                        
                        st.markdown(f'<div class="day-box {cls}">{durum}</div>', unsafe_allow_html=True)
                        
                        # Mesai varsa göster
                        if mesai not in ["0", "0.0", "nan", "None", ""]:
                            st.markdown(f'<div class="mesai-tag">+{mesai}s</div>', unsafe_allow_html=True)
                        
                        # Tarih alt yazısı
                        t_label = t_col.strftime('%d/%m') if hasattr(t_col, 'strftime') else str(t_col)[:5]
                        st.caption(t_label)

    # Maaş Metre
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yevmiye = st.number_input("Günlük Yevmiyeniz (TL)", min_value=0, step=100)
    if yevmiye > 0:
        total = yevmiye * float(row_gun.get('Personele Ödenecek Gün', 0))
        st.success(f"💰 Tahmini Hak Ediş: {total:,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.link_button("📲 FAZ-2 İK DESTEK HATTI", "https://wa.me/905459157444")
