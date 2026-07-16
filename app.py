import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# 1. SAYFA AYARLARI
# ------------------------------------------------------------------
st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

DOGRULAMA_KELIMESI = "RÖNESANS"   # doğrulama ekranında yazılması gereken kelime

# ------------------------------------------------------------------
# 2. DİL VE VERİ SÖZLÜĞÜ
# ------------------------------------------------------------------
LANGS = {
    "TR": {
        "title": "FİLYOS İNSAN KAYNAKLARI PORTALI",
        "welcome_morning": "Günaydın", "welcome_day": "İyi Günler",
        "welcome_evening": "İyi Akşamlar", "welcome_night": "İyi Geceler",
        "sicil": "KULLANICI ADI", "pass": "DOĞUM YILI", "login": "GİRİŞ YAP",
        "paid_days": "Ödenecek Gün", "total_over": "Toplam Mesai (sa)",
        "week": "HAFTA", "week_suffix": "PUANTAJ DURUM TAKVİMİ",
        "appeal_head": "İtiraz Merkezi",
        "appeal_desc": "Puantaj veya mesai kayıtlarınızda bir eksiklik ya da hata olduğunu düşünüyorsanız, aşağıdaki formu doldurarak itirazınızı iletebilirsiniz.",
        "send": "İTİRAZ ET", "lang": "Dil Seçimi", "note": "Ek Notunuz",
        "legend": "KISALTMALAR VE ANLAMLARI", "shift_end": "Mesai Tamamlandı",
        "theme": "Tema Seçimi", "month_title": "PERSONEL PUANTAJI", "overtime": "SAAT",
        "logout": "ÇIKIŞ YAP", "paydos": "Paydos Saati",
        "subject": "Konu", "err": "Bilgiler hatalı, tekrar deneyin.",
        "topic_opts": ["Seçiniz...", "Puantaj İtirazı", "Mesai İtirazı", "Diğer"],
        "summary": "AY ÖZETİ", "s_normal": "Normal Çalışma", "s_pazar": "Pazar Çalışması",
        "s_tatil": "Hafta Tatili", "s_bayram": "Bayram", "s_yok": "Çalışılmadı",
        "verify_title": "GÜVENLİK DOĞRULAMASI",
        "verify_desc": f"Sisteme giriş için aşağıdaki alana «{DOGRULAMA_KELIMESI}» yazınız.",
        "verify_field": "DOĞRULAMA", "verify_btn": "DOĞRULA VE GİR",
        "verify_err": f"Doğrulama başarısız. Lütfen «{DOGRULAMA_KELIMESI}» yazın.",
        "back": "← Geri",
        "disc_title": "BİLGİLENDİRME",
        "disc_text": "Sistemdeki veriler resmî veri değildir; güncellenebilir veri olup yalnızca bilgilendirme amaçlıdır."
    },
    "EN": {
        "title": "FILYOS HR PORTAL",
        "welcome_morning": "Good Morning", "welcome_day": "Good Day",
        "welcome_evening": "Good Evening", "welcome_night": "Good Night",
        "sicil": "USERNAME", "pass": "BIRTH YEAR", "login": "LOGIN",
        "paid_days": "Paid Days", "total_over": "Total Overtime (hrs)",
        "week": "WEEK", "week_suffix": "STATUS TABLE",
        "appeal_head": "Appeal Center",
        "appeal_desc": "If you believe there is an error or omission in your payroll or overtime records, you can submit your objection by filling out the form below.",
        "send": "SUBMIT APPEAL", "lang": "Language", "note": "Note",
        "legend": "LEGEND", "shift_end": "Shift Completed",
        "theme": "Theme", "month_title": "PERSONNEL PAYROLL", "overtime": "HRS",
        "logout": "LOGOUT", "paydos": "End of Shift",
        "subject": "Subject", "err": "Invalid credentials, please try again.",
        "topic_opts": ["Select...", "Payroll Objection", "Overtime Objection", "Other"],
        "summary": "MONTHLY SUMMARY", "s_normal": "Normal Work", "s_pazar": "Sunday Work",
        "s_tatil": "Weekend Off", "s_bayram": "Holiday", "s_yok": "Absent",
        "verify_title": "SECURITY CHECK",
        "verify_desc": f"Type «{DOGRULAMA_KELIMESI}» below to enter the system.",
        "verify_field": "VERIFICATION", "verify_btn": "VERIFY & ENTER",
        "verify_err": f"Verification failed. Please type «{DOGRULAMA_KELIMESI}».",
        "back": "← Back",
        "disc_title": "NOTICE",
        "disc_text": "The data shown here is not official; it may be updated and is provided for informational purposes only."
    },
    "UZ": {
        "title": "FILYOS KADRLAR PORTALI",
        "welcome_morning": "Xayrli tong", "welcome_day": "Xayrli kun",
        "welcome_evening": "Xayrli kech", "welcome_night": "Xayrli tun",
        "sicil": "FOYDALANUVCHI NOMI", "pass": "TUG'ILGAN YILI", "login": "KIRISH",
        "paid_days": "To'lanadigan Kun", "total_over": "Umumiy Ish (soat)",
        "week": "HAFTA", "week_suffix": "PUANTAJ JADVALI",
        "appeal_head": "E'tiroz Markazi",
        "appeal_desc": "Ish vaqti yoki qo'shimcha soatlar yozuvlarida xatolik bor deb hisoblasangiz, quyidagi shaklni to'ldirib e'tirozingizni yuborishingiz mumkin.",
        "send": "E'TIROZ YUBORISH", "lang": "Til", "note": "Eslatma",
        "legend": "QISQARTMALAR", "shift_end": "Ish yakunlandi",
        "theme": "Mavzu", "month_title": "XODIMLAR PUANTAJI", "overtime": "SOAT",
        "logout": "CHIQISH", "paydos": "Ish tugashi",
        "subject": "Mavzu", "err": "Ma'lumot noto'g'ri, qayta urinib ko'ring.",
        "topic_opts": ["Tanlang...", "Puantaj e'tirozi", "Ish vaqti e'tirozi", "Boshqa"],
        "summary": "OYLIK HISOBOT", "s_normal": "Oddiy Ish", "s_pazar": "Yakshanba Ishi",
        "s_tatil": "Dam Olish", "s_bayram": "Bayram", "s_yok": "Ishlamadi",
        "verify_title": "XAVFSIZLIK TEKSHIRUVI",
        "verify_desc": f"Tizimga kirish uchun quyidagi maydonga «{DOGRULAMA_KELIMESI}» deb yozing.",
        "verify_field": "TASDIQLASH", "verify_btn": "TASDIQLASH VA KIRISH",
        "verify_err": f"Tasdiqlash muvaffaqiyatsiz. «{DOGRULAMA_KELIMESI}» deb yozing.",
        "back": "← Orqaga",
        "disc_title": "MA'LUMOT",
        "disc_text": "Tizimdagi ma'lumotlar rasmiy emas; yangilanishi mumkin va faqat ma'lumot uchun beriladi."
    }
}

