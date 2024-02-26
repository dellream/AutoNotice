import time
from datetime import datetime
from pprint import pprint

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, \
    StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

from auth_data import jira_password, astp_password

# URLS
# Фильтр 'Для парсера'
jira_url = "https://jira.softwarecom.ru/login.jsp?os_destination=%2Fissues%2F%3Ffilter%3D34831"
astp_url = "http://10.103.0.106/maximo/webclient/login/login.jsp"


def login_jira(driver):
    """Авторизация в JIRA"""
    driver.get(url=jira_url)
    # Находим элементы формы входа на странице JIRA
    jira_login_input = driver.find_element(By.ID, 'login-form-username')
    jira_password_input = driver.find_element(By.ID, 'login-form-password')
    # Заполняем логин и пароль
    jira_login_input.clear()
    jira_login_input.send_keys('Aleksandra.Kochubei')
    jira_password_input.clear()
    jira_password_input.send_keys(jira_password)
    # Нажимаем клавишу ENTER для входа
    jira_password_input.send_keys(Keys.ENTER)
    time.sleep(1)


def parse_jira_tasks(driver):
    """Парсинг задач из JIRA"""

    all_tasks_title = []
    all_tasks_jira = []

    while True:

        try:
            # Ожидаем, пока элементы задач будут видимыми на странице
            WebDriverWait(driver, 30).until(
                expected_conditions.visibility_of_element_located(
                    (By.CLASS_NAME, "issue-link-summary")
                )
            )

            # Ищем заголовки и ключи задач на текущей странице
            current_tasks_title = driver.find_elements(By.CLASS_NAME, "issue-link-summary")
            current_tasks_jira = driver.find_elements(By.CLASS_NAME, "issue-link-key")

            # Добавляем найденные заголовки и ключи к общему списку
            all_tasks_title.extend([title.text for title in current_tasks_title])
            all_tasks_jira.extend([key.text for key in current_tasks_jira])

            # Проверяем наличие элемента пагинации
            pagination_element = driver.find_elements(By.CLASS_NAME, "nav-next")

            if pagination_element:
                print("Элемент навигации найден. Кликаем на стрелку пагинации.")
                # Кликаем на стрелку пагинации
                pagination_element[0].click()
            else:
                # Если элемента пагинации нет, выходим из цикла
                break
        except StaleElementReferenceException:
            print("Элемент пагинации устарел. Повторяем попытку.")
            continue

    # Получаем сырой номер РЗ из заголовка с возможными лишними символами
    task_title_list = [title.split(' ')[0] for title in all_tasks_title]

    # Убираем лишние символы и оставляем только цифры от номера РЗ
    cleaned_task_title_list = []

    for title in task_title_list:
        cleaned_title = ''.join(filter(str.isdigit, title))
        if cleaned_title:
            cleaned_task_title_list.append(cleaned_title)
        else:
            cleaned_task_title_list.append('В задаче не указан №РЗ')

    # Формируем словарь
    tasks_dict = {title: task for title, task in zip(cleaned_task_title_list, all_tasks_jira)}

    pprint(f'Словарь задач в JIRA: {tasks_dict}')
    print('Длина сформированного словаря задач в JIRA:', len(tasks_dict))

    return tasks_dict


def login_astp(driver):
    """Авторизация в АСТП"""
    # Открываем новую вкладку
    driver.execute_script("window.open('about:blank', '_blank');")
    # Переключаемся на новую вкладку
    driver.switch_to.window(driver.window_handles[1])
    # Загружаем страницу АСТП
    driver.get(url=astp_url)
    # Находим элементы формы входа на странице АСТП
    astp_login_input = driver.find_element(By.ID, 'username')
    astp_password_input = driver.find_element(By.ID, 'password')
    # Заполняем логин и пароль
    astp_login_input.clear()
    astp_login_input.send_keys('SUPPORTASV')
    astp_password_input.clear()
    astp_password_input.send_keys(astp_password)
    # Нажимаем клавишу ENTER для входа
    astp_password_input.send_keys(Keys.ENTER)
    WebDriverWait(driver, 180).until(
        expected_conditions.visibility_of_element_located(
            (By.ID, "m7f8f3e49_ns_menu_WO_MODULE_a")
        )
    )
    # time.sleep(1)


