from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import logging

logger = logging.getLogger(__name__)

def register_account(ws_url, phone, user_data):
    # Извлекаем адрес отладки из WebSocket URL
    debugger_address = ws_url.replace("ws://", "").split("/")[0]
    
    options = Options()
    options.add_experimental_option("debuggerAddress", debugger_address)
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://id.x5.ru/sign-up")
        
        # Заполнение формы
        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.NAME, "phone"))
        ).send_keys(phone)
        
        driver.find_element(By.NAME, "firstName").send_keys(user_data["first_name"])
        driver.find_element(By.NAME, "lastName").send_keys(user_data["last_name"])
        
        # Выбор даты рождения
        birthday_input = driver.find_element(By.NAME, "birthday")
        driver.execute_script(f"arguments[0].value = '{user_data['birth_date']}';", birthday_input)
        
        # Отправка формы
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Ожидание подтверждения
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "code"))
        )
        return True
    
    except TimeoutException as e:
        logger.error(f"Timeout during registration: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during registration: {str(e)}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

def confirm_code(ws_url, code):
    debugger_address = ws_url.replace("ws://", "").split("/")[0]
    
    options = Options()
    options.add_experimental_option("debuggerAddress", debugger_address)
    
    try:
        driver = webdriver.Chrome(options=options)
        
        # Предполагаем, что мы остались на странице ввода кода
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "code"))
        ).send_keys(code)
        
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Проверка успешной регистрации
        WebDriverWait(driver, 20).until(
            EC.url_contains("https://5ka.ru/")
        )
        return True
    except TimeoutException as e:
        logger.error(f"Timeout during code confirmation: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error during code confirmation: {str(e)}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass