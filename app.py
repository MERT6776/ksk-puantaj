import streamlit as st
import pandas as pd
import urllib.parse
import time
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. TEMA VE AYARLAR
if 'theme' not in st.session_state: st.session_state['theme'] = "Gece"

AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN", 
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
GUNLER = ["PAZARTESİ", "SALI", "ÇARŞAMBA", "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"]

# Tema Butonu
col_l, col_r = st.columns([5, 1])
with col_r:
    if st.button("☀️" if st.session_state['theme'] == "Gece" else "🌙"):
        st.session_state['theme'] = "Gündüz" if st.session_state['theme'] == "Gece" else "Gece"
        st.rerun()

# 3. ULTRA GÜÇLÜ CSS (BAYRAK GARANTİLİ)
if st.session_state['theme'] == "Gece":
    main_bg = "rgba(5, 10, 20, 0.92)"
    card_bg = "rgba(255, 255, 255, 0.08)"
    text_c = "#ffffff"
else:
    main_bg = "rgba(240, 245, 250, 0.88)"
    card_bg = "rgba(0, 0, 0, 0.06)"
    text_c = "#1e293b"

st.markdown(f"""
    <style>
    /* Streamlit arka planlarını tamamen şeffaf yap */
    .stApp {{ background: transparent !important; }}
    [data-testid="stAppViewContainer"] {{ background: transparent !important; }}
    [data-testid="stHeader"] {{ background: transparent !important; }}
    
    /* 🇹🇷 KIPKIRMIZI BAYRAK KATMANI */
    body {{
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg") !important;
        background-size: cover !important;
        background-position: center !important;
        background-attachment: fixed !important;
    }}
    
    /* Üstüne binen renk katmanı */
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: {main_bg}; z-index: -1;
    }}

    .dark-card {{
        background: {card_bg}; backdrop-filter: blur(25px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        color: {text_c};
    }}
    
    .flipper-box {{
        background: {("linear-gradient(145deg, #1e293b, #0f172a)" if st.session_state['theme'] == "Gece" else "#ffffff")};
        border-radius: 15px; border: 2px solid #475569; padding: 15px; text-align: center;
    }}
    .flipper-val {{ font-size: 36px; font-weight: 900; color: {("#facc15" if st.session_state['theme'] == "Gece" else "#1e40af")}; }}
    
    .day-box {{
        display: flex; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 12px; font-weight: 900; font-size: 18px; color: white;
    }}
    .status-n {{ background: #15803d; border: 2px solid #22c55e; }} 
    .status-htc {{ background: #b45309; border: 2px solid #fbbf24; }}
    .status-hc {{ background: #1d4ed8; border: 2px solid #60a5fa; }}
    .status-b {{ background: #991b1b; border: 2px solid #f87171; }}
    .status-old {{ background: #475569; opacity: 0.5; border: 1px solid #94a3b8; }}
    
    .mesai-tag {{ background: #facc15; color: black; padding: 2px 5px; border-radius: 6px; font-size: 11px; margin-top: 5px; font-weight: 900; }}
    .date-label {{ font-size: 10px; font-weight: 800; color: {text_c}; text-transform: uppercase; margin-top: 3px; }}
    
    .stExpander {{ background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 15px !important; }}
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df = pd.read_excel("veri.xlsx")
        # Sütunları temizle ve tarih olanları belirle
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- GİRİŞ ---
if not st.session_state['logged_in']:
    st.markdown(f"<h1 style='text-align:center; color:{text_c}; font-weight:900;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    sicil = st.text_input("FİORİ PERSONEL NO")
    sifre = st.text_input("DOĞUM YILI", type="password")
    if st.button("SİSTEME GİRİŞ YAP"):
        if df is not None:
            res = df[(df['FİORİ NO'].astype(str) == sicil) & (df['DOĞUM YILI'].astype(str) == sifre)]
            if not res.empty:
                st.session_state['user_data'] = res
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("❌ Hatalı Sicil veya Şifre!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    user_df = st.session_state['user_data']
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    # ÜST PANEL
    c_h, c_w = st.columns([3, 1])
    with c_h: st.markdown(f"## 👋 {row_gun['AD SOYAD']}")
    with c_w: st.markdown(f'<div style="text-align:right;">☁️ 12°C<br><small>Filyos</small></div>', unsafe_allow_html=True)
    
    st.markdown(f'<p style="opacity:0.8; margin-top:-15px;">{row_gun["GÖREVİ"]} | Sicil: {row_gun["FİORİ NO"]}</p>', unsafe_allow_html=True)

    # ÖZET TABELA
    c1, c2, c3 = st.columns(3)
    with c1: st.caption("🏆 Ödenecek Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Personele Ödenecek Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c2: st.caption("👷 Fiziki Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Fiziki Çalışılan Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c3: st.caption("🕔 TOPLAM MESAİ"); st.markdown(f'<div class="flipper-box" style="border-color:#facc15;"><div class="flipper-val" style="color:#facc15;">{row_saat.get("TOPLAM", 0)}</div></div>', unsafe_allow_html=True)

    st.write("### 📅 Haftalık Puantaj Detayları")
    
    # 🎯 TARİH SÜTUNLARINI YAKALAMA (En Güçlü Versiyon)
    tarih_sutunlari = []
    for col in df.columns:
        # Eğer içinde 2026 geçiyorsa veya tarih formatındaysa
        if '202' in str(col) or ('.' in str(col) and len(str(col)) >= 8):
            tarih_sutunlari.append(col)

    if not tarih_sutunlari:
        st.warning("⚠️ Takvim sütunları bulunamadı! Lütfen Excel başlıklarını kontrol edin.")
    else:
        for h_no, i in enumerate(range(0, len(tarih_sutunlari), 7), 1):
            hafta = tarih_sutunlari[i:i+7]
            h_start = str(hafta[0])[:5]
            
            with st.expander(f"📂 {h_no}. HAFTA ({h_start} Başlangıçlı)"):
                cols = st.columns(7)
                for idx, t_col in enumerate(hafta):
                    with cols[idx]:
                        durum = str(row_gun[t_col]).strip().upper()
                        mesai = str(row_saat[t_col]).strip()
                        
                        # Tarih Ayrıştırma
                        try:
                            # Excel'den gelen farklı tarih tiplerini Mart/Şubat diye ayır
                            if '.' in str(t_col):
                                d_part = str(t_col).split('.')
                                day_val = int(d_part[0])
                                month_val = int(d_part[1])
                                is_feb = month_val == 2
                            else:
                                dt = pd.to_datetime(t_col)
                                day_val = dt.day
                                month_val = dt.month
                                is_feb = month_val == 2
                            
                            label = f"{day_val:02d}/{AYLAR_TR[month_val]}"
                        except:
                            is_feb = "02" in str(t_col)
                            label = str(t_col)

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
                        
                        st.markdown(f'<div class="date-label">{label}</div>', unsafe_allow_html=True)

    # MAAŞ PANELİ
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yev = st.number_input("Günlük Net Yevmiye (₺)", min_value=0, step=100)
    if yev > 0:
        st.info(f"💵 Tahmini Maaş: {yev * float(row_gun.get('Personele Ödenecek Gün', 0)):,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.link_button("🚨 PUANTAJ İTİRAZ HATTI (WhatsApp)", "https://wa.me/905459157444")
