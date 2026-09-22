import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import urllib.parse
import random
import time
import io
import math
import threading
import re
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont, ImageFilter

st.set_page_config(page_title="Filyos Örnek Puantaj", layout="centered", initial_sidebar_state="collapsed")

MAIL_ADRES = "ret-filyos2A-ik@ronesans.com"
WHATSAPP_NO = "905459157444"          # 0545 915 7444 - Mert Düzcük
LOGIN_LOCK_SEC = 180                  # şifre 3 kez yanlış -> 3 dakika
VERIFY_LOCK_SEC = 30                  # kod 3 kez yanlış -> 30 saniye
MAX_TRY = 3
IDLE_SEC = 300                        # 5 dakika işlem yoksa otomatik çıkış

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
        "new_code": "Yeni Kod", "back": "Geri",
        "disc_title": "BİLGİLENDİRME",
        "disc_text": "Sistemdeki veriler resmî veri değildir; güncellenebilir veri olup yalnızca bilgilendirme amaçlıdır.",
        "expand_all": "TÜMÜNÜ AÇ", "collapse_all": "TÜMÜNÜ KAPAT",
        "mail_ready": "Talebiniz hazırlandı. Aşağıdaki butonlardan biriyle gönderebilirsiniz.", "open_mail": "MAİL UYGULAMASINI AÇ",
        "open_wa": "WHATSAPP İLE GÖNDER",
        "m_id": "Sicil No", "m_name": "Ad Soyad", "m_role": "Görevi", "m_prefix": "İtiraz",
        "login_locked": "Çok fazla hatalı giriş. Lütfen bekleyin.",
        "verify_locked": "Çok fazla hatalı kod. Lütfen bekleyin.",
        "forgot_title": "Şifremi Unuttum", "forgot_desc": "Kullanıcı adınızı girin; bilgilerinizle birlikte İK'ya şifre talebi maili oluşturulur.",
        "forgot_btn": "TALEP OLUŞTUR", "forgot_subject": "Şifre Talebi",
        "forgot_body": "Şifremi unuttum, yardımcı olabilir misiniz?",
        "timeout": "5 dakika işlem yapılmadığı için güvenlik amacıyla oturum kapatıldı.",
        "today": "BUGÜN", "leave_left": "YILLIK İZİN KAZANMANIZA KALAN GÜN", "hire_date": "İŞE GİRİŞ TARİHİ", "day_unit": "gün"
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
        "new_code": "New Code", "back": "Back",
        "disc_title": "NOTICE",
        "disc_text": "The data shown here is not official; it may be updated and is provided for informational purposes only.",
        "expand_all": "EXPAND ALL", "collapse_all": "COLLAPSE ALL",
        "mail_ready": "Your request is ready. Send it with one of the buttons below.", "open_mail": "OPEN MAIL APP",
        "open_wa": "SEND VIA WHATSAPP",
        "m_id": "Employee ID", "m_name": "Full Name", "m_role": "Position", "m_prefix": "Appeal",
        "login_locked": "Too many failed logins. Please wait.",
        "verify_locked": "Too many wrong codes. Please wait.",
        "forgot_title": "Forgot Password", "forgot_desc": "Enter your username; a password request email with your details will be prepared for HR.",
        "forgot_btn": "CREATE REQUEST", "forgot_subject": "Password Reset Request",
        "forgot_body": "I forgot my password, could you please help?",
        "timeout": "You were signed out for security after 5 minutes of inactivity.",
        "today": "TODAY", "leave_left": "DAYS LEFT TO EARN ANNUAL LEAVE", "hire_date": "HIRE DATE", "day_unit": "days"
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
        "new_code": "Yangi Kod", "back": "Orqaga",
        "disc_title": "MA'LUMOT",
        "disc_text": "Tizimdagi ma'lumotlar rasmiy emas; yangilanishi mumkin va faqat ma'lumot uchun beriladi.",
        "expand_all": "HAMMASINI OCHISH", "collapse_all": "HAMMASINI YOPISH",
        "mail_ready": "So'rovingiz tayyor. Quyidagi tugmalardan biri bilan yuboring.", "open_mail": "POCHTA ILOVASINI OCHISH",
        "open_wa": "WHATSAPP ORQALI YUBORISH",
        "m_id": "Tabel raqami", "m_name": "F.I.Sh", "m_role": "Lavozimi", "m_prefix": "E'tiroz",
        "login_locked": "Juda ko'p noto'g'ri kirish. Iltimos kuting.",
        "verify_locked": "Juda ko'p noto'g'ri kod. Iltimos kuting.",
        "forgot_title": "Parolni Unutdim", "forgot_desc": "Foydalanuvchi nomingizni kiriting; ma'lumotlaringiz bilan HR uchun parol so'rovi xati tayyorlanadi.",
        "forgot_btn": "SO'ROV YARATISH", "forgot_subject": "Parolni tiklash so'rovi",
        "forgot_body": "Parolimni unutdim, yordam bera olasizmi?",
        "timeout": "5 daqiqa harakat bo'lmagani uchun xavfsizlik maqsadida tizimdan chiqildi.",
        "today": "BUGUN", "leave_left": "YILLIK TA'TIL HUQUQIGA QOLGAN KUN", "hire_date": "ISHGA KIRGAN SANA", "day_unit": "kun"
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
# TEMA — Lacivert (açık) + telefon karanlık moddaysa otomatik koyu
# ------------------------------------------------------------------
THEME_LIGHT = {"bg": "#eef1f5", "card": "#ffffff", "line": "#d5dbe3", "tx": "#14202e", "soft": "#56657a",
               "acc": "#1e3a5f", "acc_tx": "#ffffff", "input": "#f7f9fb", "badge": "#ffd54a", "band": "#1e3a5f"}
