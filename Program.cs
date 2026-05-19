using System;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;

namespace SonOyuncuStealth
{
    class Program
    {
        [DllImport("user32.dll")]
        private static extern short GetAsyncKeyState(int vKey);

        private const int BLINK_KEY = 0x46; // F tuşu
        private const int MAX_BLINK_MS = 1200; // Güvenli süre

        private static bool isEngaged = false;
        private static Stopwatch timer = new Stopwatch();

        static void Main(string[] args)
        {
            Console.Title = "YAHYA STEALTH NETWORK CONTROLLER";
            Console.WriteLine("------------------------------------------");
            Console.WriteLine("YAHYA PRIVATE STEALTH - BLINK ENGINE V2");
            Console.WriteLine("Durum: Hazır. F tuşuna basılı tut.");
            Console.WriteLine("------------------------------------------");

            while (true)
            {
                bool fPressed = (GetAsyncKeyState(BLINK_KEY) & 0x8000) != 0;

                if (fPressed && !isEngaged) ToggleBlink(true);
                else if (!fPressed && isEngaged) ToggleBlink(false);
                else if (isEngaged && timer.ElapsedMilliseconds > MAX_BLINK_MS) ToggleBlink(false);

                Thread.Sleep(5);
            }
        }

        private static string GetTargetProcessPath()
        {
            // Tüm süreçleri tara
            foreach (var proc in Process.GetProcesses())
            {
                // Hem "SonOyuncu" hem "Client" kelimelerini kapsayan süreçleri yakala
                if (proc.ProcessName.Contains("SonOyuncu", StringComparison.OrdinalIgnoreCase) || 
                    proc.ProcessName.Contains("Client", StringComparison.OrdinalIgnoreCase))
                {
                    try 
                    { 
                        string path = proc.MainModule.FileName;
                        return path; 
                    } 
                    catch { continue; }
                }
            }
            return null;
        }

        private static void ToggleBlink(bool state)
        {
            string path = GetTargetProcessPath();
            string ruleName = "SO_STEALTH_BLOCK";

            if (state)
            {
                if (path == null)
                {
                    Console.WriteLine("[!] HATA: Oyun süreci bulunamadı!");
                    return;
                }

                isEngaged = true;
                timer.Restart();
                // Kuralı sıfırdan oluştur
                Execute($"advfirewall firewall add rule name=\"{ruleName}\" dir=out action=block program=\"{path}\" enable=yes");
                Console.WriteLine($"[!] BLINK ACTIVE -> {path}");
            }
            else
            {
                isEngaged = false;
                timer.Stop();
                // Kuralı temizle
                Execute($"advfirewall firewall delete rule name=\"{ruleName}\"");
                Console.WriteLine("[+] BLINK RELEASED -> Paketler sunucuya aktarıldı.");
            }
        }

        private static void Execute(string args)
        {
            try
            {
                ProcessStartInfo psi = new ProcessStartInfo("netsh", args) 
                { 
                    CreateNoWindow = true, 
                    UseShellExecute = false,
                    Verb = "runas" // Yönetici olarak çalıştırılmasını zorla
                };
                Process.Start(psi);
            }
            catch (Exception ex) { Console.WriteLine("[!] Hata: " + ex.Message); }
        }
    }
}