# KISALTMALAR (HTÇ = Pazar Çalışması, HÇ kaldırıldı)
STATUS_MAP = {
    "N": "Normal Çalışma",
    "HTÇ": "Pazar Çalışması",
    "HT": "Hafta Tatili",
    "B": "Bayram Tatili",
    "BÇ": "Bayramda Çalışma",
    "Üİ": "Personel Çalışmadı"
}

AYLAR_TR = {1: "OCAK", 2: "ŞUBAT", 3: "MART", 4: "NİSAN", 5: "MAYIS", 6: "HAZİRAN",
            7: "TEMMUZ", 8: "AĞUSTOS", 9: "EYLÜL", 10: "EKİM", 11: "KASIM", 12: "ARALIK"}
GUNLER_TR = ["PZT", "SALI", "ÇAR", "PER", "CUMA", "CMT", "PAZ"]

# ------------------------------------------------------------------
# RENK PALETLERİ
# ------------------------------------------------------------------
THEMES = {
    "Kurumsal Koyu": {"bg_grad_1": "#0a0f1e", "bg_grad_2": "#16213e", "card_bg": "rgba(255,255,255,0.06)",
        "card_border": "rgba(148,163,184,0.20)", "text_main": "#f1f5f9", "text_soft": "#94a3b8",
        "accent": "#2dd4bf", "accent_2": "#818cf8", "clock": "#5eead4", "input_bg": "rgba(15,23,42,0.75)",
        "input_text": "#f1f5f9", "shadow": "0 14px 34px rgba(0,0,0,0.38)", "overlay": "rgba(4, 8, 20, 0.55)"},
    "Açık Kurumsal": {"bg_grad_1": "#f1f5f9", "bg_grad_2": "#dbe4f0", "card_bg": "rgba(255,255,255,0.95)",
        "card_border": "rgba(15,23,42,0.10)", "text_main": "#0f172a", "text_soft": "#475569",
        "accent": "#0d9488", "accent_2": "#4f46e5", "clock": "#0f766e", "input_bg": "#ffffff",
        "input_text": "#0f172a", "shadow": "0 10px 26px rgba(15,23,42,0.10)", "overlay": "rgba(255,255,255,0.30)"},
    "Premium Mor": {"bg_grad_1": "#0f0c29", "bg_grad_2": "#302b63", "card_bg": "rgba(255,255,255,0.08)",
        "card_border": "rgba(216,180,254,0.22)", "text_main": "#faf5ff", "text_soft": "#ddd6fe",
        "accent": "#c084fc", "accent_2": "#f472b6", "clock": "#e9d5ff", "input_bg": "rgba(20,15,45,0.78)",
        "input_text": "#faf5ff", "shadow": "0 16px 42px rgba(0,0,0,0.45)", "overlay": "rgba(10, 6, 30, 0.50)"}
}

