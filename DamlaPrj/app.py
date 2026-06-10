# -*- coding: utf-8 -*-
"""
Akıllı Kuraklık Risk Analizi ve Ekonomik Etki Tahmin Sistemi
------------------------------------------------------------
Modern mobil prototip arayüzü, 81 il entegrasyonu, harita ve yan yana
Matplotlib kıyaslama modülü, sağ üst köşede ☰ hamburger akordeon menüsü,
8 adet arayüz teması, anotasyonlu çizgi grafikleri ve su dostu damlacık ile
tek dosya Python/SQLite uygulaması.
"""

import os
import sys
import sqlite3
import hashlib
import datetime
import random
import tkinter as tk
from tkinter import ttk, messagebox

# Matplotlib Entegrasyonu
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Pillow Entegrasyonu
from PIL import Image, ImageDraw, ImageTk

# --- TEMA TANIMLARI (8 Çeşitlendirilmiş Tema) ---
THEMES = {
    "Slate Koyu": {
        "bg": "#0f172a", "card": "#1e293b", "card_accent": "#1e3a8a", "input_bg": "#334155",
        "text_primary": "#f8fafc", "text_muted": "#94a3b8", "primary_btn": "#0ea5e9",
        "secondary_btn": "#10b981", "danger_btn": "#ef4444", "accent": "#0ea5e9"
    },
    "Orman Yeşili": {
        "bg": "#062f1c", "card": "#0f4a2d", "card_accent": "#14532d", "input_bg": "#166534",
        "text_primary": "#f0fdf4", "text_muted": "#86efac", "primary_btn": "#10b981",
        "secondary_btn": "#3b82f6", "danger_btn": "#f43f5e", "accent": "#10b981"
    },
    "Derin Okyanus": {
        "bg": "#0c1d2e", "card": "#152e46", "card_accent": "#0f4c81", "input_bg": "#1e4466",
        "text_primary": "#f0f9ff", "text_muted": "#7dd3fc", "primary_btn": "#06b6d4",
        "secondary_btn": "#10b981", "danger_btn": "#e11d48", "accent": "#06b6d4"
    },
    "Günbatımı": {
        "bg": "#1c1917", "card": "#2e2a28", "card_accent": "#443e3c", "input_bg": "#57534e",
        "text_primary": "#fafaf9", "text_muted": "#d6d3d1", "primary_btn": "#f59e0b",
        "secondary_btn": "#10b981", "danger_btn": "#ef4444", "accent": "#f59e0b"
    },
    "Platin Açık": {
        "bg": "#f1f5f9", "card": "#ffffff", "card_accent": "#cbd5e1", "input_bg": "#e2e8f0",
        "text_primary": "#0f172a", "text_muted": "#64748b", "primary_btn": "#3b82f6",
        "secondary_btn": "#10b981", "danger_btn": "#ef4444", "accent": "#3b82f6"
    },
    "Gece Siyahı": {
        "bg": "#000000", "card": "#121212", "card_accent": "#27272a", "input_bg": "#1f1f1f",
        "text_primary": "#ffffff", "text_muted": "#a1a1aa", "primary_btn": "#a855f7",
        "secondary_btn": "#ec4899", "danger_btn": "#ef4444", "accent": "#a855f7"
    },
    "Kiraz Çiçeği": {
        "bg": "#fff1f2", "card": "#ffe4e6", "card_accent": "#fecdd3", "input_bg": "#fda4af",
        "text_primary": "#4c0519", "text_muted": "#be123c", "primary_btn": "#db2777",
        "secondary_btn": "#e11d48", "danger_btn": "#9f1239", "accent": "#db2777"
    },
    "Lavanta Bahçesi": {
        "bg": "#1e1b4b", "card": "#312e81", "card_accent": "#4338ca", "input_bg": "#4f46e5",
        "text_primary": "#e0e7ff", "text_muted": "#c7d2fe", "primary_btn": "#818cf8",
        "secondary_btn": "#10b981", "danger_btn": "#ef4444", "accent": "#818cf8"
    }
}

DB_FILE = "kuraklik_sistemi.db"

# --- TÜRKİYE TÜM 81 İL COĞRAFİ KONUM VE BÖLGESEL İKLİM DETAYLARI ---
ALL_CITIES_GEOGRAPHY = {
    "Adana": (35.32, 36.98, "Akdeniz"), "Adıyaman": (38.28, 37.76, "Güneydoğu Anadolu"),
    "Afyonkarahisar": (30.54, 38.76, "Ege"), "Ağrı": (43.05, 39.72, "Doğu Anadolu"),
    "Amasya": (35.83, 40.65, "Karadeniz"), "Ankara": (32.85, 39.93, "İç Anadolu"),
    "Antalya": (30.70, 36.88, "Akdeniz"), "Artvin": (41.82, 41.18, "Karadeniz"),
    "Aydın": (27.84, 37.85, "Ege"), "Balıkesir": (27.88, 39.65, "Marmara"),
    "Bilecik": (29.98, 40.14, "Marmara"), "Bingöl": (40.49, 38.88, "Doğu Anadolu"),
    "Bitlis": (42.11, 38.40, "Doğu Anadolu"), "Bolu": (31.61, 40.73, "Karadeniz"),
    "Burdur": (30.29, 37.72, "Akdeniz"), "Bursa": (29.06, 40.18, "Marmara"),
    "Çanakkale": (26.41, 40.15, "Marmara"), "Çankırı": (33.62, 40.60, "İç Anadolu"),
    "Çorum": (34.95, 40.55, "Karadeniz"), "Denizli": (29.09, 37.77, "Ege"),
    "Diyarbakır": (40.24, 37.91, "Güneydoğu Anadolu"), "Edirne": (26.56, 41.68, "Marmara"),
    "Elazığ": (39.22, 38.68, "Doğu Anadolu"), "Erzincan": (39.49, 39.75, "Doğu Anadolu"),
    "Erzurum": (41.27, 39.90, "Doğu Anadolu"), "Eskişehir": (30.52, 39.78, "İç Anadolu"),
    "Gaziantep": (37.38, 37.06, "Güneydoğu Anadolu"), "Giresun": (38.39, 40.91, "Karadeniz"),
    "Gümüşhane": (39.48, 40.46, "Karadeniz"), "Hakkari": (43.74, 37.58, "Doğu Anadolu"),
    "Hatay": (36.16, 36.20, "Akdeniz"), "Isparta": (30.56, 37.76, "Akdeniz"),
    "Mersin": (34.63, 36.81, "Akdeniz"), "İstanbul": (29.01, 41.01, "Marmara"),
    "İzmir": (27.14, 38.42, "Ege"), "Kars": (43.09, 40.60, "Doğu Anadolu"),
    "Kastamonu": (33.78, 41.38, "Karadeniz"), "Kayseri": (35.48, 38.72, "İç Anadolu"),
    "Kırklareli": (27.22, 41.73, "Marmara"), "Kırşehir": (34.16, 39.14, "İç Anadolu"),
    "Kocaeli": (29.92, 40.76, "Marmara"), "Konya": (32.48, 37.87, "İç Anadolu"),
    "Kütahya": (29.98, 39.42, "Ege"), "Malatya": (38.32, 38.35, "Doğu Anadolu"),
    "Manisa": (27.43, 38.61, "Ege"), "Kahramanmaraş": (36.93, 37.58, "Akdeniz"),
    "Mardin": (40.74, 37.31, "Güneydoğu Anadolu"), "Muğla": (28.36, 37.22, "Ege"),
    "Muş": (41.49, 38.73, "Doğu Anadolu"), "Nevşehir": (34.71, 38.62, "İç Anadolu"),
    "Niğde": (34.68, 37.97, "İç Anadolu"), "Ordu": (37.88, 40.98, "Karadeniz"),
    "Rize": (40.52, 41.02, "Karadeniz"), "Sakarya": (30.40, 40.78, "Marmara"),
    "Samsun": (36.33, 41.29, "Karadeniz"), "Siirt": (41.94, 37.93, "Güneydoğu Anadolu"),
    "Sinop": (35.15, 42.03, "Karadeniz"), "Sivas": (37.02, 39.75, "İç Anadolu"),
    "Tekirdağ": (27.51, 40.98, "Marmara"), "Tokat": (36.55, 40.32, "Karadeniz"),
    "Trabzon": (39.72, 41.00, "Karadeniz"), "Tunceli": (39.55, 39.11, "Doğu Anadolu"),
    "Şanlıurfa": (38.79, 37.16, "Güneydoğu Anadolu"), "Uşak": (29.41, 38.67, "Ege"),
    "Van": (43.38, 38.50, "Doğu Anadolu"), "Yozgat": (34.81, 39.82, "İç Anadolu"),
    "Zonguldak": (31.79, 41.45, "Karadeniz"), "Aksaray": (34.03, 38.37, "İç Anadolu"),
    "Bayburt": (40.26, 40.26, "Karadeniz"), "Karaman": (33.22, 37.18, "İç Anadolu"),
    "Kırıkkale": (33.51, 39.85, "İç Anadolu"), "Batman": (41.13, 37.89, "Güneydoğu Anadolu"),
    "Şırnak": (42.45, 37.52, "Doğu Anadolu"), "Bartın": (32.34, 41.63, "Karadeniz"),
    "Ardahan": (42.70, 41.11, "Doğu Anadolu"), "Iğdır": (44.04, 39.92, "Doğu Anadolu"),
    "Yalova": (29.27, 40.65, "Marmara"), "Karabük": (32.63, 41.20, "Karadeniz"),
    "Kilis": (37.11, 36.72, "Güneydoğu Anadolu"), "Osmaniye": (36.25, 37.07, "Akdeniz"),
    "Düzce": (31.16, 40.84, "Karadeniz")
}

# --- SU DOSTU DAMLACIK RASTGELE İPUÇLARI ---
WATER_FRIEND_TIPS = [
    "Dişlerinizi fırçalarken musluğu kapatarak günde 12 litre su kurtarabilirsiniz! 💧",
    "Duş süresini sadece 1 dakika kısaltarak yılda kişi başı 9 ton su tasarrufu sağlayabilirsiniz! 🚿",
    "Meyve ve sebzeleri akan musluk altında değil, su dolu bir kapta yıkamak su israfını önler! 🍎",
    "Akıtan tek bir musluk günde ortalama 7 litre su ziyan eder. Hemen onaralım! 🔧",
    "Bitkileri akşam veya sabah erken sularsanız, buharlaşma azalır ve su toprakta kalır! 🌻",
    "Çamaşır ve bulaşık makinelerini tam doldurmadan çalıştırmamak, haftada 40 litre su kurtarır! 🧺",
    "Yağmur suyu hasadı yaparak bahçe sulamada şebeke suyu yerine yağmur suyunu kullanın! 🌧️",
    "Çamaşır suyunu ve kimyasalları az kullanmak sularımızın kirlenmesini önler! 🧪",
    "Damlama sulama yöntemi, vahşi sulamaya göre tarımda %50 su tasarrufu sağlar! 🌾",
    "Gıda israfı aynı zamanda devasa bir su israfıdır. Porsiyonlarımıza dikkat edelim! 🍔"
]


# =====================================================================
# BÖLGESEL İKLİM TAHMİNCİSİ & YEREL GÖRSEL OLUŞTURUCULAR
# =====================================================================
def get_city_climate_defaults(city_name):
    """81 ilin iklim parametrelerini bulundukları bölgelere göre gerçekçi üretir."""
    if city_name not in ALL_CITIES_GEOGRAPHY:
        return 20.0, 50.0, 50.0
    long, lat, region = ALL_CITIES_GEOGRAPHY[city_name]
    
    if region == "Marmara":
        return 19.0, 72.0, 115.0  # Düşük Risk
    elif region == "Karadeniz":
        return 16.0, 82.0, 160.0  # Düşük Risk
    elif region == "Ege":
        return 27.0, 52.0, 68.0   # Orta Risk
    elif region == "İç Anadolu":
        return 23.0, 46.0, 62.0   # Orta Risk
    elif region == "Doğu Anadolu":
        return 18.0, 48.0, 78.0   # Orta Risk
    elif region == "Akdeniz":
        return 32.0, 42.0, 12.0   # Yüksek Risk
    elif region == "Güneydoğu Anadolu":
        return 35.0, 20.0, 4.0    # Yüksek Risk
    return 20.0, 50.0, 50.0


def get_city_drought_info(city_name):
    """Seçilen ilin risk durumunu dinamik hesaplayarak uyuşmazlıkları önler."""
    temp, hum, prec = get_city_climate_defaults(city_name)
    score = DroughtAnalysisEngine.calculate_score(temp, hum, prec)
    risk = DroughtAnalysisEngine.get_risk_level(score)
    color = "#10b981" if risk == "Düşük Risk" else "#f59e0b" if risk == "Orta Risk" else "#ef4444"
    return score, risk, color


