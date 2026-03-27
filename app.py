import streamlit as st
import pandas as pd
import urllib.parse
import time
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. SEÇENEK 6: TEMA KONTROLÜ (Gündüz / Gece)
if 'theme' not in st.session_state:
    st.session_state['theme'] = "Gece"

# En üstte tema ve dil seçimi için ince bir kolon yapısı
col_lang, col_theme = st.columns([5, 1])
with col_theme:
    if st.button("☀️" if st.session_state['theme'] == "Gece" else "🌙"):
        st.session_state['theme'] = "Gündüz" if st.session_state['theme'] == "Gece" else "Gece"
        st.rerun()

# 3. DİNAMİK CSS (Seçilen Temaya Göre Değişir)
if st.session_state['theme'] == "Gece":
    bg_gradient = "radial-gradient(circle, rgba(20,30,48,0.95) 0%, rgba(5,10,15,1) 100%)"
    card_bg = "rgba(255, 255, 255, 0.05)"
    text_color = "white"
    sub_text = "#94a3b8"
else:
    bg_gradient = "linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%)"
    card_bg = "rgba(0, 0, 0, 0.05)"
    text_color = "#1e293b"
    sub_text = "#475569"

st.markdown(f"""
    <style>
    #MainMenu {{visibility: hidden;}} header {{visibility: hidden;}} footer {{visibility: hidden;}}
    [data-testid="stAppViewContainer"] {{ background: transparent !important; }}
    
    body::before {{
        content: ""; position: fixed; top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover; background-position: center; z-index: -2; opacity: 0.1;
    }}
    body::after {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: {bg_gradient}; z-index: -1;
    }}
    .dark-card {{
        background: {card_bg}; backdrop-filter: blur(20px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px; margin-bottom: 20px; color: {text_color};
    }}
    .flipper-box {{
        background: {("linear-gradient(135deg, #1e293b, #0f172a)" if st.session_state['theme'] == "Gece" else "#ffffff")};
        border: 1px solid #334155; border-radius: 15px; padding: 15px; text-align: center;
    }}
    .flipper-val {{ font-size: 34px; font-weight: 900; color: {("#ffffff" if st.session_state['theme'] == "Gece" else "#1e293b")}; }}
    .day-box {{
        display: flex; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 10px; font-weight: 900; font-size: 18px; color: white;
    }}
    .status-n {{ background: #065f46; border: 1px solid #10b981; }} 
    .status-htc {{ background: #92400e; border: 1px solid #fbbf24; }}
    .status-hc {{ background: #1e40af; border: 1px solid #60a5fa; }}
    .status-b {{ background: #7f1d1d; border: 1px solid #f87171; }}
    .status-old {{ background: #64748b; opacity: 0.5; }}
    .mesai-tag {{ background: #facc15; color: black; padding: 2px 5px; border-radius: 4px; font-size: 11px; margin-top: 3px; font-weight: 900; }}
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
    st.markdown(f"<h1 style='text-align:center; color:{text_color};'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
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
    user_df = st.session_state['user_data']
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    # SEÇENEK 4: HAVA DURUMU WIDGET (FİLYOS)
    c_head, c_weather = st.columns([3, 1])
    with c_head:
        st.markdown(f"## 👋 {row_gun['AD SOYAD']}")
    with c_weather:
        st.markdown(f"""
            <div style="text-align:right; color:{text_color};">
                <span style="font-size:20px;">☁️ 12°C</span><br>
                <small>Filyos / Zonguldak</small>
            </div>
        """, unsafe_allow_html=True)

    st.markdown(f'<p style="color:{sub_text};">{row_gun["GÖREVİ"]} | Sicil: {row_gun["FİORİ NO"]}</p>', unsafe_allow_html=True)

    # ÖZET TABELA (SGK YOK, TOPLAM MESAİ EXCEL'DEN)
    c1, c2, c3 = st.columns(3)
    c1.metric("Ödenecek Gün", row_gun.get("Personele Ödenecek Gün", 0))
    c2.metric("Fiziki Gün", row_gun.get("Fiziki Çalışılan Gün", 0))
    c3.metric("Toplam Mesai (Saat)", row_saat.get("TOPLAM", 0))

    st.write("---")
    
    # PUANTAJ DETAYI
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
                    st.caption(t_col.strftime('%d/%m') if hasattr(t_col, 'strftime') else str(t_col)[:5])

    # MAAŞ HESAP
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yev = st.number_input("Günlük Net Yevmiye (₺)", min_value=0, step=100)
    if yev > 0:
        maas = yev * float(row_gun.get('Personele Ödenecek Gün', 0))
        st.success(f"💵 Tahmini Hak Ediş: {maas:,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.link_button("🚨 PUANTAJ İTİRAZ HATTI", "https://wa.me/905459157444")
