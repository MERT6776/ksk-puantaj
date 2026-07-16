import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# 1. SAYFA AYARLARI
# ------------------------------------------------------------------
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

# ------------------------------------------------------------------
# 2. DİL VE VERİ SÖZLÜĞÜ
# ------------------------------------------------------------------
LANGS = {
    "TR": {
        "title": "FİLYOS FAZ-2 İNSAN KAYNAKLARI PORTALI",
        "welcome_morning": "Günaydın", "welcome_day": "İyi Günler",
        "welcome_evening": "İyi Akşamlar", "welcome_night": "İyi Geceler",
        "sicil": "KULLANICI ADI", "pass": "DOĞUM YILI", "login": "GİRİŞ YAP",
        "paid_days": "Ödenecek Gün", "total_over": "TOPLAM MESAİ SAATİ",
        "week": "HAFTA", "week_suffix": "PUANTAJ DURUM TAKVİMİ",
        "appeal_head": "İtiraz Merkezi",
        "appeal_desc": "Puantaj veya mesai kayıtlarınızda bir eksiklik ya da hata olduğunu düşünüyorsanız, aşağıdaki formu doldurarak itirazınızı iletebilirsiniz.",
        "send": "ALİCAN BAYAT'A GÖNDER", "lang": "Dil Seçimi", "note": "Ek Notunuz",
        "legend": "KISALTMALAR VE ANLAMLARI", "shift_end": "Mesai Tamamlandı",
        "theme": "Tema Seçimi", "month_title": "PERSONEL PUANTAJI", "overtime": "SAAT",
        "logout": "ÇIKIŞ YAP", "sys_note_title": "SİSTEM BİLGİLENDİRMESİ",
        "update_info": "Sisteme 22 Mart tarihine kadar olan puantaj ve mesai kayıtları işlenmiştir. Takip eden günlerin veri girişi devam etmektedir.",
        "paydos": "Paydos Saati", "subject": "Konu", "err": "Bilgiler hatalı, tekrar deneyin.",
        "topic_opts": ["Seçiniz...", "Puantaj İtirazı", "Mesai İtirazı", "Diğer"]
    },
    "EN": {
        "title": "FILYOS PHASE-2 HR PORTAL",
        "welcome_morning": "Good Morning", "welcome_day": "Good Day",
        "welcome_evening": "Good Evening", "welcome_night": "Good Night",
        "sicil": "USERNAME", "pass": "BIRTH YEAR", "login": "LOGIN",
        "paid_days": "Paid Days", "total_over": "TOTAL OVERTIME HOURS",
        "week": "WEEK", "week_suffix": "STATUS TABLE",
        "appeal_head": "Appeal Center",
        "appeal_desc": "If you believe there is an error or omission in your payroll or overtime records, you can submit your objection by filling out the form below.",
        "send": "SEND", "lang": "Language", "note": "Note",
        "legend": "LEGEND", "shift_end": "Shift Completed",
        "theme": "Theme", "month_title": "PERSONNEL PAYROLL", "overtime": "HRS",
        "logout": "LOGOUT", "sys_note_title": "SYSTEM NOTICE",
        "update_info": "Payroll and overtime records up to March 22 have been entered into the system. Data entry for subsequent days is ongoing.",
        "paydos": "End of Shift", "subject": "Subject", "err": "Invalid credentials, please try again.",
        "topic_opts": ["Select...", "Payroll Objection", "Overtime Objection", "Other"]
    },
    "UZ": {
        "title": "FİLYOS FAZ-2 KADRLAR PORTALI",
        "welcome_morning": "Xayrli tong", "welcome_day": "Xayrli kun",
        "welcome_evening": "Xayrli kech", "welcome_night": "Xayrli tun",
        "sicil": "FOYDALANUVCHI NOMI", "pass": "TUG'ILGAN YILI", "login": "KIRISH",
        "paid_days": "To'lanadigan Kun", "total_over": "UMUMIY ISH SOATI",
        "week": "HAFTA", "week_suffix": "PUANTAJ JADVALI",
        "appeal_head": "E'tiroz Markazi",
        "appeal_desc": "Ish vaqti yoki qo'shimcha soatlar yozuvlarida xatolik bor deb hisoblasangiz, quyidagi shaklni to'ldirib e'tirozingizni yuborishingiz mumkin.",
        "send": "YUBORISH", "lang": "Til", "note": "Eslatma",
        "legend": "QISQARTMALAR", "shift_end": "Ish yakunlandi",
        "theme": "Mavzu", "month_title": "XODIMLAR PUANTAJI", "overtime": "SOAT",
        "logout": "CHIQISH", "sys_note_title": "TIZIM MA'LUMOTI",
        "update_info": "Tizimga 22-martgacha bo'lgan ish vaqti va qo'shimcha soatlar kiritilgan. Keyingi kunlar uchun ma'lumotlarni kiritish davom etmoqda.",
        "paydos": "Ish tugashi", "subject": "Mavzu", "err": "Ma'lumot noto'g'ri, qayta urinib ko'ring.",
        "topic_opts": ["Tanlang...", "Puantaj e'tirozi", "Ish vaqti e'tirozi", "Boshqa"]
    }
}

