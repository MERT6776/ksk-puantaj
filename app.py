import streamlit as st
import pandas as pd
import urllib.parse
import time
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. TEMA KONTROLÜ
if 'theme' not in st.session_state: st.session_state['theme'] = "Gece"

AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN", 
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
GUNLER = ["PAZARTESİ", "SALI", "ÇARŞAMBA", "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"]

# Tema Butonu
c_l, c_theme = st.columns([5, 1])
with c_theme:
    if st.button("☀️" if st.session_state['theme'] == "Gece" else "🌙"):
        st.session_state['theme'] = "Gündüz" if st.session_state['theme'] == "Gece" else "Gece"
        st.rerun()

# 3. CSS (BAYRAK ARKADA - İÇERİK ÖNDE - İMZA SAĞ ALTTA)
if st.session_state['theme'] == "Gece":
    overlay_color = "rgba(10, 15, 25, 0.85)"
    text_color = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.08)"
else:
    overlay_color = "rgba(240, 245, 250, 0.85)"
    text_color = "#1e293b"
    card_bg = "rgba(0, 0, 0, 0.05)"

st.markdown(f"""
    <style>
    /* 🇹🇷 BAYRAK VE PARLAKLIK AYARI */
    .stApp {{
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    
    /* İçeriğin Bayrağın Üstünde Kalmasını Sağlayan Katman */
    [data-testid="stAppViewContainer"] {{
        background-color: {overlay_color} !important;
        backdrop-filter: brightness(1.2) saturate(1.3);
    }}

    .dark-card {{
        background: {card_bg};
        backdrop-filter: blur(15px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px;
        margin-bottom: 20px;
        color: {text_color};
    }}

    .flipper-box {{
        background: {("linear-gradient(145deg, #1e293b, #0f172a)" if st.session_state['theme'] == "Gece" else "#ffffff")};
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        border: 1px solid #475569;
    }}
    .flipper-val {{ font-size: 32px; font-weight: 900; color: {("#facc15" if st.session_state['theme'] == "Gece" else "#1e40af")}; }}

    .day-box {{
        display: flex; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 10px; font-weight: 900; font-size: 18px; color: white;
    }}
    .status-n {{ background: #15803d; border: 2px solid #22c55e; }} 
    .status-htc {{ background: #b45309; border: 2px solid #fbbf24; }}
    .status-hc {{ background: #1d4ed8; border: 2px solid #60a5fa; }}
    .status-b {{ background: #991b1b; border: 2px solid #f87171; }}
    .status-old {{ background: #475569; opacity: 0.5; }}

    .mesai-tag {{ background: #facc15; color: black; padding: 2px 4px; border-radius: 4px; font-size: 10px; margin-top: 3px; font-weight: bold; }}
    .date-label {{ font-size: 9px; font-weight: 800; color: {text_color}; text-transform: uppercase; margin-top: 2px; }}

    /* ✒️ SAĞ ALT İMZA */
    .mert-footer {{
        position: fixed;
        bottom: 10px;
        right: 20px;
        font-size: 11px;
        font-weight: 900;
        color: {text_color};
        opacity: 0.7;
        letter-spacing: 1px;
        z-index: 999;
    }}
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

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- GİRİŞ ---
if not st.session_state['logged_in']:
    st.markdown(f"<h1 style='text-align:center; color:{text_color}; font-weight:900;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    sicil = st.text_input("FİORİ PERSONEL NO")
    sifre = st.text_input("DOĞUM YILI", type="password")
    if st.button("GİRİŞ YAP"):
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
    u_df = st.session_state['user_data']
    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    st.markdown(f"## 👋 {row_g['AD SOYAD']}")
    st.caption(f"{row_g['GÖREVİ']} | Sicil: {row_g['FİORİ NO']}")

    c1, c2, c3 = st.columns(3)
    with c1: st.caption("🏆 Ödenecek"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_g.get("Personele Ödenecek Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c2: st.caption("👷 Fiziki"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_g.get("Fiziki Çalışılan Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c3: st.caption("🕔 TOPLAM MESAİ"); st.markdown(f'<div class="flipper-box" style="border-color:#facc15;"><div class="flipper-val" style="color:#facc15;">{row_s.get("TOPLAM", 0)}</div></div>', unsafe_allow_html=True)

    st.write("---")
    
    t_cols = [c for c in df.columns if '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]
    
    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        with st.expander(f"📂 {h_no}. HAFTA DETAYI"):
            cols = st.columns(7)
            for idx, t_col in enumerate(hafta):
                with cols[idx]:
                    durum = str(row_g[t_col]).strip().upper()
                    mesai = str(row_s[t_col]).strip()
                    try:
                        dt = pd.to_datetime(t_col, dayfirst=True)
                        is_feb = dt.month == 2
                        label = f"{dt.day:02d}/{AYLAR_TR[dt.month]}"
                        g_adi = GUNLER[dt.weekday()][:3]
                    except:
                        is_feb = "02" in str(t_col)
                        label = str(t_col); g_adi = ""

                    if is_feb:
                        st.markdown(f'<div class="day-box status-old">{durum}</div>', unsafe_allow_html=True)
                    else:
                        cls = "status-b"
                        if "N" in durum: cls = "status-n"
                        elif "HTÇ" in durum: cls = "status-htc"
                        elif "HÇ" in durum: cls = "status-hc"
                        st.markdown(f'<div class="day-box {cls}">{durum}</div>', unsafe_allow_html=True)
                        if mesai not in ["0", "0.0", "nan", ""]:
                            st.markdown(f'<div class="mesai-tag">+{mesai} S</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="date-label">{g_adi}<br>{label}</div>', unsafe_allow_html=True)

    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yev = st.number_input("Günlük Yevmiye (₺)", min_value=0)
    if yev > 0: st.success(f"💰 Maaş: {yev * float(row_g.get('Personele Ödenecek Gün', 0)):,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    st.link_button("🚨 İTİRAZ HATTI", "https://wa.me/905459157444")

# SAĞ ALT İMZA
st.markdown('<div class="mert-footer">POWERED BY Mert DÜZCÜK</div>', unsafe_allow_html=True)
