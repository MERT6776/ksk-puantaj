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
        "welcome": "Hoş Geldin", "gorev": "Görev", "detay_baslik": "🗓️ Günlük Puantaj Detayları",
        "odenecek": "Ödenecek Gün", "fiziki": "Fiziki Çalışılan", "sgk": "SGK Günü",
        "hesap_baslik": "İnteraktif Maaş Metre", "yevmiye": "Günlük Yevmiyeniz (TL)", "tahmini": "Tahmini Hak Ediş",
        "iletisim_baslik": "İK Destek Merkezi", "iletisim_bilgi": "İtiraz konunuzu seçip destek hattına bağlanın.",
        "konu_sec": "Destek Konusu:", "konular": ["Eksik Gün İtirazı", "Mesai Saati İtirazı", "Maaş/Yevmiye Sorunu", "Diğer Konular"],
        "destek_btn": "FAZ-2 İK DESTEK HATTI"
    }
}

# 3. Premium CSS (Termal Kutular ve Çekmeceler İçin)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} header {visibility: hidden;} footer {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stAppViewContainer"], [data-testid="stHeader"] { background: transparent !important; }
    
    body::before {
        content: ""; position: fixed; top: -10%; left: -10%; width: 120%; height: 120%;
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg");
        background-size: cover; background-position: center; z-index: -2;
        animation: droneShot 15s ease-in-out infinite alternate;
    }
    body::after {
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: linear-gradient(180deg, rgba(15,20,30,0.85) 0%, rgba(5,10,15,0.95) 100%);
        z-index: -1;
    }
    @keyframes droneShot { 0% { transform: scale(1); } 100% { transform: scale(1.1); } }

    .dark-card {
        background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px);
        border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 20px; margin-bottom: 15px;
    }
    
    /* Termal Kutucuklar */
    .day-box {
        display: inline-block; width: 35px; height: 35px; line-height: 35px;
        text-align: center; border-radius: 6px; margin: 2px;
        font-weight: bold; font-size: 12px; color: white;
    }
    .status-n { background: #166534; border: 1px solid #22c55e; } /* Normal Gün - Yeşil */
    .status-htc { background: #92400e; border: 1px solid #f59e0b; } /* Hafta Tatili - Turuncu */
    .status-hc { background: #1e40af; border: 1px solid #3b82f6; } /* Haftalık Çalışma - Mavi */
    .status-b { background: #991b1b; border: 1px solid #ef4444; } /* Boş/Devamsız - Kırmızı */
    
    .mesai-text { color: #facc15; font-size: 11px; display: block; margin-top: -10px; }
    
    .flipper-text {
        font-family: monospace; font-size: 30px; font-weight: bold;
        color: #e2e8f0; background: #0f172a; padding: 5px 10px;
        border-radius: 8px; border: 1px solid #334155;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    try: return pd.read_excel("veri.xlsx")
    except: return None

df = load_data()
t = LANG["TR"]

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- GİRİŞ ---
if not st.session_state['logged_in']:
    st.markdown("<h1 style='text-align:center; color:white;'>FİLYOS FAZ-2</h1>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="dark-card">', unsafe_allow_html=True)
        sicil = st.text_input(t['sicil'])
        sifre = st.text_input(t['sifre'], type="password")
        if st.button(t['login_btn']):
            res = df[(df['FİORİ NO'].astype(str) == sicil) & (df['DOĞUM YILI'].astype(str) == sifre)]
            if not res.empty:
                st.session_state['user_data'] = res # Tüm satırları al (Gün ve Saat)
                st.session_state['logged_in'] = True
                st.rerun()
            else: st.error(t['hata'])
        st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    user_df = st.session_state['user_data']
    # Gün ve Saat satırlarını ayır
    row_gun = user_df[user_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_saat = user_df[user_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    st.markdown(f'<div class="dark-card"><h3>👋 {t["welcome"]}, {row_gun["AD SOYAD"]}</h3></div>', unsafe_allow_html=True)

    # Özet Kartları
    c1, c2, c3 = st.columns(3)
    c1.metric(t['odenecek'], row_gun.get('Personele Ödenecek Gün', 0))
    c2.metric(t['fiziki'], row_gun.get('Fiziki Çalışılan Gün', 0))
    c3.metric(t['sgk'], row_gun.get('SGK Ödenecek Gün', 0))

    # --- AKILLI ÇEKMECELER (Netflix Stili) ---
    st.markdown(f"#### {t['detay_baslik']}")
    
    # Tarih sütunlarını bul (23.02.2026 gibi olanlar)
    tarih_sutunlari = [col for col in df.columns if '.' in str(col) and len(str(col)) > 5]
    
    # Haftalık böl (7'şerli)
    for i in range(0, len(tarih_sutunlari), 7):
        hafta_cols = tarih_sutunlari[i:i+7]
        baslangic = hafta_cols[0].split('.')[0] + " " + hafta_cols[0].split('.')[1]
        bitis = hafta_cols[-1].split('.')[0] + " " + hafta_cols[-1].split('.')[1]
        
        with st.expander(f"📅 {baslangic} - {bitis} Haftası Detayı"):
            cols = st.columns(7)
            for idx, tarih in enumerate(hafta_cols):
                with cols[idx]:
                    durum = str(row_gun[tarih]).upper()
                    mesai = str(row_saat[tarih]) if not pd.isna(row_saat[tarih]) else ""
                    
                    css_class = "status-b"
                    if "N" in durum: css_class = "status-n"
                    elif "HTÇ" in durum: css_class = "status-htc"
                    elif "HÇ" in durum: css_class = "status-hc"
                    
                    st.markdown(f'<div class="day-box {css_class}">{durum}</div>', unsafe_allow_html=True)
                    if mesai and mesai != "0" and mesai != "0.0":
                        st.markdown(f'<span class="mesai-text">+{mesai}s</span>', unsafe_allow_html=True)
                    st.caption(tarih.split('.')[0] + "/" + tarih.split('.')[1])

    # Maaş Metre ve Destek (Aynı Kaldı)
    st.markdown('<div class="dark-card">', unsafe_allow_html=True)
    yevmiye = st.number_input(t['yevmiye'], min_value=0, step=100)
    if yevmiye > 0:
        st.success(f"💸 {t['tahmini']}: {yevmiye * float(row_gun.get('Personele Ödenecek Gün', 0)):,.2f} ₺")
    st.markdown('</div>', unsafe_allow_html=True)

    st.link_button(f"📲 {t['destek_btn']}", f"https://wa.me/905459157444")
