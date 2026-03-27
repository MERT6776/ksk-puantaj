import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta

# 1. Sayfa Ayarları
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# 2. DİL VE VERİ SÖZLÜĞÜ
LANGS = {
    "TR": {
        "title": "FİLYOS FAZ-2 PORTAL", "welcome_morning": "Günaydın", "welcome_day": "İyi Günler", 
        "welcome_evening": "İyi Akşamlar", "welcome_night": "İyi Geceler", "sicil": "KULLANICI ADI", "pass": "DOĞUM YILI", 
        "login": "GİRİŞ YAP", "paid_days": "Ödenecek Gün", "phys_days": "Fiziki Gün", "total_over": "TOPLAM MESAİ",
        "week": "HAFTA", "week_suffix": "PUANTAJ DURUM TAKVİMİ", "appeal_head": "İtiraz Merkezi", "appeal_topic": "Konu Seçiniz...", 
        "appeal_days": "Gün Seçiniz...", "send": "ALİCAN BAYAT'A GÖNDER", "lang": "Dil Seçimi", 
        "note": "Ek Notunuz", "legend": "Kısaltma Rehberi (Filtrelemek İçin Tıklayın)",
        "audit": "Veri Kaynağı: Mert DÜZCÜK Onaylı Sistem", "update": "Son Güncelleme", "shift_end": "Mesai Tamamlandı"
    },
    "EN": {"title": "FILYOS PHASE-2", "welcome_morning": "Good Morning", "welcome_day": "Good Day", "welcome_evening": "Good Evening", "welcome_night": "Good Night", "sicil": "USERNAME", "pass": "BIRTH YEAR", "login": "LOGIN", "paid_days": "Paid Days", "phys_days": "Physical Days", "total_over": "TOTAL OVERTIME", "week": "WEEK", "week_suffix": "STATUS TABLE", "appeal_head": "Appeal Center", "appeal_topic": "Topic...", "appeal_days": "Days...", "send": "SEND", "lang": "Language", "note": "Note", "legend": "Legend", "audit": "Source: Mert DÜZCÜK Approved", "update": "Update", "shift_end": "Shift Completed"},
    "UZ": {"title": "FİLYOS FAZ-2", "welcome_morning": "Xayrli tong", "welcome_day": "Xayrli kun", "welcome_evening": "Xayrli kech", "welcome_night": "Xayrli tun", "sicil": "FOYDALANUVCHI NOMI", "pass": "TUG'ILGAN YILI", "login": "KIRISH", "paid_days": "To'lanadigan Kun", "phys_days": "Ishlagan Kun", "total_over": "UMUMIY ISH VAQTI", "week": "HAFTA", "week_suffix": "PUANTAJ JADVALI", "appeal_head": "E'tiroz Markazi", "appeal_topic": "Mavzu...", "appeal_days": "Kunlar...", "send": "YUBORISH", "lang": "Til", "note": "Eslatma", "legend": "Qisqartmalar", "audit": "Tasdiqlangan: Mert DÜZCÜK", "update": "Yangilanish", "shift_end": "Ish yakunlandi"}
}

STATUS_MAP = {"HTÇ": "Şirkete Fazladan Pazar Çalışması", "HÇ": "Kendine Fazladan Pazar Çalışması", "HT": "Hafta Tatili (Gün Kesilmez)", "Üİ": "Personel Çalışmadı (Gün Kesilir)", "N": "Normal Çalışma", "B": "Bayram Tatili (Gün Kesilmez)", "BÇ": "Bayramda Çalışma"}
AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN", 7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
GUNLER_TR = ["PAZARTESİ", "SALI", "ÇARŞAMBA", "PERŞEMBE", "CUMA", "CUMARTESİ", "PAZAR"]

if 'lang' not in st.session_state: st.session_state['lang'] = "TR"
if 'filter_status' not in st.session_state: st.session_state['filter_status'] = None
L = LANGS[st.session_state['lang']]

# Türkiye Saati ve Mesai
now_tr = datetime.utcnow() + timedelta(hours=3)
clock_init = now_tr.strftime("%d.%m.%Y | %H:%M:%S")
start_hour, end_hour = 8, 18
current_hour_decimal = now_tr.hour + now_tr.minute / 60
shift_pct = max(0, min(100, (current_hour_decimal - start_hour) / (end_hour - start_hour) * 100))