def navigate_to_work_tasks(driver):
    """Переход к рабочим заданиям в АСТП"""
    actions = ActionChains(driver)
    # Находим элемент родительского меню
    parent_element = driver.find_element(By.ID, "m7f8f3e49_ns_menu_WO_MODULE_a")
    # Наводим курсор на родительский элемент
    actions.move_to_element(parent_element).perform()
    # Ожидаем, пока элемент "Рабочие задания" будет видимым
    work_tasks_element = WebDriverWait(driver, 180).until(
        expected_conditions.visibility_of_element_located(
            (By.ID, "m7f8f3e49_ns_menu_WO_MODULE_sub_changeapp_WOTRACK_a")
        )
    )
    # Кликаем на элемент "Рабочие задания"
    work_tasks_element.click()
    # time.sleep(1)


def search_astp_tasks(driver, cleaned_task_title_list):
    """Поиск задач в АСТП"""
    # Находим поле ввода для поиска задач
    inputRZ = WebDriverWait(driver, 180).until(
        expected_conditions.visibility_of_element_located((By.ID, "m6a7dfd2f_tfrow_[C:1]_txt-tb"))
    )

    inputRZ.clear()  # Очищаем поле ввода
    inputRZ.send_keys(', '.join(cleaned_task_title_list))

    # Вывод всех рабочих заданий в консоль
    pprint(', '.join(cleaned_task_title_list))

    # Запоминаем количество рабочих задач после ввода списка рз до нажатия поиска
    previous_value = driver.find_element(By.ID, "m6a7dfd2f-lb3").text
    # Нажимаем клавишу поиска
    search_button = driver.find_element(By.ID, "m6a7dfd2f-ti2")
    search_button.click()

    # Без ожидания на этом этапе не кликается поиск, из-за чего формируется неправильный словарь, можно сделать
    # через time.sleep(5), но лучше другой вариант, который будет работать, если вставленные в inputRZ РЗ,
    # это не все РЗ в АСТП в стандартном фильтре

    # Ждем пока не поменяется количество рабочих задач
    WebDriverWait(driver, 30).until(
        lambda driver: driver.find_element(By.ID, "m6a7dfd2f-lb3").text != previous_value
    )


