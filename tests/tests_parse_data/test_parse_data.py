import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from parse_data import login_jira, parse_jira_tasks, login_astp, navigate_to_work_tasks, search_astp_tasks, \
    parse_astp_tasks, write_result_to_file


# Фикстура для инициализации WebDriver
@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


# Тест для функции login_jira
def test_login_jira(driver):
    login_jira(driver)
    # Проверяем, что успешно авторизовались в JIRA
    # driver.title возвращает title текущего сайта
    assert "JIRA" in driver.title


# Тест для функции parse_jira_tasks
def test_parse_jira_tasks(driver):
    # Получаем текущий путь к файлу test_parse_data.py
    current_path = os.path.dirname(os.path.abspath(__file__))
    # Относительный путь до parse_jira_tasks.html
    relative_path = 'parse_jira_tasks.html'
    # Полный путь до parse_jira_tasks.html
    html_file_path = os.path.join(current_path, relative_path)

    # Загружаем тестовую страницу
    driver.get('file://' + html_file_path)
    # Парсим задачи
    tasks_dict = parse_jira_tasks(driver)
    # Проверяем результаты парсинга
    assert len(tasks_dict) == 4
    # Проверяем, все ли задачи в JIRA правильно прочитаны
    expected_titles = ["ASV2021-1", "ASV2021-2", "ASV2021-3", "ASV2021-4"]
    # Проверяем, что заголовки РЗ соответствуют ожидаемым значениям
    expected_keys = ["123", "1234", "12345", "123456"]
    for key, expected_title in zip(expected_keys, expected_titles):
        assert tasks_dict[key] == expected_title


# Тест для функции login_astp
def test_login_astp(driver):
    login_astp(driver)
    # Проверяем, что успешно авторизовались в astp
    # driver.title возвращает title текущего сайта
    assert "Center" or "Центр запуска" in driver.title


# Тест для функции navigate_to_work_tasks
def test_navigate_to_work_tasks(driver):
    login_astp(driver)
    navigate_to_work_tasks(driver)
    assert "Start Center" in driver.title


# Тест для функции search_astp_tasks
def test_search_astp_tasks(driver):
    login_astp(driver)
    navigate_to_work_tasks(driver)
    search_astp_tasks(driver, ["123", "456", "789"])
    inputRZ = WebDriverWait(driver, 20).until(
        expected_conditions.visibility_of_element_located((By.ID, "m6a7dfd2f_tfrow_[C:1]_txt-tb"))
    )

    # Проверяем, что введенный список номеров задач соответствует ожидаемому списку
    entered_tasks = inputRZ.get_attribute("value")
    expected_tasks = "123, 456, 789"
    assert entered_tasks == expected_tasks


# Тест для функции parse_astp_tasks
def test_parse_astp_tasks(driver):
    # Получаем текущий путь к файлу test_parse_data.py
    current_path = os.path.dirname(os.path.abspath(__file__))
    # Относительный путь до parse_astp_tasks.html
    relative_path = 'parse_astp_tasks.html'
    # Полный путь до parse_astp_tasks.html
    html_file_path = os.path.join(current_path, relative_path)

    # Загружаем тестовую страницу
    driver.get('file://' + html_file_path)

    result_dict = parse_astp_tasks(driver, ["Иванов", "Сидоров", "Петров", "Заглушка"])
    assert len(result_dict) == 3
    assert result_dict["123"] == ["Иванов", "В работе"]
    assert result_dict["456"] == ["Петров", "Завершено"]
    assert result_dict["789"] == ["Сидоров", "Ожидает ответа инициатора"]


# Тест для write_result_to_file
def test_write_result_to_file():
    result_dict = {
        "123": ["Иванов", "В работе", "ASV2021-1"],
        "456": ["Петров", "Завершено", "ASV2021-2"],
        "789": ["Сидоров", "Ожидает ответа инициатора", "ASV2021-3"]
    }
    # Полный путь к файлу result.txt в текущей директории
    current_dir = os.path.dirname(os.path.abspath(__file__))
    result_file_path = os.path.join(current_dir, "result.txt")
    write_result_to_file(result_dict)
    # Проверяем существование файла
    assert os.path.isfile(result_file_path)
    with open(result_file_path, "r", encoding='utf-8') as f:
        lines = f.readlines()
    assert lines[0] == "   * Иванов: Рабочее задание 123 (https://jira.softwarecom.ru/browse/ASV2021-1)\n"


# Запуск тестов
if __name__ == "__main__":
    pytest.main()