# ------------------------------------------------------------------
# OTURUM DURUMU
# ------------------------------------------------------------------
if 'lang' not in st.session_state: st.session_state['lang'] = "TR"
if 'theme' not in st.session_state: st.session_state['theme'] = "Kurumsal Koyu"
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'awaiting_verify' not in st.session_state: st.session_state['awaiting_verify'] = False
if 'pending_user' not in st.session_state: st.session_state['pending_user'] = None

L = LANGS[st.session_state['lang']]
T = THEMES[st.session_state['theme']]

now_tr = datetime.utcnow() + timedelta(hours=3)
clock_init = now_tr.strftime("%d.%m.%Y | %H:%M:%S")
start_hour, end_hour = 8, 18
curr_decimal = now_tr.hour + now_tr.minute / 60
shift_pct = max(0, min(100, (curr_decimal - start_hour) / (end_hour - start_hour) * 100))

ay_baslik = f"{AYLAR_TR[now_tr.month]} {now_tr.year} {L['month_title']}"

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
.verify-note {{ text-align: center; color: {T["text_soft"]}; font-size: 14px; font-weight: 600; margin-bottom: 18px; }}

.user-header {{ font-size: 30px; font-weight: 900; color: {T["text_main"]}; margin-bottom: 4px; line-height: 1.2; }}
.user-sub {{ font-size: 16px; font-weight: 700; color: {T["text_soft"]}; margin-bottom: 18px; text-transform: uppercase; letter-spacing: 0.5px; }}
.paydos-label {{ font-size: 16px; font-weight: 800; color: {T["accent_2"]}; margin-top: 6px; text-transform: uppercase; letter-spacing: 0.5px; }}

.glass-card {{ background: {T["card_bg"]}; border-radius: 18px; border: 1px solid {T["card_border"]};
    padding: 22px; margin-bottom: 20px; color: {T["text_main"]}; box-shadow: {T["shadow"]}; }}
.shift-container {{ width: 100%; background: rgba(128,128,128,0.22); border-radius: 999px; height: 16px; margin: 14px 0; border: 1px solid {T["card_border"]}; overflow: hidden; }}
.shift-bar {{ width: {shift_pct}%; height: 100%; background: linear-gradient(90deg, {T["accent"]}, {T["accent_2"]}); border-radius: 999px; transition: width .4s ease; }}

