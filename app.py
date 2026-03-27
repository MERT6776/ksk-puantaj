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
        "welcome_evening": "İyi Akşamlar", "welcome_night": "İyi Geceler", "sicil": "KULLANICI ADI",
        "pass": "DOĞUM YILI", "login": "GİRİŞ YAP", "paid_days": "Ödenecek Gün",
        "phys_days": "Fiziki Gün", "total_over": "TOPLAM MESAİ SAATİ", "week": "HAFTA",
        "week_suffix": "PUANTAJ DURUM TAKVİMİ", "appeal_head": "İtiraz Merkezi",
        "send": "ALİCAN BAYAT'A GÖNDER", "lang": "Dil Seçimi", "note": "Ek Notunuz",
        "legend": "KISALTMALAR VE ANLAMLARI", "shift_end": "Mesai Tamamlandı",
        "theme": "Tema Seçimi", "month_title": "PUANTAJI", "overtime": "Saat Mesai"
    },
    "EN": {
        "title": "FILYOS PHASE-2", "welcome_morning": "Good Morning", "welcome_day": "Good Day",
        "welcome_evening": "Good Evening", "welcome_night": "Good Night", "sicil": "USERNAME",
        "pass": "BIRTH YEAR", "login": "LOGIN", "paid_days": "Paid Days",
        "phys_days": "Physical Days", "total_over": "TOTAL OVERTIME HOURS", "week": "WEEK",
        "week_suffix": "STATUS TABLE", "appeal_head": "Appeal Center",
        "send": "SEND", "lang": "Language", "note": "Note",
        "legend": "LEGEND", "shift_end": "Shift Completed",
        "theme": "Theme", "month_title": "PAYROLL", "overtime": "Hrs Overtime"
    },
    "UZ": {
        "title": "FİLYOS FAZ-2", "welcome_morning": "Xayrli tong", "welcome_day": "Xayrli kun",
        "welcome_evening": "Xayrli kech", "welcome_night": "Xayrli tun", "sicil": "FOYDALANUVCHI NOMI",
        "pass": "TUG'ILGAN YILI", "login": "KIRISH", "paid_days": "To'lanadigan Kun",
        "phys_days": "Ishlagan Kun", "total_over": "UMUMIY ISH SOATI", "week": "HAFTA",
        "week_suffix": "PUANTAJ JADVALI", "appeal_head": "E'tiroz Markazi",
        "send": "YUBORISH", "lang": "Til", "note": "Eslatma",
        "legend": "QISQARTMALAR", "shift_end": "Ish yakunlandi",
        "theme": "Mavzu", "month_title": "PUANTAJI", "overtime": "Soat Ish"
    }
}

STATUS_MAP = {
    "HTÇ": "Şirkete Fazladan Pazar Çalışması", "HÇ": "Kendine Fazladan Pazar Çalışması",
    "HT": "Hafta Tatili", "Üİ": "Personel Çalışmadı", "N": "Normal Çalışma",
    "B": "Bayram Tatili", "BÇ": "Bayramda Çalışma"
}

AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN", 7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
GUNLER_TR = ["PZT", "SALI", "ÇAR", "PER", "CUMA", "CMT", "PAZ"]

THEMES = {
    "Kurumsal Koyu": {
        "bg_grad_1": "#111827", "bg_grad_2": "#1e293b", "card_bg": "rgba(255,255,255,0.08)",
        "card_border": "rgba(255,255,255,0.16)", "text_main": "#ffffff", "text_soft": "#cbd5e1",
        "accent": "#38bdf8", "accent_2": "#f59e0b", "clock": "#ffd700", "input_bg": "rgba(255,255,255,0.06)",
        "input_text": "#ffffff", "btn_text": "#ffffff", "shadow": "0 10px 30px rgba(0,0,0,0.30)", "overlay": "rgba(2, 6, 23, 0.82)"
    },
    "Açık Kurumsal": {
        "bg_grad_1": "#f8fafc", "bg_grad_2": "#e2e8f0", "card_bg": "rgba(255,255,255,0.92)",
        "card_border": "rgba(15,23,42,0.15)", "text_main": "#0f172a", "text_soft": "#334155",
        "accent": "#1d4ed8", "accent_2": "#b45309", "clock": "#0f172a", "input_bg": "#ffffff",
        "input_text": "#0f172a", "btn_text": "#ffffff", "shadow": "0 10px 25px rgba(15,23,42,0.08)", "overlay": "rgba(255,255,255,0.60)"
    },
    "Premium Cam": {
        "bg_grad_1": "#0f172a", "bg_grad_2": "#1e1b4b", "card_bg": "rgba(255,255,255,0.10)",
        "card_border": "rgba(255,255,255,0.18)", "text_main": "#ffffff", "text_soft": "#dbeafe",
        "accent": "#60a5fa", "accent_2": "#fbbf24", "clock": "#60a5fa", "input_bg": "rgba(255,255,255,0.08)",
        "input_text": "#ffffff", "btn_text": "#ffffff", "shadow": "0 15px 40px rgba(0,0,0,0.35)", "overlay": "rgba(3, 7, 18, 0.72)"
    }
}

