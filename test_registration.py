import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

class TestRegistrationPage:
    """Класс для тестирования страницы регистрации"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Настройка перед каждым тестом"""
        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # Обязательные опции для GitHub Actions
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--headless")  # Без графического интерфейса
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # Открытие тестовой страницы на GitHub Pages
        test_url = "https://ksksdiiee.github.io/ci-cd-lab9-autotests/registration.html"
        print(f"Открываем URL: {test_url}")
        self.driver.get(test_url)
        
        # Инициализация явного ожидания
        self.wait = WebDriverWait(self.driver, 10)
        
        yield  # выполнение теста
        
        # Закрытие браузера после теста
        self.driver.quit()
    
    def fill_registration_form(self, user_data):
        """Заполняет форму регистрации данными пользователя"""
        fields = {
            "firstName": user_data.get("first_name", ""),
            "lastName": user_data.get("last_name", ""),
            "email": user_data.get("email", ""),
            "phone": user_data.get("phone", ""),
            "nickname": user_data.get("nickname", ""),
            "password": user_data.get("password", ""),
            "confirmPassword": user_data.get("password", "")
        }
        
        for field_id, value in fields.items():
            if value:
                element = self.driver.find_element(By.ID, field_id)
                element.clear()
                element.send_keys(value)
                print(f"Заполнено поле {field_id}: {value}")
        
        # Установка чекбокса согласия
        if user_data.get("terms_accepted", True):
            terms_checkbox = self.driver.find_element(By.ID, "terms")
            if not terms_checkbox.is_selected():
                terms_checkbox.click()
            print("Чекбокс согласия установлен")
    
    def test_successful_registration(self):
        """Тест успешной регистрации с валидными данными"""
        print("\n=== Тест успешной регистрации ===")
        
        # Данные для регистрации
        user_data = {
            "first_name": "Иван",
            "last_name": "Иванов",
            "email": "ivanov@example.com",
            "phone": "+7 (999) 123-45-67",
            "nickname": "ivan123",
            "password": "TestPassword123!",
            "terms_accepted": True
        }
        
        # Заполняем форму
        self.fill_registration_form(user_data)
        
        # Нажимаем кнопку регистрации
        register_button = self.driver.find_element(By.ID, "register-btn")
        register_button.click()
        print("Нажата кнопка 'Зарегистрироваться'")
        
        try:
            # Ожидание появления страницы приветствия
            welcome_page = self.wait.until(
                EC.visibility_of_element_located((By.ID, "welcome-page"))
            )
            
            # Проверка, что страница приветствия отображается
            assert welcome_page.is_displayed(), "Страница приветствия не отображается"
            print("✓ Страница приветствия отображается")
            
            # Проверка имени пользователя
            user_name_element = self.driver.find_element(By.ID, "user-name")
            displayed_name = user_name_element.text
            expected_name = f"{user_data['first_name']} {user_data['last_name']}"
            assert displayed_name == expected_name, \
                f"Имя пользователя не совпадает. Ожидалось: {expected_name}, Получено: {displayed_name}"
            print(f"✓ Имя пользователя корректно: {displayed_name}")
            
            # Проверка отображения данных
            data_elements = {
                "display-firstName": user_data["first_name"],
                "display-lastName": user_data["last_name"],
                "display-email": user_data["email"],
                "display-phone": user_data["phone"],
                "display-nickname": user_data["nickname"]
            }
            
            for element_id, expected_value in data_elements.items():
                element = self.driver.find_element(By.ID, element_id)
                actual_value = element.text
                assert actual_value == expected_value, \
                    f"Данные не совпадают для {element_id}. Ожидалось: {expected_value}, Получено: {actual_value}"
                print(f"✓ Данные {element_id}: {actual_value}")
            
            # Проверка наличия кнопки выхода
            logout_button = self.driver.find_element(By.ID, "logout-btn")
            assert logout_button.is_displayed(), "Кнопка выхода не отображается"
            logout_text = logout_button.text
            assert "Выйти" in logout_text or "Logout" in logout_text, \
                f"Текст кнопки не содержит 'Выйти': {logout_text}"
            print(f"✓ Кнопка выхода: '{logout_text}'")
            
            print("✓ ТЕСТ ПРОЙДЕН: Регистрация прошла успешно")
            
        except Exception as e:
            print(f"✗ ТЕСТ ПРОВАЛЕН: {str(e)}")
            # Сделаем скриншот при ошибке
            self.driver.save_screenshot("test_registration_failed.png")
            raise
    
    def test_registration_with_empty_fields(self):
        """Тест регистрации с пустыми обязательными полями"""
        print("\n=== Тест регистрации с пустыми полями ===")
        
        # Нажимаем кнопку регистрации без заполнения полей
        register_button = self.driver.find_element(By.ID, "register-btn")
        register_button.click()
        
        try:
            # Ожидание сообщения об ошибке
            error_message = self.wait.until(
                EC.visibility_of_element_located((By.ID, "message"))
            )
            
            assert error_message.is_displayed(), "Сообщение об ошибке не отображается"
            
            # Проверка класса сообщения
            class_attribute = error_message.get_attribute("class")
            assert "error" in class_attribute, \
                f"Сообщение не является ошибкой. Класс: {class_attribute}"
            
            # Проверка текста сообщения
            message_text = error_message.text
            expected_text = "заполните все обязательные поля"
            assert expected_text.lower() in message_text.lower(), \
                f"Текст сообщения не содержит ожидаемую фразу. Текст: {message_text}"
            
            print(f"✓ ТЕСТ ПРОЙДЕН: Получено сообщение об ошибке: '{message_text}'")
            
        except Exception as e:
            print(f"✗ ТЕСТ ПРОВАЛЕН: {str(e)}")
            self.driver.save_screenshot("test_empty_fields_failed.png")
            raise
    
    def test_registration_without_terms(self):
        """Тест регистрации без согласия с условиями"""
        print("\n=== Тест регистрации без согласия с условиями ===")
        
        # Заполняем форму, но не устанавливаем чекбокс
        user_data = {
            "first_name": "Петр",
            "last_name": "Петров",
            "email": "petrov@example.com",
            "nickname": "petr456",
            "password": "PetrPass123!",
            "terms_accepted": False  # Не устанавливаем чекбокс
        }
        
        self.fill_registration_form(user_data)
        
        # Снимаем чекбокс, если он был установлен
        terms_checkbox = self.driver.find_element(By.ID, "terms")
        if terms_checkbox.is_selected():
            terms_checkbox.click()
        
        # Нажимаем кнопку регистрации
        register_button = self.driver.find_element(By.ID, "register-btn")
        register_button.click()
        
        try:
            # Ожидание сообщения об ошибке
            error_message = self.wait.until(
                EC.visibility_of_element_located((By.ID, "message"))
            )
            
            assert error_message.is_displayed(), "Сообщение об ошибке не отображается"
            
            # Проверка текста сообщения
            message_text = error_message.text
            expected_text = "согласиться с условиями"
            assert expected_text.lower() in message_text.lower(), \
                f"Текст сообщения не содержит ожидаемую фразу. Текст: {message_text}"
            
            print(f"✓ ТЕСТ ПРОЙДЕН: Получено сообщение об ошибке: '{message_text}'")
            
        except Exception as e:
            print(f"✗ ТЕСТ ПРОВАЛЕН: {str(e)}")
            self.driver.save_screenshot("test_no_terms_failed.png")
            raise
    
    def test_registration_with_invalid_email(self):
        """Тест регистрации с невалидным email"""
        print("\n=== Тест регистрации с невалидным email ===")
        
        user_data = {
            "first_name": "Сергей",
            "last_name": "Сергеев",
            "email": "invalid-email",  # Невалидный email
            "nickname": "sergey789",
            "password": "SergeyPass123!",
            "terms_accepted": True
        }
        
        self.fill_registration_form(user_data)
        
        # Нажимаем кнопку регистрации
        register_button = self.driver.find_element(By.ID, "register-btn")
        register_button.click()
        
        try:
            # Ожидание сообщения об ошибке
            error_message = self.wait.until(
                EC.visibility_of_element_located((By.ID, "message"))
            )
            
            assert error_message.is_displayed(), "Сообщение об ошибке не отображается"
            
            # Проверка текста сообщения
            message_text = error_message.text
            expected_text = "корректный email"
            assert expected_text.lower() in message_text.lower(), \
                f"Текст сообщения не содержит ожидаемую фразу. Текст: {message_text}"
            
            print(f"✓ ТЕСТ ПРОЙДЕН: Получено сообщение об ошибке: '{message_text}'")
            
        except Exception as e:
            print(f"✗ ТЕСТ ПРОВАЛЕН: {str(e)}")
            self.driver.save_screenshot("test_invalid_email_failed.png")
            raise
    
    def test_registration_with_weak_password(self):
        """Тест регистрации со слабым паролем"""
        print("\n=== Тест регистрации со слабым паролем ===")
        
        user_data = {
            "first_name": "Алексей",
            "last_name": "Алексеев",
            "email": "alexeev@example.com",
            "nickname": "alex123",
            "password": "weak",  # Слабый пароль
            "terms_accepted": True
        }
        
        self.fill_registration_form(user_data)
        
        # Нажимаем кнопку регистрации
        register_button = self.driver.find_element(By.ID, "register-btn")
        register_button.click()
        
        try:
            # Ожидание сообщения об ошибке
            error_message = self.wait.until(
                EC.visibility_of_element_located((By.ID, "message"))
            )
            
            assert error_message.is_displayed(), "Сообщение об ошибке не отображается"
            
            # Проверка текста сообщения
            message_text = error_message.text
            expected_texts = ["пароль", "символ", "символов"]
            assert any(expected in message_text.lower() for expected in expected_texts), \
                f"Текст сообщения не содержит ожидаемую фразу. Текст: {message_text}"
            
            print(f"✓ ТЕСТ ПРОЙДЕН: Получено сообщение об ошибке: '{message_text}'")
            
        except Exception as e:
            print(f"✗ ТЕСТ ПРОЙДЕН: {str(e)}")
            self.driver.save_screenshot("test_weak_password_failed.png")
            raise
    
    def test_registration_with_mismatched_passwords(self):
        """Тест регистрации с несовпадающими паролями"""
        print("\n=== Тест регистрации с несовпадающими паролями ===")
        
        # Заполняем основную форму
        user_data = {
            "first_name": "Дмитрий",
            "last_name": "Дмитриев",
            "email": "dmitriev@example.com",
            "nickname": "dima456",
            "password": "DmitriyPass123!",
            "terms_accepted": True
        }
        
        self.fill_registration_form(user_data)
        
        # Вводим другой пароль для подтверждения
        confirm_password_field = self.driver.find_element(By.ID, "confirmPassword")
        confirm_password_field.clear()
        confirm_password_field.send_keys("DifferentPass123!")
        print("Введен несовпадающий пароль для подтверждения")
        
        # Нажимаем кнопку регистрации
        register_button = self.driver.find_element(By.ID, "register-btn")
        register_button.click()
        
        try:
            # Ожидание сообщения об ошибке
            error_message = self.wait.until(
                EC.visibility_of_element_located((By.ID, "message"))
            )
            
            assert error_message.is_displayed(), "Сообщение об ошибке не отображается"
            
            # Проверка текста сообщения
            message_text = error_message.text
            expected_text = "пароли не совпадают"
            assert expected_text.lower() in message_text.lower(), \
                f"Текст сообщения не содержит ожидаемую фразу. Текст: {message_text}"
            
            print(f"✓ ТЕСТ ПРОЙДЕН: Получено сообщение об ошибке: '{message_text}'")
            
        except Exception as e:
            print(f"✗ ТЕСТ ПРОВАЛЕН: {str(e)}")
            self.driver.save_screenshot("test_mismatched_passwords_failed.png")
            raise
    
    def test_logout_functionality(self):
        """Тест функциональности выхода из системы"""
        print("\n=== Тест функциональности выхода ===")
        
        # Сначала успешно регистрируемся
        user_data = {
            "first_name": "Анна",
            "last_name": "Аннова",
            "email": "annova@example.com",
            "nickname": "anna789",
            "password": "AnnaPass123!",
            "terms_accepted": True
        }
        
        self.fill_registration_form(user_data)
        
        register_button = self.driver.find_element(By.ID, "register-btn")
        register_button.click()
        
        # Ждем успешной регистрации
        self.wait.until(
            EC.visibility_of_element_located((By.ID, "welcome-page"))
        )
        
        # Нажимаем кнопку выхода
        logout_button = self.driver.find_element(By.ID, "logout-btn")
        logout_button.click()
        print("Нажата кнопка 'Выйти'")
        
        try:
            # Ожидание возврата к форме регистрации
            registration_form = self.wait.until(
                EC.visibility_of_element_located((By.ID, "registration-form"))
            )
            
            assert registration_form.is_displayed(), "Форма регистрации не отобразилась после выхода"
            
            # Проверка, что поля очищены
            fields_to_check = ["firstName", "lastName", "email", "nickname", "password", "confirmPassword"]
            for field_id in fields_to_check:
                field = self.driver.find_element(By.ID, field_id)
                assert field.get_attribute("value") == "", f"Поле {field_id} не очищено"
            
            # Проверка, что чекбокс не установлен
            terms_checkbox = self.driver.find_element(By.ID, "terms")
            assert not terms_checkbox.is_selected(), "Чекбокс согласия не сброшен"
            
            print("✓ ТЕСТ ПРОЙДЕН: Выход выполнен успешно, форма сброшена")
            
        except Exception as e:
            print(f"✗ ТЕСТ ПРОВАЛЕН: {str(e)}")
            self.driver.save_screenshot("test_logout_failed.png")
            raise

if __name__ == "__main__":
    # Запуск тестов вручную
    pytest.main([__file__, "-v", "-s"])