# 3. HIGH-VISIBILITY CSS
st.markdown(f"""
    <style>
    .stApp {{ background: transparent !important; }}
    body {{
        background-image: url("https://upload.wikimedia.org/wikipedia/commons/b/b4/Flag_of_Turkey.svg") !important;
        background-size: cover !important; background-position: center !important; background-attachment: fixed !important;
    }}
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: rgba(5, 10, 20, 0.88); z-index: -1; backdrop-filter: brightness(1.1) saturate(1.4);
    }}

    /* BÜYÜTÜLMÜŞ SAAT */
    #live-clock {{
        text-align: right; color: #ffd700; font-family: 'Courier New', monospace;
        font-weight: 900; font-size: 22px; letter-spacing: 2px;
        padding: 10px; text-shadow: 2px 2px 5px black;
    }}

    /* BÜYÜTÜLMÜŞ KARŞILAMA VE KULLANICI */
    .user-header {{ font-size: 32px; font-weight: 900; color: white; margin-bottom: 0px; }}
    .user-sub {{ font-size: 18px; font-weight: 700; color: rgba(255,215,0,0.9); margin-bottom: 20px; }}

    /* BÜYÜTÜLMÜŞ PAYDOS BİLGİSİ */
    .paydos-label {{ font-size: 20px; font-weight: 800; color: #ffd700; margin-top: 10px; text-transform: uppercase; }}

    .shift-container {{
        width: 100%; background: rgba(255, 255, 255, 0.1); border-radius: 12px;
        height: 16px; margin: 15px 0; border: 1px solid rgba(255, 215, 0, 0.4); overflow: hidden;
    }}
    .shift-bar {{
        width: {shift_pct}%; height: 100%; 
        background: linear-gradient(90deg, #b8860b, #ffd700);
        box-shadow: 0 0 15px #ffd700; transition: width 0.5s ease-in-out;
    }}

    .glass-card {{
        background: rgba(255, 255, 255, 0.08); backdrop-filter: blur(25px);
        border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 20px; margin-bottom: 20px; color: white;
    }}

    .stExpander {{
        background: rgba(40, 30, 20, 0.4) !important; border: 1px solid #b8860b !important;
        border-radius: 10px !important; border-left: 10px solid #b8860b !important;
    }}

    .day-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(75px, 1fr)); gap: 12px; }}
    .day-item {{ text-align: center; font-weight: 900; border-radius: 12px; padding: 12px 5px; color: white; }}
    
    .status-n {{ background: linear-gradient(135deg, #15803d, #166534); border: 1px solid #22c55e; }}
    .status-htc {{ background: linear-gradient(135deg, #b45309, #92400e); border: 1px solid #fbbf24; }}
    .status-hc {{ background: linear-gradient(135deg, #1d4ed8, #1e40af); border: 1px solid #60a5fa; }}
    .status-b {{ background: linear-gradient(135deg, #991b1b, #7f1d1d); border: 1px solid #f87171; }}

    /* ✒️ POWERED BY MERT DÜZCÜK - ZARİF BOYUTTA KALDI */
    .mert-signature {{
        position: fixed; bottom: 12px; left: 15px; font-size: 14px; font-weight: 900;
        color: white; opacity: 0.7; letter-spacing: 2px; z-index: 1000;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }}

    @media (max-width: 600px) {{
        .user-header {{ font-size: 24px; }}
        .user-sub {{ font-size: 15px; }}
        .paydos-label {{ font-size: 16px; }}
        #live-clock {{ font-size: 16px; }}
    }}
    </style>

    <div id="live-clock">{clock_init}</div>

    <script>
    function updateClock() {{
        const el = document.getElementById('live-clock');
        if(!el) return;
        const now = new Date();
        const trTime = new Date(now.toLocaleString('en-US', {{ timeZone: 'Europe/Istanbul' }}));
        const d = String(trTime.getDate()).padStart(2, '0');
        const m = String(trTime.getMonth() + 1).padStart(2, '0');
        const y = trTime.getFullYear();
        const h = String(trTime.getHours()).padStart(2, '0');
        const i = String(trTime.getMinutes()).padStart(2, '0');
        const s = String(trTime.getSeconds()).padStart(2, '0');
        el.innerHTML = d + "." + m + "." + y + " | " + h + ":" + i + ":" + s;
    }}
    setInterval(updateClock, 1000);
    window.addEventListener('load', updateClock);
    </script>
    """, unsafe_allow_html=True)