def generate_drought_images():
    """Haberler ve Akıllı Öneriler için vektörel kuraklık ve su illüstrasyonları (PNG) üretir."""
    # 1. Çatlamış toprak görseli (Akıllı Öneriler sayfasının üst kapak görseli)
    if not os.path.exists("drought_cracked.png"):
        img = Image.new("RGB", (380, 130), "#d7c49e") # Çöl beji
        draw = ImageDraw.Draw(img)
        # Çatlak hatlarını çiz
        random.seed(123)
        nodes = [(random.randint(10, 370), random.randint(10, 120)) for _ in range(35)]
        for p1 in nodes:
            dists = sorted([((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2, p2) for p2 in nodes if p1 != p2])
            for i in range(min(3, len(dists))):
                p2 = dists[i][1]
                draw.line([p1, p2], fill="#5c4033", width=2)
        # Kızgın güneş
        draw.ellipse([320, 10, 360, 50], fill="#f59e0b")
        img.save("drought_cracked.png")


def generate_news_images():
    """Haberler için renkli ve soyut kapak görselleri (PNG) oluşturur."""
    if not os.path.exists("news_baraj.png"):
        img = Image.new("RGB", (90, 70), "#ef4444")
        draw = ImageDraw.Draw(img)
        draw.ellipse([32, 22, 58, 48], fill="#ffffff")
        draw.polygon([(45, 12), (32, 35), (58, 35)], fill="#ffffff")
        draw.rectangle([43, 24, 47, 36], fill="#ef4444")
        draw.ellipse([43, 40, 47, 44], fill="#ef4444")
        img.save("news_baraj.png")
        
    if not os.path.exists("news_sulama.png"):
        img = Image.new("RGB", (90, 70), "#10b981")
        draw = ImageDraw.Draw(img)
        draw.ellipse([30, 20, 60, 50], fill="#ffffff")
        draw.line([45, 20, 45, 50], fill="#10b981", width=2)
        draw.line([45, 30, 52, 23], fill="#10b981", width=2)
        draw.line([45, 40, 38, 33], fill="#10b981", width=2)
        img.save("news_sulama.png")
        
    if not os.path.exists("news_tasarruf.png"):
        img = Image.new("RGB", (90, 70), "#0ea5e9")
        draw = ImageDraw.Draw(img)
        draw.ellipse([33, 20, 57, 44], fill="#ffffff")
        draw.ellipse([42, 29, 48, 35], fill="#0ea5e9")
        draw.ellipse([42, 50, 48, 58], fill="#ffffff")
        img.save("news_tasarruf.png")


# =====================================================================
# TEMEL ARAYÜZ VE YARDIMCI BİLEŞENLER
# =====================================================================
class Card(tk.Frame):
    def __init__(self, parent, title="", accent_color=None, card_bg="#1e293b", text_color="#f8fafc", **kwargs):
        super().__init__(parent, bg=card_bg, bd=0, highlightthickness=0, **kwargs)
        if accent_color:
            accent_bar = tk.Frame(self, bg=accent_color, height=3)
            accent_bar.pack(fill="x", side="top")
        if title:
            lbl_title = tk.Label(self, text=title, font=("Segoe UI", 10, "bold"), fg=text_color, bg=card_bg, anchor="w", padx=12, pady=8)
            lbl_title.pack(fill="x", side="top")
        self.content_frame = tk.Frame(self, bg=card_bg, padx=12, pady=10)
        self.content_frame.pack(fill="both", expand=True)


class CustomButton(tk.Button):
    def __init__(self, parent, text, bg_color, fg_color="#ffffff", command=None, **kwargs):
        super().__init__(
            parent, text=text, bg=bg_color, fg=fg_color, 
            activebackground=bg_color, activeforeground=fg_color,
            font=("Segoe UI", 9, "bold"), bd=0, relief="flat", 
            cursor="hand2", pady=8, command=command, **kwargs
        )


class ScrollableFrame(tk.Frame):
    def __init__(self, parent, bg_color="#0f172a", **kwargs):
        super().__init__(parent, bg=bg_color, **kwargs)
        self.canvas = tk.Canvas(self, bg=bg_color, bd=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg_color)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        
    def _on_mousewheel(self, event):
        try:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except Exception:
            pass


class LoginScreen(tk.Frame):
    def __init__(self, parent, controller):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        container = tk.Frame(self, bg=tc["bg"])
        container.place(relx=0.5, rely=0.5, anchor="center", width=340)
        
        tk.Label(container, text="🌾 Akıllı Kuraklık", font=("Segoe UI", 24, "bold"), fg=tc["primary_btn"], bg=tc["bg"]).pack(pady=(0, 5))
        tk.Label(container, text="Risk Analiz & Tahmin Sistemi", font=("Segoe UI", 12), fg=tc["text_muted"], bg=tc["bg"]).pack(pady=(0, 30))
        
        tk.Label(container, text="Kullanıcı Adı", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["bg"]).pack(anchor="w", pady=(0, 5))
        self.ent_user = tk.Entry(container, font=("Segoe UI", 11), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_user.pack(fill="x", ipady=8, pady=(0, 15))
        
        tk.Label(container, text="Şifre", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["bg"]).pack(anchor="w", pady=(0, 5))
        self.ent_pass = tk.Entry(container, font=("Segoe UI", 11), show="*", bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_pass.pack(fill="x", ipady=8, pady=(0, 25))
        
        CustomButton(container, text="Giriş Yap", bg_color=tc["primary_btn"], command=self.do_login).pack(fill="x", pady=(0, 15))
        
        reg_row = tk.Frame(container, bg=tc["bg"])
        reg_row.pack()
        tk.Label(reg_row, text="Hesabınız yok mu?", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["bg"]).pack(side="left")
        
        btn_reg = tk.Button(
            reg_row, text="Kayıt Ol", font=("Segoe UI", 9, "bold", "underline"),
            fg=tc["primary_btn"], bg=tc["bg"], activebackground=tc["bg"],
            activeforeground=tc["secondary_btn"], bd=0, cursor="hand2",
            command=controller.show_register_screen
        )
        btn_reg.pack(side="left", padx=5)

    def do_login(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get().strip()
        
        if not username or not password:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return
            
        res = Database.login_user(username, password)
        if res:
            user_id, theme_name = res
            self.controller.login_success(user_id, username)
        else:
            messagebox.showerror("Hata", "Geçersiz kullanıcı adı veya şifre.")


class RegisterScreen(tk.Frame):
    def __init__(self, parent, controller):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        container = tk.Frame(self, bg=tc["bg"])
        container.place(relx=0.5, rely=0.5, anchor="center", width=340)
        
        tk.Label(container, text="Kayıt Ol", font=("Segoe UI", 24, "bold"), fg=tc["secondary_btn"], bg=tc["bg"]).pack(pady=(0, 5))
        tk.Label(container, text="Yeni bir hesap oluşturun", font=("Segoe UI", 11), fg=tc["text_muted"], bg=tc["bg"]).pack(pady=(0, 30))
        
        tk.Label(container, text="Kullanıcı Adı", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["bg"]).pack(anchor="w", pady=(0, 5))
        self.ent_user = tk.Entry(container, font=("Segoe UI", 11), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_user.pack(fill="x", ipady=8, pady=(0, 15))
        
        tk.Label(container, text="Şifre", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["bg"]).pack(anchor="w", pady=(0, 5))
        self.ent_pass = tk.Entry(container, font=("Segoe UI", 11), show="*", bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_pass.pack(fill="x", ipady=8, pady=(0, 15))
        
        tk.Label(container, text="Şifre Tekrar", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["bg"]).pack(anchor="w", pady=(0, 5))
        self.ent_pass_conf = tk.Entry(container, font=("Segoe UI", 11), show="*", bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_pass_conf.pack(fill="x", ipady=8, pady=(0, 25))
        
        CustomButton(container, text="Hesap Oluştur", bg_color=tc["secondary_btn"], command=self.do_register).pack(fill="x", pady=(0, 15))
        
        log_row = tk.Frame(container, bg=tc["bg"])
        log_row.pack()
        tk.Label(log_row, text="Zaten hesabınız var mı?", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["bg"]).pack(side="left")
        
        btn_log = tk.Button(
            log_row, text="Giriş Yap", font=("Segoe UI", 9, "bold", "underline"),
            fg=tc["secondary_btn"], bg=tc["bg"], activebackground=tc["bg"],
            activeforeground=tc["primary_btn"], bd=0, cursor="hand2",
            command=controller.show_login_screen
        )
        btn_log.pack(side="left", padx=5)

    def do_register(self):
        username = self.ent_user.get().strip()
        password = self.ent_pass.get().strip()
        conf = self.ent_pass_conf.get().strip()
        
        if not username or not password or not conf:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return
            
        if password != conf:
            messagebox.showerror("Hata", "Şifreler uyuşmuyor.")
            return
            
        if len(password) < 4:
            messagebox.showerror("Hata", "Şifre en az 4 karakter olmalıdır.")
            return
            
        success = Database.register_user(username, password)
        if success:
            messagebox.showinfo("Başarılı", "Kayıt başarıyla tamamlandı. Giriş yapabilirsiniz.")
            self.controller.show_login_screen()
        else:
            messagebox.showerror("Hata", "Bu kullanıcı adı zaten alınmış.")


def draw_city_gauge_chart(parent_frame, score, tc):
    """Matplotlib yatay gösterge (gauge) grafiği çizerek şehir veya analiz skorunu gösterir."""
    for w in parent_frame.winfo_children():
        w.destroy()
        
    plt.rcParams['text.color'] = tc["text_primary"]
    fig, ax = plt.subplots(figsize=(4.0, 0.8), facecolor=tc["card"])
    ax.set_facecolor(tc["card"])
    
    # Background bar
    ax.barh(0, 100, color=tc["input_bg"], height=0.4, align='center')
    
    # Determine color by score
    if score < 35:
        bar_color = tc["secondary_btn"]
    elif score < 60:
        bar_color = tc["accent"]
    else:
        bar_color = tc["danger_btn"]
        
    # Active score bar
    ax.barh(0, score, color=bar_color, height=0.4, align='center')
    
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.5, 0.5)
    ax.axis('off')
    
    ax.text(score, 0, f"▼\n{score}", ha='center', va='bottom', fontsize=9, fontweight='bold', color=tc["text_primary"])
    ax.text(0, -0.4, "0", ha='center', va='top', fontsize=7, color=tc["text_muted"])
    ax.text(35, -0.4, "35", ha='center', va='top', fontsize=7, color=tc["text_muted"])
    ax.text(60, -0.4, "60", ha='center', va='top', fontsize=7, color=tc["text_muted"])
    ax.text(100, -0.4, "100", ha='center', va='top', fontsize=7, color=tc["text_muted"])
    
    fig.tight_layout()
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


def draw_water_circular_chart(parent_frame, consumed_liters, tc):
    """Matplotlib dairesel halka (donut) grafiği çizerek su tüketim durumunu limit ile oranlar."""
    for w in parent_frame.winfo_children():
        w.destroy()
        
    plt.rcParams['text.color'] = tc["text_primary"]
    fig, ax = plt.subplots(figsize=(2.0, 2.0), facecolor=tc["card"])
    ax.set_facecolor(tc["card"])
    
    limit = 150.0
    if consumed_liters <= limit:
        sizes = [consumed_liters, limit - consumed_liters]
        if consumed_liters <= 0:
            sizes = [0.001, limit]
        colors = [tc["secondary_btn"], tc["input_bg"]]
    else:
        sizes = [limit, consumed_liters - limit]
        colors = [tc["danger_btn"], tc["card_accent"]]
        
    ax.pie(sizes, colors=colors, startangle=90, counterclock=False,
           wedgeprops=dict(width=0.25, edgecolor=tc["card"], linewidth=1))
           
    ax.text(0, 0, f"{int(consumed_liters)} L\n/ {int(limit)} L", ha='center', va='center',
            fontsize=8, fontweight='bold', color=tc["text_primary"])
            
    ax.axis('equal')
    fig.tight_layout()
    
    canvas = FigureCanvasTkAgg(fig, master=parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
    plt.close(fig)


# =====================================================================
# VERİTABANI KATMANI
# =====================================================================
class Database:
    @staticmethod
    def get_connection():
        return sqlite3.connect(DB_FILE)

    @classmethod
    def initialize(cls):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    city TEXT DEFAULT '',
                    district TEXT DEFAULT '',
                    theme TEXT DEFAULT 'Slate Koyu'
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS drought_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    temperature REAL,
                    humidity REAL,
                    precipitation REAL,
                    score REAL,
                    risk_level TEXT,
                    date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS water_consumption (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount_liters REAL,
                    date TEXT,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
            cursor.execute("""
                         """)
            # Migration/Check if city_monthly_data has old schema
            cursor.execute("PRAGMA table_info(city_monthly_data)")
            m_cols = [row[1] for row in cursor.fetchall()]
            if m_cols and 'temperature' not in m_cols:
                cursor.execute("DROP TABLE city_monthly_data")

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS city_monthly_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city TEXT,
                    year INTEGER,
                    month INTEGER,
                    temperature REAL,
                    humidity REAL,
                    precipitation REAL,
                    dam_fullness REAL,
                    score REAL,
                    UNIQUE(city, year, month)
                )
            """)
            
            # Migration
            cursor.execute("PRAGMA table_info(users)")
            cols = [row[1] for row in cursor.fetchall()]
            if 'city' not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN city TEXT DEFAULT ''")
            if 'district' not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN district TEXT DEFAULT ''")
            if 'theme' not in cols:
                cursor.execute("ALTER TABLE users ADD COLUMN theme TEXT DEFAULT 'Slate Koyu'")
            
            # Populate yearly drought if empty
            cursor.execute("SELECT COUNT(*) FROM city_yearly_drought")
            if cursor.fetchone()[0] == 0:
                import random
                rng = random.Random(42)
                for city_name in ALL_CITIES_GEOGRAPHY:
                    temp_base, hum_base, prec_base = get_city_climate_defaults(city_name)
                    for year in range(2020, 2026):
                        t_var = rng.uniform(-2.5, 2.5)
                        h_var = rng.uniform(-10.0, 10.0)
                        p_var = rng.uniform(-20.0, 20.0)
                        
                        temp = max(-10.0, round(temp_base + t_var, 1))
                        hum = max(0.0, min(100.0, round(hum_base + h_var, 1)))
                        prec = max(0.0, round(prec_base + p_var, 1))
                        
                        score = DroughtAnalysisEngine.calculate_score(temp, hum, prec)
                        
                        cursor.execute("""
                            INSERT INTO city_yearly_drought 
                            (city, year, temperature, humidity, precipitation, score)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (city_name, year, temp, hum, prec, score))
            
            # Populate monthly data if empty
            cursor.execute("SELECT COUNT(*) FROM city_monthly_data")
            if cursor.fetchone()[0] == 0:
                import random
                rng = random.Random(42)
                for city_name in ALL_CITIES_GEOGRAPHY:
                    temp_base, hum_base, prec_base = get_city_climate_defaults(city_name)
                    for year in range(2020, 2026):
                        for month in range(1, 13):
                            if month in [12, 1, 2]: # Winter
                                t_val = temp_base - 12.0 + rng.uniform(-2.0, 2.0)
                                h_val = hum_base + 15.0 + rng.uniform(-5.0, 5.0)
                                season_prec_factor = rng.uniform(1.3, 1.8)
                                season_dam_factor = rng.uniform(0.6, 0.8)
                            elif month in [3, 4, 5]: # Spring
                                t_val = temp_base - 3.0 + rng.uniform(-2.0, 2.0)
                                h_val = hum_base + 5.0 + rng.uniform(-5.0, 5.0)
                                season_prec_factor = rng.uniform(1.0, 1.4)
                                season_dam_factor = rng.uniform(0.75, 0.95)
                            elif month in [6, 7, 8]: # Summer
                                t_val = temp_base + 8.0 + rng.uniform(-2.0, 2.0)
                                h_val = hum_base - 15.0 + rng.uniform(-5.0, 5.0)
                                season_prec_factor = rng.uniform(0.1, 0.4)
                                season_dam_factor = rng.uniform(0.3, 0.55)
                            else: # Autumn
                                t_val = temp_base + 2.0 + rng.uniform(-2.0, 2.0)
                                h_val = hum_base + rng.uniform(-5.0, 5.0)
                                season_prec_factor = rng.uniform(0.7, 1.1)
                                season_dam_factor = rng.uniform(0.4, 0.65)
                                
                            monthly_temp = round(t_val, 1)
                            monthly_hum = max(0.0, min(100.0, round(h_val, 1)))
                            monthly_prec = max(0.0, round(prec_base * season_prec_factor + rng.uniform(-10.0, 10.0), 1))
                            monthly_dam = max(0.0, min(100.0, round(100.0 * season_dam_factor + rng.uniform(-5.0, 5.0), 1)))
                            
                            monthly_score = DroughtAnalysisEngine.calculate_score(monthly_temp, monthly_hum, monthly_prec)
                            
                            cursor.execute("""
                                INSERT INTO city_monthly_data
                                (city, year, month, temperature, humidity, precipitation, dam_fullness, score)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """, (city_name, year, month, monthly_temp, monthly_hum, monthly_prec, monthly_dam, monthly_score))
            conn.commit()

    @classmethod
    def register_user(cls, username, password):
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        try:
            with cls.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, city, district, theme) VALUES (?, ?, '', '', 'Slate Koyu')",
                    (username, password_hash)
                )
                conn.commit()
                # Düzeltildi: Yeni kullanıcı tamamen sıfırdan ve temiz başlar, mock veri eklenmez
                return True
        except sqlite3.IntegrityError:
            return False

    @classmethod
    def login_user(cls, username, password):
        password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, theme FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            row = cursor.fetchone()
            return row if row else None

    @classmethod
    def update_profile(cls, user_id, city, district):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE users SET city = ?, district = ? WHERE id = ?",
                (city, district, user_id)
            )
            conn.commit()

    @classmethod
    def get_user_profile(cls, user_id):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, city, district, theme FROM users WHERE id = ?", (user_id,))
            return cursor.fetchone()

    @classmethod
    def save_analysis(cls, user_id, temp, humidity, precipitation, score, risk_level):
        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO drought_analyses 
                (user_id, temperature, humidity, precipitation, score, risk_level, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, temp, humidity, precipitation, score, risk_level, now_str))
            conn.commit()

    @classmethod
    def get_last_analysis(cls, user_id):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT score, risk_level, date, temperature, humidity, precipitation 
                FROM drought_analyses 
                WHERE user_id = ? 
                ORDER BY id DESC LIMIT 1
            """, (user_id,))
            return cursor.fetchone()

    @classmethod
    def get_analysis_history(cls, user_id, limit=5):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT score, risk_level, date 
                FROM drought_analyses 
                WHERE user_id = ? 
                ORDER BY id DESC LIMIT ?
            """, (user_id, limit))
            return cursor.fetchall()

    @classmethod
    def save_water_consumption(cls, user_id, amount_liters):
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM water_consumption WHERE user_id = ? AND date = ?", 
                (user_id, date_str)
            )
            row = cursor.fetchone()
            if row:
                cursor.execute(
                    "UPDATE water_consumption SET amount_liters = ? WHERE id = ?",
                    (amount_liters, row[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO water_consumption (user_id, amount_liters, date) VALUES (?, ?, ?)",
                    (user_id, amount_liters, date_str)
                )
            conn.commit()

    @classmethod
    def add_water_consumption(cls, user_id, amount_liters):
        date_str = datetime.date.today().strftime("%Y-%m-%d")
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, amount_liters FROM water_consumption WHERE user_id = ? AND date = ?", 
                (user_id, date_str)
            )
            row = cursor.fetchone()
            if row:
                new_total = row[1] + amount_liters
                cursor.execute(
                    "UPDATE water_consumption SET amount_liters = ? WHERE id = ?",
                    (new_total, row[0])
                )
            else:
                cursor.execute(
                    "INSERT INTO water_consumption (user_id, amount_liters, date) VALUES (?, ?, ?)",
                    (user_id, amount_liters, date_str)
                )
            conn.commit()

    @classmethod
    def get_last_water_consumption(cls, user_id):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT amount_liters, date 
                FROM water_consumption 
                WHERE user_id = ? 
                ORDER BY date DESC, id DESC LIMIT 1
            """, (user_id,))
            return cursor.fetchone()

    @classmethod
    def get_water_history(cls, user_id, limit=7):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT amount_liters, date 
                FROM water_consumption 
                WHERE user_id = ? 
                ORDER BY date DESC LIMIT ?
            """, (user_id, limit))
            return cursor.fetchall()[::-1]

    @classmethod
    def reset_water_consumption(cls, user_id):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM water_consumption WHERE user_id = ?", (user_id,))
            conn.commit()

    @classmethod
    def reset_user_data(cls, user_id):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM drought_analyses WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM water_consumption WHERE user_id = ?", (user_id,))
            cursor.execute("UPDATE users SET city = '', district = '' WHERE id = ?", (user_id,))
            conn.commit()

    @classmethod
    def delete_account(cls, user_id):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            cursor.execute("DELETE FROM drought_analyses WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM water_consumption WHERE user_id = ?", (user_id,))
            conn.commit()

    @classmethod
    def get_city_yearly_drought(cls, city_name):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT year, temperature, humidity, precipitation, score 
                FROM city_yearly_drought 
                WHERE city = ? 
                ORDER BY year ASC
            """, (city_name,))
            return cursor.fetchall()

    @classmethod
    def get_city_year_detail(cls, city_name, year):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT temperature, humidity, precipitation, score 
                FROM city_yearly_drought 
                WHERE city = ? AND year = ?
            """, (city_name, year))
            return cursor.fetchone()

    @classmethod
    def get_city_monthly_data(cls, city_name, year):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT month, precipitation, dam_fullness, temperature, humidity, score 
                FROM city_monthly_data 
                WHERE city = ? AND year = ? 
                ORDER BY month ASC
            """, (city_name, year))
            return cursor.fetchall()

    @classmethod
    def get_city_monthly_data_range(cls, city_name, start_year, start_month, end_year, end_month):
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT year, month, temperature, humidity, precipitation, score, dam_fullness
                FROM city_monthly_data
                WHERE city = ? AND (year * 100 + month) >= ? AND (year * 100 + month) <= ?
                ORDER BY year ASC, month ASC
            """, (city_name, start_year * 100 + start_month, end_year * 100 + end_month))
            return cursor.fetchall()