STATUS_MAP = {
    "HTÇ": "Şirkete Fazladan Pazar Çalışması", "HÇ": "Kendine Fazladan Pazar Çalışması",
    "HT": "Hafta Tatili", "Üİ": "Personel Çalışmadı", "N": "Normal Çalışma",
    "B": "Bayram Tatili", "BÇ": "Bayramda Çalışma"
}

AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
GUNLER_TR = ["PZT", "SALI", "ÇAR", "PER", "CUMA", "CMT", "PAZ"]

THEMES = {
    "Kurumsal Koyu": {"bg_grad_1": "#0b1220", "bg_grad_2": "#1e293b", "card_bg": "rgba(255,255,255,0.07)",
        "card_border": "rgba(255,255,255,0.14)", "text_main": "#ffffff", "text_soft": "#cbd5e1",
        "accent": "#38bdf8", "accent_2": "#f59e0b", "clock": "#ffd700", "input_bg": "rgba(15,23,42,0.85)",
        "input_text": "#ffffff", "shadow": "0 12px 30px rgba(0,0,0,0.35)", "overlay": "rgba(2, 6, 23, 0.55)"},
    "Açık Kurumsal": {"bg_grad_1": "#f8fafc", "bg_grad_2": "#e2e8f0", "card_bg": "rgba(255,255,255,0.94)",
        "card_border": "rgba(15,23,42,0.12)", "text_main": "#0f172a", "text_soft": "#475569",
        "accent": "#1d4ed8", "accent_2": "#b45309", "clock": "#0f172a", "input_bg": "#ffffff",
        "input_text": "#0f172a", "shadow": "0 10px 25px rgba(15,23,42,0.08)", "overlay": "rgba(255,255,255,0.35)"},
    "Premium Cam": {"bg_grad_1": "#0f172a", "bg_grad_2": "#1e1b4b", "card_bg": "rgba(255,255,255,0.09)",
        "card_border": "rgba(255,255,255,0.16)", "text_main": "#ffffff", "text_soft": "#dbeafe",
        "accent": "#60a5fa", "accent_2": "#fbbf24", "clock": "#60a5fa", "input_bg": "rgba(15,23,42,0.85)",
        "input_text": "#ffffff", "shadow": "0 16px 40px rgba(0,0,0,0.40)", "overlay": "rgba(3, 7, 18, 0.50)"}
}

# ------------------------------------------------------------------
# OTURUM DURUMU
# ------------------------------------------------------------------
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

ay_baslik = f"KSK {AYLAR_TR[now_tr.month]} {now_tr.year} {L['month_title']}"

