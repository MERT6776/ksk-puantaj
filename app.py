import streamlit as st
import pandas as pd
import urllib.parse
import random
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Filyos İK Portal", layout="centered", initial_sidebar_state="collapsed")

MAIL_ADRES = "ret-filyos2A-ik@ronesans.com"
LOGIN_LOCK_SEC = 180   # şifre 3 kez yanlış -> 3 dakika
VERIFY_LOCK_SEC = 30   # kod 3 kez yanlış -> 30 saniye
MAX_TRY = 3

LANG_NAMES = {"TR": "Türkçe", "EN": "English", "UZ": "O'zbek"}

# ------------------------------------------------------------------
# DİL SÖZLÜĞÜ
# ------------------------------------------------------------------
LANGS = {
    "TR": {
        "welcome_morning": "Günaydın", "welcome_day": "İyi Günler", "welcome_evening": "İyi Akşamlar", "welcome_night": "İyi Geceler",
        "sicil": "KULLANICI ADI", "pass": "DOĞUM YILI", "login": "GİRİŞ YAP",
        "paid_days": "Ödenecek Gün", "total_over": "Toplam Mesai (sa)",
        "week": "HAFTA", "week_suffix": "PUANTAJ DURUM TAKVİMİ",
        "appeal_head": "İtiraz Merkezi",
        "appeal_desc": "Puantaj veya mesai kayıtlarınızda bir eksiklik ya da hata olduğunu düşünüyorsanız, aşağıdaki formu doldurarak itirazınızı iletebilirsiniz.",
        "send": "İTİRAZ ET", "lang": "Dil Seçimi", "note": "Not", "legend": "KISALTMALAR VE ANLAMLARI",
        "theme": "Tema Seçimi", "month_title": "PERSONEL PUANTAJI", "overtime": "SAAT", "logout": "ÇIKIŞ YAP",
        "subject": "Konu", "err": "Bilgiler hatalı, tekrar deneyin.",
        "topic_opts": ["Seçiniz...", "Puantaj İtirazı", "Mesai İtirazı", "Diğer"],
        "summary": "AY ÖZETİ", "full_title": "AYLIK VERİ", "ss_warn": "Bu ekrandaki bilgiler kişiye özeldir. Ekran görüntüsü / kayıt almak yasaktır; alınan görüntüler kimliğinizle işaretlenir.",
        "verify_title": "GÜVENLİK DOĞRULAMASI", "verify_desc": "Robot olmadığınızı doğrulamak için aşağıdaki kodu giriniz.",
        "verify_field": "DOĞRULAMA KODU", "verify_btn": "DOĞRULA VE GİR", "verify_err": "Kod hatalı, lütfen tekrar deneyin.",
        "new_code": "🔄 Yeni Kod", "back": "← Geri",
        "disc_title": "BİLGİLENDİRME",
        "disc_text": "Sistemdeki veriler resmî veri değildir; güncellenebilir veri olup yalnızca bilgilendirme amaçlıdır.",
        "expand_all": "TÜMÜNÜ AÇ", "collapse_all": "TÜMÜNÜ KAPAT",
        "mail_ready": "Talebiniz hazırlandı. Aşağıdaki butona basınca mail uygulamanız açılır.", "open_mail": "MAİL UYGULAMASINI AÇ",
        "m_id": "Sicil No", "m_name": "Ad Soyad", "m_role": "Görevi", "m_prefix": "İtiraz",
        "login_locked": "Çok fazla hatalı giriş. Lütfen bekleyin.",
        "verify_locked": "Çok fazla hatalı kod. Lütfen bekleyin.",
        "forgot_title": "Şifremi Unuttum", "forgot_desc": "Kullanıcı adınızı girin; bilgilerinizle birlikte İK'ya şifre talebi maili oluşturulur.",
        "forgot_btn": "TALEP OLUŞTUR", "forgot_subject": "Şifre Talebi",
        "forgot_body": "Şifremi unuttum, yardımcı olabilir misiniz?"
    },
    "EN": {
        "welcome_morning": "Good Morning", "welcome_day": "Good Day", "welcome_evening": "Good Evening", "welcome_night": "Good Night",
        "sicil": "USERNAME", "pass": "BIRTH YEAR", "login": "LOGIN",
        "paid_days": "Paid Days", "total_over": "Total Overtime (hrs)",
        "week": "WEEK", "week_suffix": "STATUS TABLE",
        "appeal_head": "Appeal Center",
        "appeal_desc": "If you believe there is an error or omission in your payroll or overtime records, you can submit your objection by filling out the form below.",
        "send": "SUBMIT APPEAL", "lang": "Language", "note": "Note", "legend": "LEGEND",
        "theme": "Theme", "month_title": "PERSONNEL PAYROLL", "overtime": "HRS", "logout": "LOGOUT",
        "subject": "Subject", "err": "Invalid credentials, please try again.",
        "topic_opts": ["Select...", "Payroll Objection", "Overtime Objection", "Other"],
        "summary": "MONTHLY SUMMARY", "full_title": "MONTHLY DATA", "ss_warn": "The information here is personal. Screenshots and screen recording are prohibited; captures are marked with your identity.",
        "verify_title": "SECURITY CHECK", "verify_desc": "Enter the code below to verify you are not a robot.",
        "verify_field": "VERIFICATION CODE", "verify_btn": "VERIFY & ENTER", "verify_err": "Wrong code, please try again.",
        "new_code": "🔄 New Code", "back": "← Back",
        "disc_title": "NOTICE",
        "disc_text": "The data shown here is not official; it may be updated and is provided for informational purposes only.",
        "expand_all": "EXPAND ALL", "collapse_all": "COLLAPSE ALL",
        "mail_ready": "Your request is ready. Tap the button below to open your mail app.", "open_mail": "OPEN MAIL APP",
        "m_id": "Employee ID", "m_name": "Full Name", "m_role": "Position", "m_prefix": "Appeal",
        "login_locked": "Too many failed logins. Please wait.",
        "verify_locked": "Too many wrong codes. Please wait.",
        "forgot_title": "Forgot Password", "forgot_desc": "Enter your username; a password request email with your details will be prepared for HR.",
        "forgot_btn": "CREATE REQUEST", "forgot_subject": "Password Reset Request",
        "forgot_body": "I forgot my password, could you please help?"
    },
    "UZ": {
        "welcome_morning": "Xayrli tong", "welcome_day": "Xayrli kun", "welcome_evening": "Xayrli kech", "welcome_night": "Xayrli tun",
        "sicil": "FOYDALANUVCHI NOMI", "pass": "TUG'ILGAN YILI", "login": "KIRISH",
        "paid_days": "To'lanadigan Kun", "total_over": "Umumiy Ish (soat)",
        "week": "HAFTA", "week_suffix": "PUANTAJ JADVALI",
        "appeal_head": "E'tiroz Markazi",
        "appeal_desc": "Ish vaqti yoki qo'shimcha soatlar yozuvlarida xatolik bor deb hisoblasangiz, quyidagi shaklni to'ldirib e'tirozingizni yuborishingiz mumkin.",
        "send": "E'TIROZ YUBORISH", "lang": "Til", "note": "Eslatma", "legend": "QISQARTMALAR",
        "theme": "Mavzu", "month_title": "XODIMLAR PUANTAJI", "overtime": "SOAT", "logout": "CHIQISH",
        "subject": "Mavzu", "err": "Ma'lumot noto'g'ri, qayta urinib ko'ring.",
        "topic_opts": ["Tanlang...", "Puantaj e'tirozi", "Ish vaqti e'tirozi", "Boshqa"],
        "summary": "OYLIK HISOBOT", "full_title": "OYLIK MA'LUMOT", "ss_warn": "Bu ma'lumotlar shaxsiy. Skrinshot va ekran yozuvi taqiqlanadi; olingan tasvirlar shaxsingiz bilan belgilanadi.",
        "verify_title": "XAVFSIZLIK TEKSHIRUVI", "verify_desc": "Robot emasligingizni tasdiqlash uchun quyidagi kodni kiriting.",
        "verify_field": "TASDIQLASH KODI", "verify_btn": "TASDIQLASH VA KIRISH", "verify_err": "Kod noto'g'ri, qayta urinib ko'ring.",
        "new_code": "🔄 Yangi Kod", "back": "← Orqaga",
        "disc_title": "MA'LUMOT",
        "disc_text": "Tizimdagi ma'lumotlar rasmiy emas; yangilanishi mumkin va faqat ma'lumot uchun beriladi.",
        "expand_all": "HAMMASINI OCHISH", "collapse_all": "HAMMASINI YOPISH",
        "mail_ready": "So'rovingiz tayyor. Quyidagi tugmani bosing, pochta ilovangiz ochiladi.", "open_mail": "POCHTA ILOVASINI OCHISH",
        "m_id": "Tabel raqami", "m_name": "F.I.Sh", "m_role": "Lavozimi", "m_prefix": "E'tiroz",
        "login_locked": "Juda ko'p noto'g'ri kirish. Iltimos kuting.",
        "verify_locked": "Juda ko'p noto'g'ri kod. Iltimos kuting.",
        "forgot_title": "Parolni Unutdim", "forgot_desc": "Foydalanuvchi nomingizni kiriting; ma'lumotlaringiz bilan HR uchun parol so'rovi xati tayyorlanadi.",
        "forgot_btn": "SO'ROV YARATISH", "forgot_subject": "Parolni tiklash so'rovi",
        "forgot_body": "Parolimni unutdim, yordam bera olasizmi?"
    }
}