# 4. VERİ VE SELAMLAMA
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("veri.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except: return None

df = load_data()

# Selamlama
hour_greet = now_tr.hour
if 5 <= hour_greet < 12: greet_key = "welcome_morning"
elif 12 <= hour_greet < 18: greet_key = "welcome_day"
elif 18 <= hour_greet < 23: greet_key = "welcome_evening"
else: greet_key = "welcome_night"

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
            if not res.empty: st.session_state['user_data'] = res; st.session_state['logged_in'] = True; st.rerun()
            else: st.error("❌ Bilgiler Hatalı!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    u_df = st.session_state['user_data']
    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    # BÜYÜTÜLMÜŞ ÜST BİLGİ ALANI
    st.markdown(f'<div class="user-header">{L[greet_key]}, {row_g["AD SOYAD"]} 👷‍♂️</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-sub">{row_g["GÖREVİ"]} | {row_g["FİORİ NO"]}</div>', unsafe_allow_html=True)
    
    # BÜYÜTÜLMÜŞ VARDİYA BİLGİSİ
    if current_hour_decimal < end_hour:
        st.markdown(f'<div class="shift-container"><div class="shift-bar"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="paydos-label">🏁 Paydos Saati: {end_hour}:00</div>', unsafe_allow_html=True)
    else:
        st.success(f"✅ {L['shift_end']}")

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(L['paid_days'], row_g.get("Personele Ödenecek Gün", 0))
    with c2: st.metric(L['phys_days'], row_g.get("Fiziki Çalışılan Gün", 0))
    with c3: st.metric(L['total_over'], row_s.get("TOPLAM", 0))

    st.write("---")

    # Legend ve Takvim
    st.write(f"### ℹ️ {L['legend']}")
    cols_leg = st.columns(4)
    for idx, (k, v) in enumerate(STATUS_MAP.items()):
        with cols_leg[idx % 4]:
            if st.button(k, help=v, use_container_width=True):
                st.session_state['filter_status'] = None if st.session_state['filter_status'] == k else k

    t_cols = [c for c in df.columns if '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]
    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        with st.expander(f"📁 {L['week']} {h_no} {L['week_suffix']}"):
            st.markdown('<div class="day-grid">', unsafe_allow_html=True)
            for t_col in hafta:
                durum = str(row_g[t_col]).strip().upper()
                mesai = str(row_s[t_col]).strip()
                high_cls = "highlight-active" if st.session_state['filter_status'] == durum else ""
                try:
                    dt = pd.to_datetime(t_col, dayfirst=True)
                    day_label = f"{dt.day:02d}/{AYLAR_TR[dt.month] if st.session_state['lang']=='TR' else dt.strftime('%b').upper()}"
                    g_adi = GUNLER_TR[dt.weekday()][:3]
                except: day_label = str(t_col); g_adi = ""

                cls = "status-n" if "N" in durum else "status-htc" if "HT" in durum else "status-hc" if "HÇ" in durum else "status-b"
                mesai_html = f'<div style="background:#facc15; color:black; font-size:10px; padding:2px; border-radius:4px; margin-top:4px; font-weight:bold;">+{mesai}S</div>' if mesai not in ["0", "0.0", "nan", ""] else ""
                st.markdown(f'<div class="day-item {cls} {high_cls}">{durum}<br><span style="font-size:10px; opacity:0.9;">{g_adi} {day_label}</span>{mesai_html}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # İtiraz Paneli
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader(f"🚨 {L['appeal_head']}")
    konu = st.selectbox(L['lang'], ["...", "Gün/Puantaj", "Mesai", "Diğer"], label_visibility="collapsed")
    notunuz = st.text_area(L['note'])
    if st.button(L['send']):
        msg = f"İTİRAZ: {row_g['AD SOYAD']}\nKonu: {konu}\nNot: {notunuz}"
        st.link_button("GÖNDER", f"https://wa.me/905435314160?text={urllib.parse.quote(msg)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="text-align:center; font-size:11px; color:rgba(255,255,255,0.5); margin-top:25px;">{L["audit"]}<br>{L["update"]}: {now_tr.strftime("%d.%m.%Y %H:%M")}</div>', unsafe_allow_html=True)

st.markdown('<div class="mert-signature">POWERED BY Mert DÜZCÜK</div>', unsafe_allow_html=True)
