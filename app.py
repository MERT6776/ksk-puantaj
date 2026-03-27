import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. Sayfa Ayarları ve Mobil Uyum Hazırlığı
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. DİL VE TEMA SÖZLÜĞÜ
LANGS = {
    "TR": {
        "title": "FİLYOS FAZ-2 PORTAL", "welcome": "Hoş Geldin", "sicil": "FİORİ NO", "pass": "DOĞUM YILI", 
        "login": "GİRİŞ YAP", "paid_days": "Ödenecek Gün", "phys_days": "Fiziki Gün", "total_over": "TOPLAM MESAİ",
        "week": "HAFTA", "appeal_head": "İtiraz Merkezi", "appeal_topic": "Konu Seçiniz...", "appeal_days": "Gün Seçiniz...",
        "send": "ALİCAN BAYAT'A GÖNDER", "lang": "Dil Seçimi", "note": "Ek Notunuz", "legend": "Kısaltma Rehberi"
    },
    "EN": {
        "title": "FILYOS PHASE-2 PORTAL", "welcome": "Welcome", "sicil": "STAFF NO", "pass": "BIRTH YEAR", 
        "login": "LOGIN", "paid_days": "Paid Days", "phys_days": "Physical Days", "total_over": "TOTAL OVERTIME",
        "week": "WEEK", "appeal_head": "Appeal Center", "appeal_topic": "Select Topic...", "appeal_days": "Select Days...",
        "send": "SEND TO ALICAN BAYAT", "lang": "Language", "note": "Extra Note", "legend": "Legend"
    },
    "UZ": {
        "title": "FİLYOS FAZ-2 PORTALI", "welcome": "Xush kelibsiz", "sicil": "XODIM NO", "pass": "TUG'ILGAN YILI", 
        "login": "KIRISH", "paid_days": "To'lanadigan Kun", "phys_days": "Ishlagan Kun", "total_over": "UMUMIY ISH VAQTI",
        "week": "HAFTA", "appeal_head": "E'tiroz Markazi", "appeal_topic": "Mavzuni tanlang...", "appeal_days": "Kunlarni tanlang...",
        "send": "ALICAN BAYATGA YUBORISH", "lang": "Tilni tanlang", "note": "Qo'shimcha eslatma", "legend": "Qisqartmalar"
    }
}

STATUS_MAP = {
    "HTÇ": "Şirkete Fazladan Pazar Çalışması",
    "HÇ": "Kendine Fazladan Pazar Çalışması",
    "HT": "Hafta Tatili (Gün Kesilmez)",
    "Üİ": "Personel Çalışmadı (Gün Kesilir)",
    "N": "Normal Çalışma",
    "B": "Bayram Tatili (Gün Kesilmez)",
    "BÇ": "Bayramda Çalışma"
}

AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN", 7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
GUNLER_TR = ["PAZARTESİ", "SALI", "ÇARŞAMBA", "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"]

if 'lang' not in st.session_state: st.session_state['lang'] = "TR"
L = LANGS[st.session_state['lang']]

# 3. PREMIUM CSS (PARLAK BAYRAK - MOBİL UYUM - CAM TASARIM)
st.markdown(f"""
    <style>
    .stApp {{ background: transparent !important; }}
    body {{
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg") !important;
        background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(5, 10, 20, 0.85); z-index: -1; backdrop-filter: brightness(1.1) saturate(1.4) blur(2px);
    }}
    .glass-card {{
        background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(25px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px; margin-bottom: 20px; color: white;
    }}
    /* Mobil Uyumlu Takvim Izgarası */
    .day-grid {{
        display: grid; grid-template-columns: repeat(auto-fill, minmax(70px, 1fr)); gap: 10px; margin-top: 15px;
    }}
    .day-item {{
        text-align: center; font-weight: 900; border-radius: 12px; padding: 12px 5px; color: white; transition: 0.3s;
    }}
    .status-n {{ background: linear-gradient(135deg, #15803d, #166534); border: 1px solid #22c55e; }}
    .status-htc {{ background: linear-gradient(135deg, #b45309, #92400e); border: 1px solid #fbbf24; }}
    .status-hc {{ background: linear-gradient(135deg, #1d4ed8, #1e40af); border: 1px solid #60a5fa; }}
    .status-b {{ background: linear-gradient(135deg, #991b1b, #7f1d1d); border: 1px solid #f87171; }}
    .status-old {{ background: rgba(71, 85, 105, 0.6); border: 1px solid #94a3b8; }}
    
    .overtime-tag {{ background: #facc15; color: black; font-size: 11px; padding: 2px 5px; border-radius: 5px; margin-top: 5px; font-weight: 900; }}
    .date-label {{ font-size: 10px; font-weight: 800; color: white; text-transform: uppercase; margin-top: 4px; }}
    
    /* ✒️ POWERED BY MERT DÜZCÜK - SOL ALT BÜYÜK */
    .mert-signature {{
        position: fixed; bottom: 20px; left: 20px; font-size: 22px; font-weight: 900;
        color: white; opacity: 0.9; letter-spacing: 3px; z-index: 1000; text-shadow: 3px 3px 6px rgba(0,0,0,0.9);
    }}
    
    /* Legend (Rehber) Tasarımı */
    .legend-item {{ font-size: 12px; margin-bottom: 5px; display: flex; align-items: center; gap: 8px; }}
    .legend-dot {{ width: 12px; height: 12px; border-radius: 3px; }}

    @media (max-width: 600px) {{
        .mert-signature {{ font-size: 16px; bottom: 10px; left: 10px; }}
        .day-grid {{ grid-template-columns: repeat(auto-fill, minmax(60px, 1fr)); }}
    }}
    </style>
    """, unsafe_allow_html=True)