/* BİLGİLENDİRME KUTUSU */
.info-banner {{ background-color: {T["card_bg"]}; border-left: 5px solid {T["accent"]}; padding: 15px 16px; border-radius: 10px; margin-bottom: 20px; box-shadow: {T["shadow"]}; }}
.info-title {{ margin: 0; color: {T["accent"]}; font-size: 14px; font-weight: 900; letter-spacing: 1px; }}
.info-text {{ margin: 6px 0 0 0; font-size: 13.5px; font-weight: 600; color: {T["text_main"]}; opacity: 0.92; }}

/* AY ÖZETİ KARTI */
.ozet-card {{ background: {T["card_bg"]}; border: 1px solid {T["card_border"]}; border-radius: 18px; padding: 22px; margin-bottom: 20px; box-shadow: {T["shadow"]}; }}
.ozet-head {{ display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 900; letter-spacing: 1.5px; color: {T["accent"]}; text-transform: uppercase; margin-bottom: 16px; }}
.ozet-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(92px, 1fr)); gap: 12px; }}
.ozet-tile {{ background: rgba(148,163,184,0.08); border: 1px solid {T["card_border"]}; border-radius: 14px; padding: 14px 8px; text-align: center; }}
.ozet-num {{ font-size: 26px; font-weight: 900; color: {T["text_main"]}; line-height: 1; }}
.ozet-num.hl1 {{ color: {T["accent"]}; }}
.ozet-num.hl2 {{ color: {T["accent_2"]}; }}
.ozet-lbl {{ font-size: 11px; font-weight: 700; color: {T["text_soft"]}; margin-top: 7px; text-transform: uppercase; letter-spacing: 0.4px; }}

.stExpander {{ background: {T["card_bg"]} !important; border: 1px solid {T["card_border"]} !important; border-radius: 14px !important; margin-bottom: 12px !important; box-shadow: {T["shadow"]}; }}
summary {{ color: {T["text_main"]} !important; font-weight: 800 !important; }}

.hafta-baslik {{ font-size: 12.5px; font-weight: 900; letter-spacing: 1px; color: {T["accent"]}; text-transform: uppercase; margin: 16px 0 7px; }}
.day-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 7px; margin-bottom: 4px; }}
.day-item {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center;
    border-radius: 11px; color: #fff !important; padding: 7px 3px; min-height: 74px; box-shadow: 0 5px 11px rgba(0,0,0,0.20);
    transition: transform 0.15s ease; gap: 3px; }}