if 'lang' not in st.session_state: st.session_state['lang'] = "TR"
if 'theme' not in st.session_state: st.session_state['theme'] = "Kurumsal Koyu"
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False

L = LANGS[st.session_state['lang']]
T = THEMES[st.session_state['theme']]

now_tr = datetime.utcnow() + timedelta(hours=3)
clock_init = now_tr.strftime("%d.%m.%Y | %H:%M:%S")
start_hour, end_hour = 8, 18
curr_decimal = now_tr.hour + now_tr.minute / 60
shift_pct = max(0, min(100, (curr_decimal - start_hour) / (end_hour - start_hour) * 100))
ay_baslik = f"{AYLAR_TR[now_tr.month]} {now_tr.year} {L['month_title']}"

# 3. CSS / TEMA
st.markdown(f"""
    <style>
    .stApp {{ background: linear-gradient(135deg, {T["bg_grad_1"]} 0%, {T["bg_grad_2"]} 100%) !important; color: {T["text_main"]} !important; }}
    body {{ background: linear-gradient(135deg, {T["bg_grad_1"]} 0%, {T["bg_grad_2"]} 100%) !important; background-attachment: fixed !important; }}
    [data-testid="stAppViewContainer"]::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background: {T["overlay"]}; z-index: -1; backdrop-filter: blur(3px);
    }}
    .block-container {{ padding-top: 1rem !important; padding-bottom: 2rem !important; max-width: 920px !important; }}
    
    #live-clock {{ 
        text-align: right; color: {T["clock"]}; font-family: 'Courier New', monospace; 
        font-weight: 900; font-size: 22px; letter-spacing: 1.5px; padding-bottom: 15px; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.2); 
    }}
    
    .portal-title {{ text-align: center; color: {T["text_main"]}; letter-spacing: 3px; font-weight: 900; margin-bottom: 12px; }}
    .month-title {{ text-align: center; color: {T["accent"]}; font-size: 18px; font-weight: 800; margin-top: -8px; margin-bottom: 18px; letter-spacing: 1px; }}
    .user-header {{ font-size: 32px; font-weight: 900; color: {T["text_main"]}; margin-bottom: 6px; }}
    .user-sub {{ font-size: 18px; font-weight: 700; color: {T["text_soft"]}; margin-bottom: 18px; }}
    .paydos-label {{ font-size: 18px; font-weight: 800; color: {T["accent_2"]}; margin-top: 8px; text-transform: uppercase; }}
    
    .glass-card {{ background: {T["card_bg"]}; backdrop-filter: blur(20px); border-radius: 18px; border: 1px solid {T["card_border"]}; padding: 20px; margin-bottom: 20px; color: {T["text_main"]}; box-shadow: {T["shadow"]}; }}
    .shift-container {{ width: 100%; background: rgba(128,128,128,0.2); border-radius: 999px; height: 18px; margin: 14px 0; border: 1px solid {T["card_border"]}; overflow: hidden; }}
    .shift-bar {{ width: {shift_pct}%; height: 100%; background: linear-gradient(90deg, {T["accent"]}, {T["accent_2"]}); box-shadow: 0 0 20px {T["accent"]}; border-radius: 999px; }}
    
    div[data-testid="metric-container"] {{ background: {T["card_bg"]}; border: 1px solid {T["card_border"]}; border-radius: 16px; padding: 12px; box-shadow: {T["shadow"]}; }}
    [data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{ color: {T["text_main"]} !important; }}
    
    .stExpander {{ background: {T["card_bg"]} !important; border: 1px solid {T["card_border"]} !important; border-radius: 14px !important; margin-bottom: 12px !important; box-shadow: {T["shadow"]}; }}
    summary {{ color: {T["text_main"]} !important; font-weight: 800 !important; }}
    
    .day-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(92px, 1fr)); gap: 12px; margin-top: 10px; }}
    .day-item {{ text-align: center; font-weight: 900; border-radius: 14px; padding: 12px 6px; color: white !important; min-height: 95px; box-shadow: 0 8px 16px rgba(0,0,0,0.18); transition: transform 0.15s ease, box-shadow 0.15s ease; }}
    .day-item:hover {{ transform: translateY(-2px); box-shadow: 0 12px 24px rgba(0,0,0,0.22); }}
    
    .status-n {{ background: linear-gradient(135deg, #15803d, #166534); border: 1px solid #22c55e; }}
    .status-htc {{ background: linear-gradient(135deg, #b45309, #92400e); border: 1px solid #fbbf24; }}
    .status-hc {{ background: linear-gradient(135deg, #1d4ed8, #1e40af); border: 1px solid #60a5fa; }}
    .status-ht {{ background: linear-gradient(135deg, #312e81, #3730a3); border: 1px solid #818cf8; }}
    .status-b {{ background: linear-gradient(135deg, #991b1b, #7f1d1d); border: 1px solid #f87171; }}
    .status-bc {{ background: linear-gradient(135deg, #c2410c, #ea580c); border: 1px solid #fb923c; }}
    .status-ui {{ background: linear-gradient(135deg, #4b5563, #374151); border: 1px solid #9ca3af; }}
    .status-default {{ background: linear-gradient(135deg, #334155, #1e293b); border: 1px solid #64748b; }}
    
    .stTextInput > div > div > input, .stTextArea textarea, .stSelectbox > div > div {{ background: {T["input_bg"]} !important; color: {T["input_text"]} !important; border: 1px solid {T["card_border"]} !important; border-radius: 12px !important; }}
    .stTextInput label, .stTextArea label, .stSelectbox label {{ color: {T["text_soft"]} !important; font-weight: 700 !important; }}
    .stButton > button, .stLinkButton > a {{ width: 100%; border-radius: 12px !important; border: none !important; font-weight: 800 !important; min-height: 46px; background: linear-gradient(90deg, {T["accent"]}, {T["accent_2"]}) !important; color: #ffffff !important; box-shadow: 0 10px 22px rgba(0,0,0,0.18); }}
    
    .mert-signature {{ position: fixed; bottom: 12px; left: 15px; font-size: 13px; font-weight: 900; color: {T["text_soft"]}; opacity: 0.8; letter-spacing: 2px; z-index: 1000; }}
    @media (max-width: 600px) {{ .user-header {{ font-size: 25px; }} #live-clock {{ font-size: 16px; }} .day-grid {{ grid-template-columns: repeat(auto-fill, minmax(82px, 1fr)); gap: 10px; }} .day-item {{ min-height: 88px; font-size: 13px; }} }}
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
    </script>
""", unsafe_allow_html=True)

