import requests
import logging

logger = logging.getLogger(__name__)

def get_browser_list(api_key):
    url = "http://127.0.0.1:54345/browser/list"
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Запрос списка профилей: {url}")
        logger.info(f"Используемый API ключ: {api_key}")
        
        response = requests.get(url, headers=headers, timeout=10)
        logger.info(f"Статус ответа: {response.status_code}")
        logger.info(f"Текст ответа: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Проверка разных форматов ответа
            if isinstance(data, list):
                return data
            
            if data.get("success", False):
                return data.get("data", [])
            
            if "data" in data and isinstance(data["data"], list):
                return data["data"]
            
            logger.error(f"Неожиданный формат ответа: {data}")
            return []
        
        # Обработка ошибок авторизации
        if response.status_code == 401:
            logger.error("Ошибка авторизации: неверный API ключ")
            return []
        
        # Обработка других ошибок
        logger.error(f"Ошибка сервера: {response.status_code}")
        return []
        
    except requests.exceptions.ConnectionError:
        logger.error("Не удалось подключиться к BitBrowser. Убедитесь, что приложение запущено.")
        return []
    except requests.exceptions.Timeout:
        logger.error("Таймаут подключения к BitBrowser API")
        return []
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        return []

def check_browser_exists(api_key, browser_id):
    browsers = get_browser_list(api_key)
    for browser in browsers:
        if browser.get("id") == browser_id:
            return True
    return False

def get_browser_ws(api_key, browser_id):
    url = "http://127.0.0.1:54345/browser/open"
    payload = {
        "id": browser_id
    }
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Отправка запроса к BitBrowser: {url}")
        logger.info(f"Заголовки: {headers}")
        logger.info(f"Данные: {payload}")
        
        response = requests.post(
            url, 
            json=payload, 
            headers=headers,
            timeout=30
        )
        data = response.json()
        
        logger.info(f"Ответ BitBrowser: {response.status_code} {response.text}")
        
        if response.status_code == 200 and data.get("success", False):
            ws_url = data["data"]["ws"]
            logger.info(f"WebSocket URL: {ws_url}")
            return ws_url
        
        # Обработка специфических ошибок
        error_msg = data.get("msg") or data.get("message") or "Неизвестная ошибка BitBrowser"
        
        if "не были найдены" in error_msg:
            raise Exception(f"Профиль {browser_id} не найден. Проверьте ID профиля")
        
        raise Exception(f"Ошибка BitBrowser: {error_msg}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Сетевой сбой: {str(e)}")
    except Exception as e:
        raise Exception(f"Неожиданная ошибка: {str(e)}")

def close_browser(api_key, browser_id):
    url = "http://127.0.0.1:54345/browser/close"
    payload = {"id": browser_id}
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        logger.error(f"Ошибка закрытия браузера: {str(e)}")
        return {}