THEME_DARK = {"bg": "#11151b", "card": "#1a2029", "line": "#2b3440", "tx": "#e9edf2", "soft": "#94a0ae",
              "acc": "#e4a53a", "acc_tx": "#11151b", "input": "#141920", "badge": "#e4a53a", "band": "#0b0e12"}

def css_vars(t):
    return ";".join(f"--{k.replace('_', '-')}:{v}" for k, v in t.items())

# ------------------------------------------------------------------
# OTURUM DURUMU
# ------------------------------------------------------------------
def init_state():
    d = {'lang': "TR", 'logged_in': False, 'awaiting_verify': False,
         'pending_user': None, 'verify_code': "", 'week_open': {}, 'itiraz_ready': False, 'itiraz_mailto': "",
         'itiraz_wa': "", 'login_fails': 0, 'verify_fails': 0, 'forgot_ready': False, 'forgot_mailto': "",
         'llock_key': None, 'vlock_key': None, 'last_active': time.time(), 'timed_out': False}
    for k, v in d.items():
        if k not in st.session_state:
            st.session_state[k] = v
init_state()

if st.session_state['lang'] not in LANGS:
    st.session_state['lang'] = "TR"

L = LANGS[st.session_state['lang']]
LNG = st.session_state['lang']
now_tr = datetime.utcnow() + timedelta(hours=3)

# ------------------------------------------------------------------
# SUNUCU TARAFLI KİLİT (Fiori no'ya bağlı; sayfa yenilense de kalkmaz)
# ------------------------------------------------------------------
@st.cache_resource
def lock_store():
    return {"data": {}, "mutex": threading.Lock()}

def lock_remaining(kind, key):
    s = lock_store()
    with s["mutex"]:
        rec = s["data"].get((kind, key))
        if not rec:
            return 0
        rem = int(math.ceil(rec.get("until", 0) - time.time()))
        return rem if rem > 0 else 0

def lock_fail(kind, key, seconds):
    """Hatalı denemeyi kaydeder. MAX_TRY'a ulaşınca kilitler. Kilitlendiyse True döner."""
    s = lock_store()
    with s["mutex"]:
        rec = s["data"].setdefault((kind, key), {"fails": 0, "until": 0})
        if rec["until"] and rec["until"] <= time.time():
            rec["until"] = 0
        rec["fails"] += 1
        if rec["fails"] >= MAX_TRY:
            rec["fails"] = 0
            rec["until"] = time.time() + seconds
            return True
        return False

def lock_clear(kind, key):
    s = lock_store()
    with s["mutex"]:
        s["data"].pop((kind, key), None)

