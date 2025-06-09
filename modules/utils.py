import csv
import random
from datetime import datetime, timedelta
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def generate_user_data():
    try:
        # Загрузка имен и фамилий
        with open("data/names.txt", "r", encoding="utf-8") as f:
            names = f.read().splitlines()
        with open("data/surnames.txt", "r", encoding="utf-8") as f:
            surnames = f.read().splitlines()
        
        # Генерация случайных данных
        first_name = random.choice(names)
        last_name = random.choice(surnames)
        
        # Дата рождения (18-65 лет)
        end_date = datetime.now() - timedelta(days=365*18)
        start_date = end_date - timedelta(days=365*47)
        random_days = random.randint(0, (end_date - start_date).days)
        birth_date = (start_date + timedelta(days=random_days)).strftime("%d.%m.%Y")
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "birth_date": birth_date
        }
    except Exception as e:
        logger.error(f"Error generating user data: {str(e)}")
        return {
            "first_name": "Иван",
            "last_name": "Иванов",
            "birth_date": "01.01.1980"
        }

def save_account(account_data):
    try:
        with open("accounts.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=account_data.keys())
            if f.tell() == 0:
                writer.writeheader()
            writer.writerow(account_data)
    except Exception as e:
        logger.error(f"Error saving account: {str(e)}")

def get_today_registrations():
    try:
        df = pd.read_csv("accounts.csv")
        today = datetime.now().strftime("%Y-%m-%d")
        return df[df["registered_at"].str.startswith(today)].shape[0]
    except FileNotFoundError:
        return 0
    except Exception as e:
        logger.error(f"Error reading registrations: {str(e)}")
        return 0