import streamlit as st
import pandas as pd
import urllib.parse
import time
from datetime import datetime

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. Premium Görsel Güzelleştirme (Modern & Keskin)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent !important; }
    
    body::before {
        content: ""; position: fixed; top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover; background-position: center; z-index: -2; opacity: 0.2;
    }
    body::after {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(180deg, rgba(15,20,30,0.95) 0%, rgba(5,10,15,1) 100%);
        z-index: -1;
    }
    .dark-card {
        background: rgba(255, 255, 255, 0.07); backdrop-filter: blur(20px);
        border-radius: 15px; border: 1px solid rgba(255, 255, 255, 0.15);
        padding: 20px; margin-bottom: 15px; box-shadow: 0 8px 32px 0 rgba(0,0,0,0.8);
    }
    .flipper-box {
        background: linear-gradient(145deg, #0f172a, #1e293b); border: 2px solid #334155; 
        border-radius: 12px; padding: 15px; text-align: center;
    }
    .flipper-val { font-family: 'JetBrains Mono', monospace; font-size: 36px; font-weight: 800; color: #f8fafc; }
    .mesai-val { color: #facc15 !important; text-shadow: 0 0 10px rgba(250, 204, 21, 0.5); }
    
    .day-box {
        display: flex; align-items: center; justify-content: center;
        width: 100%; aspect-ratio: 1/1; border-radius: 10px; margin-bottom: 5px;
        font-weight: 900; font-size: 18px; color: white; transition: 0.3s;
    }
    .status-n { background: #15803d; border: 2px solid #22c55e; box-shadow: 0 0 15px rgba(34,197,94,0.3); } 
    .status-htc { background: #b45309; border: 2px solid #fbbf24; }
    .status-hc { background: #1d4ed8; border: 2px solid #60a5fa; }
    .status-b { background: #7f1d1d; border: 2px solid #f87171; }
    
    .mesai-tag { background: #facc15; color: black; padding: 3px 6px; border-radius: 6px; font-size: 12px; margin-top: 5px; font-weight: 900; }
    .stExpander { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 12px !important; }
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
    st.markdown("<h1 style='text-align:center; color:white; letter-spacing:3px;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#94a3b8;'>PERSONEL PUANTAJ PORTALI</p>", unsafe_allow_html=True)
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    sicil = st.text_input("FİORİ PERSONEL NO", placeholder="Sicil numaranız")
    sifre = st.text_input("DOĞUM YILI (Şifre)", type="password", placeholder="Doğum yılınız")
    if st.button("SİSTEME GÜVENLİ GİRİŞ"):
        if df is not None:
            res = df[(df['FİORİ NO'].astype(str) == sicil) & (df['DOĞUM YILI'].astype(str) == sifre)]
            if not res.empty:
                st.session_state['user_data'] = res
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error("❌ Giriş bilgileri eşleşmedi!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    user_df = st.session_state['user_data']
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    st.markdown(f'<div class="dark-card"><h3>🏗️ {row_gun["AD SOYAD"]}</h3><p style="color:#facc15; margin:0;">{row_gun["GÖREVİ"]} | Sicil: {row_gun["FİORİ NO"]}</p></div>', unsafe_allow_html=True)

    # ÖZET TABELA (SGK Silindi, Toplam Mesai Excel'den Geldi)
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.caption("🏆 Ödenecek Gün")
        st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Personele Ödenecek Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c2: 
        st.caption("👷 Fiziki Çalışılan")
        st.markdown(f'<div class="flipper-box"><div class="flipper-val">{row_gun.get("Fiziki Çalışılan Gün", 0)}</div></div>', unsafe_allow_html=True)
    with c3: 
        # Excel'deki "TOPLAM" sütunundan direkt çekiyoruz
        t_mesai = row_saat.get('TOPLAM', 0)
        st.caption("🕔 TOPLAM MESAİ (Saat)")
        st.markdown(f'<div class="flipper-box" style="border-color:#facc15;"><div class="flipper-val mesai-val">{t_mesai}</div></div>', unsafe_allow_html=True)

    st.write("### 📅 HAFTALIK PUANTAJ TAKVİMİ")
    
    tarih_sutunlari = [col for col in df.columns if isinstance(col, datetime) or (isinstance(col, str) and '202' in col)]
    
    # Haftalık Çekmeceler (Hafta Adları Eklendi)
    for h_no, i in enumerate(range(0, len(tarih_sutunlari), 7), 1):
        hafta = tarih_sutunlari[i:i+7]
        # O haftanın mesaisini Excel'den hesapla
        h_mesai_toplam = 0
        for t_col in hafta:
            v = str(row_saat[t_col]).strip().replace(',', '.')
            try: h_mesai_toplam += float(v) if v not in ["nan", "", "None"] else 0
            except: pass
            
        h_label = hafta[0].strftime('%d.%m') if hasattr(hafta[0], 'strftime') else str(hafta[0])[:5]
        
        with st.expander(f"📂 {h_no}. HAFTA ({h_label} Başlangıçlı) - Toplam: {h_mesai_toplam} Saat"):
            cols = st.columns(len(hafta))
            for idx, t_col in enumerate(hafta):
                with cols[idx]:
                    durum = str(row_gun[t_col]).strip().upper()
                    mesai = str(row_saat[t_col]).strip()
                    g_adi = GUNLER[t_col.weekday()] if hasattr(t_col, 'weekday') else ""
                    
                    cls = "status-b"
                    if "N" in durum: cls = "status-n"
                    elif "HTÇ" in durum: cls = "status-htc"
                    elif "HÇ" in durum: cls = "status-hc"
                    
                    st.markdown(f'<div class="day-box {cls}">{durum}</div>', unsafe_allow_html=True)
                    if mesai not in ["0", "0.0", "nan", "None", ""]:
                        st.markdown(f'<div class="mesai-tag">+{mesai} S</div>', unsafe_allow_html=True)
                    st.caption(f"**{g_adi}**")
                    st.caption(t_col.strftime('%d/%m') if hasattr(t_col, 'strftime') else str(t_col)[:5])

    # MAAŞ HESAPLAMA
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    st.write("#### 💸 Maaş Hesaplama Paneli")
    yev = st.number_input("Günlük Net Yevmiyeniz (₺)", min_value=0, step=100)
    if yev > 0:
        maas = yev * float(row_gun.get('Personele Ödenecek Gün', 0))
        st.info(f"💵 **Tahmini Hak Ediş:** {maas:,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.link_button("📲 İK DESTEK HATTI (WhatsApp)", "https://wa.me/905459157444")