# ------------------------------------------------------------------
# İKONLAR (ince çizgili SVG)
# ------------------------------------------------------------------
def icon(name, size=16):
    paths = {
        "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
        "shield": '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
        "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
        "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
        "flag": '<path d="M5 21V4h11l-1.5 4L16 12H5"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
        "eye": '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    }
    return (f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{paths[name]}</svg>')

# ------------------------------------------------------------------
# CSS
# ------------------------------------------------------------------
st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700;800;900&display=swap');
:root {{ {css_vars(THEME_LIGHT)}; }}
@media (prefers-color-scheme: dark) {{ :root {{ {css_vars(THEME_DARK)}; }} }}
html, body, .stApp, [data-testid="stAppViewContainer"] {{ background: var(--bg) !important; color: var(--tx) !important; font-family: 'Source Sans 3', system-ui, sans-serif; }}
[data-testid="stHeader"], [data-testid="stToolbar"], #MainMenu, footer {{ display: none !important; }}
.block-container {{ padding-top: 0.6rem !important; padding-bottom: 2rem !important; max-width: 760px !important; }}
.ic {{ vertical-align: -3px; margin-right: 6px; }}
.month-title {{ text-align: center; color: var(--acc); font-size: 17px; font-weight: 900; margin: 10px 0 18px; letter-spacing: 1.5px; }}
.portal-title {{ text-align: center; color: var(--tx); letter-spacing: 1.2px; font-weight: 900; margin: 10px 0 6px; font-size: 22px; line-height: 1.25; }}
.verify-note {{ text-align: center; color: var(--soft); font-size: 14px; font-weight: 600; margin-bottom: 14px; }}
.lock-wrap {{ text-align: center; background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 26px 18px; margin: 10px 0 14px; }}
.lock-wrap .ic {{ color: var(--acc); margin: 0; }}
.lock-msg {{ font-size: 16px; font-weight: 800; color: var(--tx); margin: 10px 0; }}
.lock-count {{ font-family: 'Courier New', monospace; font-size: 46px; font-weight: 900; color: var(--acc); }}
.user-header {{ font-size: 26px; font-weight: 900; color: var(--tx); margin: 8px 0 4px; line-height: 1.2; }}
.user-sub {{ font-size: 14px; font-weight: 700; color: var(--soft); margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px; }}
.info-banner {{ background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--acc); padding: 13px 15px; border-radius: 10px; margin-bottom: 12px; }}
.info-title {{ margin: 0; color: var(--acc); font-size: 13px; font-weight: 900; letter-spacing: 1px; }}
.info-text {{ margin: 5px 0 0 0; font-size: 13.5px; font-weight: 600; color: var(--tx); }}
.warn-banner {{ background: rgba(216,74,74,0.10); border-left: 4px solid #d84a4a; padding: 11px 14px; border-radius: 10px; margin-bottom: 16px; font-size: 13px; font-weight: 700; color: var(--tx); }}
.warn-banner .ic {{ color: #d84a4a; }}
.ozet-card {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 18px; margin-bottom: 16px; }}
.ozet-head {{ font-size: 13px; font-weight: 900; letter-spacing: 1.5px; color: var(--acc); text-transform: uppercase; margin-bottom: 14px; }}
.ozet-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; }}
.ozet-tile {{ background: var(--bg); border: 1px solid var(--line); border-radius: 10px; padding: 16px 8px; text-align: center; }}
.ozet-num {{ font-size: 32px; font-weight: 900; color: var(--tx); line-height: 1; font-variant-numeric: tabular-nums; }}
.ozet-num.hl1 {{ color: var(--acc); }}
.ozet-num.sm {{ font-size: 21px; padding: 5px 0 4px; }}
.ozet-unit {{ font-size: 15px; font-weight: 700; color: var(--soft); }}
.ozet-lbl {{ font-size: 12px; font-weight: 700; color: var(--soft); margin-top: 8px; text-transform: uppercase; letter-spacing: 0.4px; }}
.day-grid {{ display: grid; grid-template-columns: repeat(7, 1fr); gap: 7px; margin-bottom: 12px; }}
.list-baslik {{ font-size: 13px; font-weight: 900; letter-spacing: 1px; color: var(--acc); text-transform: uppercase; margin: 22px 0 8px; }}
.full-list {{ display: grid; grid-template-columns: 1fr; gap: 7px; margin-bottom: 16px; }}
.full-list .day-item {{ flex-direction: row; justify-content: flex-start; align-items: center; min-height: 0; padding: 10px 14px; gap: 12px; text-align: left; }}
.full-list .day-meta {{ flex-direction: row; align-items: baseline; gap: 8px; }}
.full-list .durum-text {{ font-size: 18px; min-width: 40px; }}
.full-list .mesai-badge {{ margin: 0 0 0 auto; }}
.day-item {{ position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; border-radius: 10px; color: #fff !important; padding: 7px 3px; min-height: 74px; gap: 3px; }}
.day-meta {{ display: flex; flex-direction: column; align-items: center; gap: 2px; }}
.durum-text {{ font-size: 20px; font-weight: 900; line-height: 1; }}
.tarih-text {{ font-size: 12px; font-weight: 900; line-height: 1; letter-spacing: 0.2px; }}
.gun-text {{ font-size: 10.5px; font-weight: 800; line-height: 1; opacity: 0.85; }}
.mesai-badge {{ background: var(--badge); color: #111; font-size: 11px; padding: 2px 8px; border-radius: 6px; margin-top: 2px; font-weight: 900; font-variant-numeric: tabular-nums; }}
.day-item.today {{ outline: 3px solid var(--tx); outline-offset: 2px; }}
.today-tag {{ position: absolute; top: -8px; left: 10px; font-size: 9px; font-weight: 900; background: var(--tx); color: var(--bg); padding: 1px 6px; border-radius: 4px; letter-spacing: .5px; }}
.status-n {{ background: #2f6b52; }}
.status-htc {{ background: #b3641a; }}
.status-ht {{ background: #4b5aa8; }}
.status-b {{ background: #9b2c3c; }}
.status-bc {{ background: #c2531c; }}
.status-ui {{ background: #6b7684; }}
.status-default {{ background: #3b4452; }}
.appeal-head {{ font-size: 19px; font-weight: 800; color: var(--tx); margin: 0 0 6px; }}
.appeal-head .ic {{ color: var(--acc); }}
.appeal-desc {{ font-size: 13.5px; font-weight: 600; color: var(--soft); font-style: italic; margin-bottom: 12px; }}
.watermark {{ position: fixed; inset: 0; pointer-events: none; z-index: 999; overflow: hidden; }}
.watermark span {{ position: absolute; white-space: nowrap; font-size: 13px; font-weight: 800; color: var(--tx); opacity: 0.07; transform: rotate(-28deg); letter-spacing: 1px; user-select: none; }}
.page-foot {{ text-align: center; font-size: 12px; color: var(--soft); margin-top: 28px; padding-top: 12px; border-top: 1px solid var(--line); letter-spacing: .3px; }}
/* Streamlit bileşenleri */
[data-testid="stVerticalBlockBorderWrapper"] {{ background: var(--card) !important; border-color: var(--line) !important; border-radius: 12px !important; }}
.stTextInput > div > div > input, .stTextArea textarea, .stSelectbox > div > div {{ background-color: var(--input) !important; color: var(--tx) !important; border: 1.5px solid var(--line) !important; border-radius: 10px !important; }}
[data-baseweb="input"], [data-baseweb="base-input"] {{ background: var(--input) !important; border-color: var(--line) !important; border-radius: 10px !important; }}
[data-baseweb="input"] input {{ color: var(--tx) !important; -webkit-text-fill-color: var(--tx) !important; }}
[data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{ color: var(--soft) !important; font-weight: 700 !important; letter-spacing: 0.5px; }}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] * {{ color: var(--soft) !important; }}
[data-testid="stExpander"] details {{ background: var(--card) !important; border: 1px solid var(--line) !important; border-radius: 10px !important; }}
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * {{ color: var(--tx) !important; background: transparent !important; }}
[data-testid="stExpanderDetails"] p, [data-testid="stExpanderDetails"] li, [data-testid="stExpanderDetails"] strong {{ color: var(--tx) !important; }}
[data-testid="stRadio"] label, [data-testid="stRadio"] p {{ color: var(--tx) !important; }}
[data-testid="stRadio"] [role="radiogroup"] label {{ background: var(--card) !important; border: 1px solid var(--line); border-radius: 8px; padding: 5px 10px !important; margin: 3px 6px 3px 0 !important; }}
.stButton, .stLinkButton, [data-testid="stFormSubmitButton"], [data-testid="stElementContainer"]:has(.stButton), [data-testid="stElementContainer"]:has(.stLinkButton), [data-testid="stElementContainer"]:has([data-testid="stFormSubmitButton"]) {{ width: 100% !important; }}
.stButton > button, .stLinkButton > a, [data-testid="stFormSubmitButton"] > button {{ width: 100% !important; border-radius: 10px !important; border: none !important; font-weight: 800 !important; min-height: 46px; letter-spacing: 0.5px; background: var(--acc) !important; color: var(--acc-tx) !important; box-shadow: none !important; }}
.stButton > button p, .stLinkButton > a p, [data-testid="stFormSubmitButton"] > button p {{ color: var(--acc-tx) !important; font-weight: 800 !important; }}
.stButton > button[kind="secondary"] {{ background: var(--card) !important; color: var(--tx) !important; border: 1px solid var(--line) !important; text-align: left; justify-content: flex-start; }}
.stButton > button[kind="secondary"] p {{ color: var(--tx) !important; font-weight: 700 !important; }}
[class*="st-key-wa_btn"] .stLinkButton > a {{ background: #1f9d55 !important; }}
[class*="st-key-wa_btn"] .stLinkButton > a p {{ color: #fff !important; }}
[data-testid="stAlert"] {{ border-radius: 10px !important; }}
[data-testid="stImage"] img {{ border-radius: 12px; border: 1px solid var(--line); }}
hr {{ border-color: var(--line) !important; }}
@media (max-width: 600px) {{
    .portal-title {{ font-size: 19px; }} .month-title {{ font-size: 15px; }} .user-header {{ font-size: 22px; }}
    .day-grid {{ grid-template-columns: 1fr; gap: 7px; }}
    .day-item {{ flex-direction: row; justify-content: flex-start; align-items: center; min-height: 0; padding: 10px 14px; gap: 12px; text-align: left; }}
    .day-meta {{ flex-direction: row; align-items: baseline; gap: 8px; }}
    .durum-text {{ font-size: 18px; min-width: 40px; }}
    .mesai-badge {{ margin: 0 0 0 auto; }}
}}
</style>""", unsafe_allow_html=True)

# ------------------------------------------------------------------
# ÜST BANT (canlı saat) + telefonda rakam klavyesi + 5 dk otomatik çıkış
# ------------------------------------------------------------------
def top_band(numeric_inputs=False, idle_logout=False):
    band_l, band_d = THEME_LIGHT["band"], THEME_DARK["band"]
    components.html(f"""
<div class="band"><span class="t">FİLYOS FAZ-2 · PERSONEL PUANTAJI</span><span id="c"></span></div>
<style>
html,body{{margin:0;background:transparent;font-family:'Source Sans 3',system-ui,sans-serif}}
.band{{display:flex;justify-content:space-between;align-items:center;background:{band_l};color:#fff;
padding:0 14px;height:40px;box-sizing:border-box;border-radius:10px;font-size:clamp(9px,2.75vw,12px);font-weight:700;letter-spacing:.3px;white-space:nowrap;gap:10px}}
.band .t{{overflow:hidden;text-overflow:ellipsis}}
.band #c{{flex:none;font-family:'Courier New',monospace;font-weight:700;opacity:.9;letter-spacing:0}}
@media (prefers-color-scheme: dark){{.band{{background:{band_d};border:1px solid #2b3440}}}}

</style>
<script>
function tick(){{
  const t=new Date(new Date().toLocaleString('en-US',{{timeZone:'Europe/Istanbul'}}));
  const p=n=>String(n).padStart(2,'0');
  document.getElementById('c').textContent=p(t.getDate())+'.'+p(t.getMonth()+1)+'.'+t.getFullYear()+'  '+p(t.getHours())+':'+p(t.getMinutes());
}}
tick(); setInterval(tick,1000);
let P; try {{ P = window.parent.document; }} catch(e) {{ P = null; }}
{"" if not numeric_inputs else '''
function numPad(){
  if(!P) return;
  P.querySelectorAll('input[type="text"],input[type="password"]').forEach(function(i){
    if(i.getAttribute('inputmode')!=='numeric'){ i.setAttribute('inputmode','numeric'); i.setAttribute('pattern','[0-9]*'); i.setAttribute('autocomplete','off'); }
  });
}
numPad(); if(P){ new MutationObserver(numPad).observe(P.body,{childList:true,subtree:true}); }
'''}
{"" if not idle_logout else f'''
if(P){{
  let last=Date.now();
  ['click','touchstart','scroll','keydown','mousemove'].forEach(function(ev){{ P.addEventListener(ev,function(){{last=Date.now();}},{{passive:true,capture:true}}); }});
  setInterval(function(){{
    if(Date.now()-last > {IDLE_SEC*1000}){{
      try{{ const w=window.parent; const u=new URL(w.location.href); u.searchParams.set('timeout','1'); w.location.href=u.toString(); }}catch(e){{}}
    }}
  }},5000);
}}
'''}
</script>""", height=44)

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

def get_date_cols(df):
    return [c for c in df.columns if isinstance(c, (datetime, pd.Timestamp)) or '202' in str(c) or ('.' in str(c) and len(str(c)) >= 8)]

def get_status_class(durum):
    durum = str(durum).strip().upper()
    return {"N": "status-n", "HTÇ": "status-htc", "HT": "status-ht", "BÇ": "status-bc", "B": "status-b", "Üİ": "status-ui"}.get(durum, "status-default")

def norm_key(v):
    s = str(v).strip()
    return s[:-2] if s.endswith(".0") else s

# ------------------------------------------------------------------
# RESİMLİ DOĞRULAMA KODU (bozuk / karışık)
# ------------------------------------------------------------------
def _font(size):
    for f in ["DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
              "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "arialbd.ttf"]:
        try:
            return ImageFont.truetype(f, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()

def captcha_image(code):
    W, H = 320, 100
    rnd = random.Random()
    img = Image.new("RGB", (W, H), (244, 241, 232))
    d = ImageDraw.Draw(img)
    for _ in range(110):  # arka plan noktaları
        x, y = rnd.randint(0, W), rnd.randint(0, H)
        r = rnd.randint(1, 2)
        c = rnd.randint(150, 200)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(c, c - 8, c + 6))
    for _ in range(2):  # arka plan ince eğriler
        a, f, ph = rnd.uniform(12, 25), rnd.uniform(40, 70), rnd.uniform(0, 6.28)
        y0 = rnd.randint(30, 70)
        d.line([(x, int(y0 + a * math.sin(x / f + ph))) for x in range(0, W + 6, 6)], fill=(170, 160, 150), width=2)
    colors = [(27, 59, 111), (122, 33, 48), (40, 88, 58), (85, 58, 130), (20, 32, 46)]
    font = _font(56)
    x = 22
    for ch in code:
        tile = Image.new("RGBA", (100, 110), (0, 0, 0, 0))
        ImageDraw.Draw(tile).text((50, 55), ch, font=font, fill=rnd.choice(colors) + (255,), anchor="mm")
        tile = tile.rotate(rnd.randint(-25, 25), resample=Image.BICUBIC)
        img.paste(tile, (x, rnd.randint(-12, 2)), tile)
        x += rnd.randint(64, 72)
    src = img.copy()  # hafif dalga bozulması
    px_s, px_d = src.load(), img.load()
    amp, per, ph = rnd.uniform(2, 3.5), rnd.uniform(30, 45), rnd.uniform(0, 6.28)
    for yy in range(H):
        off = int(amp * math.sin(2 * math.pi * yy / per + ph))
        for xx in range(W):
            px_d[xx, yy] = px_s[min(W - 1, max(0, xx + off)), yy]
    d = ImageDraw.Draw(img)
    a, f, ph = rnd.uniform(10, 18), rnd.uniform(35, 55), rnd.uniform(0, 6.28)
    d.line([(x, int(H / 2 + a * math.sin(x / f + ph))) for x in range(0, W + 6, 6)], fill=(45, 45, 45), width=2)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def new_code():
    st.session_state['verify_code'] = f"{random.randint(0, 9999):04d}"
    st.session_state['captcha_png'] = captcha_image(st.session_state['verify_code'])

def show_lock(remaining, mesaj):
    st.markdown(f"""
        <div class="lock-wrap">{icon('clock', 40)}
            <div class="lock-msg">{mesaj}</div>
            <div class="lock-count">{remaining}</div>
        </div>""", unsafe_allow_html=True)

def build_day_item(t_col, row_g, row_s, date_mapping, lng):
    durum = str(row_g.get(t_col, "")).strip().upper()   # HARF AYNI KALIR (çevrilmez)
    mesai = str(row_s.get(t_col, "")).strip()
    if mesai.endswith(".0"):
        mesai = mesai[:-2]
    dt_obj = date_mapping.get(t_col)
    today_cls, today_tag = "", ""
    if dt_obj:
        day_label = f"{str(dt_obj.day).zfill(2)} {AYLAR[lng][dt_obj.month]}"
        g_adi = GUNLER[lng][dt_obj.weekday()]
        if dt_obj.date() == now_tr.date():
            today_cls, today_tag = " today", f'<span class="today-tag">{L["today"]}</span>'
    else:
        day_label = str(t_col).split(' ')[0]; g_adi = ""
    cls = get_status_class(durum)
    mesai_html = f'<div class="mesai-badge">{mesai} {L["overtime"]}</div>' if mesai not in ["0", "0.0", "nan", "", "None"] else ""
    return (f'<div class="day-item {cls}{today_cls}">{today_tag}<span class="durum-text">{durum}</span>'
            f'<div class="day-meta"><span class="tarih-text">{day_label}</span>'
            f'<span class="gun-text">{g_adi}</span></div>{mesai_html}</div>')

def izin_sayisi(v):
    """KALAN YILLIK İZİN hücresinden sayıyı alır ("KALAN SÜRE 25 GÜN" -> 25)."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "–"
    if isinstance(v, (int, float)):
        return int(v) if float(v) % 1 == 0 else str(v).replace(".", ",")
    m = re.search(r"\d+(?:[.,]\d+)?", str(v))
    return m.group(0) if m else "–"

def giris_tarihi(v):
    try:
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        ts = pd.to_datetime(v, dayfirst=True)
        if pd.isna(ts):
            return None
        return datetime(ts.year, ts.month, ts.day)
    except Exception:
        return None

def watermark(text):
    spans = "".join(f'<span style="top:{r * 120 - 60}px;left:{(r % 2) * -110 - 40}px">'
                    f'{text} &nbsp;&nbsp;&nbsp; {text} &nbsp;&nbsp;&nbsp; {text}</span>' for r in range(14))
    st.markdown(f'<div class="watermark">{spans}</div>', unsafe_allow_html=True)

def footer():
    st.markdown('<div class="page-foot">Filyos Faz-2 · Personel ve Çalışma İlişkileri</div>', unsafe_allow_html=True)

def do_logout():
    for k in ['logged_in', 'awaiting_verify', 'itiraz_ready']:
        st.session_state[k] = False
    st.session_state['user_data'] = None
    st.session_state['pending_user'] = None

df = load_data()

# Ay başlığı Excel'deki tarihlerden alınır (bugünün tarihinden değil)
ay_ref = now_tr
if df is not None:
    _d = [parse_date_super_safe(c) for c in get_date_cols(df)]
    _d = [x for x in _d if x]
    if _d:
        ay_ref = _d[0]
ay_baslik = f"{AYLAR[LNG][ay_ref.month]} {ay_ref.year} {L['month_title']}"

# 5 dk hareketsizlik — sunucu tarafı yedek kontrol
if st.query_params.get("timeout"):
    do_logout()
    st.session_state['timed_out'] = True
    try:
        del st.query_params["timeout"]
    except Exception:
        pass
if st.session_state['logged_in'] and time.time() - st.session_state['last_active'] > IDLE_SEC:
    do_logout()
    st.session_state['timed_out'] = True
st.session_state['last_active'] = time.time()

# ==================================================================
# EKRAN 1 — GİRİŞ
# ==================================================================
if not st.session_state['logged_in'] and not st.session_state['awaiting_verify']:
    top_band(numeric_inputs=True)
    st.markdown(f"<div class='month-title'>{ay_baslik}</div>", unsafe_allow_html=True)

    if st.session_state.get('timed_out'):
        st.info(L['timeout'])

    # Şifre kilidi (3 hatalı -> 3 dk) — Fiori no'ya bağlı, sunucuda tutulur
    lk = st.session_state.get('llock_key')
    if lk:
        rem = lock_remaining("login", lk)
        if rem > 0:
            show_lock(rem, L['login_locked'])
            time.sleep(1)
            st.rerun()
        else:
            st.session_state['llock_key'] = None

    with st.container(border=True):
        st.radio(L['lang'], ["TR", "EN", "UZ"], key='lang', format_func=lambda k: LANG_NAMES[k], horizontal=True)
        sicil = st.text_input(L['sicil'])
        sifre = st.text_input(L['pass'], type="password")

        if st.button(L['login'], type="primary", icon=":material/login:"):
            key = norm_key(sicil)
            if key and lock_remaining("login", key) > 0:
                st.session_state['llock_key'] = key
                st.rerun()
            if df is not None:
                fiori_col = df['FİORİ NO'].map(norm_key)
                dogum_col = df['DOĞUM YILI'].map(norm_key)
                res = df[(fiori_col == key) & (dogum_col == norm_key(sifre))]
                if not res.empty:
                    lock_clear("login", key)
                    st.session_state['timed_out'] = False
                    st.session_state['pending_user'] = res
                    st.session_state['awaiting_verify'] = True
                    new_code()
                    st.rerun()
                else:
                    if lock_fail("login", key or "-", LOGIN_LOCK_SEC):
                        st.session_state['llock_key'] = key or "-"
                        st.rerun()
                    else:
                        st.error(L['err'])

    # Şifremi Unuttum
    with st.expander(L['forgot_title'], icon=":material/key:"):
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
            st.success(L['mail_ready'])
            st.link_button(L['open_mail'], st.session_state['forgot_mailto'], icon=":material/mail:")
    footer()

# ==================================================================
# EKRAN 2 — DOĞRULAMA (resimli kod)
# ==================================================================
elif st.session_state['awaiting_verify'] and not st.session_state['logged_in']:
    top_band(numeric_inputs=True)
    st.markdown(f"<div class='portal-title'>{icon('shield', 22)}{L['verify_title']}</div>", unsafe_allow_html=True)

    p_user = st.session_state['pending_user']
    vkey = norm_key(p_user.iloc[0]['FİORİ NO'])

    # Kod kilidi (3 hatalı -> 30 sn) — Fiori no'ya bağlı, sunucuda tutulur
    rem = lock_remaining("verify", vkey)
    if rem > 0:
        show_lock(rem, L['verify_locked'])
        time.sleep(1)
        st.rerun()

    st.markdown(f"<div class='verify-note'>{L['verify_desc']}</div>", unsafe_allow_html=True)
    if not st.session_state.get('captcha_png'):
        new_code()
    st.image(st.session_state['captcha_png'], use_container_width=True)

    with st.container(border=True):
        girilen_kod = st.text_input(L['verify_field'], max_chars=4)

        if st.button(L['verify_btn'], type="primary", icon=":material/verified_user:"):
            if str(girilen_kod).strip() == st.session_state['verify_code']:
                lock_clear("verify", vkey)
                st.session_state['user_data'] = p_user
                st.session_state['logged_in'] = True
                st.session_state['awaiting_verify'] = False
                st.session_state['pending_user'] = None
                st.session_state['captcha_png'] = None
                st.rerun()
            else:
                if lock_fail("verify", vkey, VERIFY_LOCK_SEC):
                    new_code()
                    st.rerun()
                else:
                    st.error(L['verify_err'])

        cyk1, cyk2 = st.columns(2)
        with cyk1:
            if st.button(L['new_code'], icon=":material/refresh:"):
                new_code()
                st.rerun()
        with cyk2:
            if st.button(L['back'], icon=":material/arrow_back:"):
                st.session_state['awaiting_verify'] = False
                st.session_state['pending_user'] = None
                st.session_state['captcha_png'] = None
                st.rerun()
    footer()

# ==================================================================
# EKRAN 3 — ANA PANEL
# ==================================================================
else:
    top_band(idle_logout=True)
    u_df = st.session_state['user_data']

    ust1, ust2 = st.columns([2, 1])
    with ust1:
        st.radio(L['lang'], ["TR", "EN", "UZ"], key='lang', format_func=lambda k: LANG_NAMES[k], horizontal=True, label_visibility="collapsed")
    with ust2:
        if st.button(L['logout'], type="primary", use_container_width=True, icon=":material/logout:"):
            do_logout()
            st.rerun()

    row_g = u_df[u_df['N-M'].astype(str).str.contains('Gün', na=False, case=False)].iloc[0]
    row_s = u_df[u_df['N-M'].astype(str).str.contains('SAAT', na=False, case=False)].iloc[0]

    # Filigran: ad + Fiori no + tarih/saat
    watermark(f"{row_g['AD SOYAD']} · {norm_key(row_g['FİORİ NO'])} · {now_tr.strftime('%d.%m.%Y %H:%M')}")

    t_cols = get_date_cols(df)
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

    st.markdown(f'<div class="user-header">{greet}, {row_g["AD SOYAD"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="user-sub">{cevir_gorev(row_g["GÖREVİ"], LNG)}</div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="info-banner"><div class="info-title">{icon('info')}{L['disc_title']}</div><p class="info-text">{L['disc_text']}</p></div>""", unsafe_allow_html=True)

    kalan_izin = izin_sayisi(row_g.get("KALAN YILLIK İZİN", None))
    g_dt = giris_tarihi(row_g.get("İŞE GİRİŞ TARİHİ", None))
    giris_txt = g_dt.strftime("%d.%m.%Y") if g_dt else "–"

    st.markdown(f"""
        <div class="ozet-card">
            <div class="ozet-head">{icon('chart')}{L['summary']}</div>
            <div class="ozet-grid">
                <div class="ozet-tile"><div class="ozet-num hl1">{odenecek}</div><div class="ozet-lbl">{L['paid_days']}</div></div>
                <div class="ozet-tile"><div class="ozet-num">{toplam_mesai}</div><div class="ozet-lbl">{L['total_over']}</div></div>
                <div class="ozet-tile"><div class="ozet-num">{kalan_izin}{'' if kalan_izin == '–' else f' <span class="ozet-unit">{L["day_unit"]}</span>'}</div><div class="ozet-lbl">{L['leave_left']}</div></div>
                <div class="ozet-tile"><div class="ozet-num sm">{giris_txt}</div><div class="ozet-lbl">{L['hire_date']}</div></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.write("---")

    with st.expander(L['legend'], icon=":material/info:"):
        for k, v in STATUS_MAP.items():
            st.markdown(f"**{k}:** {v[LNG]}")

    num_weeks = max(1, (len(t_cols) + 6) // 7)
    for w in range(1, num_weeks + 1):
        st.session_state['week_open'].setdefault(w, True)

    hepsi_acik = all(st.session_state['week_open'].get(w, True) for w in range(1, num_weeks + 1))
    if st.button(L['collapse_all'] if hepsi_acik else L['expand_all'], type="primary",
                 icon=":material/unfold_less:" if hepsi_acik else ":material/unfold_more:"):
        yeni = not hepsi_acik
        for w in range(1, num_weeks + 1):
            st.session_state['week_open'][w] = yeni
        st.rerun()

    for h_no, i in enumerate(range(0, len(t_cols), 7), 1):
        hafta = t_cols[i:i+7]
        acik = st.session_state['week_open'].get(h_no, True)
        if st.button(f"{L['week']} {h_no}", key=f"wtoggle_{h_no}", icon=":material/remove:" if acik else ":material/add:"):
            st.session_state['week_open'][h_no] = not acik
            st.rerun()
        if acik:
            grid_html = '<div class="day-grid">'
            for t_col in hafta:
                grid_html += build_day_item(t_col, row_g, row_s, date_mapping, LNG)
            grid_html += '</div>'
            st.markdown(grid_html, unsafe_allow_html=True)

    # 2. PUANTAJ — AYLIK VERİ (tüm günler alt alta), aç/kapa düğmeli
    st.markdown(f'<div class="list-baslik">{icon("list")}{L["full_title"]}</div>', unsafe_allow_html=True)
    full_open = st.session_state.setdefault('full_open', True)
    if st.button(L['collapse_all'] if full_open else L['expand_all'], key="full_toggle", type="primary",
                 icon=":material/unfold_less:" if full_open else ":material/unfold_more:"):
        st.session_state['full_open'] = not full_open
        st.rerun()
    if st.session_state.get('full_open', True):
        full_html = '<div class="full-list">'
        for t_col in t_cols:
            full_html += build_day_item(t_col, row_g, row_s, date_mapping, LNG)
        full_html += '</div>'
        st.markdown(full_html, unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(f'<div class="appeal-head">{icon("flag", 20)}{L["appeal_head"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="appeal-desc">{L["appeal_desc"]}</div>', unsafe_allow_html=True)

        with st.form("itiraz_form"):
            konu = st.radio(L['subject'], L['topic_opts'], horizontal=True, label_visibility="collapsed")
            notunuz = st.text_area(L['note'])
            gonder = st.form_submit_button(L['send'], icon=":material/send:")

        if gonder:
            mail_konu = f"{L['m_prefix']} - {row_g['AD SOYAD']} ({konu})"
            mail_govde = (f"{L['m_id']}: {norm_key(row_g['FİORİ NO'])}\n{L['m_name']}: {row_g['AD SOYAD']}\n"
                          f"{L['m_role']}: {row_g['GÖREVİ']}\n{L['subject']}: {konu}\n{L['note']}: {notunuz}")
            st.session_state['itiraz_mailto'] = f"mailto:{MAIL_ADRES}?subject={urllib.parse.quote(mail_konu)}&body={urllib.parse.quote(mail_govde)}"
            wa_text = f"*{mail_konu}*\n{mail_govde}"
            st.session_state['itiraz_wa'] = f"https://wa.me/{WHATSAPP_NO}?text={urllib.parse.quote(wa_text)}"
            st.session_state['itiraz_ready'] = True

        if st.session_state.get('itiraz_ready'):
            st.success(L['mail_ready'])
            st.link_button(L['open_mail'], st.session_state['itiraz_mailto'], icon=":material/mail:")
            with st.container(key="wa_btn"):
                st.link_button(L['open_wa'], st.session_state['itiraz_wa'], icon=":material/chat:")
    footer()
