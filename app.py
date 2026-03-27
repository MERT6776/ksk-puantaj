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

# Tema Değiştirici Buton
col_l, col_r = st.columns([5, 1])
with col_r:
    if st.button("☀️" if st.session_state['theme'] == "Gece" else "🌙"):
        st.session_state['theme'] = "Gündüz" if st.session_state['theme'] == "Gece" else "Gece"
        st.rerun()

# 3. PREMIUM CSS (Kıpkırmızı Bayrak ve Lüks Tasarım)
if st.session_state['theme'] == "Gece":
    overlay = "rgba(5, 10, 20, 0.90)"
    card_bg = "rgba(255, 255, 255, 0.05)"
    text_c = "#ffffff"
else:
    overlay = "rgba(240, 245, 250, 0.85)"
    card_bg = "rgba(0, 0, 0, 0.05)"
    text_c = "#1e293b"

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}} header {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stAppViewContainer"] {{ background: transparent !important; }}
    
    /* 🇹🇷 KIPKIRMIZI CANLI BAYRAK */
    body::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover; background-position: center; z-index: -2;
        animation: flagWave 15s ease-in-out infinite alternate;
    }}
    body::after {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: {overlay}; z-index: -1;
    }}
    @keyframes flagWave {{
        0% {{ transform: scale(1); filter: brightness(1.1); }}
        100% {{ transform: scale(1.1) translate(-1%, 1%); filter: brightness(1.2); }}
    }}

    .dark-card {{
        background: {card_bg}; backdrop-filter: blur(30px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }}
    
    .flipper-box {{
        background: {("linear-gradient(145deg, #1e293b, #0f172a)" if st.session_state['theme'] == "Gece" else "#ffffff")};
        border-radius: 15px; border: 1px solid #334155; padding: 15px; text-align: center;
    }}
    .flipper-val {{ font-size: 36px; font-weight: 900; color: {("#facc15" if st.session_state['theme'] == "Gece" else "#1e40af")}; }}
    
    .day-box {{
        display: flex; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 12px; font-weight: 900; font-size: 20px; color: white;
    }}
    .status-n {{ background: #15803d; border: 2px solid #22c55e; }} 
    .status-htc {{ background: #b45309; border: 2px solid #fbbf24; }}
    .status-hc {{ background: #1d4ed8; border: 2px solid #60a5fa; }}
    .status-b {{ background: #991b1b; border: 2px solid #f87171; }}
    .status-old {{ background: #475569; border: 1px solid #94a3b8; opacity: 0.5; }}
    
    .mesai-tag {{ background: #facc15; color: black; padding: 3px 6px; border-radius: 6px; font-size: 11px; margin-top: 5px; font-weight: 900; }}
    .date-label {{ font-size: 10px; font-weight: bold; color: {text_c}; text-transform: uppercase; margin-top: 3px; }}
    
    /* 🚨 İTİRAZ BUTONU - CANLI KIRMIZI */
    .stLinkButton>a {{
        background: linear-gradient(90deg, #b91c1c 0%, #dc2626 100%) !important;
        border: 2px solid #ef4444 !important; border-radius: 50px !important;
        height: 60px !important; line-height: 45px !important; font-size: 20px !important; font-weight: 900 !important;
        box-shadow: 0 0 25px rgba(220, 38, 38, 0.5) !important; transition: 0.3s !important;
    }}
    .stLinkButton>a:hover {{ transform: scale(1.03); box-shadow: 0 0 35px rgba(220, 38, 38, 0.7) !important; }}
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
    st.markdown(f"<h1 style='text-align:center; color:{text_c}; font-weight:900;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    sicil = st.text_input("FİORİ PERSONEL NO")
    sifre = st.text_input("DOĞUM YILI", type="password")
    if st.button("SİSTEME GÜVENLİ GİRİŞ"):
        if df is not None:
            res = df[(df['FİORİ NO'].astype(str) == sicil) & (df['DOĞUM YILI'].astype(str) == sifre)]
            if not res.empty:
                st.session_state['user_data'] = res
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("❌ Sicil veya Şifre Hatalı!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    user_df = st.session_state['user_data']
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    # HAVA DURUMU
    c_h, c_w = st.columns([3, 1])
    with c_h: st.markdown(f"## 👋 Hoş Geldin, {row_gun['AD SOYAD']}")
    with c_w: st.markdown(f'<div style="text-align:right; color:{text_c};">☁️ 12°C<br><small>Zonguldak/Filyos</small></div>', unsafe_allow_html=True)
    
    st.markdown(f'<p style="color:{text_c}; opacity:0.8; margin-top:-15px;">{row_gun["GÖREVİ"]} | Sicil: {row_gun["FİORİ NO"]}</p>', unsafe_allow_html=True)

    # ÖZET TABELA (SGK YOK, TOPLAM MESAİ EXCEL'DEN)
    c1, c2, c3 = st.columns(3)
    with c1: st.caption("🏆 Ödenecek Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Personele Ödenecek Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c2: st.caption("🚜 Fiziki Gün"); st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Fiziki Çalışılan Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c3: st.caption("🕔 TOPLAM MESAİ"); st.markdown(f'<div class="flipper-box" style="border-color:#facc15;"><div class="flipper-val" style="color:#facc15;">{row_saat.get("TOPLAM", 0)}</div></div>', unsafe_allow_html=True)

    st.write("### 📅 Haftalık Detaylı Takvim")
    
    # 🎯 LAZER TARİH TESPİTİ (Hata Payını Sıfıra İndirdik)
    tarih_sutunlari = []
    for col in df.columns:
        if any(char.isdigit() for char in str(col)) and '.' in str(col):
            tarih_sutunlari.append(col)

    if not tarih_sutunlari:
        st.warning("⚠️ Takvim verisi yüklenemedi. Lütfen Excel formatını kontrol edin.")
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
                        
                        # Tarih Objesine Dönüştür (Format: 02/ŞUBAT)
                        try:
                            dt_obj = pd.to_datetime(t_col, dayfirst=True)
                            is_feb = dt_obj.month == 2
                            formatted_date = f"{dt_obj.day:02d}/{AYLAR_TR[dt_obj.month]}"
                            g_adi = GUNLER[dt_obj.weekday()]
                        except:
                            is_feb = "02" in str(t_col) # Yedek plan
                            formatted_date = str(t_col)
                            g_adi = ""

                        if is_feb:
                            # Şubat günleri: Gri ve Mesai Yok
                            st.markdown(f'<div class="day-box status-old">{durum}</div>', unsafe_allow_html=True)
                        else:
                            # Mart günleri: Renkli ve Mesaili
                            cls = "status-b"
                            if "N" in durum: cls = "status-n"
                            elif "HTÇ" in durum: cls = "status-htc"
                            elif "HÇ" in durum: cls = "status-hc"
                            st.markdown(f'<div class="day-box {cls}">{durum}</div>', unsafe_allow_html=True)
                            if mesai not in ["0", "0.0", "nan", "None", ""]:
                                st.markdown(f'<div class="mesai-tag">+{mesai} S</div>', unsafe_allow_html=True)
                        
                        st.caption(f"**{g_adi[:3]}**")
                        st.markdown(f'<div class="date-label">{formatted_date}</div>', unsafe_allow_html=True)

    # MAAŞ PANELİ
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yev = st.number_input("Günlük Net Yevmiye (₺)", min_value=0, step=100)
    if yev > 0:
        total = yev * float(row_gun.get('Personele Ödenecek Gün', 0))
        st.info(f"💵 Tahmini Maaş: {total:,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 🚨 KIRMIZI İTİRAZ BUTONU
    st.link_button("🚨 PUANTAJ İTİRAZ HATTI (WhatsApp)", "https://wa.me/905459157444")
