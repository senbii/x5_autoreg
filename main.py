import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
import time
import random
import logging
from datetime import datetime
from modules import bitbrowser, vaksms, x5_reg, utils

# Настройка логирования
logging.basicConfig(
    filename='errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoregApp:
    def __init__(self, root):
        self.root = root
        self.root.title("X5 Autoregistrator")
        self.root.geometry("800x600")
        self.is_running = False
        self.load_config()
        
        self.setup_ui()
        self.update_log("Приложение запущено. Загружена конфигурация.")
    
    def load_config(self):
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
        except FileNotFoundError:
            self.config = {
                "bitbrowser_token": "",
                "vaksms_token": "",
                "max_accounts": 400,
                "delay_min": 30,
                "delay_max": 120,
                "browser_ids": []
            }
            self.save_config()
    
    def save_config(self):
        with open('config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def setup_ui(self):
        # Фрейм настроек
        settings_frame = ttk.LabelFrame(self.root, text="Настройки")
        settings_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(settings_frame, text="BitBrowser Token:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.bb_token_entry = ttk.Entry(settings_frame, width=50)
        self.bb_token_entry.insert(0, self.config["bitbrowser_token"])
        self.bb_token_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(settings_frame, text="VakSMS Token:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.sms_token_entry = ttk.Entry(settings_frame, width=50)
        self.sms_token_entry.insert(0, self.config["vaksms_token"])
        self.sms_token_entry.grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(settings_frame, text="ID профилей (через запятую):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.browser_ids_entry = ttk.Entry(settings_frame, width=50)
        self.browser_ids_entry.insert(0, ",".join(self.config["browser_ids"]))
        self.browser_ids_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Кнопка обновления списка профилей
        self.refresh_btn = ttk.Button(settings_frame, text="Обновить профили", command=self.refresh_profiles)
        self.refresh_btn.grid(row=2, column=2, padx=5, pady=2)
        
        ttk.Label(settings_frame, text="Макс. аккаунтов:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.max_acc_entry = ttk.Entry(settings_frame, width=10)
        self.max_acc_entry.insert(0, str(self.config["max_accounts"]))
        self.max_acc_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        ttk.Label(settings_frame, text="Задержка (сек):").grid(row=4, column=0, sticky="w", padx=5, pady=2)
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.grid(row=4, column=1, sticky="w")
        ttk.Label(delay_frame, text="От").pack(side="left")
        self.delay_min_entry = ttk.Entry(delay_frame, width=5)
        self.delay_min_entry.insert(0, str(self.config["delay_min"]))
        self.delay_min_entry.pack(side="left", padx=2)
        ttk.Label(delay_frame, text="до").pack(side="left")
        self.delay_max_entry = ttk.Entry(delay_frame, width=5)
        self.delay_max_entry.insert(0, str(self.config["delay_max"]))
        self.delay_max_entry.pack(side="left", padx=2)
        
        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_btn = ttk.Button(btn_frame, text="Старт", command=self.start)
        self.start_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="Стоп", command=self.stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        self.save_btn = ttk.Button(btn_frame, text="Сохранить настройки", command=self.save_settings)
        self.save_btn.pack(side="right", padx=5)
        
        # Логгер
        log_frame = ttk.LabelFrame(self.root, text="Лог выполнения")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_area = scrolledtext.ScrolledText(log_frame, wrap="word")
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_area.config(state="disabled")
    
    def refresh_profiles(self):
        try:
            token = self.bb_token_entry.get().strip()
            if not token:
                messagebox.showerror("Ошибка", "Введите BitBrowser Token")
                return
            
            self.update_log("Запрос списка профилей...")
            
            profiles = bitbrowser.get_browser_list(token)
            if not profiles:
                self.update_log("Не удалось получить список профилей. Проверьте:", error=True)
                self.update_log("1. BitBrowser запущен", error=True)
                self.update_log("2. API ключ верный", error=True)
                self.update_log("3. Порт API 54345 открыт", error=True)
                return
            
            profile_ids = [p["id"] for p in profiles if "id" in p]
            
            if not profile_ids:
                self.update_log("Получен пустой список профилей. Проверьте:", error=True)
                self.update_log("1. В BitBrowser созданы профили", error=True)
                self.update_log("2. Профили включены", error=True)
                return
            
            self.config["browser_ids"] = profile_ids
            self.browser_ids_entry.delete(0, tk.END)
            self.browser_ids_entry.insert(0, ",".join(profile_ids))
            self.save_config()
            self.update_log(f"Получено {len(profile_ids)} профилей")
        except Exception as e:
            self.update_log(f"Ошибка обновления профилей: {str(e)}", error=True)
    
    def save_settings(self):
        try:
            self.config["bitbrowser_token"] = self.bb_token_entry.get()
            self.config["vaksms_token"] = self.sms_token_entry.get()
            self.config["browser_ids"] = [x.strip() for x in self.browser_ids_entry.get().split(",") if x.strip()]
            self.config["max_accounts"] = int(self.max_acc_entry.get())
            self.config["delay_min"] = int(self.delay_min_entry.get())
            self.config["delay_max"] = int(self.delay_max_entry.get())
            
            self.save_config()
            self.update_log("Настройки успешно сохранены!")
        except Exception as e:
            self.update_log(f"Ошибка сохранения: {str(e)}", error=True)
    
    def update_log(self, message, error=False):
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        
        self.log_area.config(state="normal")
        self.log_area.insert(tk.END, log_msg + "\n")
        
        if error:
            self.log_area.tag_add("error", "end-1c linestart", "end-1c lineend")
            self.log_area.tag_config("error", foreground="red")
            logging.error(message)
        
        self.log_area.config(state="disabled")
        self.log_area.see(tk.END)
    
    def start(self):
        if not self.config["bitbrowser_token"]:
            self.update_log("Ошибка: BitBrowser Token не указан!", error=True)
            return
        
        if not self.config["vaksms_token"]:
            self.update_log("Ошибка: VakSMS Token не указан!", error=True)
            return
        
        if not self.config["browser_ids"]:
            self.update_log("Ошибка: ID профилей не указаны!", error=True)
            return
        
        self.is_running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        # Запуск в отдельном потоке
        self.thread = threading.Thread(target=self.run_registration, daemon=True)
        self.thread.start()
    
    def stop(self):
        self.is_running = False
        self.update_log("Процесс остановки...")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
    
    def run_registration(self):
        registered_today = utils.get_today_registrations()
        max_acc = min(self.config["max_accounts"], 400)
        
        if registered_today >= max_acc:
            self.update_log(f"Достигнут лимит: {registered_today}/{max_acc} аккаунтов сегодня")
            self.stop()
            return
        
        self.update_log(f"Начало регистрации. За сегодня: {registered_today}/{max_acc}")
        
        while self.is_running and registered_today < max_acc:
            browser_id = random.choice(self.config["browser_ids"])
            
            try:
                # Проверка существования профиля
                if not bitbrowser.check_browser_exists(
                    self.config["bitbrowser_token"],
                    browser_id
                ):
                    self.update_log(f"Профиль {browser_id} не найден! Пропускаем...", error=True)
                    continue
                
                # Подключение к BitBrowser
                ws_url = bitbrowser.get_browser_ws(
                    self.config["bitbrowser_token"],
                    browser_id
                )
                self.update_log(f"Запущен профиль {browser_id}")
                
                # Генерация данных
                user_data = utils.generate_user_data()
                
                # Получение номера телефона
                phone, activation_id = vaksms.get_number(self.config["vaksms_token"], "x5id")
                self.update_log(f"Получен номер: {phone}")
                
                # Регистрация аккаунта
                result = x5_reg.register_account(
                    ws_url, 
                    phone, 
                    user_data
                )
                
                if result:
                    # Получение кода SMS
                    code = vaksms.get_code(
                        self.config["vaksms_token"], 
                        activation_id
                    )
                    
                    if code:
                        # Подтверждение кода
                        if x5_reg.confirm_code(ws_url, code):
                            # Сохранение аккаунта
                            utils.save_account({
                                "phone": phone,
                                "first_name": user_data["first_name"],
                                "last_name": user_data["last_name"],
                                "birth_date": user_data["birth_date"],
                                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            })
                            registered_today += 1
                            self.update_log(f"Успешная регистрация! {phone} | {registered_today}/{max_acc}")
                        else:
                            self.update_log("Ошибка подтверждения кода", error=True)
                    else:
                        self.update_log("Не получен SMS код", error=True)
                else:
                    self.update_log("Ошибка регистрации", error=True)
            except Exception as e:
                self.update_log(f"Ошибка: {str(e)}", error=True)
            finally:
                try:
                    bitbrowser.close_browser(
                        self.config["bitbrowser_token"],
                        browser_id
                    )
                except Exception as e:
                    self.update_log(f"Ошибка при закрытии браузера: {str(e)}", error=True)
            
            if self.is_running and registered_today < max_acc:
                delay = random.randint(
                    self.config["delay_min"],
                    self.config["delay_max"]
                )
                self.update_log(f"Пауза: {delay} сек...")
                time.sleep(delay)
        
        self.update_log("Регистрация завершена!")
        self.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoregApp(root)
    root.mainloop()