.day-item:hover {{ transform: translateY(-2px); box-shadow: 0 9px 18px rgba(0,0,0,0.28); }}
.day-meta {{ display: flex; flex-direction: column; align-items: center; gap: 2px; }}
.durum-text {{ font-size: 20px; font-weight: 900; line-height: 1; text-shadow: 1px 1px 3px rgba(0,0,0,0.4); }}
.tarih-text {{ font-size: 12px; font-weight: 900; line-height: 1; letter-spacing: 0.2px; }}
.gun-text {{ font-size: 10.5px; font-weight: 800; line-height: 1; opacity: 0.9; }}
.mesai-badge {{ background: #facc15; color: #111; font-size: 11px; padding: 2px 7px; border-radius: 6px; margin-top: 2px; font-weight: 900; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }}

.status-n {{ background: linear-gradient(135deg, #0d9488, #0f766e); border: 1px solid #2dd4bf; }}
.status-htc {{ background: linear-gradient(135deg, #b45309, #92400e); border: 1px solid #fbbf24; }}
.status-ht {{ background: linear-gradient(135deg, #4338ca, #3730a3); border: 1px solid #818cf8; }}
.status-b {{ background: linear-gradient(135deg, #9f1239, #881337); border: 1px solid #fb7185; }}
.status-bc {{ background: linear-gradient(135deg, #c2410c, #ea580c); border: 1px solid #fb923c; }}
.status-ui {{ background: linear-gradient(135deg, #475569, #334155); border: 1px solid #94a3b8; }}
.status-default {{ background: linear-gradient(135deg, #334155, #1e293b); border: 1px solid #64748b; }}

.stTextInput > div > div > input, .stTextArea textarea, .stSelectbox > div > div {{
    background-color: {T["input_bg"]} !important; color: {T["input_text"]} !important;
    border: 2px solid {T["card_border"]} !important; border-radius: 12px !important; }}
.stTextInput label, .stTextArea label, .stSelectbox label {{ color: {T["text_soft"]} !important; font-weight: 700 !important; letter-spacing: 0.5px; }}

.stButton > button, .stLinkButton > a {{ width: 100%; border-radius: 12px !important; border: none !important;
    font-weight: 900 !important; min-height: 46px; letter-spacing: 0.5px;
    background: linear-gradient(90deg, {T["accent"]}, {T["accent_2"]}) !important;
    color: #0b1020 !important; text-shadow: none !important; box-shadow: 0 10px 22px rgba(0,0,0,0.20); }}

.mert-signature {{ position: fixed; bottom: 12px; left: 15px; font-size: 12px; font-weight: 900; color: {T["text_soft"]}; opacity: 0.75; letter-spacing: 2px; z-index: 1000; }}

@media (max-width: 600px) {{
    .portal-title {{ font-size: 21px; }} .month-title {{ font-size: 15px; }}
    .user-header {{ font-size: 24px; }} #live-clock {{ font-size: 16px; }}
    .day-grid {{ grid-template-columns: 1fr; gap: 7px; }}
    .day-item {{ flex-direction: row; justify-content: flex-start; align-items: center; min-height: 0; padding: 10px 14px; gap: 12px; text-align: left; }}
    .day-meta {{ flex-direction: row; align-items: baseline; gap: 8px; }}
    .durum-text {{ font-size: 18px; min-width: 32px; }}
    .mesai-badge {{ margin: 0 0 0 auto; }}
    .ozet-grid {{ grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 9px; }}
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
        "N": "status-n", "HTÇ": "status-htc", "HT": "status-ht",
        "BÇ": "status-bc", "B": "status-b", "Üİ": "status-ui"
    }.get(durum, "status-default")

def norm_key(v):
    s = str(v).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

df = load_data()

# ------------------------------------------------------------------
# EKRAN 1 — GİRİŞ (Kullanıcı Adı + Doğum Yılı)
# ------------------------------------------------------------------
if not st.session_state['logged_in'] and not st.session_state['awaiting_verify']:
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
            fiori_col = df['FİORİ NO'].map(norm_key)
            dogum_col = df['DOĞUM YILI'].map(norm_key)
            res = df[(fiori_col == norm_key(sicil)) & (dogum_col == norm_key(sifre))]
            if not res.empty:
                st.session_state['pending_user'] = res
                st.session_state['awaiting_verify'] = True
                st.rerun()
            else:
                st.error("❌ " + L['err'])
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# EKRAN 2 — DOĞRULAMA (RÖNESANS yazmadan giremez)
# ------------------------------------------------------------------
elif st.session_state['awaiting_verify'] and not st.session_state['logged_in']:
    st.markdown(f"<h1 class='portal-title'>🔐 {L['verify_title']}</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='verify-note'>{L['verify_desc']}</div>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    dogrulama = st.text_input(L['verify_field'], placeholder=DOGRULAMA_KELIMESI)

    if st.button(L['verify_btn']):
        if str(dogrulama).strip().upper() == DOGRULAMA_KELIMESI:
            st.session_state['user_data'] = st.session_state['pending_user']
            st.session_state['logged_in'] = True
            st.session_state['awaiting_verify'] = False
            st.session_state['pending_user'] = None
            st.rerun()
        else:
            st.error("🤖 " + L['verify_err'])

    if st.button(L['back']):
        st.session_state['awaiting_verify'] = False
        st.session_state['pending_user'] = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------
# EKRAN 3 — ANA PANEL
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
            st.session_state['awaiting_verify'] = False
            st.session_state['user_data'] = None
            st.session_state['pending_user'] = None
            st.rerun()

    L = LANGS[st.session_state['lang']]
    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    t_cols = [c for c in df.columns if isinstance(c, (datetime, pd.Timestamp))
              or '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]
    date_mapping = {}
    last_date = None
    for t_col in t_cols:
        dt_obj = parse_date_super_safe(t_col, last_date)
        if dt_obj:
            last_date = dt_obj
        date_mapping[t_col] = dt_obj

    cnt_unused = None
    calc_total = 0
    for t_col in t_cols:
        m_val = str(row_s.get(t_col, "")).strip()
        if m_val not in ["", "0", "0.0", "nan", "None"]:
            try:
                calc_total += float(m_val.replace(',', '.'))
            except Exception:
                pass
    toplam_mesai = f"{int(calc_total)}" if calc_total % 1 == 0 else f"{calc_total}"
    odenecek = row_g.get("Personele Ödenecek Gün", 0)
    try:
        odenecek = int(odenecek) if float(odenecek) % 1 == 0 else odenecek
    except Exception:
        pass

    hour_greet = now_tr.hour
    greet_txt = (L["welcome_morning"] if 5 <= hour_greet < 12 else
                 L["welcome_day"] if 12 <= hour_greet < 18 else
                 L["welcome_evening"] if 18 <= hour_greet < 23 else L["welcome_night"])

    st.write("")
    st.markdown(f'<div class="user-header">{greet_txt}, {row_g["AD SOYAD"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-sub">{row_g["GÖREVİ"]}</div>', unsafe_allow_html=True)

    # BİLGİLENDİRME KUTUSU
    st.markdown(f"""
        <div class="info-banner">
            <h4 class="info-title">ℹ️ {L['disc_title']}</h4>
            <p class="info-text">{L['disc_text']}</p>
        </div>
    """, unsafe_allow_html=True)

    # AY ÖZETİ KARTI
    st.markdown(f"""
        <div class="ozet-card">
            <div class="ozet-head">📊 {L['summary']}</div>
            <div class="ozet-grid">
                <div class="ozet-tile"><div class="ozet-num hl1">{odenecek}</div><div class="ozet-lbl">{L['paid_days']}</div></div>
                <div class="ozet-tile"><div class="ozet-num hl2">{toplam_mesai}</div><div class="ozet-lbl">{L['total_over']}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if curr_decimal < end_hour:
        st.markdown('<div class="shift-container"><div class="shift-bar"></div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="paydos-label">🏁 {L["paydos"]}: {end_hour}:00</div>', unsafe_allow_html=True)
    else:
        st.success(f"✅ {L['shift_end']}")

    st.write("---")

    with st.expander(f"ℹ️ {L['legend']}"):
        for k, v in STATUS_MAP.items():
            st.markdown(f"**{k}:** {v}")

    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        st.markdown(f'<div class="hafta-baslik">📅 {L["week"]} {h_no}</div>', unsafe_allow_html=True)
        grid_html = '<div class="day-grid">'
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
            grid_html += (
                f'<div class="day-item {cls}">'
                f'<span class="durum-text">{durum}</span>'
                f'<div class="day-meta"><span class="tarih-text">{day_label}</span>'
                f'<span class="gun-text">{g_adi}</span></div>'
                f'{mesai_html}</div>'
            )
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader(f"🚨 {L['appeal_head']}")
    st.markdown(f'<p style="font-size:14px; font-weight:600; color:{T["text_soft"]}; margin-bottom:15px;"><i>{L["appeal_desc"]}</i></p>', unsafe_allow_html=True)

    konu = st.selectbox(L['subject'], L['topic_opts'], label_visibility="collapsed")
    notunuz = st.text_area(L['note'])
    mail_adres = "ret-filyos2A-ik@ronesans.com"
    mail_konu = f"İtiraz - {row_g['AD SOYAD']} ({konu})"
    mail_govde = f"Ad Soyad: {row_g['AD SOYAD']}\nGörevi: {row_g['GÖREVİ']}\nKonu: {konu}\nNot: {notunuz}"
    mailto = f"mailto:{mail_adres}?subject={urllib.parse.quote(mail_konu)}&body={urllib.parse.quote(mail_govde)}"
    st.link_button("✉️ " + L['send'], mailto)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="mert-signature">POWERED BY Mert DÜZCÜK</div>', unsafe_allow_html=True)