# KISALTMALAR — harfler AYNI kalır, sadece açıklama dile göre değişir
STATUS_MAP = {
    "N":   {"TR": "Normal Çalışma",     "EN": "Normal Work",     "UZ": "Oddiy Ish"},
    "HTÇ": {"TR": "Pazar Çalışması",    "EN": "Sunday Work",     "UZ": "Yakshanba Ishi"},
    "HT":  {"TR": "Hafta Tatili",       "EN": "Weekly Day Off",  "UZ": "Dam Olish Kuni"},
    "B":   {"TR": "Bayram Tatili",      "EN": "Public Holiday",  "UZ": "Bayram Dam Olishi"},
    "BÇ":  {"TR": "Bayramda Çalışma",   "EN": "Work on Holiday", "UZ": "Bayramda Ishlash"},
    "Üİ":  {"TR": "Personel Çalışmadı", "EN": "Did Not Work",    "UZ": "Ishlamadi"}
}

AYLAR = {
    "TR": {1:"OCAK",2:"ŞUBAT",3:"MART",4:"NİSAN",5:"MAYIS",6:"HAZİRAN",7:"TEMMUZ",8:"AĞUSTOS",9:"EYLÜL",10:"EKİM",11:"KASIM",12:"ARALIK"},
    "EN": {1:"JANUARY",2:"FEBRUARY",3:"MARCH",4:"APRIL",5:"MAY",6:"JUNE",7:"JULY",8:"AUGUST",9:"SEPTEMBER",10:"OCTOBER",11:"NOVEMBER",12:"DECEMBER"},
    "UZ": {1:"YANVAR",2:"FEVRAL",3:"MART",4:"APREL",5:"MAY",6:"IYUN",7:"IYUL",8:"AVGUST",9:"SENTABR",10:"OKTABR",11:"NOYABR",12:"DEKABR"}
}
GUNLER = {
    "TR": ["PZT","SALI","ÇAR","PER","CUMA","CMT","PAZ"],
    "EN": ["MON","TUE","WED","THU","FRI","SAT","SUN"],
    "UZ": ["DUSH","SESH","CHOR","PAY","JUMA","SHAN","YAKSH"]
}

