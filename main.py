import customtkinter as ctk
from pymem import Pymem
from pymem.pattern import pattern_scan_all
import threading
import time
import ctypes
import random
import math

# Winlator/Windows API tuş gönderimi
class WinAPI:
    @staticmethod
    def key_event(key_code, down=True):
        flags = 0 if down else 2
        ctypes.windll.user32.keybd_event(key_code, 0, flags, 0)

class YahyaWinlatorFix(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Y-M2 Mobile Engine - Winlator Edition")
        self.geometry("850x850") # Ekran boyutunu Winlator'a göre ayarladım
        ctk.set_appearance_mode("dark")
        
        self.pm = None
        self.is_running = False
        self.is_fishing = False
        self.count_caught = 0
        
        self.setup_ui()

    def setup_ui(self):
        self.header = ctk.CTkLabel(self, text="MOBILE DELUXE ENGINE", font=("Impact", 30), text_color="#00FF41")
        self.header.pack(pady=10)

        # Ana Panel
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Kontroller
        self.btn_power = ctk.CTkButton(self.main_frame, text="SİSTEMİ BAĞLA", command=self.connect_game, fg_color="#1f538d")
        self.btn_power.pack(pady=10, padx=20, fill="x")

        # Mod Seçimi
        self.mode = ctk.StringVar(value="IDLE")
        ctk.CTkRadioButton(self.main_frame, text="Beklemede", variable=self.mode, value="IDLE").pack(pady=5)
        ctk.CTkRadioButton(self.main_frame, text="Balık Botu", variable=self.mode, value="FISH").pack(pady=5)

        # HATANIN KAYNAĞI BURASIYDI: to_ yerine to kullanıldı
        ctk.CTkLabel(self.main_frame, text="Çekme Gecikmesi (sn)").pack()
        self.fish_slider = ctk.CTkSlider(self.main_frame, from_=1, to=5, number_of_steps=4) # 'to_' düzeltildi
        self.fish_slider.pack(padx=10, pady=5)
        self.fish_slider.set(2.5)

        # Durum Göstergesi
        self.fish_light = ctk.CTkLabel(self.main_frame, text="●", font=("Consolas", 60), text_color="gray")
        self.fish_light.pack()

        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=350)
        self.progress_bar.pack(pady=10)
        self.progress_bar.set(0)

        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 11))
        self.log_box.pack(fill="x", padx=10, pady=10)

    def log(self, msg):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
        self.log_box.see("end")

    def connect_game(self):
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        try:
            self.pm = Pymem("metin2client.exe")
            self.log("Winlator üzerinden oyuna bağlanıldı!")
            # Pattern tarama Winlator'da yavaş olabilir, o yüzden hata kontrolü sıkı
            f_ptr = pattern_scan_all(self.pm.process_handle, rb"\x8B\x81\x64\x01\x00\x00\x85\xC0")
            
            if f_ptr:
                self.is_running = True
                self.main_loop(f_ptr)
        except Exception as e:
            self.log(f"Bağlantı Hatası: {e}")

    def main_loop(self, f_ptr):
        while self.is_running:
            if self.mode.get() == "FISH":
                # Olta At (F3)
                WinAPI.key_event(0x72, True); time.sleep(0.1); WinAPI.key_event(0x72, False)
                
                # Balık Bekle
                timeout = time.time() + 45
                while time.time() < timeout:
                    try:
                        bubble = self.pm.read_int(f_ptr + 0x64)
                        if bubble == 1:
                            self.catch_sequence()
                            break
                    except: break
                    time.sleep(0.2)
                time.sleep(3)
            time.sleep(0.1)

    def catch_sequence(self):
        self.fish_light.configure(text_color="#00FF41")
        wait = self.fish_slider.get()
        for i in range(101):
            self.progress_bar.set(i/100)
            time.sleep(wait/100)
        
        WinAPI.key_event(0x72, True); time.sleep(0.1); WinAPI.key_event(0x72, False)
        self.log("Balık çekildi!")
        self.fish_light.configure(text_color="gray")
        self.progress_bar.set(0)

if __name__ == "__main__":
    app = YahyaWinlatorFix()
    app.mainloop()
    