# 4. VERİ MOTORU VE ÇELİK TARİH ÇÖZÜCÜ
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("veri.xlsx")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except:
        return None

def filyos_date_engine(t_col):
    """Exceldeki metni ZORLA Gün-Ay-Yıl olarak parçalar. Şaşmaz."""
    try:
        clean_str = str(t_col).split(' ')[0]
        if '.' in clean_str:
            parts = clean_str.split('.')
            if len(parts) >= 2:
                gun = int(parts[0])
                ay_num = int(parts[1])
                yil = int(parts[2]) if len(parts) >= 3 else 2026
                dt_obj = datetime(yil, ay_num, gun)
                return dt_obj, f"{str(gun).zfill(2)} {AYLAR_TR[ay_num]}", GUNLER_TR[dt_obj.weekday()]
        
        dt_obj = pd.to_datetime(clean_str, dayfirst=True)
        return dt_obj, f"{str(dt_obj.day).zfill(2)} {AYLAR_TR[dt_obj.month]}", GUNLER_TR[dt_obj.weekday()]
    except:
        return None, str(t_col), ""

def get_status_class(durum):
    durum = str(durum).strip().upper()
    if durum == "N": return "status-n"
    elif durum == "HTÇ": return "status-htc"
    elif durum == "HÇ": return "status-hc"
    elif durum == "HT": return "status-ht"
    elif durum == "BÇ": return "status-bc"
    elif durum == "B": return "status-b"
    elif durum == "Üİ": return "status-ui"
    else: return "status-default"

df = load_data()

# --- LOGIN EKRANI ---
if not st.session_state['logged_in']:
    st.markdown(f"<h1 class='portal-title'>{L['title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='month-title'>{ay_baslik}</div>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    secilen_dil = st.selectbox(L['lang'], ["TR", "EN", "UZ"], index=["TR", "EN", "UZ"].index(st.session_state['lang']))
    st.session_state['lang'] = secilen_dil
    L = LANGS[st.session_state['lang']]

    secilen_tema = st.selectbox(L['theme'], list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state['theme']))
    st.session_state['theme'] = secilen_tema

    sicil = st.text_input(L['sicil'])
    sifre = st.text_input(L['pass'], type="password")

    if st.button(L['login']):
        if df is not None:
            res = df[(df['FİORİ NO'].astype(str).str.strip() == str(sicil).strip()) & (df['DOĞUM YILI'].astype(str).str.strip() == str(sifre).strip())]
            if not res.empty:
                st.session_state['user_data'] = res
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ Bilgiler Hatalı!")
    st.markdown('</div>', unsafe_allow_html=True)

