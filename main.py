import customtkinter as ctk
from pymem import Pymem
from pymem.pattern import pattern_scan_all
import threading
import time
import ctypes
import random

# Windows/Winlator API Protokolü
class WinAPI:
    @staticmethod
    def key_event(key_code, down=True):
        flags = 0 if down else 2
        ctypes.windll.user32.keybd_event(key_code, 0, flags, 0)

class YahyaFinalPure(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("System Framework v11.5 - Final Pure")
        self.geometry("850x850") # Winlator ekranına tam uyum
        ctk.set_appearance_mode("dark")
        
        self.pm = None
        self.is_running = False
        self.count_caught = 0
        self.start_time = time.time()
        
        self.setup_ui()

    def setup_ui(self):
        # Başlık ve İstatistik
        self.header = ctk.CTkLabel(self, text="ULTIMATE PURE FISHING", font=("Impact", 35), text_color="#00FF41")
        self.header.pack(pady=15)

        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=15, pady=10)

        # Kontroller Paneli
        self.ctrl_frame = ctk.CTkFrame(self.main_container, width=300)
        self.ctrl_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.btn_connect = ctk.CTkButton(self.ctrl_frame, text="OYUNA BAĞLAN", command=self.start_engine, fg_color="#1f538d", height=40)
        self.btn_connect.pack(pady=20, padx=20, fill="x")

        self.mode_var = ctk.StringVar(value="IDLE")
        ctk.CTkRadioButton(self.ctrl_frame, text="Beklemede", variable=self.mode_var, value="IDLE").pack(pady=10)
        ctk.CTkRadioButton(self.ctrl_frame, text="Botu Başlat", variable=self.mode_var, value="FISH").pack(pady=10)

        ctk.CTkLabel(self.ctrl_frame, text="Çekme Gecikmesi (sn)").pack(pady=(20, 5))
        # Winlator Fix: to_ yerine to
        self.delay_slider = ctk.CTkSlider(self.ctrl_frame, from_=1.0, to=5.0, number_of_steps=8)
        self.delay_slider.pack(padx=10)
        self.delay_slider.set(2.5)

        # Görsel Takip Paneli
        self.visual_frame = ctk.CTkFrame(self.main_container)
        self.visual_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        self.status_light = ctk.CTkLabel(self.visual_frame, text="●", font=("Consolas", 100), text_color="gray")
        self.status_light.pack(pady=20)

        self.progress = ctk.CTkProgressBar(self.visual_frame, width=400, height=20)
        self.progress.pack(pady=10)
        self.progress.set(0)

        self.lbl_stats = ctk.CTkLabel(self.visual_frame, text="Balık: 0 | Süre: 00:00", font=("Consolas", 16), text_color="#00FF41")
        self.lbl_stats.pack(pady=10)

        # Log Çıktısı
        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 12), fg_color="#000")
        self.log_box.pack(fill="x", padx=15, pady=15)

    def log(self, msg):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
        self.log_box.see("end")

    def start_engine(self):
        threading.Thread(target=self.core_logic, daemon=True).start()

    def core_logic(self):
        try:
            self.pm = Pymem("metin2client.exe")
            self.log("Winlator üzerinden Metin2'ye bağlanıldı.")
            # Balık kabarcığı adresi (Pattern)
            f_addr = pattern_scan_all(self.pm.process_handle, rb"\x8B\x81\x64\x01\x00\x00\x85\xC0")
            
            if f_addr:
                self.is_running = True
                self.run_bot(f_addr)
        except:
            self.log("HATA: Oyun bulunamadı!")

    def run_bot(self, f_ptr):
        while self.is_running:
            # İstatistik güncelle
            uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.start_time))
            self.lbl_stats.configure(text=f"Balık: {self.count_caught} | Süre: {uptime}")

            if self.mode_var.get() == "FISH":
                # 1. Olta At (F3)
                WinAPI.key_event(0x72, True); time.sleep(0.1); WinAPI.key_event(0x72, False)
                self.log("Olta atıldı...")

                # 2. Balık Bekle
                timeout = time.time() + 45
                while time.time() < timeout and self.mode_var.get() == "FISH":
                    bubble = self.pm.read_int(f_ptr + 0x64)
                    if bubble == 1:
                        self.catch_process()
                        break
                    time.sleep(0.1)
                
                time.sleep(3) # Yeni tur beklemesi
            time.sleep(0.5)

    def catch_process(self):
        self.status_light.configure(text_color="#00FF41") # Yeşil Işık
        self.log("BALIK GELDİ!")
        
        # İnsansı Gecikme (Slider'dan alınan değer + rastgelelik)
        wait = self.delay_slider.get() + random.uniform(-0.2, 0.2)
        for i in range(101):
            self.progress.set(i/100)
            time.sleep(wait/100)

        # Oltayı Çek (F3)
        WinAPI.key_event(0x72, True); time.sleep(0.1); WinAPI.key_event(0x72, False)
        self.count_caught += 1
        self.log(f"Yakalandı! (Toplam: {self.count_caught})")
        
        self.status_light.configure(text_color="gray")
        self.progress.set(0)

if __name__ == "__main__":
    app = YahyaFinalPure()
    app.mainloop()
    