# ------------------------------------------------------------------
# 3. CSS / TEMA
# ------------------------------------------------------------------
st.markdown(f"""<style>
.stApp {{ background: linear-gradient(135deg, {T["bg_grad_1"]} 0%, {T["bg_grad_2"]} 100%) !important; color: {T["text_main"]} !important; }}
body {{ background: linear-gradient(135deg, {T["bg_grad_1"]} 0%, {T["bg_grad_2"]} 100%) !important; background-attachment: fixed !important; }}
[data-testid="stAppViewContainer"]::before {{ content: ""; position: fixed; inset: 0; background: {T["overlay"]}; z-index: -1; }}
.block-container {{ padding-top: 1.2rem !important; padding-bottom: 2.5rem !important; max-width: 900px !important; }}

#live-clock {{ text-align: right; color: {T["clock"]}; font-family: 'Courier New', monospace;
    font-weight: 900; font-size: 21px; letter-spacing: 1.5px; padding-bottom: 14px; text-shadow: 0 2px 4px rgba(0,0,0,0.25); }}

.portal-title {{ text-align: center; color: {T["text_main"]}; letter-spacing: 1.5px; font-weight: 900; margin-bottom: 8px; font-size: 27px; line-height: 1.25; }}
.month-title {{ text-align: center; color: {T["accent"]}; font-size: 18px; font-weight: 900; margin: -2px 0 24px; letter-spacing: 1.5px; }}

.user-header {{ font-size: 30px; font-weight: 900; color: {T["text_main"]}; margin-bottom: 4px; line-height: 1.2; }}
.user-sub {{ font-size: 16px; font-weight: 700; color: {T["text_soft"]}; margin-bottom: 18px; text-transform: uppercase; letter-spacing: 0.5px; }}
.paydos-label {{ font-size: 16px; font-weight: 800; color: {T["accent_2"]}; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}

.glass-card {{ background: {T["card_bg"]}; border-radius: 18px; border: 1px solid {T["card_border"]};
    padding: 22px; margin-bottom: 20px; color: {T["text_main"]}; box-shadow: {T["shadow"]}; }}
.shift-container {{ width: 100%; background: rgba(128,128,128,0.22); border-radius: 999px; height: 16px; margin: 14px 0; border: 1px solid {T["card_border"]}; overflow: hidden; }}
.shift-bar {{ width: {shift_pct}%; height: 100%; background: linear-gradient(90deg, {T["accent"]}, {T["accent_2"]}); border-radius: 999px; transition: width .4s ease; }}

div[data-testid="stMetric"] {{ background: {T["card_bg"]}; border: 1px solid {T["card_border"]}; border-radius: 16px; padding: 14px 16px; box-shadow: {T["shadow"]}; }}
[data-testid="stMetricLabel"], [data-testid="stMetricValue"] {{ color: {T["text_main"]} !important; }}

.stExpander {{ background: {T["card_bg"]} !important; border: 1px solid {T["card_border"]} !important; border-radius: 14px !important; margin-bottom: 12px !important; box-shadow: {T["shadow"]}; }}
summary {{ color: {T["text_main"]} !important; font-weight: 800 !important; }}

.day-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(86px, 1fr)); gap: 10px; margin-top: 4px; }}
.day-item {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
    border-radius: 12px; color: #fff !important; padding: 7px 3px; min-height: 84px; box-shadow: 0 6px 12px rgba(0,0,0,0.2);
    transition: transform 0.15s ease; gap: 3px; }}
.day-item:hover {{ transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.28); }}
.durum-text {{ font-size: 22px; font-weight: 900; line-height: 1; text-shadow: 1px 1px 3px rgba(0,0,0,0.4); }}
.tarih-text {{ font-size: 13px; font-weight: 900; line-height: 1; letter-spacing: 0.3px; }}
.gun-text {{ font-size: 11px; font-weight: 800; line-height: 1; opacity: 0.9; }}
.mesai-badge {{ background: #facc15; color: #111; font-size: 12px; padding: 2px 8px; border-radius: 6px; margin-top: 3px; font-weight: 900; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }}

.status-n {{ background: linear-gradient(135deg, #15803d, #166534); border: 1px solid #22c55e; }}
.status-htc {{ background: linear-gradient(135deg, #b45309, #92400e); border: 1px solid #fbbf24; }}
.status-hc {{ background: linear-gradient(135deg, #1d4ed8, #1e40af); border: 1px solid #60a5fa; }}
.status-ht {{ background: linear-gradient(135deg, #312e81, #3730a3); border: 1px solid #818cf8; }}
.status-b {{ background: linear-gradient(135deg, #991b1b, #7f1d1d); border: 1px solid #f87171; }}
.status-bc {{ background: linear-gradient(135deg, #c2410c, #ea580c); border: 1px solid #fb923c; }}
.status-ui {{ background: linear-gradient(135deg, #4b5563, #374151); border: 1px solid #9ca3af; }}
.status-default {{ background: linear-gradient(135deg, #334155, #1e293b); border: 1px solid #64748b; }}

.stTextInput > div > div > input, .stTextArea textarea, .stSelectbox > div > div {{
    background-color: {T["input_bg"]} !important; color: {T["input_text"]} !important;
    border: 2px solid {T["card_border"]} !important; border-radius: 12px !important; }}
.stTextInput label, .stTextArea label, .stSelectbox label {{ color: {T["text_soft"]} !important; font-weight: 700 !important; letter-spacing: 0.5px; }}

.stButton > button, .stLinkButton > a {{ width: 100%; border-radius: 12px !important; border: none !important;
    font-weight: 900 !important; min-height: 46px; letter-spacing: 0.5px;
    background: linear-gradient(90deg, {T["accent"]}, {T["accent_2"]}) !important;
    color: #0f172a !important; text-shadow: none !important; box-shadow: 0 10px 22px rgba(0,0,0,0.18); }}

.info-banner {{ background-color: rgba(234, 179, 8, 0.14); border-left: 5px solid #eab308; padding: 15px 16px; border-radius: 10px; margin-bottom: 20px; }}
.info-title {{ margin: 0; color: #eab308; font-size: 15px; font-weight: 900; letter-spacing: 1px; }}
.info-text {{ margin: 6px 0 0 0; font-size: 14px; font-weight: 600; color: {T["text_main"]}; opacity: 0.9; }}

.mert-signature {{ position: fixed; bottom: 12px; left: 15px; font-size: 12px; font-weight: 900; color: {T["text_soft"]}; opacity: 0.75; letter-spacing: 2px; z-index: 1000; }}

@media (max-width: 600px) {{
    .portal-title {{ font-size: 21px; }} .month-title {{ font-size: 15px; }}
    .user-header {{ font-size: 24px; }} #live-clock {{ font-size: 16px; }}
    .day-grid {{ grid-template-columns: repeat(auto-fill, minmax(80px, 1fr)); gap: 8px; }}
    .day-item {{ min-height: 80px; padding: 5px 2px; }}
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
</script>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# 4. VERİ MOTORU
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("veri.xlsx")
        df.columns = [str(c).strip() if not isinstance(c, (datetime, pd.Timestamp)) else c for c in df.columns]
        return df
    except Exception:
        return None

def parse_date_super_safe(t_col, last_date=None):
    if isinstance(t_col, (datetime, pd.Timestamp)):
        return datetime(t_col.year, t_col.month, t_col.day)
    clean_str = str(t_col).split(' ')[0]
    dt_obj = None
    if '.' in clean_str:
        parts = clean_str.split('.')
        if len(parts) >= 2:
            try:
                yil = int(parts[2]) if len(parts) >= 3 else now_tr.year
                dt_obj = datetime(yil, int(parts[1]), int(parts[0]))
            except Exception:
                pass
    elif '-' in clean_str:
        parts = clean_str.split('-')
        if len(parts) == 3:
            try:
                if len(parts[0]) == 4:
                    dt_obj = datetime(int(parts[0]), int(parts[1]), int(parts[2]))
                else:
                    dt_obj = datetime(int(parts[2]), int(parts[1]), int(parts[0]))
            except Exception:
                pass
    if dt_obj is None:
        try:
            ts = pd.to_datetime(clean_str, dayfirst=True)
            dt_obj = datetime(ts.year, ts.month, ts.day)
        except Exception:
            pass
    return dt_obj

def get_status_class(durum):
    durum = str(durum).strip().upper()
    return {
        "N": "status-n", "HTÇ": "status-htc", "HÇ": "status-hc", "HT": "status-ht",
        "BÇ": "status-bc", "B": "status-b", "Üİ": "status-ui"
    }.get(durum, "status-default")

df = load_data()

# ------------------------------------------------------------------
# LOGIN EKRANI
# ------------------------------------------------------------------
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
            res = df[(df['FİORİ NO'].astype(str).str.strip() == str(sicil).strip()) &
                     (df['DOĞUM YILI'].astype(str).str.strip() == str(sifre).strip())]
            if not res.empty:
                st.session_state['user_data'] = res
                st.session_state['logged_in'] = True
                st.rerun()
            else:
                st.error("❌ " + L['err'])
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# ANA EKRAN
# ------------------------------------------------------------------
else:
    u_df = st.session_state['user_data']

    ust1, ust2, ust3 = st.columns([1, 1, 1])
    with ust1:
        yeni_dil = st.selectbox(L['lang'], ["TR", "EN", "UZ"], index=["TR", "EN", "UZ"].index(st.session_state['lang']), key="top_lang", label_visibility="collapsed")
        if yeni_dil != st.session_state['lang']:
            st.session_state['lang'] = yeni_dil; st.rerun()
    with ust2:
        yeni_tema = st.selectbox(L['theme'], list(THEMES.keys()), index=list(THEMES.keys()).index(st.session_state['theme']), key="top_theme", label_visibility="collapsed")
        if yeni_tema != st.session_state['theme']:
            st.session_state['theme'] = yeni_tema; st.rerun()
    with ust3:
        if st.button("🚪 " + L['logout'], use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['user_data'] = None
            st.rerun()

    L = LANGS[st.session_state['lang']]
    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    hour_greet = now_tr.hour
    greet_txt = (L["welcome_morning"] if 5 <= hour_greet < 12 else
                 L["welcome_day"] if 12 <= hour_greet < 18 else
                 L["welcome_evening"] if 18 <= hour_greet < 23 else L["welcome_night"])

    st.write("")
    st.markdown(f'<div class="user-header">{greet_txt}, {row_g["AD SOYAD"]} 👷‍♂️</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-sub">{row_g["GÖREVİ"]}</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div class="info-banner">
            <h4 class="info-title">📌 {L['sys_note_title']}</h4>
            <p class="info-text">{L['update_info']}</p>
        </div>
    """, unsafe_allow_html=True)

    if curr_decimal < end_hour:
        st.markdown('<div class="shift-container"><div class="shift-bar"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="paydos-label">🏁 {L["paydos"]}: {end_hour}:00</div>', unsafe_allow_html=True)
    else:
        st.success(f"✅ {L['shift_end']}")

    # Tarih sütunları
    t_cols = [c for c in df.columns if isinstance(c, (datetime, pd.Timestamp))
              or '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]

    date_mapping = {}
    last_date = None
    for t_col in t_cols:
        dt_obj = parse_date_super_safe(t_col, last_date)
        if dt_obj:
            last_date = dt_obj
        date_mapping[t_col] = dt_obj

    # Toplam mesai
    calc_total = 0
    for t_col in t_cols:
        m_val = str(row_s.get(t_col, "")).strip()
        if m_val not in ["", "0", "0.0", "nan", "None"]:
            try:
                calc_total += float(m_val.replace(',', '.'))
            except Exception:
                pass
    toplam_mesai_gosterim = f"{int(calc_total)}" if calc_total % 1 == 0 else f"{calc_total}"

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(L['paid_days'], row_g.get("Personele Ödenecek Gün", 0))
    with c2:
        st.metric(L['total_over'], toplam_mesai_gosterim)

    st.write("---")

    with st.expander(f"ℹ️ {L['legend']}"):
        for k, v in STATUS_MAP.items():
            st.markdown(f"**{k}:** {v}")

    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        with st.expander(f"📁 {L['week_suffix']} — {L['week']} {h_no}"):
            st.markdown('<div class="day-grid">', unsafe_allow_html=True)
            for t_col in hafta:
                durum = str(row_g.get(t_col, "")).strip().upper()
                mesai = str(row_s.get(t_col, "")).strip()
                dt_obj = date_mapping.get(t_col)
                if dt_obj:
                    day_label = f"{str(dt_obj.day).zfill(2)} {AYLAR_TR[dt_obj.month]}"
                    g_adi = GUNLER_TR[dt_obj.weekday()]
                else:
                    day_label = str(t_col).split(' ')[0]
                    g_adi = ""
                cls = get_status_class(durum)
                mesai_html = ""
                if mesai not in ["0", "0.0", "nan", "", "None"]:
                    mesai_html = f'<div class="mesai-badge">⚡ {mesai} {L["overtime"]}</div>'
                st.markdown(f'''
                    <div class="day-item {cls}">
                        <span class="durum-text">{durum}</span>
                        <span class="tarih-text">{day_label}</span>
                        <span class="gun-text">{g_adi}</span>
                        {mesai_html}
                    </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader(f"🚨 {L['appeal_head']}")
    st.markdown(f'<p style="font-size:14px; font-weight:600; color:{T["text_soft"]}; margin-bottom:15px;"><i>{L["appeal_desc"]}</i></p>', unsafe_allow_html=True)

    konu = st.selectbox(L['subject'], L['topic_opts'], label_visibility="collapsed")
    notunuz = st.text_area(L['note'])
    if st.button(L['send']):
        msg = f"İTİRAZ: {row_g['AD SOYAD']}\nKonu: {konu}\nNot: {notunuz}"
        st.link_button("GÖNDER ➡️", f"https://wa.me/905435314160?text={urllib.parse.quote(msg)}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="mert-signature">POWERED BY Mert DÜZCÜK</div>', unsafe_allow_html=True)
