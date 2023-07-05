import base64
import json
import requests


# value_header = "A.Yakimov:242531422qQZz#"
# base64_bytes = value_header.encode('ascii')
# base64_bytes_string = str(base64.b64encode(base64_bytes))[2:-1]
# headers = {"Authorization": "Basic " + base64_bytes_string,
#            "Accept": "*/*",
#            "Content-Type": "application/json"
#            }
#
#
# def get_data():
#     url = 'http://10.0.2.9/rest/api/2/search?jql=project%20%3D%20HD'
#     response = requests.get(url=url, headers=headers)
#     return json.loads(response.text)
#
# qwe = get_data()
employees_secondName = ['якимов', 'бакаева', 'кожевникова', 'кочубей', 'попова', 'коньковский', 'тарановский', ]

result_dict = {}

# Данные для добавления в словарь
data = [
    ("10914784", ['иванова;ASV2021-2310 эскалация;бакаева', 'Ожидает ответа инициатора']),
    ("11009439", ['Кожевникова 2.14.10.| ASV2021-2279', 'Ожидает ответа инициатора']),
    ("11018277", ['якимов 1.24.| incasso основа ASV2021-2338', 'Ожидает ответа инициатора']),
    ("11018362", ['1.4.| Кожевникова (ASV2021-2313)', 'Ожидает ответа инициатора'])
]

# Добавление данных в словарь
for task_number, values in data:
    result_dict[task_number] = values

# Вывод словаря
print(result_dict)



# Изменение словаря в соответствии с форматом {Номер задачи: [Фамилия исполнителя, Статус задачи]}
for task_number, values in data:
    cell_value = values[0]
    for surname in employees_secondName:
        if surname.lower() in cell_value.lower():
            result_dict[task_number] = [surname.capitalize(), values[1]]
            break

print(result_dict)