# =====================================================================
# HESAP MOTORU
# =====================================================================
class DroughtAnalysisEngine:
    @staticmethod
    def calculate_score(temp, humidity, precipitation):
        score = (temp * 0.5) + ((100 - humidity) * 0.3) + ((200 - precipitation) * 0.2)
        return max(0.0, round(score, 1))

    @staticmethod
    def get_risk_level(score):
        if score < 35:
            return "Düşük Risk"
        elif score < 60:
            return "Orta Risk"
        else:
            return "Yüksek Risk"

    @staticmethod
    def estimate_economic_impact(risk_level):
        if risk_level == "Düşük Risk":
            return {"yield_loss": 5, "price_increase": 3}
        elif risk_level == "Orta Risk":
            return {"yield_loss": 15, "price_increase": 10}
        else:
            return {"yield_loss": 30, "price_increase": 25}

    @staticmethod
    def get_recommendations(risk_level):
        if risk_level == "Düşük Risk":
            return {
                "water_saving": [
                    "Evsel su tüketiminde gereksiz akıntıları önleyin.",
                    "Musluklara debi düşürücü perlatör takın.",
                    "Çamaşır makinelerini tam doldurmadan çalıştırmayın."
                ],
                "agriculture": [
                    "Damlama sulama sistemlerinin genel kontrollerini yapın.",
                    "Toprak nemini korumak için hafif malçlama yapabilirsiniz.",
                    "Sulama zamanlarını sabah erken veya akşam geç saatlere planlayın."
                ],
                "sustainability": [
                    "Yağmur suyu depolama tanklarını gözden geçirin.",
                    "Bireysel su ayak izinizi takip etmeye başlayın."
                ]
            }
        elif risk_level == "Orta Risk":
            return {
                "water_saving": [
                    "Bahçe sulamasında hortum yerine damlama kullanın.",
                    "Sebze ve meyve yıkama sularını çiçek sulamada değerlendirin.",
                    "Duş sürelerini 5 dakikanın altına indirmeye çalışın."
                ],
                "agriculture": [
                    "Buharlaşma kayıplarını en aza indirmek için malçlama yapın.",
                    "Gece sulamasına öncelik vererek buharlaşmayı azaltın.",
                    "Bitkileri aşırı gübrelemekten kaçının."
                ],
                "sustainability": [
                    "Yağmur suyu hasadı ünitelerini aktif olarak kullanın.",
                    "Gri su geri kazanımı imkanlarını araştırın."
                ]
            }
        else:
            return {
                "water_saving": [
                    "Acil durum harici su tüketimlerini tamamen kısıtlayın.",
                    "Araba ve balkon yıkama gibi işlemleri erteleyin.",
                    "Evdeki tüm su sızıntılarını anında onarın."
                ],
                "agriculture": [
                    "Bitkilerde kontrollü su kısıtlamasına gidin.",
                    "Vahşi sulamayı tamamen durdurun.",
                    "Kuraklığa dayanıklı, az su isteyen ürün desenlerine geçin."
                ],
                "sustainability": [
                    "Bölgesel su kaynakları durum planlarına harfiyen uyun.",
                    "İklim değişikliği ve kuraklık eylem planlarını destekleyin."
                ]
            }


class DroughtAIPredictor:
    @staticmethod
    def fit_and_project(city_name, forecast_months=6):
        history = Database.get_city_monthly_data_range(city_name, 2020, 1, 2025, 12)
        if not history:
            return None
            
        n = len(history)
        xs = list(range(n))
        
        temps = [row[2] for row in history]
        hums = [row[3] for row in history]
        precs = [row[4] for row in history]
        scores = [row[5] for row in history]
        dams = [row[6] for row in history]
        
        def calc_slope_intercept(x, y):
            n_val = len(x)
            sum_x = sum(x)
            sum_y = sum(y)
            sum_xx = sum(xi**2 for xi in x)
            sum_xy = sum(xi*yi for xi, yi in zip(x, y))
            denom = (n_val * sum_xx - sum_x**2)
            if denom == 0:
                return 0.0, sum_y / n_val
            m_val = (n_val * sum_xy - sum_x * sum_y) / denom
            c_val = (sum_y - m_val * sum_x) / n_val
            return m_val, c_val
            
        m_t, c_t = calc_slope_intercept(xs, temps)
        m_h, c_h = calc_slope_intercept(xs, hums)
        m_p, c_p = calc_slope_intercept(xs, precs)
        
        month_groups = {m: [] for m in range(1, 13)}
        for row in history:
            y, m, temp, hum, prec, score, dam = row
            month_groups[m].append((temp, hum, prec, dam))
            
        last_row = history[-1]
        last_year, last_month = last_row[0], last_row[1]
        last_score = last_row[5]
        
        projections = []
        curr_year, curr_month = last_year, last_month
        
        for step in range(1, forecast_months + 1):
            curr_month += 1
            if curr_month > 12:
                curr_month = 1
                curr_year += 1
                
            avg_t = sum(item[0] for item in month_groups[curr_month]) / len(month_groups[curr_month])
            avg_h = sum(item[1] for item in month_groups[curr_month]) / len(month_groups[curr_month])
            avg_p = sum(item[2] for item in month_groups[curr_month]) / len(month_groups[curr_month])
            avg_d = sum(item[3] for item in month_groups[curr_month]) / len(month_groups[curr_month])
            
            forecast_index = n + step - 1
            history_center = n / 2.0
            steps_ahead = forecast_index - history_center
            
            fc_t = round(avg_t + m_t * steps_ahead, 1)
            fc_h = max(5.0, min(100.0, round(avg_h + m_h * steps_ahead, 1)))
            fc_p = max(0.0, round(avg_p + m_p * steps_ahead, 1))
            fc_d = max(0.0, min(100.0, round(avg_d + calc_slope_intercept(xs, dams)[0] * steps_ahead, 1)))
            
            fc_score = DroughtAnalysisEngine.calculate_score(fc_t, fc_h, fc_p)
            projections.append({
                "year": curr_year,
                "month": curr_month,
                "temperature": fc_t,
                "humidity": fc_h,
                "precipitation": fc_p,
                "dam_fullness": fc_d,
                "score": fc_score,
                "risk_level": DroughtAnalysisEngine.get_risk_level(fc_score)
            })
            
        s_last = max(1.0, last_score)
        
        ch_1 = projections[0]
        ch_3 = projections[2] if len(projections) >= 3 else projections[-1]
        ch_6 = projections[5] if len(projections) >= 6 else projections[-1]
        
        pct_1 = ((ch_1["score"] - s_last) / s_last) * 100
        pct_3 = ((ch_3["score"] - s_last) / s_last) * 100
        pct_6 = ((ch_6["score"] - s_last) / s_last) * 100
        
        temp_annual_slope = m_t * 12
        prec_annual_slope = m_p * 12
        
        if pct_3 >= 0:
            explanation = (
                f"Son 6 yıllık veriler incelendiğinde, {city_name} için yıllık sıcaklık artış hızı "
                f"+{temp_annual_slope:.1f}°C/yıl ve yağış azalma eğilimi {prec_annual_slope:.1f} mm/yıl olarak hesaplanmıştır. "
                f"Bu olumsuz iklim eğilimleri ve mevsimsel koşullar nedeniyle önümüzdeki 3 ay içerisinde "
                f"kuraklık risk skorunun %{pct_3:.1f} artması (%{ch_3['score']:.1f} seviyesine ulaşması) "
                f"ve '{ch_3['risk_level']}' seviyesinde seyretmesi beklenmektedir."
            )
        else:
            explanation = (
                f"Son 6 yıllık veriler incelendiğinde, {city_name} için yıllık sıcaklık artış hızı "
                f"+{temp_annual_slope:.1f}°C/yıl ve yağış azalma eğilimi {prec_annual_slope:.1f} mm/yıl olsa da, "
                f"önümüzdeki dönemdeki mevsimsel yağış ve sıcaklık geçişleri nedeniyle kuraklık risk skorunun "
                f"%{abs(pct_3):.1f} oranında azalması (%{ch_3['score']:.1f} seviyesine inmesi) beklenmektedir. "
                f"Ancak uzun vadeli genel iklim projeksiyonları risk seviyesinin hassas kalacağını öngörmektedir."
            )
            
        return {
            "projections": projections,
            "pct_1": round(pct_1, 1),
            "pct_3": round(pct_3, 1),
            "pct_6": round(pct_6, 1),
            "score_1": ch_1["score"],
            "score_3": ch_3["score"],
            "score_6": ch_6["score"],
            "risk_1": ch_1["risk_level"],
            "risk_3": ch_3["risk_level"],
            "risk_6": ch_6["risk_level"],
            "explanation": explanation
        }


# =====================================================================
# GÖSTERİŞLİ AKORDEON (Collapsible Card) BİLEŞENİ
# =====================================================================
class CollapsibleCard(tk.Frame):
    def __init__(self, parent, title, tc, **kwargs):
        super().__init__(parent, bg=tc["card"], bd=0, highlightthickness=0, **kwargs)
        self.tc = tc
        self.expanded = False
        
        self.header_frame = tk.Frame(self, bg=tc["card_accent"], cursor="hand2")
        self.header_frame.pack(fill="x")
        
        self.lbl_title = tk.Label(self.header_frame, text=title, font=("Segoe UI", 10, "bold"), fg=tc["text_primary"], bg=tc["card_accent"], padx=10, pady=8)
        self.lbl_title.pack(side="left")
        
        self.lbl_arrow = tk.Label(self.header_frame, text="▶", font=("Segoe UI", 10, "bold"), fg=tc["text_muted"], bg=tc["card_accent"], padx=10)
        self.lbl_arrow.pack(side="right")
        
        self.content_frame = tk.Frame(self, bg=tc["card"], padx=12, pady=10)
        
        self.header_frame.bind("<Button-1>", self.toggle)
        self.lbl_title.bind("<Button-1>", self.toggle)
        self.lbl_arrow.bind("<Button-1>", self.toggle)
        
    def toggle(self, event):
        if self.expanded:
            self.content_frame.pack_forget()
            self.lbl_arrow.config(text="▶")
            self.expanded = False
        else:
            self.content_frame.pack(fill="x")
            self.lbl_arrow.config(text="▼")
            self.expanded = True


