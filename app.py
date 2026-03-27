import streamlit as st
import pandas as pd
import urllib.parse
import time
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. Premium CSS (Daha keskin renkler ve büyük fontlar)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent !important; }
    body::before {
        content: ""; position: fixed; top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover; background-position: center; z-index: -2; opacity: 0.25;
    }
    body::after {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(180deg, rgba(15,20,30,0.95) 0%, rgba(5,10,15,1) 100%);
        z-index: -1;
    }
    .dark-card {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(15px);
        border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px; margin-bottom: 15px;
    }
    .flipper-box {
        background: #0f172a; border: 2px solid #334155; border-radius: 8px;
        padding: 10px; text-align: center; box-shadow: inset 0 0 15px rgba(0,0,0,0.5);
    }
    .flipper-val { font-family: monospace; font-size: 32px; font-weight: bold; color: #facc15; }
    .day-box {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 8px; margin-bottom: 5px;
        font-weight: bold; font-size: 16px; color: white;
    }
    .status-n { background: #166534; border: 1px solid #22c55e; } 
    .status-htc { background: #92400e; border: 1px solid #f59e0b; }
    .status-hc { background: #1e40af; border: 1px solid #3b82f6; }
    .status-b { background: #450a0a; border: 1px solid #ef4444; }
    .mesai-tag { background: #facc15; color: black; padding: 2px 5px; border-radius: 4px; font-size: 11px; margin-top: 3px; font-weight: 900; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("veri.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- GİRİŞ ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align:center; color:white;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    sicil = st.text_input("FİORİ NO")
    sifre = st.text_input("DOĞUM YILI", type="password")
    if st.button("SİSTEME GİRİŞ YAP"):
        if df is not None:
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
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    st.markdown(f'<div class="dark-card"><h3>👋 Hoş Geldin, {row_gun["AD SOYAD"]}</h3><small>{row_gun["GÖREVİ"]} | Sicil: {row_gun["FİORİ NO"]}</small></div>', unsafe_allow_html=True)

    # Özet Veriler & TOPLAM MESAİ (Senin istediğin o büyük rakam)
    tarih_sutunlari = [col for col in df.columns if isinstance(col, datetime) or (isinstance(col, str) and '202' in col)]
    
    # Tüm mesai saatlerini topla
    toplam_mesai_saati = 0
    for t_col in tarih_sutunlari:
        val = str(row_saat[t_col]).strip().replace(',', '.')
        try: toplam_mesai_saati += float(val) if val not in ["nan", "", "None"] else 0
        except: pass

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.caption("Ödenecek Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Personele Ödenecek Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c2: st.caption("Fiziki Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Fiziki Çalışılan Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c3: st.caption("SGK Günü"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("SGK Ödenecek Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c4: st.caption("TOPLAM MESAİ"); st.markdown(f'<div class="flipper-box" style="border-color:#facc15;"><div class="flipper-val" style="color:#facc15;">{toplam_mesai_saati}</div></div>', unsafe_allow_html=True)

    st.write("### 🗓️ Haftalık Detaylı Puantaj")
    
    # Haftalık gruplama ve gün isimleri
    for i in range(0, len(tarih_sutunlari), 7):
        hafta = tarih_sutunlari[i:i+7]
        h_mesai = 0
        for t_col in hafta:
            v = str(row_saat[t_col]).strip().replace(',', '.')
            try: h_mesai += float(v) if v not in ["nan", "", "None"] else 0
            except: pass
            
        h_label = hafta[0].strftime('%d.%m') if hasattr(hafta[0], 'strftime') else str(hafta[0])[:5]
        with st.expander(f"📅 {h_label} Haftası (Toplam Mesai: {h_mesai} Saat)"):
            cols = st.columns(len(hafta))
            for idx, t_col in enumerate(hafta):
                with cols[idx]:
                    durum = str(row_gun[t_col]).strip().upper()
                    mesai = str(row_saat[t_col]).strip()
                    
                    # Gün ismini bul (Pazartesi vs)
                    g_adi = GUNLER[t_col.weekday()] if hasattr(t_col, 'weekday') else ""
                    
                    cls = "status-b"
                    if "N" in durum: cls = "status-n"
                    elif "HTÇ" in durum: cls = "status-htc"
                    elif "HÇ" in durum: cls = "status-hc"
                    
                    st.markdown(f'<div class="day-box {cls}">{durum}</div>', unsafe_allow_html=True)
                    if mesai not in ["0", "0.0", "nan", "None", ""]:
                        st.markdown(f'<div class="mesai-tag">+{mesai} S</div>', unsafe_allow_html=True)
                    st.caption(f"**{g_adi[:3]}**") # Günün ilk 3 harfi (Paz, Sal...)
                    st.caption(t_col.strftime('%d/%m') if hasattr(t_col, 'strftime') else str(t_col)[:5])

    # Maaş Metre
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yevmiye = st.number_input("Günlük Yevmiyeniz (TL)", min_value=0, step=100)
    if yevmiye > 0:
        total = yevmiye * float(row_gun.get('Personele Ödenecek Gün', 0))
        st.success(f"💰 Tahmini Maaş: {total:,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.link_button("📲 FAZ-2 İK DESTEK HATTI", "https://wa.me/905459157444")
