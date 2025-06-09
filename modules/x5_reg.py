from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def register_account(ws_url, phone, user_data):
    options = Options()
    options.add_experimental_option("debuggerAddress", ws_url.split("/")[-1])
    
    driver = webdriver.Chrome(options=options)
    driver.get("https://id.x5.ru/sign-up")
    
    try:
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
        return {"success": True, "activation_id": phone}
    
    except TimeoutException:
        return None
    finally:
        driver.quit()

def confirm_code(ws_url, code):
    options = Options()
    options.add_experimental_option("debuggerAddress", ws_url.split("/")[-1])
    
    driver = webdriver.Chrome(options=options)
    
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.NAME, "code"))
        ).send_keys(code)
        
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        # Проверка успешной регистрации
        WebDriverWait(driver, 20).until(
            EC.url_contains("https://5ka.ru/")
        )
        return True
    except TimeoutException:
        return False
    finally:
        driver.quit()