# =====================================================================
# ANA MOBİL YERLEŞİM (Bottom Navigation Tab Bar + Sağ Üst Menü Dikey Çizgili)
# =====================================================================
class MainAppLayout(tk.Frame):
    def __init__(self, parent, controller):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        
        # --- HEADER (Üst Bar) ---
        self.header = tk.Frame(self, bg=tc["card"], height=50)
        self.header.pack(side="top", fill="x")
        self.header.pack_propagate(False)
        
        self.lbl_logo = tk.Label(self.header, text="🌾 Akıllı Kuraklık Risk Sistemi", font=("Segoe UI", 11, "bold"), fg=tc["text_primary"], bg=tc["card"])
        self.lbl_logo.pack(side="left", padx=10, fill="y")
        
        # Düzeltildi: Menü butonu sağ üst köşede ☰ olarak yerleştirildi
        self.btn_menu = tk.Button(
            self.header, text="☰", font=("Segoe UI", 14, "bold"),
            fg=tc["text_primary"], bg=tc["card"], activebackground=tc["card"],
            activeforeground=tc["primary_btn"], bd=0, cursor="hand2", command=self.open_menu_tab
        )
        self.btn_menu.pack(side="right", padx=15, fill="y")
        
        # --- İÇERİK BÖLGESİ ---
        self.content_area = tk.Frame(self, bg=tc["bg"])
        self.content_area.pack(side="top", fill="both", expand=True)
        
        # --- BOTTOM NAV (Alt Menü - 4 Sekmeye Düşürüldü) ---
        self.bottom_nav = tk.Frame(self, bg=tc["card"], height=60)
        self.bottom_nav.pack(side="bottom", fill="x")
        self.bottom_nav.pack_propagate(False)
        
        self.nav_items = [
            ("🏠\nÖzet", "dashboard"),
            ("🗺️\nHarita", "map"),
            ("🤖\nAI & Analiz", "analysis"),
            ("📈\nGrafikler", "charts"),
            ("💧\nSu Takibi", "water")
        ]
        
        self.nav_buttons = {}
        for idx, (label, tab_name) in enumerate(self.nav_items):
            self.bottom_nav.columnconfigure(idx, weight=1)
            btn = tk.Button(
                self.bottom_nav, text=label, font=("Segoe UI", 8),
                fg=tc["text_muted"], bg=tc["card"], activebackground=tc["card"],
                activeforeground=tc["primary_btn"], bd=0, relief="flat", cursor="hand2",
                command=lambda name=tab_name: self.switch_tab(name)
            )
            btn.grid(row=0, column=idx, sticky="nsew", pady=5)
            self.nav_buttons[tab_name] = btn
            
        self.active_tab = None
        self.switch_tab("dashboard")

    def switch_tab(self, tab_name):
        if self.active_tab == tab_name:
            return
            
        for w in self.content_area.winfo_children():
            w.destroy()
            
        tc = self.controller.theme_colors
        for name, btn in self.nav_buttons.items():
            btn.config(fg=tc["text_muted"])
            
        if tab_name in self.nav_buttons:
            self.nav_buttons[tab_name].config(fg=tc["primary_btn"])
            
        self.active_tab = tab_name
        
        if tab_name == "dashboard":
            DashboardTab(self.content_area, self.controller)
        elif tab_name == "map":
            DroughtMapTab(self.content_area, self.controller, self)
        elif tab_name == "analysis":
            AnalysisTab(self.content_area, self.controller, self)
        elif tab_name == "charts":
            ChartsTab(self.content_area, self.controller)
        elif tab_name == "water":
            WaterTrackerTab(self.content_area, self.controller, self)
        elif tab_name == "menu":
            MenuTab(self.content_area, self.controller, self)
        elif tab_name == "recommendations_page":
            RecommendationsScreen(self.content_area, self.controller, self)

    def open_menu_tab(self):
        """Sağ üst menü ikonuna tıklandığında menü sekmesini açar."""
        self.switch_tab("menu")