# 4. VERİ MOTORU
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("veri.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

# --- GİRİŞ EKRANI ---
if not st.session_state['logged_in']:
    st.markdown(f"<h1 style='text-align:center; color:white; letter-spacing:4px;'>{L['title']}</h1>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.session_state['lang'] = st.selectbox(L['lang'], ["TR", "EN", "UZ"])
    sicil = st.text_input(L['sicil'])
    sifre = st.text_input(L['pass'], type="password")
    if st.button(L['login']):
        if df is not None:
            res = df[(df['FİORİ NO'].astype(str) == sicil) & (df['DOĞUM YILI'].astype(str) == sifre)]
            if not res.empty:
                st.session_state['user_data'] = res; st.session_state['logged_in'] = True; st.rerun()
            else: st.error("❌ Bilgiler Hatalı!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    u_df = st.session_state['user_data']
    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    st.markdown(f'<div style="font-size:55px;">👷‍♂️</div>', unsafe_allow_html=True)
    st.markdown(f"## {L['welcome']}, {row_g['AD SOYAD']}")
    st.caption(f"{row_g['GÖREVİ']} | {row_g['FİORİ NO']}")

    # Özet Kartları
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(L['paid_days'], row_g.get("Personele Ödenecek Gün", 0))
    with c2: st.metric(L['phys_days'], row_g.get("Fiziki Çalışılan Gün", 0))
    with c3: st.metric(L['total_over'], row_s.get("TOPLAM", 0))

    st.write("---")
    
    # 🗓️ TAKVİM (Mobil Uyumlu)
    t_cols = [c for c in df.columns if '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]
    
    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        with st.expander(f"📂 {h_no}. {L['week']}"):
            st.markdown('<div class="day-grid">', unsafe_allow_html=True)
            for t_col in hafta:
                durum = str(row_g[t_col]).strip().upper()
                mesai = str(row_s[t_col]).strip()
                try:
                    dt = pd.to_datetime(t_col, dayfirst=True)
                    is_feb = dt.month == 2
                    day_label = f"{dt.day:02d}/{AYLAR_TR[dt.month] if st.session_state['lang']=='TR' else dt.strftime('%b').upper()}"
                    g_adi = GUNLER_TR[dt.weekday()][:3]
                except:
                    is_feb = "02" in str(t_col); day_label = str(t_col); g_adi = ""

                cls = "status-old" if is_feb else ("status-n" if "N" in durum else "status-htc" if "HT" in durum else "status-hc" if "HÇ" in durum else "status-b")
                mesai_html = f'<div class="overtime-tag">+{mesai}S</div>' if not is_feb and mesai not in ["0", "0.0", "nan", ""] else ""
                
                st.markdown(f"""
                    <div class="day-item {cls}">
                        {durum}<br>
                        <span class="date-label">{g_adi} {day_label}</span>
                        {mesai_html}
                    </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 📑 KISALTMA REHBERİ (Legend)
    with st.expander(f"ℹ️ {L['legend']}"):
        for k, v in STATUS_MAP.items():
            st.markdown(f"**{k}:** {v}")

    # 🚨 İTİRAZ PANELİ
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader(f"🚨 {L['appeal_head']}")
    konu = st.selectbox(L['lang'], ["...", "Gün/Puantaj İtirazı", "Mesai Saati İtirazı", "Diğer"], label_visibility="collapsed")
    detay_gunler = ""
    if konu != "...":
        secilenler = st.multiselect(L['appeal_days'], t_cols)
        if secilenler: detay_gunler = "\n\nSeçilen Günler: " + ", ".join([str(g) for g in secilenler])
    
    notunuz = st.text_area(L['note'])
    if st.button(L['send']):
        msg = f"PERSONEL İTİRAZ BİLDİRİMİ\n-------------------\nAd Soyad: {row_g['AD SOYAD']}\nSicil: {row_g['FİORİ NO']}\nKonu: {konu}{detay_gunler}\nNot: {notunuz}\n\nAlican Bey, kontrolünü rica ederim."
        st.link_button("ALİCAN BEY'E WHATSAPP'TAN YAZ", f"https://wa.me/905435314160?text={urllib.parse.quote(msg)}")
    st.markdown('</div>', unsafe_allow_html=True)

# ✒️ POWERED BY MERT DÜZCÜK - SOL ALT MÜHÜR
st.markdown('<div class="mert-signature">POWERED BY Mert DÜZCÜK</div>', unsafe_allow_html=True)
