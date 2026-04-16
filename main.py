import customtkinter as ctk
from pymem import Pymem
from pymem.pattern import pattern_scan_all
import threading
import time
import ctypes
import math

# Windows Alt Seviye Girişleri (Gizli Tuş Gönderimi)
class WinAPI:
    @staticmethod
    def key_event(key_code, down=True):
        flags = 0 if down else 2
        ctypes.windll.user32.keybd_event(key_code, 0, flags, 0)

class YahyaGhostEngine(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WinUpdateService v6.0") # Gizli isim
        self.geometry("750x800")
        ctk.set_appearance_mode("dark")
        
        self.pm = None
        self.is_running = False
        self.auto_farm_active = False
        self.local_x, self.local_y = 0, 0
        self.entities = []
        
        self.setup_ui()

    def setup_ui(self):
        self.header = ctk.CTkLabel(self, text="GHOST ENGINE v6.0", font=("Consolas", 24, "bold"), text_color="#00FF41")
        self.header.pack(pady=20)

        self.btn_connect = ctk.CTkButton(self, text="SİSTEMİ BAŞLAT", command=self.start_engine, fg_color="#1a1a1a", border_width=2, border_color="#00FF41")
        self.btn_connect.pack(pady=10)

        self.farm_switch = ctk.CTkSwitch(self, text="OTOMATİK HEDEF & SALDIRI", command=self.toggle_farm)
        self.farm_switch.pack(pady=10)

        self.radar_canvas = ctk.CTkCanvas(self, width=400, height=400, bg="#050505", highlightthickness=0)
        self.radar_canvas.pack(pady=15)

        self.log_box = ctk.CTkTextbox(self, width=680, height=180, font=("Consolas", 11))
        self.log_box.pack(pady=10)

    def log(self, msg):
        self.log_box.insert("end", f"[LOG] {msg}\n")
        self.log_box.see("end")

    def toggle_farm(self):
        self.auto_farm_active = self.farm_switch.get()
        self.log(f"Auto-Farm: {'AKTİF' if self.auto_farm_active else 'PASİF'}")

    def start_engine(self):
        threading.Thread(target=self.core_logic, daemon=True).start()

    def core_logic(self):
        try:
            self.pm = Pymem("metin2client.exe")
            self.log(f"Bağlantı Kuruldu! PID: {self.pm.process_id}")
            
            # --- KRİTİK İMZALAR (Oyun Versiyonuna Göre Değişebilir) ---
            l_addr = pattern_scan_all(self.pm.process_handle, rb"\xD9\x51\x10\xD9\x51\x14\xD9\x51\x18")
            e_addr = pattern_scan_all(self.pm.process_handle, rb"\x8B\x42\x20\x85\xC0\x74")

            if l_addr and e_addr:
                self.is_running = True
                self.log("Adresler cımbızla çekildi. Av başlıyor.")
                self.main_loop(l_addr, e_addr)
            else:
                self.log("HATA: İmzalar eşleşmedi, güncelleme gerekebilir.")
        except Exception as e:
            self.log(f"Bağlantı Hatası: {e}")

    def main_loop(self, l_addr, e_addr):
        while self.is_running:
            try:
                self.local_x = self.pm.read_float(l_addr + 0x10)
                self.local_y = self.pm.read_float(l_addr + 0x14)
                
                self.entities = []
                e_ptr = self.pm.read_int(e_addr)
                target_mob = None
                min_dist = 1500

                for i in range(50):
                    try:
                        obj = self.pm.read_int(e_ptr + (i * 4))
                        if obj == 0: continue
                        ex = self.pm.read_float(obj + 0x10)
                        ey = self.pm.read_float(obj + 0x14)
                        dist = math.sqrt((ex - self.local_x)**2 + (ey - self.local_y)**2)
                        self.entities.append({'x': ex, 'y': ey})
                        if dist < min_dist:
                            min_dist = dist
                            target_mob = (ex, ey)
                    except: continue

                if self.auto_farm_active and target_mob:
                    dx = target_mob[0] - self.local_x
                    dy = target_mob[1] - self.local_y
                    angle = math.degrees(math.atan2(dy, dx))
                    try:
                        self.pm.write_float(l_addr + 0x18, angle) # Yaw yazımı
                    except: pass
                    WinAPI.key_event(0x20, True) # Space bas
                    time.sleep(0.01)
                    WinAPI.key_event(0x20, False) # Bırak

                self.update_radar()
                time.sleep(0.04)
            except: break

    def update_radar(self):
        self.radar_canvas.delete("all")
        cx, cy = 200, 200
        self.radar_canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill="#00FF41", outline="")
        for e in self.entities:
            rx = cx + (e['x'] - self.local_x) / 10
            ry = cy - (e['y'] - self.local_y) / 10
            if 5 < rx < 395 and 5 < ry < 395:
                self.radar_canvas.create_oval(rx-2, ry-2, rx+2, ry+2, fill="#FF0000", outline="")

if __name__ == "__main__":
    app = YahyaGhostEngine()
    app.mainloop()
          