# =====================================================================
# SEKME 1 - ÖZET (Dashboard & Görsel Haberler & Su Dostu Damlacık)
# =====================================================================
class DashboardTab(tk.Frame):
    def __init__(self, parent, controller):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.user_id = controller.current_user_id
        self.pack(fill="both", expand=True)
        
        scroll = ScrollableFrame(self, bg_color=tc["bg"])
        scroll.pack(fill="both", expand=True)
        sf = scroll.scrollable_frame
        
        # Karşılama ve Konum Risk Eşlemesi
        p_data = Database.get_user_profile(self.user_id)
        city_name = p_data[1] if p_data else ""
        if city_name in ALL_CITIES_GEOGRAPHY:
            score, risk, col = get_city_drought_info(city_name)
            city_str = f" ({p_data[2]}, {city_name})"
            location_status_text = f"Risk Seviyesi: {risk} (Skor: {score}/100)"
            location_status_color = col
        else:
            city_str = " (Konum Seçilmedi)"
            location_status_text = "Risk analizi için lütfen menüden konum tanımlayın."
            location_status_color = tc["text_muted"]
            
        tk.Label(sf, text=f"Hoş Geldiniz, {controller.current_username} 👋", font=("Segoe UI", 14, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(15, 2))
        tk.Label(sf, text=f"📍 Konumunuz:{city_str}", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # --- EK BİLEŞEN: SU DOSTU DAMLACIK (Talep Edilen İpucu Balyozu) ---
        c_friend = Card(sf, accent_color=tc["primary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
        c_friend.pack(fill="x", padx=15, pady=6)
        ff = c_friend.content_frame
        
        random_tip = random.choice(WATER_FRIEND_TIPS)
        tk.Label(ff, text="Su Dostu Damlacık 💧", font=("Segoe UI", 10, "bold"), fg=tc["primary_btn"], bg=tc["card"], anchor="w").pack(fill="x")
        tk.Label(ff, text=random_tip, font=("Segoe UI", 8, "italic"), fg=tc["text_primary"], bg=tc["card"], wraplength=330, justify="left", anchor="w").pack(fill="x", pady=(3, 0))

        # Kullanıcı Verileri
        last_anal = Database.get_last_analysis(self.user_id)
        last_water = Database.get_last_water_consumption(self.user_id)
        
        # Konum kuraklığı
        c_loc = Card(sf, title="Konumunuzun Kuraklık Durumu", accent_color=location_status_color, card_bg=tc["card"], text_color=tc["text_primary"])
        c_loc.pack(fill="x", padx=15, pady=6)
        lf = c_loc.content_frame
        tk.Label(lf, text=location_status_text, font=("Segoe UI", 10, "bold"), fg=location_status_color, bg=tc["card"], anchor="w").pack(fill="x")
        if city_name in ALL_CITIES_GEOGRAPHY:
            c_temp, c_hum, c_prec = get_city_climate_defaults(city_name)
            tk.Label(lf, text=f"Sıcaklık: {c_temp}°C | Nem: %{c_hum} | Yağış: {c_prec}mm", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"], anchor="w").pack(fill="x", pady=(3, 0))

        # Son yapılan analiz (Başlangıçta sıfırlanmış olarak gelir)
        if last_anal:
            score, risk, date_str, temp, hum, prec = last_anal
            col = tc["secondary_btn"] if risk == "Düşük Risk" else tc["accent"] if risk == "Orta Risk" else tc["danger_btn"]
            
            c_anal = Card(sf, title="Son Yaptığınız Kişisel Analiz", accent_color=col, card_bg=tc["card"], text_color=tc["text_primary"])
            c_anal.pack(fill="x", padx=15, pady=6)
            f = c_anal.content_frame
            
            r_frame = tk.Frame(f, bg=tc["card"])
            r_frame.pack(fill="x", pady=2)
            tk.Label(r_frame, text=f"Skor: {score}/100", font=("Segoe UI", 11, "bold"), fg=tc["text_primary"], bg=tc["card"]).pack(side="left")
            tk.Label(r_frame, text=risk, font=("Segoe UI", 10, "bold"), fg=col, bg=tc["card"]).pack(side="right")
            
            tk.Label(f, text=f"Sıcaklık: {temp}°C  |  Nem: %{hum}  |  Yağış: {prec}mm", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
            
            eco = DroughtAnalysisEngine.estimate_economic_impact(risk)
            c_eco = Card(sf, title="Ekonomik Etki Öngörüleri", accent_color=tc["primary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
            c_eco.pack(fill="x", padx=15, pady=6)
            ef = c_eco.content_frame
            
            row1 = tk.Frame(ef, bg=tc["card"])
            row1.pack(fill="x", pady=1)
            tk.Label(row1, text="Tarımsal Verim Kaybı:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["card"]).pack(side="left")
            tk.Label(row1, text=f"%{eco['yield_loss']}", font=("Segoe UI", 9, "bold"), fg=tc["danger_btn"], bg=tc["card"]).pack(side="right")
            
            row2 = tk.Frame(ef, bg=tc["card"])
            row2.pack(fill="x", pady=1)
            tk.Label(row2, text="Gıda Fiyat Artış Hızı:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["card"]).pack(side="left")
            tk.Label(row2, text=f"+ %{eco['price_increase']}", font=("Segoe UI", 9, "bold"), fg=tc["accent"], bg=tc["card"]).pack(side="right")
        else:
            # Düzeltildi: Yeni üye girişi yaptığında başlangıçta analiz verileri tertemiz başlar
            c_no = Card(sf, title="Son Yaptığınız Kişisel Analiz", accent_color=tc["accent"], card_bg=tc["card"], text_color=tc["text_primary"])
            c_no.pack(fill="x", padx=15, pady=6)
            tk.Label(c_no.content_frame, text="Henüz kişisel bir analiz yapmadınız. Başlamak için alt menüden 'Analiz' sekmesini kullanın.", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"], wraplength=330, justify="left").pack(pady=5)

        # Su tüketimi (Başlangıçta sıfırlanmış olarak gelir)
        c_water = Card(sf, title="Günlük Su Tüketim Durumu", accent_color=tc["secondary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
        c_water.pack(fill="x", padx=15, pady=6)
        wf = c_water.content_frame
        
        chart_f = tk.Frame(wf, bg=tc["card"], height=130)
        chart_f.pack(fill="x", pady=5)
        
        if last_water:
            amt, date_w = last_water
            status = "Normal Tüketim" if amt <= 150 else "Yüksek Tüketim!"
            col_w = tc["secondary_btn"] if amt <= 150 else tc["danger_btn"]
            
            tk.Label(wf, text=status, font=("Segoe UI", 9, "bold"), fg=col_w, bg=tc["card"]).pack(pady=(2, 0))
            draw_water_circular_chart(chart_f, amt, tc)
        else:
            tk.Label(wf, text="Bugün için henüz tüketim kaydı girilmedi.", font=("Segoe UI", 8, "italic"), fg=tc["text_muted"], bg=tc["card"]).pack(pady=(2, 0))
            draw_water_circular_chart(chart_f, 0.0, tc)

        # Görsel Haberler
        tk.Label(sf, text="Kuraklık & Su Gündemi", font=("Segoe UI", 12, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(15, 5))
        
        news_data = [
            ("Baraj Doluluk Oranları Düşüşte!", "İstanbul barajlarında ortalama doluluk %30 seviyelerine geriledi. Yetkililer tasarruf çağrısını yeniledi.", "news_baraj.png"),
            ("Modern Damla Sulamaya Hibe", "Tarım Bakanlığı kuraklıkla mücadele için basınçlı damla sulama projelerine %50 devlet desteği sunuyor.", "news_sulama.png"),
            ("Bireysel Su Tasarrufu Kampanyası", "Musluklara perlatör takılması ve duş sürelerinin 1 dk azaltılmasıyla yılda milyonlarca ton su kurtarılabilir.", "news_tasarruf.png")
        ]
        
        self.image_refs = []
        for title, desc, img_path in news_data:
            c_news = Card(sf, card_bg=tc["card"])
            c_news.pack(fill="x", padx=15, pady=6)
            nf = c_news.content_frame
            
            row_news = tk.Frame(nf, bg=tc["card"])
            row_news.pack(fill="x")
            
            try:
                img_pil = Image.open(img_path)
                img_tk = ImageTk.PhotoImage(img_pil)
                self.image_refs.append(img_tk)
                
                lbl_img = tk.Label(row_news, image=img_tk, bg=tc["card"], width=90, height=70)
                lbl_img.pack(side="left", padx=(0, 10))
            except Exception as e:
                lbl_img = tk.Frame(row_news, bg=tc["input_bg"], width=90, height=70)
                lbl_img.pack(side="left", padx=(0, 10))
                lbl_img.pack_propagate(False)
                tk.Label(lbl_img, text="Haber", fg=tc["text_muted"], bg=tc["input_bg"]).pack(expand=True)
                
            text_frame = tk.Frame(row_news, bg=tc["card"])
            text_frame.pack(side="right", fill="both", expand=True)
            
            tk.Label(text_frame, text=title, font=("Segoe UI", 9, "bold"), fg=tc["text_primary"], bg=tc["card"], wraplength=210, justify="left", anchor="w").pack(fill="x")
            tk.Label(text_frame, text=desc, font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"], wraplength=210, justify="left", anchor="w").pack(fill="x", pady=(2, 0))
            
        tk.Frame(sf, bg=tc["bg"], height=20).pack()


# =====================================================================
# SEKME 2 - TÜRKİYE KURAKLIK HARİTASI & ŞEHİR KARŞILAŞTIRMA (2'li Sekmeli)
# =====================================================================
class DroughtMapTab(tk.Frame):
    def __init__(self, parent, controller, main_layout):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.main_layout = main_layout
        self.pack(fill="both", expand=True)
        
        # --- SEGMENT CONTROL (Üst Düğmeler: Harita Görünümü / Şehir Karşılaştırma) ---
        self.seg_bar = tk.Frame(self, bg=tc["card"], height=40)
        self.seg_bar.pack(side="top", fill="x")
        self.seg_bar.pack_propagate(False)
        
        self.btn_map_view = tk.Button(
            self.seg_bar, text="Risk Haritası 🗺️", font=("Segoe UI", 9, "bold"),
            fg=tc["primary_btn"], bg=tc["card"], activebackground=tc["card"],
            activeforeground=tc["primary_btn"], bd=0, relief="flat", cursor="hand2",
            command=self.show_map_view
        )
        self.btn_map_view.pack(side="left", fill="both", expand=True)
        
        self.btn_comp_view = tk.Button(
            self.seg_bar, text="Şehir Karşılaştırma 📊", font=("Segoe UI", 9, "bold"),
            fg=tc["text_muted"], bg=tc["card"], activebackground=tc["card"],
            activeforeground=tc["primary_btn"], bd=0, relief="flat", cursor="hand2",
            command=self.show_comparison_view
        )
        self.btn_comp_view.pack(side="right", fill="both", expand=True)
        
        # Sekme kapsayıcısı
        self.view_container = tk.Frame(self, bg=tc["bg"])
        self.view_container.pack(fill="both", expand=True)
        
        self.active_sub_view = None
        self.show_map_view()

    def show_map_view(self):
        if self.active_sub_view == "map":
            return
        for w in self.view_container.winfo_children():
            w.destroy()
        self.active_sub_view = "map"
        
        tc = self.controller.theme_colors
        self.btn_map_view.config(fg=tc["primary_btn"])
        self.btn_comp_view.config(fg=tc["text_muted"])
        
        DroughtMapView(self.view_container, self.controller, self.main_layout)

    def show_comparison_view(self):
        if self.active_sub_view == "comparison":
            return
        for w in self.view_container.winfo_children():
            w.destroy()
        self.active_sub_view = "comparison"
        
        tc = self.controller.theme_colors
        self.btn_map_view.config(fg=tc["text_muted"])
        self.btn_comp_view.config(fg=tc["primary_btn"])
        
        CityComparisonView(self.view_container, self.controller)


class DroughtMapView(tk.Frame):
    """81 ilin tamamını Canvas üzerinde meteorolojik yoğunlukta çizen harita görünümü."""
    def __init__(self, parent, controller, main_layout):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.main_layout = main_layout
        self.pack(fill="both", expand=True)
        
        scroll = ScrollableFrame(self, bg_color=tc["bg"])
        scroll.pack(fill="both", expand=True)
        sf = scroll.scrollable_frame
        
        tk.Label(sf, text="81 İl Kuraklık Risk Dağılımı", font=("Segoe UI", 13, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(10, 2))
        tk.Label(sf, text="İllere dokunarak kuraklık analiz grafiğini görüntüleyin:", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(0, 5))
        
        m_card = Card(sf, card_bg=tc["card"])
        m_card.pack(fill="x", padx=15, pady=5)
        mcf = m_card.content_frame
        
        # Canvas Boyutları
        self.canvas = tk.Canvas(mcf, width=370, height=180, bg=tc["card"], bd=0, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Türkiye şematik poligonu
        turkey_outline = [
            (15, 65), (25, 27), (71, 35), (128, 27), (185, 12), (289, 32),
            (355, 27), (370, 72), (365, 135), (298, 140), (208, 165), (195, 147),
            (110, 152), (43, 147), (25, 102)
        ]
        self.canvas.create_polygon(turkey_outline, fill=tc["input_bg"], outline=tc["text_muted"], width=1)
        
        # 81 İlin tamamını formüle göre dinamik renkli nokta olarak çiz (Çakışmaları önlemek için)
        for city_name, (lon, lat, _) in ALL_CITIES_GEOGRAPHY.items():
            # Enlem/boylamı canvas koordinatlarına oranla
            cx = 15 + (lon - 26.0) * 18.2
            cy = 165 - (lat - 36.0) * 23.5
            
            _, _, color = get_city_drought_info(city_name)
            
            # Küçük nokta çizimi (Daha sık ve temiz durması için 3.5px yarıçap)
            self.canvas.create_oval(cx-3.5, cy-3.5, cx+3.5, cy+3.5, fill=color, outline=tc["card"], width=0.5, tags=city_name)
            
            # Tıklama olayı bağlama
            self.canvas.tag_bind(city_name, "<Button-1>", lambda e, name=city_name: self.city_clicked(name))
            
        # Bilgi Paneli (Matplotlib mini göstergeli)
        self.info_card = Card(sf, title="Şehir Detayı", card_bg=tc["card"], text_color=tc["text_primary"])
        self.info_card.pack(fill="x", padx=15, pady=(10, 30))
        self.inf_f = self.info_card.content_frame
        
        self.lbl_default = tk.Label(self.inf_f, text="Grafikleri görüntülemek için haritadaki bir noktaya tıklayın.", font=("Segoe UI", 8, "italic"), fg=tc["text_muted"], bg=tc["card"], justify="center")
        self.lbl_default.pack(pady=15, fill="x")

    def city_clicked(self, city_name):
        for w in self.inf_f.winfo_children():
            w.destroy()
            
        tc = self.controller.theme_colors
        temp, hum, prec = get_city_climate_defaults(city_name)
        score, risk, col = get_city_drought_info(city_name)
        
        tk.Label(self.inf_f, text=f"📍 {city_name} Detay Analizi", font=("Segoe UI", 11, "bold"), fg=tc["text_primary"], bg=tc["card"], anchor="w").pack(fill="x", pady=(0, 2))
        
        det_row = tk.Frame(self.inf_f, bg=tc["card"])
        det_row.pack(fill="x", pady=2)
        tk.Label(det_row, text=f"Sıcaklık: {temp}°C | Nem: %{hum} | Yağış: {prec}mm", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"]).pack(side="left")
        
        # Grafik Entegrasyonu
        chart_frame = tk.Frame(self.inf_f, bg=tc["card"], height=90)
        chart_frame.pack(fill="x", pady=5)
        draw_city_gauge_chart(chart_frame, score, tc)
        
        # Aksiyon Butonları
        act_frame = tk.Frame(self.inf_f, bg=tc["card"])
        act_frame.pack(fill="x", pady=(10, 0))
        
        CustomButton(
            act_frame, text="Profil Konumu Yap 📍", bg_color=tc["secondary_btn"],
            command=lambda: self.set_as_profile_location(city_name)
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        CustomButton(
            act_frame, text="Analiz Formuna Aktar 📈", bg_color=tc["primary_btn"],
            command=lambda: self.export_to_analysis(city_name, temp, hum, prec)
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def set_as_profile_location(self, city):
        Database.update_profile(self.controller.current_user_id, city, "Merkez")
        messagebox.showinfo("Başarılı", f"Profil konumunuz {city} olarak güncellendi. Dashboard sayfasından da takip edebilirsiniz.")

    def export_to_analysis(self, city, temp, hum, prec):
        self.main_layout.switch_tab("analysis")
        tab_obj = self.main_layout.content_area.winfo_children()[0]
        if isinstance(tab_obj, AnalysisTab):
            tab_obj.cb_city.set(city)
            tab_obj.ent_temp.delete(0, tk.END)
            tab_obj.ent_temp.insert(0, str(temp))
            tab_obj.ent_hum.delete(0, tk.END)
            tab_obj.ent_hum.insert(0, str(hum))
            tab_obj.ent_prec.delete(0, tk.END)
            tab_obj.ent_prec.insert(0, str(prec))
            tab_obj.city_selected(None)


class CityComparisonView(tk.Frame):
    """Talep Edilen Özellik: İki il arasında iklim ve skor kıyaslayan yan yana Matplotlib panel."""
    def __init__(self, parent, controller):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        scroll = ScrollableFrame(self, bg_color=tc["bg"])
        scroll.pack(fill="both", expand=True)
        sf = scroll.scrollable_frame
        
        tk.Label(sf, text="Şehir Karşılaştırma Paneli", font=("Segoe UI", 13, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(10, 2))
        tk.Label(sf, text="Kıyaslamak istediğiniz iki şehri seçin:", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        c_card = Card(sf, card_bg=tc["card"])
        c_card.pack(fill="x", padx=15, pady=5)
        cf = c_card.content_frame
        
        # Seçim Kapsayıcısı
        sel_row = tk.Frame(cf, bg=tc["card"])
        sel_row.pack(fill="x", pady=5)
        
        cities_list = sorted(list(ALL_CITIES_GEOGRAPHY.keys()))
        
        # 1. Şehir
        f1 = tk.Frame(sel_row, bg=tc["card"])
        f1.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f1, text="1. Şehir", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
        self.cb_c1 = ttk.Combobox(f1, values=cities_list, state="readonly", font=("Segoe UI", 9))
        self.cb_c1.pack(fill="x", pady=(2, 0))
        self.cb_c1.set("İstanbul")
        self.cb_c1.bind("<<ComboboxSelected>>", self.do_comparison)
        
        # 2. Şehir
        f2 = tk.Frame(sel_row, bg=tc["card"])
        f2.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f2, text="2. Şehir", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
        self.cb_c2 = ttk.Combobox(f2, values=cities_list, state="readonly", font=("Segoe UI", 9))
        self.cb_c2.pack(fill="x", pady=(2, 0))
        self.cb_c2.set("Ankara")
        self.cb_c2.bind("<<ComboboxSelected>>", self.do_comparison)
        
        # Grafik Alanı
        self.chart_container = tk.Frame(sf, bg=tc["bg"])
        self.chart_container.pack(fill="x", padx=15, pady=(10, 30))
        
        self.do_comparison(None)

    def do_comparison(self, event):
        for w in self.chart_container.winfo_children():
            w.destroy()
            
        c1 = self.cb_c1.get()
        c2 = self.cb_c2.get()
        
        if c1 == c2:
            tk.Label(self.chart_container, text="Lütfen iki farklı şehir seçin.", font=("Segoe UI", 9, "italic"), fg=self.controller.theme_colors["text_muted"], bg=self.controller.theme_colors["bg"], pady=20).pack()
            return
            
        # İklim ve skor bilgilerini getir
        t1, h1, p1 = get_city_climate_defaults(c1)
        s1, _, _ = get_city_drought_info(c1)
        
        t2, h2, p2 = get_city_climate_defaults(c2)
        s2, _, _ = get_city_drought_info(c2)
        
        # Matplotlib Double Bar Grafik Çizimi
        tc = self.controller.theme_colors
        plt.rcParams['text.color'] = tc["text_primary"]
        plt.rcParams['axes.labelcolor'] = tc["text_muted"]
        
        fig, ax = plt.subplots(figsize=(4.5, 3.2), facecolor=tc["card"])
        ax.set_facecolor(tc["card"])
        
        categories = ['Sıcaklık\n(°C)', 'Nem\n(%)', 'Yağış\n(mm)', 'Risk\nSkoru']
        vals_c1 = [t1, h1, p1, s1]
        vals_c2 = [t2, h2, p2, s2]
        
        x = [0, 1.2, 2.4, 3.6]
        width = 0.35
        
        # Çubukları çiz (Tema renklerini doğrudan entegre eder)
        bar1 = ax.bar([pos - width/2 for pos in x], vals_c1, width, label=c1, color=tc["primary_btn"])
        bar2 = ax.bar([pos + width/2 for pos in x], vals_c2, width, label=c2, color=tc["secondary_btn"])
        
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=8, color=tc["text_muted"])
        ax.tick_params(colors=tc["text_muted"])
        ax.legend(facecolor=tc["card"], edgecolor=tc["input_bg"], loc="upper right", fontsize=8)
        
        # Rakamları çubukların üzerine yaz
        for b in bar1 + bar2:
            h = b.get_height()
            ax.annotate(f'{int(h)}',
                        xy=(b.get_x() + b.get_width() / 2, h),
                        xytext=(0, 2),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=7, color=tc["text_primary"])
                        
        for spine in ax.spines.values():
            spine.set_color(tc["input_bg"])
            
        ax.set_title(f"{c1} vs {c2} Karşılaştırması", fontsize=9, color=tc["text_primary"], pad=5)
        ax.grid(True, color=tc["input_bg"], axis='y', linestyle=':', alpha=0.5)
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True)
        plt.close(fig)


# =====================================================================
# SEKME 3 - ANALİZ (81 İl Seçimi ve Anlık Skor Grafik Önizleme)
# =====================================================================
class AnalysisTab(tk.Frame):
    def __init__(self, parent, controller, main_layout):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.main_layout = main_layout
        self.user_id = controller.current_user_id
        self.pack(fill="both", expand=True)
        
        scroll = ScrollableFrame(self, bg_color=tc["bg"])
        scroll.pack(fill="both", expand=True)
        self.sf = scroll.scrollable_frame
        
        # Title
        tk.Label(self.sf, text="🤖 AI Kuraklık Tahmin & Analiz", font=("Segoe UI", 14, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(15, 2))
        tk.Label(self.sf, text="Yapay zeka geçmiş verileri analiz ederek kuraklık projeksiyonları üretir:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # Seçim Kartı
        sel_card = Card(self.sf, accent_color=tc["primary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
        sel_card.pack(fill="x", padx=15, pady=5)
        sc = sel_card.content_frame
        
        tk.Label(sc, text="Analiz Yapılacak Şehir", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(0, 2))
        
        p_data = Database.get_user_profile(self.user_id)
        saved_city = p_data[1] if (p_data and p_data[1]) else "İstanbul"
        
        sorted_cities = sorted(list(ALL_CITIES_GEOGRAPHY.keys()))
        self.cb_city = ttk.Combobox(sc, values=sorted_cities, state="readonly", font=("Segoe UI", 9))
        self.cb_city.pack(fill="x", pady=(0, 10))
        self.cb_city.set(saved_city)
        self.cb_city.bind("<<ComboboxSelected>>", self.city_selected)
        
        # Projeksiyon Grafik Kartı
        self.proj_card = Card(self.sf, title="Kuraklık Projeksiyon Grafiği (Son 12 Ay & Gelecek 6 Ay)", card_bg=tc["card"])
        self.proj_card.pack(fill="x", padx=15, pady=5)
        self.chart_container = self.proj_card.content_frame
        
        # Yapay Zeka Sonuç Özet Kartları Row
        self.cards_frame = tk.Frame(self.sf, bg=tc["bg"])
        self.cards_frame.pack(fill="x", padx=15, pady=5)
        
        # Yorum Açıklama Kartı
        self.card_explanation = Card(self.sf, title="🤖 Yapay Zeka Yorumu", accent_color=tc["accent"], card_bg=tc["card"], text_color=tc["text_primary"])
        self.card_explanation.pack(fill="x", padx=15, pady=5)
        self.lbl_explanation = tk.Label(self.card_explanation.content_frame, text="", font=("Segoe UI", 9, "italic"), fg=tc["text_primary"], bg=tc["card"], wraplength=320, justify="left", anchor="w")
        self.lbl_explanation.pack(fill="x", pady=5)
        
        # Akıllı AI Önerileri Kartı
        self.recommendations_title = tk.Label(self.sf, text="💡 AI Destekli Eylem Planı", font=("Segoe UI", 11, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w")
        self.recommendations_title.pack(fill="x", padx=15, pady=(15, 2))
        
        self.recommendations_container = tk.Frame(self.sf, bg=tc["bg"])
        self.recommendations_container.pack(fill="x")
        
        # MANUEL ANALİZ FORMU (Collapsible Bottom Card)
        self.card_manual = CollapsibleCard(self.sf, "⚙️ Manuel İklim Analiz Formu", tc)
        self.card_manual.pack(fill="x", padx=15, pady=(15, 30))
        mf = self.card_manual.content_frame
        
        tk.Label(mf, text="Manuel iklim değerleri girerek kuraklık skorunu test edebilirsiniz:", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(0, 10))
        
        tk.Label(mf, text="Ortalama Sıcaklık (°C)", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 2))
        self.ent_temp = tk.Entry(mf, font=("Segoe UI", 9), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_temp.pack(fill="x", ipady=4, pady=(0, 10))
        
        tk.Label(mf, text="Nem Oranı (%)", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 2))
        self.ent_hum = tk.Entry(mf, font=("Segoe UI", 9), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_hum.pack(fill="x", ipady=4, pady=(0, 10))
        
        tk.Label(mf, text="Yağış Miktarı (mm)", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 2))
        self.ent_prec = tk.Entry(mf, font=("Segoe UI", 9), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_prec.pack(fill="x", ipady=4, pady=(0, 15))
        
        CustomButton(mf, text="Değerleri Analiz Et ve Kaydet", bg_color=tc["primary_btn"], command=self.do_analysis).pack(fill="x")
        
        self.manual_result_container = tk.Frame(mf, bg=tc["card"])
        self.manual_result_container.pack(fill="x", pady=(10, 0))
        
        self.update_ai_predictions()

    def city_selected(self, event):
        self.update_ai_predictions()
        
    def update_ai_predictions(self):
        city = self.cb_city.get()
        if not city:
            return
            
        tc = self.controller.theme_colors
        
        # Load historical monthly records for projection plot
        history = Database.get_city_monthly_data_range(city, 2020, 1, 2025, 12)
        
        # Fit AI Trend model
        res = DroughtAIPredictor.fit_and_project(city)
        if not res or not history:
            return
            
        # 1. Draw projection chart
        self.draw_projection_chart(self.chart_container, city, history, res["projections"], tc)
        
        # 2. Update prediction summary cards
        for w in self.cards_frame.winfo_children():
            w.destroy()
            
        # Draw 1, 3, 6 months projection boxes
        horisons = [
            ("1 Ay Sonra", res["score_1"], res["pct_1"], res["risk_1"]),
            ("3 Ay Sonra", res["score_3"], res["pct_3"], res["risk_3"]),
            ("6 Ay Sonra", res["score_6"], res["pct_6"], res["risk_6"])
        ]
        
        for name, score, pct, risk in horisons:
            self.cards_frame.columnconfigure(horisons.index((name, score, pct, risk)), weight=1)
            f_box = tk.Frame(self.cards_frame, bg=tc["card"], highlightthickness=1, highlightbackground=tc["input_bg"], padx=6, pady=8)
            f_box.pack(side="left", fill="both", expand=True, padx=3)
            
            tk.Label(f_box, text=name, font=("Segoe UI", 8, "bold"), fg=tc["text_primary"], bg=tc["card"]).pack()
            
            risk_color = tc["secondary_btn"] if risk == "Düşük Risk" else tc["accent"] if risk == "Orta Risk" else tc["danger_btn"]
            tk.Label(f_box, text=f"Skor: {score:.1f}", font=("Segoe UI", 9, "bold"), fg=tc["text_primary"], bg=tc["card"]).pack(pady=2)
            tk.Label(f_box, text=risk, font=("Segoe UI", 7, "bold"), fg=risk_color, bg=tc["card"]).pack()
            
            trend_symbol = "▲" if pct >= 0 else "▼"
            trend_color = tc["danger_btn"] if pct >= 0 else tc["secondary_btn"]
            tk.Label(f_box, text=f"{trend_symbol} %{abs(pct):.1f}", font=("Segoe UI", 8, "bold"), fg=trend_color, bg=tc["card"]).pack(pady=(2, 0))
            
        # 3. Update explanation comment
        self.lbl_explanation.config(text=res["explanation"])
        
        # 4. Update Smart recommendations dynamically
        for w in self.recommendations_container.winfo_children():
            w.destroy()
            
        risk_3 = res["risk_3"]
        prec_3 = res["projections"][2]["precipitation"]
        
        # Show recommendation cards
        if risk_3 == "Yüksek Risk":
            c_irr = Card(self.recommendations_container, title="🌾 Tarımsal Sulama Eylem Planı", accent_color=tc["danger_btn"])
            c_irr.pack(fill="x", padx=15, pady=4)
            tk.Label(c_irr.content_frame, text="Acil kuraklık tedbirleri kapsamında tarımda vahşi sulama durdurulmalı, sulamalar sadece gece saatlerinde damlama yöntemiyle yapılmalıdır. Toprak nem kaybını önlemek amacıyla malçlama katman kalınlığı artırılmalıdır.", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=310, justify="left", anchor="w").pack(fill="x")
            
            c_crop = Card(self.recommendations_container, title="🚜 Çiftçiler İçin Ürün Seçim Önerisi", accent_color=tc["accent"])
            c_crop.pack(fill="x", padx=15, pady=4)
            tk.Label(c_crop.content_frame, text="Bölgedeki yüksek risk nedeniyle su ihtiyacı fazla olan yonca, mısır veya çeltik gibi ürünlerin ekimi yerine; kuraklığa yüksek direnç gösteren arpa, mercimek, nohut, aspir gibi alternatiflerin tercih edilmesi önerilir.", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=310, justify="left", anchor="w").pack(fill="x")
        elif risk_3 == "Orta Risk":
            c_irr = Card(self.recommendations_container, title="🌾 Kontrollü Sulama Tavsiyesi", accent_color=tc["accent"])
            c_irr.pack(fill="x", padx=15, pady=4)
            tk.Label(c_irr.content_frame, text="Sulama planlaması, yerel nem sensörleri ve toprak analizi sonuçlarına göre optimize edilmelidir. Gün ortasındaki buharlaşmayı önlemek için sabah erken veya akşam geç sulama yapılmalıdır.", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=310, justify="left", anchor="w").pack(fill="x")
            
            c_crop = Card(self.recommendations_container, title="🚜 Çiftçiler İçin Kontrollü Ekim Planı", accent_color=tc["primary_btn"])
            c_crop.pack(fill="x", padx=15, pady=4)
            tk.Label(c_crop.content_frame, text="Buğday ve kanola gibi orta derecede su tüketen tahıllarda kısıtlı sulama uygulaması tercih edilerek su rezervleri korunmalıdır.", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=310, justify="left", anchor="w").pack(fill="x")
        else:
            c_irr = Card(self.recommendations_container, title="🌾 Standart Sulama ve Koruma Planı", accent_color=tc["secondary_btn"])
            c_irr.pack(fill="x", padx=15, pady=4)
            tk.Label(c_irr.content_frame, text="Mevcut sulama rejimi yeterlidir. Ancak ileride oluşabilecek kuraklık risklerine hazırlık amacıyla yağmur suyu depolama tanklarının doldurulması ve tasarruflu tüketimin sürdürülmesi önerilir.", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=310, justify="left", anchor="w").pack(fill="x")
            
        if prec_3 < 40.0:
            c_prec = Card(self.recommendations_container, title="💧 Evsel Su Tasarrufu & Tedbirler", accent_color=tc["secondary_btn"])
            c_prec.pack(fill="x", padx=15, pady=4)
            tk.Label(c_prec.content_frame, text=f"Önümüzdeki 3 ayda beklenen düşük yağış ortalaması ({int(prec_3)} mm) nedeniyle, evsel su tüketiminde tasarruflu perlatörler kullanılmalı, duş süreleri kısıtlanmalı ve gri su yeniden kazanılmalıdır.", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=310, justify="left", anchor="w").pack(fill="x")

        # Set default values for manual fields based on selected city defaults
        temp, hum, prec = get_city_climate_defaults(city)
        self.ent_temp.delete(0, tk.END)
        self.ent_temp.insert(0, str(temp))
        self.ent_hum.delete(0, tk.END)
        self.ent_hum.insert(0, str(hum))
        self.ent_prec.delete(0, tk.END)
        self.ent_prec.insert(0, str(prec))

    def draw_projection_chart(self, parent_frame, city_name, history_data, projections, tc):
        for w in parent_frame.winfo_children():
            w.destroy()
            
        plt.rcParams['text.color'] = tc["text_primary"]
        plt.rcParams['axes.labelcolor'] = tc["text_muted"]
        plt.rcParams['xtick.color'] = tc["text_muted"]
        plt.rcParams['ytick.color'] = tc["text_muted"]
        
        fig, ax = plt.subplots(figsize=(5.0, 2.5), facecolor=tc["card"])
        ax.set_facecolor(tc["card"])
        
        # Historical last 12 months
        hist_len = min(12, len(history_data))
        hist_slice = history_data[-hist_len:]
        
        hist_dates = [f"{row[1]:02d}/{str(row[0])[2:]}" for row in hist_slice]
        hist_scores = [row[5] for row in hist_slice]
        
        # Forecast 6 months
        fc_dates = [f"{row['month']:02d}/{str(row['year'])[2:]}" for row in projections]
        fc_scores = [row["score"] for row in projections]
        
        all_dates = hist_dates + fc_dates
        x_indices = list(range(len(all_dates)))
        
        hist_indices = x_indices[:len(hist_dates)]
        fc_indices = x_indices[len(hist_dates) - 1:]
        
        fc_scores_extended = [hist_scores[-1]] + fc_scores
        
        # Plot history
        ax.plot(hist_indices, hist_scores, color=tc["primary_btn"], linewidth=2.0, marker='o', markersize=3, label="Geçmiş (Son 12 Ay)")
        # Plot forecast projection
        ax.plot(fc_indices, fc_scores_extended, color=tc["danger_btn"], linewidth=2.0, linestyle="--", marker='^', markersize=4, label="AI Projeksiyon (6 Ay)")
        
        ax.set_xticks(x_indices)
        step = max(1, len(all_dates) // 5)
        ax.set_xticklabels([all_dates[i] if i % step == 0 else "" for i in x_indices], fontsize=7)
        ax.tick_params(labelsize=7)
        
        ax.set_ylabel("Risk Skoru", fontsize=8)
        ax.set_ylim(0, 105)
        ax.grid(True, color=tc["input_bg"], linestyle=':', alpha=0.5)
        ax.legend(facecolor=tc["card"], edgecolor=tc["input_bg"], fontsize=7, loc="upper left")
        
        for spine in ax.spines.values():
            spine.set_color(tc["input_bg"])
            
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, master=parent_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True)
        plt.close(fig)

    def do_analysis(self):
        for w in self.manual_result_container.winfo_children():
            w.destroy()
            
        try:
            temp = float(self.ent_temp.get().strip())
            hum = float(self.ent_hum.get().strip())
            prec = float(self.ent_prec.get().strip())
        except ValueError:
            messagebox.showerror("Hata", "Lütfen tüm verileri sayısal formatta girin.")
            return
            
        if not (0 <= hum <= 100):
            messagebox.showerror("Hata", "Nem oranı %0 ile %100 arasında olmalıdır.")
            return
        if prec < 0:
            messagebox.showerror("Hata", "Yağış miktarı negatif olamaz.")
            return
            
        score = DroughtAnalysisEngine.calculate_score(temp, hum, prec)
        risk = DroughtAnalysisEngine.get_risk_level(score)
        
        Database.save_analysis(self.user_id, temp, hum, prec, score, risk)
        
        tc = self.controller.theme_colors
        col = tc["secondary_btn"] if risk == "Düşük Risk" else tc["accent"] if risk == "Orta Risk" else tc["danger_btn"]
        
        r_card = Card(self.manual_result_container, title="Analiz Başarıyla Kaydedildi", accent_color=col, card_bg=tc["card"], text_color=tc["text_primary"])
        r_card.pack(fill="x", pady=5)
        rcf = r_card.content_frame
        
        row = tk.Frame(rcf, bg=tc["card"])
        row.pack(fill="x", pady=2)
        tk.Label(row, text=f"Skor: {score}/100", font=("Segoe UI", 9, "bold"), fg=tc["text_primary"], bg=tc["card"]).pack(side="left")
        tk.Label(row, text=risk.upper(), font=("Segoe UI", 9, "bold"), fg=col, bg=tc["card"]).pack(side="right")
        
        res_chart_f = tk.Frame(rcf, bg=tc["card"], height=95)
        res_chart_f.pack(fill="x", pady=5)
        draw_city_gauge_chart(res_chart_f, score, tc)
        
        eco = DroughtAnalysisEngine.estimate_economic_impact(risk)
        
        sep = ttk.Separator(rcf, orient="horizontal")
        sep.pack(fill="x", pady=8)
        
        tk.Label(rcf, text="Tarımsal Verim Kaybı:", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
        tk.Label(rcf, text=f"%{eco['yield_loss']}", font=("Segoe UI", 9, "bold"), fg=tc["danger_btn"], bg=tc["card"]).pack(anchor="w", pady=(0, 5))
        
        tk.Label(rcf, text="Gıda Fiyat Artış Tahmini:", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
        tk.Label(rcf, text=f"+ %{eco['price_increase']}", font=("Segoe UI", 9, "bold"), fg=tc["accent"], bg=tc["card"]).pack(anchor="w", pady=(0, 10))
        
        CustomButton(
            rcf, text="Akıllı Önerileri İncele 💡", bg_color=tc["input_bg"],
            command=lambda: self.main_layout.switch_tab("recommendations_page")
        ).pack(fill="x")


# =====================================================================
# SEKME 4 - SU TÜKETİMİ (Boş Başlar, Sıfırlanabilir)
# =====================================================================
class WaterTrackerTab(tk.Frame):
    def __init__(self, parent, controller, main_layout):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.main_layout = main_layout
        self.user_id = controller.current_user_id
        self.pack(fill="both", expand=True)
        
        scroll = ScrollableFrame(self, bg_color=tc["bg"])
        scroll.pack(fill="both", expand=True)
        sf = scroll.scrollable_frame
        
        tk.Label(sf, text="Günlük Su Tüketim Takibi", font=("Segoe UI", 14, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(15, 2))
        tk.Label(sf, text="Günlük su kullanım miktarınızı girerek takip edin:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        input_card = Card(sf, accent_color=tc["secondary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
        input_card.pack(fill="x", padx=15, pady=5)
        ic = input_card.content_frame
        
        tk.Label(ic, text="Manuel Değer Girişi (Litre)", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 2))
        
        row_entry = tk.Frame(ic, bg=tc["card"])
        row_entry.pack(fill="x", pady=5)
        
        self.ent_water = tk.Entry(row_entry, font=("Segoe UI", 11, "bold"), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_water.pack(side="left", fill="both", expand=True, ipady=6, padx=(0, 8))
        self.ent_water.insert(0, "150")
        
        CustomButton(row_entry, text="Değeri Kaydet 💧", bg_color=tc["secondary_btn"], command=self.save_water).pack(side="right")
        
        tk.Label(ic, text=f"Kayıt bugünün tarihiyle yapılacaktır ({datetime.date.today().strftime('%d.%m.%Y')}).", font=("Segoe UI", 8, "italic"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 0))
        
        self.tracker_chart_frame = tk.Frame(ic, bg=tc["card"], height=120)
        self.tracker_chart_frame.pack(fill="x", pady=(10, 0))
        
        # Aktivite Tabanlı Hesaplayıcı Kartı
        self.ACTIVITIES = {
            "Duş Alma": {"rate": 8.0, "unit": "Süre (Dakika)"},
            "Çamaşır Makinesi": {"rate": 50.0, "unit": "Yıkama Sayısı (Adet)"},
            "Bulaşık Makinesi": {"rate": 12.0, "unit": "Yıkama Sayısı (Adet)"},
            "Elde Bulaşık Yıkama": {"rate": 10.0, "unit": "Süre (Dakika)"},
            "Tuvalet Kullanımı": {"rate": 6.0, "unit": "Kullanım Sayısı (Kez)"},
            "El/Yüz Yıkama": {"rate": 6.0, "unit": "Süre (Dakika)"}
        }
        
        calc_card = Card(sf, title="Aktivite Tabanlı Su Hesaplayıcı", accent_color=tc["primary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
        calc_card.pack(fill="x", padx=15, pady=5)
        cc = calc_card.content_frame
        
        row_act = tk.Frame(cc, bg=tc["card"])
        row_act.pack(fill="x", pady=2)
        
        f_act = tk.Frame(row_act, bg=tc["card"])
        f_act.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_act, text="Aktivite Seçin", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
        self.cb_activity = ttk.Combobox(f_act, values=list(self.ACTIVITIES.keys()), state="readonly", font=("Segoe UI", 9))
        self.cb_activity.pack(fill="x", pady=(2, 0))
        self.cb_activity.set("Duş Alma")
        self.cb_activity.bind("<<ComboboxSelected>>", self.on_activity_changed)
        
        f_qty = tk.Frame(row_act, bg=tc["card"], width=120)
        f_qty.pack(side="right", padx=(5, 0))
        self.lbl_activity_unit = tk.Label(f_qty, text="Süre (Dakika)", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"])
        self.lbl_activity_unit.pack(anchor="w")
        self.ent_activity_qty = tk.Entry(f_qty, font=("Segoe UI", 9), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"], width=12)
        self.ent_activity_qty.pack(fill="x", ipady=4, pady=(2, 0))
        self.ent_activity_qty.insert(0, "10")
        self.ent_activity_qty.bind("<KeyRelease>", self.update_activity_calc)
        
        self.lbl_activity_calc = tk.Label(cc, text="Hesaplanan Tüketim: 80 Litre (Oran: 8 L/dk)", font=("Segoe UI", 9, "bold"), fg=tc["primary_btn"], bg=tc["card"])
        self.lbl_activity_calc.pack(anchor="w", pady=(8, 8))
        
        CustomButton(cc, text="Tüketime Ekle 💧", bg_color=tc["primary_btn"], command=self.add_activity_consumption).pack(fill="x")
        
        # Haftalık Özet Kartı
        self.weekly_card = Card(sf, title="Haftalık Tüketim Analizi", accent_color=tc["accent"], card_bg=tc["card"], text_color=tc["text_primary"])
        self.weekly_card.pack(fill="x", padx=15, pady=5)
        
        act_row = tk.Frame(sf, bg=tc["bg"])
        act_row.pack(fill="x", padx=15, pady=(15, 5))
        
        tk.Label(act_row, text="Su Kullanım Geçmişiniz", font=("Segoe UI", 11, "bold"), fg=tc["text_primary"], bg=tc["bg"]).pack(side="left")
        
        CustomButton(
            act_row, text="Sıfırla 🗑️", bg_color=tc["danger_btn"],
            command=self.reset_water_data
        ).pack(side="right")
        
        self.history_container = tk.Frame(sf, bg=tc["bg"])
        self.history_container.pack(fill="x", padx=15, pady=(5, 30))
        self.load_history()

    def on_activity_changed(self, event):
        act = self.cb_activity.get()
        if act in self.ACTIVITIES:
            unit = self.ACTIVITIES[act]["unit"]
            self.lbl_activity_unit.config(text=unit)
            self.ent_activity_qty.delete(0, tk.END)
            if unit == "Süre (Dakika)":
                self.ent_activity_qty.insert(0, "10" if act == "Duş Alma" else "5")
            else:
                self.ent_activity_qty.insert(0, "1")
            self.update_activity_calc(None)

    def update_activity_calc(self, event):
        act = self.cb_activity.get()
        if act in self.ACTIVITIES:
            rate = self.ACTIVITIES[act]["rate"]
            unit = self.ACTIVITIES[act]["unit"]
            try:
                qty = float(self.ent_activity_qty.get().strip())
                if qty < 0:
                    qty = 0
            except ValueError:
                qty = 0
            liters = qty * rate
            unit_suffix = "L/dk" if "Süre" in unit else "L/yıkama" if "Yıkama" in unit else "L/kez"
            self.lbl_activity_calc.config(text=f"Hesaplanan Tüketim: {int(liters)} Litre (Oran: {int(rate)} {unit_suffix})")

    def add_activity_consumption(self):
        act = self.cb_activity.get()
        if act in self.ACTIVITIES:
            rate = self.ACTIVITIES[act]["rate"]
            try:
                qty = float(self.ent_activity_qty.get().strip())
            except ValueError:
                messagebox.showerror("Hata", "Lütfen geçerli bir miktar girin.")
                return
            if qty <= 0:
                messagebox.showerror("Hata", "Miktar sıfırdan büyük olmalıdır.")
                return
            liters = qty * rate
            Database.add_water_consumption(self.user_id, liters)
            messagebox.showinfo("Başarılı", f"Aktivite tüketimi ({int(liters)} Litre) bugünün kaydına eklendi.")
            self.load_history()

    def update_circular_tracker(self):
        last_water = Database.get_last_water_consumption(self.user_id)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        tc = self.controller.theme_colors
        if last_water and last_water[1] == today_str:
            draw_water_circular_chart(self.tracker_chart_frame, last_water[0], tc)
        else:
            draw_water_circular_chart(self.tracker_chart_frame, 0.0, tc)

    def load_history(self):
        for w in self.history_container.winfo_children():
            w.destroy()
            
        tc = self.controller.theme_colors
        history = Database.get_water_history(self.user_id, limit=7)
        
        # Haftalık Özet Kartını Güncelle
        for w in self.weekly_card.content_frame.winfo_children():
            w.destroy()
            
        wcf = self.weekly_card.content_frame
        if history:
            total_water = sum(row[0] for row in history)
            avg_water = total_water / len(history)
            weekly_limit = 150.0 * 7
            savings_pct = ((weekly_limit - total_water) / weekly_limit) * 100
            
            row_tot = tk.Frame(wcf, bg=tc["card"])
            row_tot.pack(fill="x", pady=2)
            tk.Label(row_tot, text="7 Günlük Toplam Tüketim:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["card"]).pack(side="left")
            tk.Label(row_tot, text=f"{int(total_water)} Litre", font=("Segoe UI", 10, "bold"), fg=tc["text_primary"], bg=tc["card"]).pack(side="right")
            
            row_avg = tk.Frame(wcf, bg=tc["card"])
            row_avg.pack(fill="x", pady=2)
            tk.Label(row_avg, text="Günlük Ortalama Tüketim:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["card"]).pack(side="left")
            tk.Label(row_avg, text=f"{int(avg_water)} Litre / gün", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(side="right")
            
            row_status = tk.Frame(wcf, bg=tc["card"])
            row_status.pack(fill="x", pady=4)
            if savings_pct >= 0:
                status_text = f"Tasarruflu (%{int(savings_pct)} Tasarruf)"
                status_color = tc["secondary_btn"]
            else:
                status_text = f"Limit Aşımı! (+{int(abs(total_water - weekly_limit))} Litre)"
                status_color = tc["danger_btn"]
            tk.Label(row_status, text="Haftalık Tasarruf Durumu:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["card"]).pack(side="left")
            tk.Label(row_status, text=status_text, font=("Segoe UI", 10, "bold"), fg=status_color, bg=tc["card"]).pack(side="right")
        else:
            tk.Label(wcf, text="Haftalık istatistikleri görmek için tüketim verisi ekleyin.", font=("Segoe UI", 8, "italic"), fg=tc["text_muted"], bg=tc["card"]).pack(pady=5)

        if not history:
            tk.Label(
                self.history_container, text="Kayıtlı su tüketim veriniz bulunmamaktadır. \nYeni tüketim verisi ekleyerek başlayabilirsiniz.",
                font=("Segoe UI", 9, "italic"), fg=tc["text_muted"], bg=tc["bg"], pady=20, justify="center"
            ).pack(fill="x")
            self.update_circular_tracker()
            return
            
        for amt, date_str in reversed(history):
            try:
                d = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                day_name = d.strftime("%d.%m.%Y")
            except ValueError:
                day_name = date_str
                
            row = tk.Frame(self.history_container, bg=tc["card"], pady=8, padx=12)
            row.pack(fill="x", pady=4)
            
            col_limit = tc["secondary_btn"] if amt <= 150 else tc["danger_btn"]
            accent = tk.Frame(row, bg=col_limit, width=4)
            accent.pack(side="left", fill="y", padx=(0, 10))
            
            tk.Label(row, text=day_name, font=("Segoe UI", 9, "bold"), fg=tc["text_primary"], bg=tc["card"]).pack(side="left")
            tk.Label(row, text=f"{amt} Litre", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(side="right")
        self.update_circular_tracker()

    def save_water(self):
        try:
            amt = float(self.ent_water.get().strip())
        except ValueError:
            messagebox.showerror("Hata", "Lütfen su miktarını sayısal formatta girin.")
            return
        if amt <= 0:
            messagebox.showerror("Hata", "Miktar sıfırdan büyük olmalıdır.")
            return
            
        Database.save_water_consumption(self.user_id, amt)
        messagebox.showinfo("Başarılı", "Tüketim kaydı başarıyla eklendi.")
        self.ent_water.delete(0, tk.END)
        self.ent_water.insert(0, "150")
        self.load_history()

    def reset_water_data(self):
        if messagebox.askyesno("Sıfırla", "Tüm su tüketim verilerini silmek istediğinize emin misiniz? Bu işlem geri alınamaz."):
            Database.reset_water_consumption(self.user_id)
            messagebox.showinfo("Başarılı", "Tüketim verileriniz tamamen sıfırlandı.")
            self.load_history()


# =====================================================================
# DİKEY HAMBURGER MENÜ ☰ (Sağ Üst Köşeden Erişilen Akordeon Panel)
# =====================================================================
class MenuTab(tk.Frame):
    def __init__(self, parent, controller, main_layout):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.main_layout = main_layout
        self.user_id = controller.current_user_id
        self.pack(fill="both", expand=True)
        
        scroll = ScrollableFrame(self, bg_color=tc["bg"])
        scroll.pack(fill="both", expand=True)
        sf = scroll.scrollable_frame
        
        tk.Label(sf, text="Uygulama Menüsü & Ayarlar ☰", font=("Segoe UI", 14, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(15, 2))
        tk.Label(sf, text="Tüm panel detaylarını buradan yönetebilirsiniz:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # --- AKORDEON ELEMANLARI (CollapsibleCard) ---
        
        # 1. KULLANICI PROFİL AYARLARI
        self.card_profile = CollapsibleCard(sf, "👤 Kullanıcı Profil Ayarları", tc)
        self.card_profile.pack(fill="x", padx=15, pady=5)
        
        p_data = Database.get_user_profile(self.user_id)
        saved_city = p_data[1] if p_data else ""
        saved_dist = p_data[2] if p_data else ""
        
        pf = self.card_profile.content_frame
        tk.Label(pf, text="Şehir", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 2))
        self.cb_profile_city = ttk.Combobox(pf, values=sorted(list(ALL_CITIES_GEOGRAPHY.keys())), state="readonly", font=("Segoe UI", 9))
        self.cb_profile_city.pack(fill="x", pady=(0, 10))
        self.cb_profile_city.set(saved_city if saved_city else "Seçiniz")
        
        tk.Label(pf, text="Semt / İlçe", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 2))
        self.ent_dist = tk.Entry(pf, font=("Segoe UI", 9), bg=tc["input_bg"], fg=tc["text_primary"], bd=0, insertbackground=tc["text_primary"])
        self.ent_dist.pack(fill="x", ipady=6, pady=(0, 15))
        self.ent_dist.insert(0, saved_dist)
        
        CustomButton(pf, text="Konumumu Profilime Kaydet", bg_color=tc["primary_btn"], command=self.save_profile).pack(fill="x")
        
        # 2. AKILLI ÖNERİ SAYFASI LİNKİ (Düzeltildi: Ayrı ekrana yönlendirir)
        self.card_recommend = CollapsibleCard(sf, "💡 Akıllı Öneri Merkezi", tc)
        self.card_recommend.pack(fill="x", padx=15, pady=5)
        rf = self.card_recommend.content_frame
        tk.Label(rf, text="Kişisel veya bölgesel kuraklık risk durumunuza uygun su tasarrufu, tarım ve sürdürülebilirlik önerilerini ayrıntılı bir ekranda inceleyin.", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"], wraplength=320, justify="left").pack(anchor="w", pady=(0, 10))
        CustomButton(
            rf, text="Önerileri Ayrı Ekranda İncele 💡", bg_color=tc["primary_btn"],
            command=lambda: self.main_layout.switch_tab("recommendations_page")
        ).pack(fill="x")

        # 3. ARAYÜZ RENK TEMASI (8 Tema + Varsayılana Dön Butonu)
        self.card_theme = CollapsibleCard(sf, "🎨 Arayüz Renk Teması", tc)
        self.card_theme.pack(fill="x", padx=15, pady=5)
        tf = self.card_theme.content_frame
        
        tk.Label(tf, text="Tema Seçimi", font=("Segoe UI", 9, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w", pady=(5, 2))
        self.cb_theme = ttk.Combobox(tf, values=list(THEMES.keys()), state="readonly", font=("Segoe UI", 9))
        self.cb_theme.pack(fill="x", pady=(0, 10))
        self.cb_theme.set(controller.theme_name)
        self.cb_theme.bind("<<ComboboxSelected>>", self.theme_selected)
        
        # Düzeltildi: Varsayılana Dön (Reset to Default) butonu eklendi
        CustomButton(tf, text="Varsayılan Slate Temasına Dön", bg_color=tc["input_bg"], command=self.theme_reset_default).pack(fill="x")

        # 4. YARDIM & SSS
        self.card_help = CollapsibleCard(sf, "❓ Yardım & Sıkça Sorulan Sorular", tc)
        self.card_help.pack(fill="x", padx=15, pady=5)
        hf = self.card_help.content_frame
        faq_data = [
            ("Kuraklık Skoru nasıl hesaplanır?", "Kuraklık skoru; sıcaklığın %50, nem eksikliğinin %30 ve yağış eksikliğinin %20 ağırlıklandırılarak toplandığı meteorolojik formülle hesaplanır."),
            ("Günlük su limiti ne kadardır?", "Bireysel su tasarrufu için günlük ideal su tüketim limiti kişi başı 150 Litre olarak önerilmektedir."),
            ("Karşılaştırma paneli nasıl kullanılır?", "Harita sekmesindeki Şehir Karşılaştırma alanından seçtiğiniz iki ilin iklim ve risk verilerini yan yana çubuk grafik olarak kıyaslayabilirsiniz."),
            ("Uygulamaya telefondan nasıl girebilirim?", "Bu Python/Tkinter uygulamasını telefondan çalıştırmak için: \n1) PyDroid 3 (Android): Google Play'den PyDroid 3 kurup app.py'ı telefona kopyalayarak çalıştırabilirsiniz.\n2) Uzak Masaüstü: AnyDesk veya Chrome Remote Desktop ile bilgisayarınıza telefondan bağlanabilirsiniz.\n3) Web Yayını: İlerleyen aşamalarda bu backend Flask/Django ile web sitesine dönüştürülüp mobil tarayıcılardan açılabilir.")
        ]
        for q, a in faq_data:
            tk.Label(hf, text=f"Q: {q}", font=("Segoe UI", 8, "bold"), fg=tc["text_primary"], bg=tc["card"], anchor="w").pack(fill="x", pady=(3, 0))
            tk.Label(hf, text=a, font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"], wraplength=320, justify="left", anchor="w").pack(fill="x", pady=(0, 5))

        # 5. HESAP & VERİ YÖNETİMİ
        self.card_mgmt = CollapsibleCard(sf, "⚙️ Hesap & Veri Yönetimi", tc)
        self.card_mgmt.pack(fill="x", padx=15, pady=5)
        mf = self.card_mgmt.content_frame
        tk.Label(mf, text="Hesap geçmişini sıfırlayabilir veya hesabı tamamen silebilirsiniz. Bu işlem geri alınamaz.", font=("Segoe UI", 8), fg=tc["text_muted"], bg=tc["card"], wraplength=320, justify="left").pack(anchor="w", pady=(0, 10))
        
        btn_row = tk.Frame(mf, bg=tc["card"])
        btn_row.pack(fill="x")
        CustomButton(btn_row, text="Verileri Sıfırla 🗑️", bg_color=tc["input_bg"], command=self.reset_all_data).pack(side="left", fill="x", expand=True, padx=(0, 5))
        CustomButton(btn_row, text="Hesabı Sil ❌", bg_color=tc["danger_btn"], command=self.delete_account).pack(side="right", fill="x", expand=True, padx=(5, 0))

        # Oturumu Kapat Butonu
        CustomButton(sf, text="Oturumu Kapat 🚪", bg_color=tc["danger_btn"], command=self.controller.logout).pack(fill="x", padx=15, pady=(15, 5))

        tk.Frame(sf, bg=tc["bg"], height=30).pack()

    def save_profile(self):
        city = self.cb_profile_city.get()
        dist = self.ent_dist.get().strip()
        if city == "Seçiniz" or not dist:
            messagebox.showwarning("Eksik Bilgi", "Lütfen Şehir ve Semt alanlarını doldurun.")
            return
        Database.update_profile(self.user_id, city, dist)
        messagebox.showinfo("Başarılı", "Profil bilgileriniz başarıyla güncellendi.")
        
    def theme_selected(self, event):
        new_theme = self.cb_theme.get()
        self.apply_new_theme(new_theme)
        
    def theme_reset_default(self):
        self.apply_new_theme("Slate Koyu")
        
    def apply_new_theme(self, new_theme):
        if new_theme in THEMES:
            with Database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET theme = ? WHERE id = ?", (new_theme, self.user_id))
                conn.commit()
            self.controller.theme_name = new_theme
            self.controller.theme_colors = THEMES[new_theme]
            self.controller.login_success(self.user_id, self.controller.current_username)
            self.controller.main_app_layout.switch_tab("menu")
            messagebox.showinfo("Tema Güncellendi", f"Uygulama renkleri '{new_theme}' olarak güncellendi!")

    def reset_all_data(self):
        if messagebox.askyesno("Verileri Sıfırla", "Tüm analizleriniz, su takipleri ve profil konum bilgileriniz silinecektir. Devam etmek istiyor musunuz?"):
            Database.reset_user_data(self.user_id)
            messagebox.showinfo("Sıfırlandı", "Tüm hesap geçmişi sıfırlandı.")
            self.controller.login_success(self.user_id, self.controller.current_username)
            self.controller.main_app_layout.switch_tab("menu")

    def delete_account(self):
        if messagebox.askyesno("Hesabı Kapat", "Hesabınız ve tüm iklim/su verileriniz kalıcı olarak silinecektir. Emin misiniz?"):
            Database.delete_account(self.user_id)
            messagebox.showinfo("Silindi", "Hesabınız tamamen silinmiştir.")
            self.controller.logout()


# =====================================================================
# BAĞIMSIZ AKILLI ÖNERİ SAYFASI (Talep Edilen Gelişmiş Ayrı Ekran)
# =====================================================================
class RecommendationsScreen(tk.Frame):
    def __init__(self, parent, controller, main_layout):
        tc = controller.theme_colors
        super().__init__(parent, bg=tc["bg"])
        self.controller = controller
        self.main_layout = main_layout
        self.user_id = controller.current_user_id
        self.pack(fill="both", expand=True)
        
        # --- DÖNÜŞ HEADER'I ---
        self.top_bar = tk.Frame(self, bg=tc["card"], height=40)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)
        
        CustomButton(
            self.top_bar, text="⬅ Geri Dön", bg_color=tc["card"], fg_color=tc["primary_btn"],
            command=lambda: self.main_layout.switch_tab("menu") # Geriye menü sekmesine atar
        ).pack(side="left", padx=5, fill="y")
        
        tk.Label(self.top_bar, text="Öneri Merkezi", font=("Segoe UI", 10, "bold"), fg=tc["text_primary"], bg=tc["card"]).pack(side="right", padx=15, fill="y")
        
        scroll = ScrollableFrame(self, bg_color=tc["bg"])
        scroll.pack(fill="both", expand=True)
        sf = scroll.scrollable_frame
        
        # Kuraklığı temsil eden Pillow üretimi cracked resim
        generate_drought_images()
        self.cracked_img_ref = None
        try:
            img_pil = Image.open("drought_cracked.png")
            img_tk = ImageTk.PhotoImage(img_pil)
            self.cracked_img_ref = img_tk
            
            lbl_banner = tk.Label(sf, image=img_tk, bg=tc["bg"])
            lbl_banner.pack(fill="x", padx=15, pady=(15, 5))
        except Exception:
            pass
            
        tk.Label(sf, text="Akıllı Öneri ve Eylemler", font=("Segoe UI", 13, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=5)
        
        # Son risk skoruna göre önerileri çek
        last_anal = Database.get_last_analysis(self.user_id)
        if last_anal:
            score, risk, _, _, _, _ = last_anal
            col = tc["secondary_btn"] if risk == "Düşük Risk" else tc["accent"] if risk == "Orta Risk" else tc["danger_btn"]
            risk_desc = f"Analiz Durumunuz: {risk} (Skor: {score}/100)"
        else:
            risk = "Düşük Risk"
            col = tc["text_muted"]
            risk_desc = "Kişisel analiziniz olmadığı için genel öneriler listelenmektedir."
            
        # Risk Bilgi Kartı
        c_badge = Card(sf, card_bg=tc["card"], accent_color=col)
        c_badge.pack(fill="x", padx=15, pady=5)
        tk.Label(c_badge.content_frame, text=risk_desc, font=("Segoe UI", 9, "bold"), fg=col, bg=tc["card"], anchor="w").pack(fill="x")
        
        tips = DroughtAnalysisEngine.get_recommendations(risk)
        
        # Öneri Kartları
        c1 = Card(sf, title="💧 Bireysel Tasarruf Planı", accent_color=tc["secondary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
        c1.pack(fill="x", padx=15, pady=6)
        for t in tips["water_saving"]:
            tk.Label(c1.content_frame, text=f"• {t}", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=320, justify="left", anchor="w").pack(fill="x", pady=2)
            
        c2 = Card(sf, title="🌾 Tarımsal ve Bahçe Tedbirleri", accent_color=tc["primary_btn"], card_bg=tc["card"], text_color=tc["text_primary"])
        c2.pack(fill="x", padx=15, pady=6)
        for t in tips["agriculture"]:
            tk.Label(c2.content_frame, text=f"• {t}", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=320, justify="left", anchor="w").pack(fill="x", pady=2)
            
        c3 = Card(sf, title="🌱 Uzun Vadeli Sürdürülebilirlik", accent_color=tc["accent"], card_bg=tc["card"], text_color=tc["text_primary"])
        c3.pack(fill="x", padx=15, pady=(6, 25))
        for t in tips["sustainability"]:
            tk.Label(c3.content_frame, text=f"• {t}", font=("Segoe UI", 8), fg=tc["text_primary"], bg=tc["card"], wraplength=320, justify="left", anchor="w").pack(fill="x", pady=2)


# =====================================================================
# SEKME 5 - GRAFİKLER SAYFASI (Gelişmiş Etkileşimli Panel)
# =====================================================================
class ChartsTab(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=controller.theme_colors["bg"])
        self.controller = controller
        self.user_id = controller.current_user_id
        self.pack(fill="both", expand=True)
        
        scroll = ScrollableFrame(self, bg_color=controller.theme_colors["bg"])
        scroll.pack(fill="both", expand=True)
        sf = scroll.scrollable_frame
        
        tc = controller.theme_colors
        tk.Label(sf, text="Gelişmiş Veri Raporları", font=("Segoe UI", 14, "bold"), fg=tc["text_primary"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(15, 2))
        tk.Label(sf, text="Aylık yağış, nem, sıcaklık ve kuraklık riski değişim grafikleri:", font=("Segoe UI", 9), fg=tc["text_muted"], bg=tc["bg"], anchor="w").pack(fill="x", padx=15, pady=(0, 10))
        
        # Filtreleme Kartı
        filter_card = Card(sf, accent_color=tc["accent"], card_bg=tc["card"], text_color=tc["text_primary"])
        filter_card.pack(fill="x", padx=15, pady=5)
        fc = filter_card.content_frame
        
        # Şehir Seçimi
        row_city = tk.Frame(fc, bg=tc["card"])
        row_city.pack(fill="x", pady=2)
        tk.Label(row_city, text="Sorgulanacak Şehir:", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(side="left")
        
        sorted_cities = sorted(list(ALL_CITIES_GEOGRAPHY.keys()))
        self.cb_city = ttk.Combobox(row_city, values=sorted_cities, state="readonly", font=("Segoe UI", 9), width=15)
        self.cb_city.pack(side="left", padx=10)
        self.cb_city.set("İstanbul")
        self.cb_city.bind("<<ComboboxSelected>>", self.on_filter_changed)
        
        # Tarih aralığı seçicileri
        row_date = tk.Frame(fc, bg=tc["card"])
        row_date.pack(fill="x", pady=6)
        
        years = ["2020", "2021", "2022", "2023", "2024", "2025"]
        months = [str(m) for m in range(1, 13)]
        
        # Başlangıç
        f_start = tk.Frame(row_date, bg=tc["card"])
        f_start.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(f_start, text="Başlangıç Dönemi", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
        
        row_start_combo = tk.Frame(f_start, bg=tc["card"])
        row_start_combo.pack(fill="x", pady=2)
        self.cb_start_year = ttk.Combobox(row_start_combo, values=years, state="readonly", font=("Segoe UI", 8), width=6)
        self.cb_start_year.pack(side="left", padx=(0, 2))
        self.cb_start_year.set("2025")
        self.cb_start_year.bind("<<ComboboxSelected>>", self.on_filter_changed)
        
        self.cb_start_month = ttk.Combobox(row_start_combo, values=months, state="readonly", font=("Segoe UI", 8), width=4)
        self.cb_start_month.pack(side="left")
        self.cb_start_month.set("1")
        self.cb_start_month.bind("<<ComboboxSelected>>", self.on_filter_changed)
        
        # Bitiş
        f_end = tk.Frame(row_date, bg=tc["card"])
        f_end.pack(side="right", fill="x", expand=True, padx=(5, 0))
        tk.Label(f_end, text="Bitiş Dönemi", font=("Segoe UI", 8, "bold"), fg=tc["text_muted"], bg=tc["card"]).pack(anchor="w")
        
        row_end_combo = tk.Frame(f_end, bg=tc["card"])
        row_end_combo.pack(fill="x", pady=2)
        self.cb_end_year = ttk.Combobox(row_end_combo, values=years, state="readonly", font=("Segoe UI", 8), width=6)
        self.cb_end_year.pack(side="left", padx=(0, 2))
        self.cb_end_year.set("2025")
        self.cb_end_year.bind("<<ComboboxSelected>>", self.on_filter_changed)
        
        self.cb_end_month = ttk.Combobox(row_end_combo, values=months, state="readonly", font=("Segoe UI", 8), width=4)
        self.cb_end_month.pack(side="left")
        self.cb_end_month.set("12")
        self.cb_end_month.bind("<<ComboboxSelected>>", self.on_filter_changed)
        
        # Hover Metin Şeridi
        self.lbl_hover_info = tk.Label(sf, text="📍 İpucu: Değerleri görmek için farenizi grafik üzerinde hareket ettirin.", font=("Segoe UI", 8, "italic"), fg=tc["primary_btn"], bg=tc["bg"], anchor="center", pady=4)
        self.lbl_hover_info.pack(fill="x", padx=15, pady=2)
        
        # Grafik Kartı
        self.graph_card = Card(sf, title="Zaman Serisi Analiz Grafikleri (2x2 Panel)", card_bg=tc["card"])
        self.graph_card.pack(fill="x", padx=15, pady=(2, 25))
        self.charts_container = self.graph_card.content_frame
        
        self.dates = []
        self.temps = []
        self.hums = []
        self.precs = []
        self.scores = []
        self.hover_lines = []
        self.hover_annotations = []
        self.last_hover_idx = -1
        
        self.update_charts()
        
    def on_filter_changed(self, event):
        self.update_charts()
        
    def update_charts(self):
        for w in self.charts_container.winfo_children():
            w.destroy()
            
        city = self.cb_city.get()
        try:
            sy = int(self.cb_start_year.get())
            sm = int(self.cb_start_month.get())
            ey = int(self.cb_end_year.get())
            em = int(self.cb_end_month.get())
        except ValueError:
            return
            
        # Tarih kontrolü
        if (sy * 100 + sm) > (ey * 100 + em):
            sy, ey = ey, sy
            sm, em = em, sm
            self.cb_start_year.set(str(sy))
            self.cb_start_month.set(str(sm))
            self.cb_end_year.set(str(ey))
            self.cb_end_month.set(str(em))
            
        data = Database.get_city_monthly_data_range(city, sy, sm, ey, em)
        if not data:
            tk.Label(self.charts_container, text="Seçilen tarih aralığında veri bulunamadı.", font=("Segoe UI", 9, "italic"), fg=self.controller.theme_colors["text_muted"], bg=self.controller.theme_colors["card"], pady=20).pack()
            return
            
        self.dates = [f"{row[1]:02d}/{str(row[0])[2:]}" for row in data]
        self.temps = [row[2] for row in data]
        self.hums = [row[3] for row in data]
        self.precs = [row[4] for row in data]
        self.scores = [row[5] for row in data]
        
        tc = self.controller.theme_colors
        
        plt.rcParams['text.color'] = tc["text_primary"]
        plt.rcParams['axes.labelcolor'] = tc["text_muted"]
        plt.rcParams['xtick.color'] = tc["text_muted"]
        plt.rcParams['ytick.color'] = tc["text_muted"]
        
        # 2x2 Subplots
        self.fig, self.axs = plt.subplots(2, 2, figsize=(6.0, 5.0), facecolor=tc["card"])
        self.fig.patch.set_facecolor(tc["card"])
        
        colors = [tc["primary_btn"], tc["secondary_btn"], tc["accent"], tc["danger_btn"]]
        titles = ["Aylık Sıcaklık Değişimi (°C)", "Aylık Ortalama Nem (%)", "Aylık Yağış Miktarı (mm)", "Kuraklık Risk Skoru Zaman Serisi"]
        datasets = [self.temps, self.hums, self.precs, self.scores]
        
        x_indices = list(range(len(self.dates)))
        
        for idx, ax in enumerate(self.axs.flat):
            ax.set_facecolor(tc["card"])
            ax.plot(x_indices, datasets[idx], color=colors[idx], linewidth=1.8, marker='o', markersize=3)
            ax.set_title(titles[idx], fontsize=8, fontweight="bold", color=tc["text_primary"])
            ax.grid(True, color=tc["input_bg"], linestyle=':', alpha=0.5)
            
            ax.set_xticks(x_indices)
            step = max(1, len(self.dates) // 4)
            ax.set_xticklabels([self.dates[i] if i % step == 0 else "" for i in x_indices], fontsize=7)
            ax.tick_params(labelsize=7)
            
            for spine in ax.spines.values():
                spine.set_color(tc["input_bg"])
                
        self.fig.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.charts_container)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        self.cid = self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.last_hover_idx = -1
        
    def on_hover(self, event):
        if event.inaxes is None or not self.dates:
            return
            
        x_pos = event.xdata
        if x_pos is None:
            return
            
        idx = int(round(x_pos))
        idx = max(0, min(idx, len(self.dates) - 1))
        
        if idx == self.last_hover_idx:
            return
        self.last_hover_idx = idx
        
        tc = self.controller.theme_colors
        
        for line in self.hover_lines:
            try:
                line.remove()
            except:
                pass
        for ann in self.hover_annotations:
            try:
                ann.remove()
            except:
                pass
        self.hover_lines.clear()
        self.hover_annotations.clear()
        
        datasets = [self.temps, self.hums, self.precs, self.scores]
        units = ["°C", "%", " mm", ""]
        
        for ax_idx, ax in enumerate(self.axs.flat):
            l = ax.axvline(x=idx, color=tc["primary_btn"], linestyle="--", linewidth=1.0, alpha=0.8)
            self.hover_lines.append(l)
            
            val = datasets[ax_idx][idx]
            ann = ax.annotate(
                f"{val}{units[ax_idx]}",
                xy=(idx, val),
                xytext=(8, 8),
                textcoords="offset points",
                bbox=dict(boxstyle="round,pad=0.2", fc=tc["card"], ec=tc["input_bg"], alpha=0.9, lw=0.5),
                fontsize=7,
                color=tc["text_primary"]
            )
            self.hover_annotations.append(ann)
            
        self.lbl_hover_info.config(
            text=f"📍 {self.dates[idx]} | Sıcaklık: {self.temps[idx]}°C | Nem: %{self.hums[idx]} | Yağış: {self.precs[idx]}mm | Risk: {self.scores[idx]}",
            fg=tc["secondary_btn"]
        )
        self.canvas.draw_idle()


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Akıllı Kuraklık Analiz Sistemi")
        width, height = 420, 760
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")
        self.resizable(False, False)
        self.current_user_id = None
        self.current_username = ""
        self.theme_name = "Slate Koyu"
        self.theme_colors = THEMES[self.theme_name]
        self.configure(bg=self.theme_colors["bg"])
        generate_drought_images()
        generate_news_images()
        self.container = tk.Frame(self, bg=self.theme_colors["bg"])
        self.container.pack(fill="both", expand=True)
        self.setup_styles()
        self.show_login_screen()

    def get_color(self, key):
        return self.theme_colors.get(key, "#ffffff")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=self.get_color("bg"), foreground=self.get_color("text_primary"))
        style.configure("TFrame", background=self.get_color("bg"))
        style.configure("Vertical.TScrollbar", gripcount=0, background=self.get_color("input_bg"), bordercolor=self.get_color("bg"))

    def show_login_screen(self):
        for w in self.container.winfo_children():
            w.destroy()
        LoginScreen(self.container, self)

    def show_register_screen(self):
        for w in self.container.winfo_children():
            w.destroy()
        RegisterScreen(self.container, self)

    def login_success(self, user_id, username):
        self.current_user_id = user_id
        self.current_username = username
        profile = Database.get_user_profile(user_id)
        if profile:
            self.theme_name = profile[3] if profile[3] else "Slate Koyu"
            self.theme_colors = THEMES[self.theme_name]
        self.configure(bg=self.get_color("bg"))
        self.setup_styles()
        for w in self.container.winfo_children():
            w.destroy()
        self.main_app_layout = MainAppLayout(self.container, self)
        self.main_app_layout.pack(fill="both", expand=True)

    def logout(self):
        self.current_user_id = None
        self.current_username = ""
        self.theme_name = "Slate Koyu"
        self.theme_colors = THEMES[self.theme_name]
        self.configure(bg=self.get_color("bg"))
        self.setup_styles()
        self.show_login_screen()


# =====================================================================
# ÇALIŞTIRMA GİRİŞİ
# =====================================================================
if __name__ == "__main__":
    Database.initialize()
    app = App()
    app.mainloop()
