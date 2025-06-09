import requests
import logging

logger = logging.getLogger(__name__)

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
        
        logger.info(f"Ответ BitBrowser: {response.status_code} {response.text}")
        data = response.json()
        
        # Обработка успешного ответа по новому формату
        if response.status_code == 200 and data.get("success", False):
            ws_url = data["data"]["ws"]
            logger.info(f"WebSocket URL: {ws_url}")
            return ws_url
        
        # Обработка ошибок
        if response.status_code == 401:
            raise Exception("Ошибка авторизации. Проверьте API ключ")
        elif response.status_code == 404:
            raise Exception("Эндпоинт не найден. Проверьте URL и метод")
        
        # Обработка других кодов ошибок
        response.raise_for_status()
        
        # Если ответ не содержит ожидаемых данных
        error_msg = data.get("msg") or data.get("message") or "Неизвестная ошибка BitBrowser"
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
    
# if __name__ == "__main__":
#     import sys
#     logging.basicConfig(level=logging.INFO)
    
#     if len(sys.argv) < 3:
#         print("Использование: python bitbrowser.py <API_KEY> <BROWSER_ID>")
#         sys.exit(1)
    
#     api_key = sys.argv[1]
#     browser_id = sys.argv[2]
    
#     try:
#         ws_url = get_browser_ws(api_key, browser_id)
#         print(f"WebSocket URL: {ws_url}")
#     except Exception as e:
#         print(f"Ошибка: {str(e)}")