# --- ANA EKRAN ---
else:
    u_df = st.session_state['user_data']

    ust1, ust2 = st.columns([1, 1])
    with ust1:
        yeni_dil = st.selectbox(L['lang'], ["TR", "EN", "UZ"], index=["TR", "EN", "UZ"].index(st.session_state['lang']), key="top_lang")
        if yeni_dil != st.session_state['lang']: st.session_state['lang'] = yeni_dil; st.rerun()
    with ust2:
        yeni_tema = st.selectbox(L['theme'], list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state['theme']), key="top_theme")
        if yeni_tema != st.session_state['theme']: st.session_state['theme'] = yeni_tema; st.rerun()

    L = LANGS[st.session_state['lang']]
    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    hour_greet = now_tr.hour
    greet_txt = L["welcome_morning"] if 5 <= hour_greet < 12 else L["welcome_day"] if 12 <= hour_greet < 18 else L["welcome_evening"] if 18 <= hour_greet < 23 else L["welcome_night"]

    st.markdown(f'<div class="user-header">{greet_txt}, {row_g["AD SOYAD"]} 👷‍♂️</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-sub">{row_g["GÖREVİ"]} | {row_g["FİORİ NO"]}</div>', unsafe_allow_html=True)
    st.markdown(f"<div class='month-title'>{ay_baslik}</div>", unsafe_allow_html=True)

    if curr_decimal < end_hour:
        st.markdown('<div class="shift-container"><div class="shift-bar"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="paydos-label">🏁 Paydos Saati: {end_hour}:00</div>', unsafe_allow_html=True)
    else:
        st.success(f"✅ {L['shift_end']}")

    # ========================================================
    # 🚀 %100 ADALET MOTORU: SADECE GÖRÜNEN MESAİLERİ TOPLA!
    # Excel'in TOPLAM sütununa körüz, tamamen sildim! 
    # ========================================================
    t_cols = [c for c in df.columns if '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]
    calc_total = 0
    
    for t_col in t_cols:
        dt_obj, _, _ = filyos_date_engine(t_col)
        # Şubat ayının mesaileri EKRANDA GİZLİ olduğu için, HESABA DA KATILMIYOR!
        is_february = (dt_obj is not None and dt_obj.month == 2)
        m_val = str(row_s.get(t_col, "")).strip()
        
        if not is_february and m_val not in ["", "0", "0.0", "nan", "None"]:
            try:
                calc_total += float(m_val.replace(',', '.'))
            except:
                pass
                
    total_overtime_val = calc_total
    toplam_mesai_gosterim = f"{int(total_overtime_val)}" if total_overtime_val % 1 == 0 else f"{total_overtime_val}"

    st.write("")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric(L['paid_days'], row_g.get("Personele Ödenecek Gün", 0))
    with c2: st.metric(L['phys_days'], row_g.get("Fiziki Çalışılan Gün", 0))
    with c3: st.metric(L['total_over'], toplam_mesai_gosterim)

    st.write("---")

    with st.expander(f"ℹ️ {L['legend']}"):
        for k, v in STATUS_MAP.items(): st.markdown(f"**{k}:** {v}")

    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        with st.expander(f"📁 {L['week']} {h_no} {L['week_suffix']}"):
            st.markdown('<div class="day-grid">', unsafe_allow_html=True)
            for t_col in hafta:
                durum = str(row_g.get(t_col, "")).strip().upper()
                mesai = str(row_s.get(t_col, "")).strip()

                dt_obj, day_label, g_adi = filyos_date_engine(t_col)
                cls = get_status_class(durum)

                # ŞUBAT AYI MESAI GIZLEME
                is_february = (dt_obj is not None and dt_obj.month == 2)
                mesai_html = ""
                if not is_february and mesai not in ["0", "0.0", "nan", "", "None"]:
                    mesai_html = f'<div style="background:#facc15; color:black; font-size:11px; padding:2px; border-radius:4px; margin-top:4px; font-weight:bold;">⚡ {mesai} {L["overtime"]}</div>'

                st.markdown(f'''
                    <div class="day-item {cls}">
                        {durum}<br>
                        <span style="font-size:10px; font-weight:800;">{day_label}</span><br>
                        <span style="font-size:9px; opacity:0.85;">{g_adi}</span>
                        {mesai_html}
                    </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader(f"🚨 {L['appeal_head']}")
    konu = st.selectbox("Konu", ["...", "Puantaj İtirazı", "Mesai İtirazı", "Diğer"], label_visibility="collapsed")
    notunuz = st.text_area(L['note'])
    if st.button(L['send']):
        msg = f"İTİRAZ: {row_g['AD SOYAD']}\nKonu: {konu}\nNot: {notunuz}"
        st.link_button("GÖNDER", f"https://wa.me/905435314160?text={urllib.parse.quote(msg)}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="mert-signature">POWERED BY Mert DÜZCÜK</div>', unsafe_allow_html=True)
