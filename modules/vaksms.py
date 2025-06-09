import requests
import time

BASE_URL = "https://vak-sms.com/api"

def get_number(api_key, service):
    url = f"{BASE_URL}/getNumber"
    params = {
        "apiKey": api_key,
        "service": service,
        "country": "ru"
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("response") == "1":
        return data["tel"], data["id"]
    raise Exception(f"VakSMS error: {data.get('message', 'Unknown error')}")

def get_code(api_key, activation_id):
    url = f"{BASE_URL}/getSmsCode"
    params = {
        "apiKey": api_key,
        "id": activation_id
    }
    
    for _ in range(20):  # Ожидание 2 минуты
        response = requests.get(url, params=params)
        data = response.json()
        
        if data.get("response") == "1":
            return data["smsCode"]
        time.sleep(6)
    
    return None