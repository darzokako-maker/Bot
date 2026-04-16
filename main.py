import customtkinter as ctk
from pymem import Pymem
from pymem.pattern import pattern_scan_all
import threading
import time
import ctypes
import math
import random

# Windows Çekirdek Giriş Protokolü (Gizlilik İçin)
class WinAPI:
    @staticmethod
    def key_event(key_code, down=True):
        flags = 0 if down else 2
        ctypes.windll.user32.keybd_event(key_code, 0, flags, 0)

class YahyaMasterEngine(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("System Analyst v10.0 - Private Framework")
        self.geometry("950x950")
        ctk.set_appearance_mode("dark")
        
        # Hafıza ve Kontrol Değişkenleri
        self.pm = None
        self.is_running = False
        self.mode = ctk.StringVar(value="IDLE")
        
        # Dinamik Değerler
        self.local_x, self.local_y, self.yaw = 0, 0, 0
        self.entities = []
        self.fish_wait_min = 2.0
        self.fish_wait_max = 4.0

        self.setup_ui()

    def setup_ui(self):
        # Üst Başlık
        self.header = ctk.CTkLabel(self, text="Y-M2 MASTER ENGINE v10", font=("Impact", 40), text_color="#00FF41")
        self.header.pack(pady=15)

        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # --- SOL PANEL: AYARLAR ---
        self.left_panel = ctk.CTkFrame(self.main_container, width=300)
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)

        self.btn_power = ctk.CTkButton(self.left_panel, text="SİSTEMİ BAŞLAT", fg_color="#1f538d", height=45, command=self.start_engine)
        self.btn_power.pack(pady=20, padx=20, fill="x")

        # Mod Seçimi
        self.mode_frame = ctk.CTkFrame(self.left_panel)
        self.mode_frame.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(self.mode_frame, text="ÇALIŞMA MODU", font=("Consolas", 14, "bold")).pack(pady=5)
        for text, m in [("Beklemede", "IDLE"), ("Mob Farm (Otomatik)", "MOB"), ("Balık Botu (Görsel)", "FISH")]:
            ctk.CTkRadioButton(self.mode_frame, text=text, variable=self.mode, value=m).pack(pady=5, padx=20, anchor="w")

        # Balık Ayarları (Slider)
        self.fish_settings = ctk.CTkFrame(self.left_panel)
        self.fish_settings.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(self.fish_settings, text="Balık Çekme Gecikmesi (sn)", font=("Consolas", 12)).pack(pady=5)
        self.fish_slider = ctk.CTkSlider(self.fish_settings, from_=1, to_=5, number_of_steps=4)
        self.fish_slider.pack(padx=10, pady=5)
        self.fish_slider.set(2.5)

        # Veri Paneli
        self.data_panel = ctk.CTkFrame(self.left_panel, fg_color="#000")
        self.data_panel.pack(fill="x", padx=15, pady=20)
        self.lbl_stats = ctk.CTkLabel(self.data_panel, text="X: 0 | Y: 0\nYaw: 0°", font=("Consolas", 14), text_color="#00FF41")
        self.lbl_stats.pack(pady=10)

        # --- SAĞ PANEL: RADAR VE GÖRSEL TAKİP ---
        self.right_panel = ctk.CTkFrame(self.main_container)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.radar_canvas = ctk.CTkCanvas(self.right_panel, width=450, height=450, bg="#0a0a0a", highlightthickness=1, highlightbackground="#00FF41")
        self.radar_canvas.pack(pady=10)

        # Balık Durum Işığı ve Progress
        self.fish_indicator = ctk.CTkLabel(self.right_panel, text="●", font=("Consolas", 50), text_color="gray")
        self.fish_indicator.pack()
        self.fish_progress = ctk.CTkProgressBar(self.right_panel, width=400)
        self.fish_progress.pack(pady=10)
        self.fish_progress.set(0)

        # Log
        self.log_box = ctk.CTkTextbox(self, height=120, font=("Consolas", 11), fg_color="#000")
        self.log_box.pack(fill="x", padx=20, pady=15)

    def log(self, msg):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
        self.log_box.see("end")

    def start_engine(self):
        threading.Thread(target=self.core_worker, daemon=True).start()

    def core_worker(self):
        try:
            self.pm = Pymem("metin2client.exe")
            self.log("Bağlantı başarılı. Bellek haritası çıkarılıyor...")
            
            # Patternler (Bu kısımlar servera göre güncellenmeli)
            l_addr = pattern_scan_all(self.pm.process_handle, rb"\xD9\x51\x10\xD9\x51\x14\xD9\x51\x18")
            e_addr = pattern_scan_all(self.pm.process_handle, rb"\x8B\x42\x20\x85\xC0\x74")
            f_addr = pattern_scan_all(self.pm.process_handle, rb"\x8B\x81\x64\x01\x00\x00\x85\xC0")

            if l_addr:
                self.is_running = True
                self.main_loop(l_addr, e_addr, f_addr)
        except:
            self.log("HATA: Oyun bulunamadı veya yetki yetersiz!")

    def main_loop(self, l_ptr, e_ptr, f_ptr):
        while self.is_running:
            try:
                # 1. Temel Verileri Oku
                self.local_x = self.pm.read_float(l_ptr + 0x10)
                self.local_y = self.pm.read_float(l_ptr + 0x14)
                self.yaw = self.pm.read_float(l_ptr + 0x18)
                self.lbl_stats.configure(text=f"X: {self.local_x:.1f} | Y: {self.local_y:.1f}\nYaw: {int(self.yaw)}°")

                current_mode = self.mode.get()
                
                # 2. Mob Farm Mantığı
                if current_mode == "MOB":
                    self.run_mob_farm(l_ptr, e_ptr)
                
                # 3. Balık Botu Mantığı
                elif current_mode == "FISH":
                    self.run_fish_farm(f_ptr)

                self.render_radar()
                time.sleep(0.03)
            except: break

    def run_mob_farm(self, l_ptr, e_ptr):
        base = self.pm.read_int(e_ptr)
        self.entities = []
        target = None
        min_dist = 1200
        
        for i in range(40):
            try:
                obj = self.pm.read_int(base + (i * 4))
                if obj == 0: continue
                ex, ey = self.pm.read_float(obj + 0x10), self.pm.read_float(obj + 0x14)
                dist = math.sqrt((ex - self.local_x)**2 + (ey - self.local_y)**2)
                self.entities.append((ex, ey))
                if dist < min_dist:
                    min_dist, target = dist, (ex, ey)
            except: continue

        if target:
            angle = math.degrees(math.atan2(target[1] - self.local_y, target[0] - self.local_x))
            self.pm.write_float(l_ptr + 0x18, angle)
            WinAPI.key_event(0x20, True) # Space
            time.sleep(0.01)
            WinAPI.key_event(0x20, False)

    def run_fish_farm(self, f_ptr):
        try:
            # Balık durumu kontrolü
            bubble = self.pm.read_int(f_ptr + 0x64)
            if bubble == 1:
                self.fish_indicator.configure(text_color="#00FF41")
                self.log("Balık vurdu! Ayarlanan sürede çekiliyor...")
                
                wait = self.fish_slider.get() + random.uniform(-0.3, 0.3)
                for i in range(101):
                    self.fish_progress.set(i/100)
                    time.sleep(wait/100)
                
                WinAPI.key_event(0x72, True) # F3
                time.sleep(0.1)
                WinAPI.key_event(0x72, False)
                self.log("Çekildi! 3sn sonra tekrar atılıyor...")
                time.sleep(3)
                WinAPI.key_event(0x72, True) # F3 at
                time.sleep(0.1)
                WinAPI.key_event(0x72, False)
                self.fish_progress.set(0)
            else:
                self.fish_indicator.configure(text_color="gray")
        except: pass

    def render_radar(self):
        self.radar_canvas.delete("all")
        cx, cy = 225, 225
        # Kendi yönün (Yaw Çizgisi)
        rad = math.radians(self.yaw)
        self.radar_canvas.create_line(cx, cy, cx+math.cos(rad)*35, cy-math.sin(rad)*35, fill="#00FF41", width=2)
        # Oyuncu
        self.radar_canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill="#00FF41", outline="white")
        # Moblar
        for ex, ey in self.entities:
            rx, ry = cx + (ex - self.local_x)/10, cy - (ey - self.local_y)/10
            if 0 < rx < 450 and 0 < ry < 450:
                self.radar_canvas.create_oval(rx-3, ry-3, rx+3, ry+3, fill="red", outline="")

if __name__ == "__main__":
    app = YahyaMasterEngine()
    app.mainloop()
    