GOREV_MAP = {
    "DESTEK HİZMETLER DİREKTÖRÜ": {"EN": "SUPPORT SERVICES DIRECTOR", "UZ": "YORDAMCHI XIZMATLAR DIREKTORI"},
    "İNSAN KAYNAKLARI ŞEFİ": {"EN": "HR CHIEF", "UZ": "KADRLAR BO'LIMI BOSHLIG'I"},
    "İNSAN KAYNAKLARI UZMANI": {"EN": "HR SPECIALIST", "UZ": "KADRLAR MUTAXASSISI"},
    "DEMİR USTASI": {"EN": "STEEL FIXER FOREMAN", "UZ": "ARMATURACHI USTA"},
    "İSKELE USTASI": {"EN": "SCAFFOLDING FOREMAN", "UZ": "LESA USTASI"},
    "KALIP USTASI": {"EN": "FORMWORK FOREMAN", "UZ": "QOLIP USTASI"}
}

def cevir_gorev(gorev, lang):
    g = str(gorev).strip()
    if lang == "TR":
        return g
    return GOREV_MAP.get(g.upper(), {}).get(lang, g)

# ------------------------------------------------------------------
# TEMALAR (iç anahtar sabit, isim dile göre)
# ------------------------------------------------------------------
THEMES = {
    "corporate_light": {"bg_grad_1": "#f1f5f9", "bg_grad_2": "#dbe4f0", "card_bg": "rgba(255,255,255,0.95)",
        "card_border": "rgba(15,23,42,0.10)", "text_main": "#0f172a", "text_soft": "#475569",
        "accent": "#0d9488", "accent_2": "#4f46e5", "clock": "#0f766e", "input_bg": "#ffffff",
        "input_text": "#0f172a", "shadow": "0 10px 26px rgba(15,23,42,0.10)", "overlay": "rgba(255,255,255,0.30)"}
}
THEME_NAMES = {
    "corporate_light": {"TR": "Açık Kurumsal", "EN": "Corporate Light", "UZ": "Yorug' Korporativ"}
}