def parse_astp_tasks(driver, employees_second_name, tasks_list):
    """Парсинг задач из АСТП"""

    result_dict = {}
    chunk_count = ((len(tasks_list) + 20) // 20)
    print(chunk_count)
    current_row_index = 0  # Инициализация переменной для хранения текущего номера строки

    for iteration in range(1, chunk_count + 1):

        # Считываем страницу в каждой итерации (при переключении страниц)
        astp_page_source = driver.page_source
        astp_soup = BeautifulSoup(astp_page_source, "lxml")

        # Запись html для дебага при необходимости
        # with open(f'astp_page_{iteration}.html', 'w', encoding='utf-8') as file:
        #     file.write(astp_page_source)

        current_row_len = len(astp_soup.select('tr.tablerow')) + current_row_index - 1

        print(f'Индекс начальной строки на странице #{iteration}: ', current_row_index)
        print(f'Индекс конечной строки на странице #{iteration}: ', current_row_len)

        error_occurred = False  # Инициализируем флаг ошибки

        # Проходим по каждой строке на странице
        for i in range(current_row_index, current_row_len):
            print(f'Итерация i = {i}')
            row = astp_soup.select('tr.tablerow')[i - current_row_index]
            # Находим ячейки с номером задачи, статусом и фамилией сотрудника
            cell_task_number = row.find('td', id=f'm6a7dfd2f_tdrow_[C:1]-c[R:{i}]')
            cell_status = row.find('td', id=f'm6a7dfd2f_tdrow_[C:11]-c[R:{i}]')
            cell_second_name = row.find('td', id=f'm6a7dfd2f_tdrow_[C:21]-c[R:{i}]')
            if cell_status is not None:
                cell_status_text = cell_status.get_text()
                cell_second_name_text = cell_second_name.get_text()
                cell_task_number_text = cell_task_number.get_text()
                result_dict[cell_task_number_text] = [cell_second_name_text, cell_status_text]
            else:
                print(f'\n*** Внимание! *** Данные в итерации {iteration} '
                      f'не были считаны, произошла ошибка парсинга\n')
                error_occurred = True
                break
        if not error_occurred:
            print(f'Данные в итерации {iteration} были считаны')

        # Форматируем данные для вывода
        for task_number, values in result_dict.items():
            cell_value = values[0]
            for surname in employees_second_name:
                if surname.lower() in cell_value.lower():
                    result_dict[task_number] = [surname.capitalize(), values[1]]
                    break

        pprint(f'Промежуточный словарь результатов после итерации {iteration}: {result_dict}')

        current_row_index = current_row_len  # Обновляем значение индекса последней строки

        WebDriverWait(driver, 180).until(
            expected_conditions.visibility_of_element_located((By.ID, "m6a7dfd2f-ti7_img"))
        )

        # Проверяем, есть ли другие страницы с РЗ
        if iteration != chunk_count:
            toggle_element = driver.find_element(By.ID, 'm6a7dfd2f-ti7_img')  # Попытка обновить ссылку на элемент
            toggle_element.click()
            print(f'Кликнули на стрелку пагинации в итерации {iteration}')
            time.sleep(10)
        else:
            break

    pprint(f'\nСловарь результатов парсера: {result_dict}')
    return result_dict


def format_and_sort_file(result_dict, output_file='result.html'):
    """Отформатировать и отсортировать файл по фамилиям"""
    # Разделить строки на два блока: "В работе" и "Ожидает ответа инициатора"
    in_progress_block = {}
    pending_block = {}

    for task_number, values in result_dict.items():
        if 'В работе' in values[1]:
            surname = values[0]
            if surname not in in_progress_block:
                in_progress_block[surname] = []
            in_progress_block[surname].append(
                f'Рабочее задание {task_number} '
                f'(<a href="https://jira.softwarecom.ru/browse/{values[2]}">'
                f'https://jira.softwarecom.ru/browse/{values[2]}'
                f'</a>)\n'
            )
        elif 'Ожидает ответа инициатора' in values[1]:
            surname = values[0]
            if surname not in pending_block:
                pending_block[surname] = []
            pending_block[surname].append(
                f'Рабочее задание {task_number} '
                f'(<a href="https://jira.softwarecom.ru/browse/{values[2]}">'
                f'https://jira.softwarecom.ru/browse/{values[2]}'
                f'</a>)\n'
            )

    # Отсортировать каждый блок по фамилиям
    sorted_in_progress_block = sorted(in_progress_block.items(), key=lambda x: x[0])
    sorted_pending_block = sorted(pending_block.items(), key=lambda x: x[0])

    # Записать отсортированные блоки в новый файл
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('<html><body>\n')

        file.write('<h3>Рабочие задания "В работе":</h3>\n\n')
        for surname, tasks in sorted_in_progress_block:
            file.write(f'<p><b>{surname}:</b></p>\n')
            file.write('<ul>\n')
            for task in tasks:
                file.write(f'  <li>{task}</li>\n')
            file.write('</ul>\n')

        file.write(
            '<h3>Рабочие задания "Ожидает ответа инициатора" (внимание, данные РЗ могут быть под заглушками):</h3>\n\n')
        for surname, tasks in sorted_pending_block:
            file.write(f'<p><b>{surname}:</b></p>\n')
            file.write('<ul>\n')
            for task in tasks:
                file.write(f'  <li>{task}</li>\n')
            file.write('</ul>\n')

        file.write('</body></html>')

    print(f'Файл успешно отформатирован и отсортирован. Результат сохранен в {output_file}')


def timer(func):
    """Декоратор для подсчета времени выполнения"""

    def wrapper_around_func(*args, **kwargs):
        # Показываем время перед выполнением функции
        start_time = datetime.now()
        print(start_time.strftime('%H:%M:%S'))
        # Запускаем функцию с её аргументами и именованными аргументами
        result = func(*args, **kwargs)
        # Время после выполнения функции
        end_time = datetime.now()
        # Показываем сколько времени заняло выполнение функции
        execution_time = end_time - start_time
        # Отформатируем время с двумя знаками после запятой
        formatted_time = f"{execution_time.total_seconds():.2f}"
        print(f"Время выполнения: {formatted_time}")
        return result

    return wrapper_around_func


@timer
def webscrapper():
    employees_second_name = [
        'якимов',
        'кожевникова',
        'кочубей',
        'попова',
        'коньковский',
        'пушкин',
        'ибрагимов',
        'маркушин',
        'чуракова',
        'вольнова',
        'обух',
        'цветков',
        'грязева',
        'баранова'
    ]

    try:
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        login_jira(driver)
        print('1. Авторизация в JIRA пройдена успешно')

        tasks_dict = parse_jira_tasks(driver)
        print('2. Задачи в JIRA найдены успешно')

        login_astp(driver)
        print('3. Авторизация в АСТП пройдена успешно')

        navigate_to_work_tasks(driver)
        print('4. Переход к рабочим задачам пройден')

        search_astp_tasks(driver, list(tasks_dict.keys()))
        print('5. Рабочие задачи были успешно найдены')
        time.sleep(5)

        result_dict = parse_astp_tasks(driver, employees_second_name, list(tasks_dict.keys()))
        print('6. Сформирован словарь результатов')

        for key, value in tasks_dict.items():
            if key in result_dict:
                result_dict[key].append(value)

        format_and_sort_file(result_dict)

    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    webscrapper()
