import customtkinter as ctk
from pymem import Pymem
from pymem.pattern import pattern_scan_all
import threading
import time
import ctypes
import math

# Windows API - Donanım Seviyesi Giriş Protokolü
class WinAPI:
    @staticmethod
    def key_event(key_code, down=True):
        flags = 0 if down else 2
        ctypes.windll.user32.keybd_event(key_code, 0, flags, 0)

class YahyaUltimateEngine(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("System Service Framework v6.5")
        self.geometry("800x850")
        ctk.set_appearance_mode("dark")
        
        # Engine Değişkenleri
        self.pm = None
        self.is_running = False
        self.is_connected = False
        self.auto_farm_active = False
        
        # Adresler
        self.local_player_addr = None
        self.entity_list_addr = None
        
        # UI Kurulumu
        self.setup_ui()

    def setup_ui(self):
        # Başlık ve Durum
        self.header = ctk.CTkLabel(self, text="Y-M2 ULTIMATE ENGINE", font=("Impact", 32), text_color="#00FF41")
        self.header.pack(pady=20)

        self.status_bar = ctk.CTkLabel(self, text="DURUM: OYUN BEKLENİYOR...", text_color="orange", font=("Consolas", 14))
        self.status_bar.pack()

        # Ana Kontrol Paneli
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(pady=10, padx=20, fill="both", expand=True)

        # Sol Panel: Kontroller
        self.left_panel = ctk.CTkFrame(self.main_frame, width=250)
        self.left_panel.pack(side="left", padx=10, pady=10, fill="y")

        self.btn_connect = ctk.CTkButton(self.left_panel, text="SİSTEMİ AKTİF ET", command=self.start_engine, fg_color="#1f538d", hover_color="#14375e")
        self.btn_connect.pack(pady=15, padx=10)

        self.farm_switch = ctk.CTkSwitch(self.left_panel, text="OTOMATİK FARM", command=self.toggle_farm)
        self.farm_switch.pack(pady=10, padx=10)

        self.label_info = ctk.CTkLabel(self.left_panel, text="CANLI VERİLER", font=("Consolas", 12, "bold"))
        self.label_info.pack(pady=(20, 5))

        self.data_display = ctk.CTkLabel(self.left_panel, text="X: 0\nY: 0\nYaw: 0", justify="left", font=("Consolas", 12))
        self.data_display.pack(pady=5)

        # Sağ Panel: Radar
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", padx=10, pady=10, fill="both", expand=True)

        self.radar_canvas = ctk.CTkCanvas(self.right_panel, width=400, height=400, bg="#080808", highlightthickness=1, highlightbackground="#00FF41")
        self.radar_canvas.pack(pady=10, padx=10)

        # Alt Panel: Loglar
        self.log_box = ctk.CTkTextbox(self, height=150, font=("Consolas", 11), fg_color="#000", text_color="#00FF41")
        self.log_box.pack(pady=10, padx=20, fill="x")

    def log(self, msg):
        self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] > {msg}\n")
        self.log_box.see("end")

    def toggle_farm(self):
        self.auto_farm_active = self.farm_switch.get()
        self.log(f"Auto-Farm Modu: {'AKTİF' if self.auto_farm_active else 'PASİF'}")

    def start_engine(self):
        if not self.is_connected:
            threading.Thread(target=self.core_logic, daemon=True).start()

    def core_logic(self):
        try:
            self.pm = Pymem("metin2client.exe")
            self.is_connected = True
            self.status_bar.configure(text="DURUM: BAĞLANDI (TARANIYOR...)", text_color="#00FF41")
            self.log(f"Proses bulundu (PID: {self.pm.process_id}). İmza taraması başladı.")

            # Hata payını sıfırlayan hassas tarama (Pattern Scanning)
            l_pattern = rb"\xD9\x51\x10\xD9\x51\x14\xD9\x51\x18"
            e_pattern = rb"\x8B\x42\x20\x85\xC0\x74"

            self.local_player_addr = pattern_scan_all(self.pm.process_handle, l_pattern)
            self.entity_list_addr = pattern_scan_all(self.pm.process_handle, e_pattern)

            if self.local_player_addr and self.entity_list_addr:
                self.log(f"Local Player: {hex(self.local_player_addr)}")
                self.log(f"Entity List: {hex(self.entity_list_addr)}")
                self.status_bar.configure(text="DURUM: SİSTEM AKTİF", text_color="#00FF41")
                self.is_running = True
                self.main_loop()
            else:
                self.log("HATA: İmzalar bulunamadı! Güncel pattern lazım.")
                self.is_connected = False
        except Exception as e:
            self.log(f"Bağlantı Hatası: Oyun açık mı?")
            self.is_connected = False

    def main_loop(self):
        while self.is_running:
            try:
                # 1. Kendi Verilerini Oku
                lx = self.pm.read_float(self.local_player_addr + 0x10)
                ly = self.pm.read_float(self.local_player_addr + 0x14)
                yaw = self.pm.read_float(self.local_player_addr + 0x18)
                
                self.data_display.configure(text=f"X: {lx:.2f}\nY: {ly:.2f}\nYaw: {yaw:.2f}")

                # 2. Varlık Taraması ve Hedefleme
                entities = []
                e_base = self.pm.read_int(self.entity_list_addr)
                target_coords = None
                min_dist = 2000

                for i in range(40): # İlk 40 varlık (Performans dostu)
                    try:
                        ptr = self.pm.read_int(e_base + (i * 4))
                        if ptr == 0: continue
                        
                        ex = self.pm.read_float(ptr + 0x10)
                        ey = self.pm.read_float(ptr + 0x14)
                        dist = math.sqrt((ex - lx)**2 + (ey - ly)**2)
                        
                        entities.append((ex, ey))
                        
                        if dist < min_dist and dist > 10: # Çok yakındakine bakma
                            min_dist = dist
                            target_coords = (ex, ey)
                    except: continue

                # 3. Otomatik İşlemler
                if self.auto_farm_active and target_coords:
                    # Karakteri döndür
                    angle = math.degrees(math.atan2(target_coords[1] - ly, target_coords[0] - lx))
                    self.pm.write_float(self.local_player_addr + 0x18, angle)
                    
                    # Atak yap
                    WinAPI.key_event(0x20, True)
                    time.sleep(0.01)
                    WinAPI.key_event(0x20, False)

                self.update_radar(lx, ly, entities)
                time.sleep(0.03) # ~33 FPS
            except Exception as e:
                self.log(f"Döngü hatası: {e}")
                break

    def update_radar(self, lx, ly, entities):
        self.radar_canvas.delete("all")
        cx, cy = 200, 200
        # Merkez (Oyuncu)
        self.radar_canvas.create_oval(cx-6, cy-6, cx+6, cy+6, fill="#00FF41", outline="white")
        
        for ex, ey in entities:
            rx = cx + (ex - lx) / 10
            ry = cy - (ey - ly) / 10
            if 0 < rx < 400 and 0 < ry < 400:
                self.radar_canvas.create_oval(rx-3, ry-3, rx+3, ry+3, fill="red", outline="")

if __name__ == "__main__":
    app = YahyaUltimateEngine()
    app.mainloop()
    
