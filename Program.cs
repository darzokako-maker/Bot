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

        private const string TARGET_PROCESS = "SonOyuncu Client"; 
        private const int BLINK_KEY = 0x46; // F tuşu
        private const int MAX_BLINK_MS = 1200; // 1.2 saniye güvenlik sınırı

        private static bool isEngaged = false;
        private static Stopwatch timer = new Stopwatch();

        static void Main(string[] args)
        {
            Console.Title = "YAHYA STEALTH NETWORK CONTROLLER";
            Console.ForegroundColor = ConsoleColor.Cyan;
            Console.WriteLine("==================================================");
            Console.WriteLine("   YAHYA PRIVATE STEALTH - BLINK MODULE ACTIVE   ");
            Console.WriteLine("==================================================");
            Console.ForegroundColor = ConsoleColor.White;
            Console.WriteLine("[-] SonOyuncu odaklanildi. F'ye basili tutarak aktif et.");

            while (true)
            {
                bool fPressed = (GetAsyncKeyState(BLINK_KEY) & 0x8000) != 0;

                if (fPressed && !isEngaged) ToggleBlink(true);
                else if (!fPressed && isEngaged) ToggleBlink(false);
                else if (isEngaged && timer.ElapsedMilliseconds > MAX_BLINK_MS) ToggleBlink(false);

                Thread.Sleep(5);
            }
        }

        private static void ToggleBlink(bool state)
        {
            if (state)
            {
                isEngaged = true;
                timer.Restart();
                Execute("advfirewall firewall add rule name=\"SO_BLINK_ACTIVE\" dir=out action=block program=\"" + GetProcessPath(TARGET_PROCESS) + "\" enable=yes");
                Console.ForegroundColor = ConsoleColor.Red;
                Console.WriteLine("[!] BLINK ENGAGED (Paketler tutuluyor)");
            }
            else
            {
                isEngaged = false;
                timer.Stop();
                Execute("advfirewall firewall delete rule name=\"SO_BLINK_ACTIVE\"");
                Console.ForegroundColor = ConsoleColor.Green;
                Console.WriteLine("[+] BLINK RELEASED (Paketler iletildi) - Süre: " + timer.ElapsedMilliseconds + "ms");
            }
        }

        private static string GetProcessPath(string processName)
        {
            Process[] processes = Process.GetProcessesByName(processName);
            if (processes.Length > 0)
            {
                try { return processes[0].MainModule.FileName; } catch { }
            }
            return "C:\\Program Files\\SonOyuncu\\SonOyuncu Client.exe";
        }

        private static void Execute(string args)
        {
            var p = new ProcessStartInfo("netsh", args) { CreateNoWindow = true, UseShellExecute = false };
            Process.Start(p);
        }
    }
}