# ------------------------------------------------------------------
# OTURUM DURUMU
# ------------------------------------------------------------------
def init_state():
    d = {'lang': "TR", 'theme': "corporate_light", 'logged_in': False, 'awaiting_verify': False,
         'pending_user': None, 'verify_code': "", 'week_open': {}, 'itiraz_ready': False, 'itiraz_mailto': "",
         'login_fails': 0, 'login_lock_until': 0.0, 'verify_fails': 0, 'verify_lock_until': 0.0,
         'forgot_ready': False, 'forgot_mailto': ""}
    for k, v in d.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

# Eski/geçersiz oturum değerlerine karşı koruma (KeyError önler)
if st.session_state['theme'] not in THEMES:
    st.session_state['theme'] = "corporate_light"
if st.session_state['lang'] not in LANGS:
    st.session_state['lang'] = "TR"

L = LANGS[st.session_state['lang']]
T = THEMES[st.session_state['theme']]
LNG = st.session_state['lang']

now_tr = datetime.utcnow() + timedelta(hours=3)
clock_init = now_tr.strftime("%d.%m.%Y | %H:%M:%S")
ay_baslik = f"{AYLAR[LNG][now_tr.month]} {now_tr.year} {L['month_title']}"

# ------------------------------------------------------------------
# CSS
# ------------------------------------------------------------------
st.markdown(f"""<style>
.stApp {{ background: linear-gradient(135deg, {T["bg_grad_1"]} 0%, {T["bg_grad_2"]} 100%) !important; color: {T["text_main"]} !important; }}
body {{ background: linear-gradient(135deg, {T["bg_grad_1"]} 0%, {T["bg_grad_2"]} 100%) !important; background-attachment: fixed !important; }}
[data-testid="stAppViewContainer"]::before {{ content: ""; position: fixed; inset: 0; background: {T["overlay"]}; z-index: -1; }}
.block-container {{ padding-top: 1.2rem !important; padding-bottom: 2.5rem !important; max-width: 900px !important; }}
#live-clock {{ text-align: right; color: {T["clock"]}; font-family: 'Courier New', monospace; font-weight: 900; font-size: 21px; letter-spacing: 1.5px; padding-bottom: 14px; text-shadow: 0 2px 4px rgba(0,0,0,0.25); }}
.month-title {{ text-align: center; color: {T["accent"]}; font-size: 18px; font-weight: 900; margin: 6px 0 24px; letter-spacing: 1.5px; }}
.portal-title {{ text-align: center; color: {T["text_main"]}; letter-spacing: 1.5px; font-weight: 900; margin-bottom: 8px; font-size: 26px; line-height: 1.25; }}
.verify-note {{ text-align: center; color: {T["text_soft"]}; font-size: 14px; font-weight: 600; margin-bottom: 16px; }}
.kod-box {{ text-align: center; font-family: 'Courier New', monospace; font-size: 40px; font-weight: 900; letter-spacing: 12px; color: {T["accent"]}; background: {T["card_bg"]}; border: 2px dashed {T["accent"]}; border-radius: 14px; padding: 16px 10px; margin-bottom: 16px; }}
.lock-wrap {{ text-align: center; background: {T["card_bg"]}; border: 1px solid {T["card_border"]}; border-radius: 18px; padding: 30px 20px; margin-top: 10px; box-shadow: {T["shadow"]}; }}
.lock-msg {{ font-size: 16px; font-weight: 800; color: {T["accent_2"]}; margin: 10px 0; }}
.lock-count {{ font-family: 'Courier New', monospace; font-size: 48px; font-weight: 900; color: {T["accent"]}; }}
.user-header {{ font-size: 30px; font-weight: 900; color: {T["text_main"]}; margin-bottom: 4px; line-height: 1.2; }}
.user-sub {{ font-size: 16px; font-weight: 700; color: {T["text_soft"]}; margin-bottom: 18px; text-transform: uppercase; letter-spacing: 0.5px; }}
.glass-card {{ background: {T["card_bg"]}; border-radius: 18px; border: 1px solid {T["card_border"]}; padding: 22px; margin-bottom: 20px; color: {T["text_main"]}; box-shadow: {T["shadow"]}; }}
.info-banner {{ background-color: {T["card_bg"]}; border-left: 5px solid {T["accent"]}; padding: 15px 16px; border-radius: 10px; margin-bottom: 20px; box-shadow: {T["shadow"]}; }}
.info-title {{ margin: 0; color: {T["accent"]}; font-size: 14px; font-weight: 900; letter-spacing: 1px; }}
.info-text {{ margin: 6px 0 0 0; font-size: 13.5px; font-weight: 600; color: {T["text_main"]}; opacity: 0.92; }}
.warn-banner {{ background-color: rgba(239,68,68,0.12); border-left: 5px solid #ef4444; padding: 12px 16px; border-radius: 10px; margin-bottom: 20px; font-size: 13px; font-weight: 700; color: {T["text_main"]}; }}
.ozet-card {{ background: {T["card_bg"]}; border: 1px solid {T["card_border"]}; border-radius: 18px; padding: 22px; margin-bottom: 20px; box-shadow: {T["shadow"]}; }}
.ozet-head {{ display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 900; letter-spacing: 1.5px; color: {T["accent"]}; text-transform: uppercase; margin-bottom: 16px; }}
.ozet-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
.ozet-tile {{ background: rgba(148,163,184,0.08); border: 1px solid {T["card_border"]}; border-radius: 14px; padding: 16px 8px; text-align: center; }}
.ozet-num {{ font-size: 30px; font-weight: 900; color: {T["text_main"]}; line-height: 1; }}
.ozet-num.hl1 {{ color: {T["accent"]}; }}
.ozet-num.hl2 {{ color: {T["accent_2"]}; }}
.ozet-lbl {{ font-size: 12px; font-weight: 700; color: {T["text_soft"]}; margin-top: 8px; text-transform: uppercase; letter-spacing: 0.4px; }}
.day-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 7px; margin-bottom: 12px; }}
.list-baslik {{ font-size: 13px; font-weight: 900; letter-spacing: 1px; color: {T["accent"]}; text-transform: uppercase; margin: 22px 0 8px; }}
.full-list {{ display: grid; grid-template-columns: 1fr; gap: 7px; margin-bottom: 16px; }}
.full-list .day-item {{ flex-direction: row; justify-content: flex-start; align-items: center; min-height: 0; padding: 10px 14px; gap: 12px; text-align: left; }}
.full-list .day-meta {{ flex-direction: row; align-items: baseline; gap: 8px; }}
.full-list .durum-text {{ font-size: 18px; min-width: 32px; }}
.full-list .mesai-badge {{ margin: 0 0 0 auto; }}
.day-item {{ display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border-radius: 11px; color: #fff !important; padding: 7px 3px; min-height: 74px; box-shadow: 0 5px 11px rgba(0,0,0,0.20); transition: transform 0.15s ease; gap: 3px; }}
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
.stTextInput > div > div > input, .stTextArea textarea, .stSelectbox > div > div {{ background-color: {T["input_bg"]} !important; color: {T["input_text"]} !important; border: 2px solid {T["card_border"]} !important; border-radius: 12px !important; }}
.stTextInput label, .stTextArea label, .stSelectbox label {{ color: {T["text_soft"]} !important; font-weight: 700 !important; letter-spacing: 0.5px; }}
/* Açık temada görünürlük garantisi */
[data-baseweb="select"] * {{ color: {T["input_text"]} !important; }}
[data-testid="stExpander"] summary {{ color: {T["text_main"]} !important; background: {T["card_bg"]} !important; }}
[data-testid="stExpander"] summary p, [data-testid="stExpander"] summary span {{ color: {T["text_main"]} !important; }}
[data-testid="stExpander"] summary svg {{ fill: {T["text_main"]} !important; }}
.stButton > button, .stLinkButton > a, .stForm [data-testid="stFormSubmitButton"] > button {{ width: 100%; border-radius: 12px !important; border: none !important; font-weight: 900 !important; min-height: 46px; letter-spacing: 0.5px; background: linear-gradient(90deg, {T["accent"]}, {T["accent_2"]}) !important; color: #0b1020 !important; text-shadow: none !important; box-shadow: 0 10px 22px rgba(0,0,0,0.20); }}
.stButton > button[kind="secondary"] {{ background: {T["card_bg"]} !important; color: {T["text_main"]} !important; border: 1px solid {T["card_border"]} !important; box-shadow: none !important; text-align: left; }}
.mert-signature {{ position: fixed; bottom: 12px; left: 15px; font-size: 12px; font-weight: 900; color: {T["text_soft"]}; opacity: 0.75; letter-spacing: 2px; z-index: 1000; }}
@media (max-width: 600px) {{
    .portal-title {{ font-size: 21px; }} .month-title {{ font-size: 15px; }} .user-header {{ font-size: 24px; }} #live-clock {{ font-size: 16px; }}
    .kod-box {{ font-size: 32px; letter-spacing: 8px; }}
    .day-grid {{ grid-template-columns: 1fr; gap: 7px; }}
    .day-item {{ flex-direction: row; justify-content: flex-start; align-items: center; min-height: 0; padding: 10px 14px; gap: 12px; text-align: left; }}
    .day-meta {{ flex-direction: row; align-items: baseline; gap: 8px; }}
    .durum-text {{ font-size: 18px; min-width: 32px; }}
    .mesai-badge {{ margin: 0 0 0 auto; }}
}}
</style>
<div id="live-clock">{clock_init}</div>
<script>
function updateClock() {{
    const el = document.getElementById('live-clock'); if(!el) return;
    const now = new Date(); const trTime = new Date(now.toLocaleString('en-US', {{ timeZone: 'Europe/Istanbul' }}));
    const d=String(trTime.getDate()).padStart(2,'0'), m=String(trTime.getMonth()+1).padStart(2,'0'), y=trTime.getFullYear();
    const h=String(trTime.getHours()).padStart(2,'0'), i=String(trTime.getMinutes()).padStart(2,'0'), s=String(trTime.getSeconds()).padStart(2,'0');
    el.innerHTML = d+"."+m+"."+y+" | "+h+":"+i+":"+s;
}}
setInterval(updateClock, 1000);
</script>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# YARDIMCI FONKSİYONLAR
# ------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("veri.xlsx")
        df.columns = [str(c).strip() if not isinstance(c, (datetime, pd.Timestamp)) else c for c in df.columns]
        return df
    except Exception:
        return None

def parse_date_super_safe(t_col):
    if isinstance(t_col, (datetime, pd.Timestamp)):
        return datetime(t_col.year, t_col.month, t_col.day)
    try:
        ts = pd.to_datetime(str(t_col).split(' ')[0], dayfirst=True)
        return datetime(ts.year, ts.month, ts.day)
    except Exception:
        return None

def get_status_class(durum):
    durum = str(durum).strip().upper()
    return {"N": "status-n", "HTÇ": "status-htc", "HT": "status-ht", "BÇ": "status-bc", "B": "status-b", "Üİ": "status-ui"}.get(durum, "status-default")

def norm_key(v):
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") else s

def set_lock(param_key, seconds):
    st.query_params[param_key] = str(int(time.time() + seconds))

def clear_lock(param_key):
    try:
        del st.query_params[param_key]
    except Exception:
        pass

def check_lock(param_key, mesaj):
    """URL'ye gömülü kilit süresini kontrol eder. Kilitliyse geri sayan ekranı
    gösterir (sunucu taraflı, JS'siz). Süre bitince kilidi temizler.
    Sayfa yenilense bile URL'de kaldığı için kilit devam eder."""
    val = st.query_params.get(param_key)
    if not val:
        return
    try:
        lock_ts = float(val)
    except Exception:
        clear_lock(param_key)
        return
    remaining = int(round(lock_ts - time.time()))
    if remaining > 0:
        st.markdown(f"""
            <div class="lock-wrap">
                <div style="font-size:44px;">⏳</div>
                <div class="lock-msg">{mesaj}</div>
                <div class="lock-count">{remaining}</div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
        st.rerun()
    else:
        clear_lock(param_key)

def build_day_item(t_col, row_g, row_s, date_mapping, lng):
    durum = str(row_g.get(t_col, "")).strip().upper()   # HARF AYNI KALIR (çevrilmez)
    mesai = str(row_s.get(t_col, "")).strip()
    dt_obj = date_mapping.get(t_col)
    if dt_obj:
        day_label = f"{str(dt_obj.day).zfill(2)} {AYLAR[lng][dt_obj.month]}"
        g_adi = GUNLER[lng][dt_obj.weekday()]
    else:
        day_label = str(t_col).split(' ')[0]; g_adi = ""
    cls = get_status_class(durum)
    mesai_html = f'<div class="mesai-badge">⚡ {mesai} {L["overtime"]}</div>' if mesai not in ["0", "0.0", "nan", "", "None"] else ""
    return (f'<div class="day-item {cls}"><span class="durum-text">{durum}</span>'
            f'<div class="day-meta"><span class="tarih-text">{day_label}</span>'
            f'<span class="gun-text">{g_adi}</span></div>{mesai_html}</div>')

df = load_data()

# ==================================================================
# EKRAN 1 — GİRİŞ
# ==================================================================
if not st.session_state['logged_in'] and not st.session_state['awaiting_verify']:
    st.markdown(f"<div class='month-title'>{ay_baslik}</div>", unsafe_allow_html=True)

    # Şifre kilidi (3 hatalı -> 3 dk), geri sayan
    check_lock('llock', L['login_locked'])

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.selectbox(L['lang'], ["TR", "EN", "UZ"], key='lang', format_func=lambda k: LANG_NAMES[k])

    sicil = st.text_input(L['sicil'])
    sifre = st.text_input(L['pass'], type="password")

    if st.button(L['login'], type="primary"):
        if df is not None:
            fiori_col = df['FİORİ NO'].map(norm_key)
            dogum_col = df['DOĞUM YILI'].map(norm_key)
            res = df[(fiori_col == norm_key(sicil)) & (dogum_col == norm_key(sifre))]
            if not res.empty:
                clear_lock('llock')
                st.session_state['pending_user'] = res
                st.session_state['awaiting_verify'] = True
                st.session_state['verify_code'] = f"{random.randint(0, 9999):04d}"
                st.session_state['verify_fails'] = 0
                st.session_state['login_fails'] = 0
                st.rerun()
            else:
                st.session_state['login_fails'] += 1
                if st.session_state['login_fails'] >= MAX_TRY:
                    set_lock('llock', LOGIN_LOCK_SEC)
                    st.session_state['login_fails'] = 0
                    st.rerun()
                else:
                    st.error("❌ " + L['err'])
    st.markdown('</div>', unsafe_allow_html=True)

    # Şifremi Unuttum
    with st.expander("🔑 " + L['forgot_title']):
        st.caption(L['forgot_desc'])
        with st.form("forgot_form"):
            f_sicil = st.text_input(L['sicil'], key="forgot_input")
            f_gonder = st.form_submit_button(L['forgot_btn'])
        if f_gonder:
            ad, gorev = "-", "-"
            if df is not None:
                fr = df[df['FİORİ NO'].map(norm_key) == norm_key(f_sicil)]
                if not fr.empty:
                    ad = fr.iloc[0]['AD SOYAD']; gorev = fr.iloc[0]['GÖREVİ']
            govde = (f"{L['forgot_body']}\n"
                     f"{L['m_id']}: {f_sicil}\n{L['m_name']}: {ad}\n{L['m_role']}: {gorev}")
            st.session_state['forgot_mailto'] = f"mailto:{MAIL_ADRES}?subject={urllib.parse.quote(L['forgot_subject'])}&body={urllib.parse.quote(govde)}"
            st.session_state['forgot_ready'] = True
        if st.session_state.get('forgot_ready'):
            st.success("✅ " + L['mail_ready'])
            st.link_button("📧 " + L['open_mail'], st.session_state['forgot_mailto'])

# ==================================================================
# EKRAN 2 — DOĞRULAMA
# ==================================================================
elif st.session_state['awaiting_verify'] and not st.session_state['logged_in']:
    # Kod kilidi (3 hatalı -> 30 sn), geri sayan
    st.markdown(f"<h1 class='portal-title'>🔐 {L['verify_title']}</h1>", unsafe_allow_html=True)
    check_lock('vlock', L['verify_locked'])

    st.markdown(f"<div class='verify-note'>{L['verify_desc']}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kod-box'>{st.session_state['verify_code']}</div>", unsafe_allow_html=True)
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    girilen_kod = st.text_input(L['verify_field'], max_chars=4)

    if st.button(L['verify_btn'], type="primary"):
        if str(girilen_kod).strip() == st.session_state['verify_code']:
            clear_lock('vlock'); clear_lock('llock')
            st.session_state['user_data'] = st.session_state['pending_user']
            st.session_state['logged_in'] = True
            st.session_state['awaiting_verify'] = False
            st.session_state['pending_user'] = None
            st.session_state['verify_fails'] = 0
            st.rerun()
        else:
            st.session_state['verify_fails'] += 1
            if st.session_state['verify_fails'] >= MAX_TRY:
                set_lock('vlock', VERIFY_LOCK_SEC)
                st.session_state['verify_fails'] = 0
                st.rerun()
            else:
                st.error("🤖 " + L['verify_err'])

    cyk1, cyk2 = st.columns(2)
    with cyk1:
        if st.button(L['new_code']):
            st.session_state['verify_code'] = f"{random.randint(0, 9999):04d}"
            st.rerun()
    with cyk2:
        if st.button(L['back']):
            st.session_state['awaiting_verify'] = False
            st.session_state['pending_user'] = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ==================================================================
# EKRAN 3 — ANA PANEL
# ==================================================================
else:
    u_df = st.session_state['user_data']

    ust1, ust2 = st.columns([2, 1])
    with ust1:
        st.selectbox(L['lang'], ["TR", "EN", "UZ"], key='lang', format_func=lambda k: LANG_NAMES[k], label_visibility="collapsed")
    with ust2:
        if st.button("🚪 " + L['logout'], type="primary", use_container_width=True):
            for k in ['logged_in', 'awaiting_verify', 'itiraz_ready']:
                st.session_state[k] = False
            st.session_state['user_data'] = None
            st.session_state['pending_user'] = None
            st.rerun()

    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    t_cols = [c for c in df.columns if isinstance(c, (datetime, pd.Timestamp)) or '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]
    date_mapping = {t_col: parse_date_super_safe(t_col) for t_col in t_cols}

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

    hg = now_tr.hour
    greet = (L["welcome_morning"] if 5 <= hg < 12 else L["welcome_day"] if 12 <= hg < 18 else L["welcome_evening"] if 18 <= hg < 23 else L["welcome_night"])

    st.write("")
    st.markdown(f'<div class="user-header">{greet}, {row_g["AD SOYAD"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-sub">{cevir_gorev(row_g["GÖREVİ"], LNG)}</div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="info-banner"><h4 class="info-title">ℹ️ {L['disc_title']}</h4><p class="info-text">{L['disc_text']}</p></div>""", unsafe_allow_html=True)

    st.markdown(f"""
        <div class="ozet-card">
            <div class="ozet-head">📊 {L['summary']}</div>
            <div class="ozet-grid">
                <div class="ozet-tile"><div class="ozet-num hl1">{odenecek}</div><div class="ozet-lbl">{L['paid_days']}</div></div>
                <div class="ozet-tile"><div class="ozet-num hl2">{toplam_mesai}</div><div class="ozet-lbl">{L['total_over']}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write("---")

    with st.expander(f"ℹ️ {L['legend']}"):
        for k, v in STATUS_MAP.items():
            st.markdown(f"**{k}:** {v[LNG]}")

    num_weeks = max(1, (len(t_cols) + 6) // 7)
    for w in range(1, num_weeks + 1):
        st.session_state['week_open'].setdefault(w, True)

    hepsi_acik = all(st.session_state['week_open'].get(w, True) for w in range(1, num_weeks + 1))
    if st.button(("🔼 " + L['collapse_all']) if hepsi_acik else ("🔽 " + L['expand_all']), type="primary"):
        yeni = not hepsi_acik
        for w in range(1, num_weeks + 1):
            st.session_state['week_open'][w] = yeni
        st.rerun()

    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        acik = st.session_state['week_open'].get(h_no, True)
        isaret = "➖" if acik else "➕"
        if st.button(f"{isaret}  {L['week']} {h_no}", key=f"wtoggle_{h_no}"):
            st.session_state['week_open'][h_no] = not acik
            st.rerun()
        if acik:
            grid_html = '<div class="day-grid">'
            for t_col in hafta:
                grid_html += build_day_item(t_col, row_g, row_s, date_mapping, LNG)
            grid_html += '</div>'
            st.markdown(grid_html, unsafe_allow_html=True)

    # 2. PUANTAJ — AYLIK VERİ (tüm günler alt alta), aç/kapa düğmeli
    st.markdown(f'<div class="list-baslik">📋 {L["full_title"]}</div>', unsafe_allow_html=True)
    full_open = st.session_state.setdefault('full_open', True)
    if st.button(("🔼 " + L['collapse_all']) if full_open else ("🔽 " + L['expand_all']), key="full_toggle", type="primary"):
        st.session_state['full_open'] = not full_open
        st.rerun()
    if st.session_state.get('full_open', True):
        full_html = '<div class="full-list">'
        for t_col in t_cols:
            full_html += build_day_item(t_col, row_g, row_s, date_mapping, LNG)
        full_html += '</div>'
        st.markdown(full_html, unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader(f"🚨 {L['appeal_head']}")
    st.markdown(f'<p style="font-size:14px; font-weight:600; color:{T["text_soft"]}; margin-bottom:15px;"><i>{L["appeal_desc"]}</i></p>', unsafe_allow_html=True)

    with st.form("itiraz_form"):
        konu = st.selectbox(L['subject'], L['topic_opts'], label_visibility="collapsed")
        notunuz = st.text_area(L['note'])
        gonder = st.form_submit_button("🚨 " + L['send'])

    if gonder:
        mail_konu = f"{L['m_prefix']} - {row_g['AD SOYAD']} ({konu})"
        mail_govde = (f"{L['m_id']}: {row_g['FİORİ NO']}\n{L['m_name']}: {row_g['AD SOYAD']}\n"
                      f"{L['m_role']}: {row_g['GÖREVİ']}\n{L['subject']}: {konu}\n{L['note']}: {notunuz}")
        st.session_state['itiraz_mailto'] = f"mailto:{MAIL_ADRES}?subject={urllib.parse.quote(mail_konu)}&body={urllib.parse.quote(mail_govde)}"
        st.session_state['itiraz_ready'] = True

    if st.session_state.get('itiraz_ready'):
        st.success("✅ " + L['mail_ready'])
        st.link_button("📧 " + L['open_mail'], st.session_state['itiraz_mailto'])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="mert-signature">POWERED BY Mert DÜZCÜK</div>', unsafe_allow_html=True)
