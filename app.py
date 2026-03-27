import streamlit as st
import pandas as pd
import urllib.parse
import time
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. TEMA KONTROLÜ
if 'theme' not in st.session_state:
    st.session_state['theme'] = "Gece"

# Ayların Türkçe İsimleri
AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN", 
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}

# En Üst Panel (Tema ve Dil)
col_l, col_r = st.columns([5, 1])
with col_r:
    if st.button("☀️" if st.session_state['theme'] == "Gece" else "🌙"):
        st.session_state['theme'] = "Gündüz" if st.session_state['theme'] == "Gece" else "Gece"
        st.rerun()

# 3. PREMIUM CSS (Kıpkırmızı Dalgalanan Bayrak ve Lüks Geçişler)
if st.session_state['theme'] == "Gece":
    overlay = "rgba(10, 15, 25, 0.85)"
    card_bg = "rgba(255, 255, 255, 0.05)"
    text_c = "#f8fafc"
else:
    overlay = "rgba(240, 242, 245, 0.85)"
    card_bg = "rgba(0, 0, 0, 0.05)"
    text_c = "#1e293b"

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}} header {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stAppViewContainer"] {{ background: transparent !important; }}
    
    /* 🇹🇷 KIPKIRMIZI DALGALANAN TÜRK BAYRAĞI ARKA PLANI */
    body::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover; background-position: center; z-index: -2;
        animation: wave 10s ease-in-out infinite alternate;
    }}
    /* Geçişli Filtre */
    body::after {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: {overlay}; z-index: -1;
    }}
    
    @keyframes wave {{
        0% {{ transform: scale(1.0) translate(0,0); }}
        100% {{ transform: scale(1.1) translate(-2%, 1%); }}
    }}

    .dark-card {{
        background: {card_bg}; backdrop-filter: blur(25px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px; margin-bottom: 20px; color: {text_c};
    }}
    
    .flipper-box {{
        background: {("linear-gradient(145deg, #1e293b, #0f172a)" if st.session_state['theme'] == "Gece" else "#ffffff")};
        border-radius: 15px; border: 1px solid #334155; padding: 15px; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4);
    }}
    .flipper-val {{ font-size: 34px; font-weight: 900; color: {("#facc15" if st.session_state['theme'] == "Gece" else "#1e40af")}; }}
    
    .day-box {{
        display: flex; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 12px; font-weight: 900; font-size: 20px; color: white;
    }}
    .status-n {{ background: #15803d; border: 2px solid #22c55e; }} 
    .status-htc {{ background: #b45309; border: 2px solid #fbbf24; }}
    .status-hc {{ background: #1d4ed8; border: 2px solid #60a5fa; }}
    .status-b {{ background: #991b1b; border: 2px solid #f87171; }}
    .status-old {{ background: #475569; opacity: 0.55; }}
    
    .mesai-tag {{ background: #facc15; color: black; padding: 2px 6px; border-radius: 6px; font-size: 12px; margin-top: 4px; font-weight: 900; }}
    .date-label {{ font-size: 10px; font-weight: bold; color: {text_c}; text-transform: uppercase; margin-top: 2px; }}
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
    st.markdown(f"<h1 style='text-align:center; color:{text_c}; font-weight:900;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
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
            else: st.error("❌ Hatalı Bilgi!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    user_df = st.session_state['user_data']
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    # HAVA DURUMU VE BAŞLIK
    c_h, c_w = st.columns([3, 1])
    with c_h: st.markdown(f"## 👋 {row_gun['AD SOYAD']}")
    with c_w: st.markdown(f'<div style="text-align:right; color:{text_c};">☁️ 12°C<br><small>Zonguldak/Filyos</small></div>', unsafe_allow_html=True)
    
    st.markdown(f'<p style="color:{text_c}; opacity:0.8;">{row_gun["GÖREVİ"]} | Sicil: {row_gun["FİORİ NO"]}</p>', unsafe_allow_html=True)

    # ÖZET TABELA (SGK SİLİNDİ, MESAİ EXCEL'DEN)
    c1, c2, c3 = st.columns(3)
    with c1: st.caption("🏆 Ödenecek Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Personele Ödenecek Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c2: st.caption("🚜 Fiziki Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Fiziki Çalışılan Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c3: st.caption("🕔 TOPLAM MESAİ"); st.markdown(f'<div class="flipper-box"><div class="flipper-val" style="color:#facc15;">{row_saat.get("TOPLAM", 0)}</div></div>', unsafe_allow_html=True)

    st.write("---")
    
    # TARİH SÜTUNLARI VE ÇEKMECELER
    tarih_sutunlari = [col for col in df.columns if isinstance(col, datetime) or (isinstance(col, str) and '202' in col)]
    
    for h_no, i in enumerate(range(0, len(tarih_sutunlari), 7), 1):
        hafta = tarih_sutunlari[i:i+7]
        h_start = hafta[0].strftime('%d.%m') if hasattr(hafta[0], 'strftime') else str(hafta[0])[:5]
        
        with st.expander(f"📂 {h_no}. HAFTA ({h_start} Başlangıçlı)"):
            cols = st.columns(7)
            for idx, t_col in enumerate(hafta):
                with cols[idx]:
                    durum = str(row_gun[t_col]).strip().upper()
                    mesai = str(row_saat[t_col]).strip()
                    is_feb = hasattr(t_col, 'month') and t_col.month == 2
                    g_adi = GUNLER[t_col.weekday()] if hasattr(t_col, 'weekday') else ""
                    
                    # Tarih Formatı: 02/ŞUBAT
                    t_day = t_col.day if hasattr(t_col, 'day') else "00"
                    t_month = AYLAR_TR.get(t_col.month, "AY") if hasattr(t_col, 'month') else "AY"
                    formatted_date = f"{t_day:02d}/{t_month}"
                    
                    if is_feb:
                        st.markdown(f'<div class="day-box status-old">{durum}</div>', unsafe_allow_html=True)
                    else:
                        cls = "status-b"
                        if "N" in durum: cls = "status-n"
                        elif "HTÇ" in durum: cls = "status-htc"
                        elif "HÇ" in durum: cls = "status-hc"
                        st.markdown(f'<div class="day-box {cls}">{durum}</div>', unsafe_allow_html=True)
                        if mesai not in ["0", "0.0", "nan", "None", ""]:
                            st.markdown(f'<div class="mesai-tag">+{mesai} S</div>', unsafe_allow_html=True)
                    
                    st.caption(f"**{g_adi[:3]}**")
                    st.markdown(f'<div class="date-label">{formatted_date}</div>', unsafe_allow_html=True)

    # MAAŞ METRE
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yev = st.number_input("Günlük Net Yevmiye (₺)", min_value=0, step=100)
    if yev > 0:
        total = yev * float(row_gun.get('Personele Ödenecek Gün', 0))
        st.success(f"💰 Tahmini Maaş: {total:,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.link_button("🚨 PUANTAJ İTİRAZ HATTI", "https://wa.me/905459157444")
