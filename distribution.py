import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from auth_data import yandex_password


def send_email(sender_email, sender_password, recipient_emails, cc_emails, subject, message):
    smtp_server = "smtp.yandex.com"  # Адрес SMTP-сервера Яндекса
    smtp_port = 587  # Порт SMTP-сервера Яндекса

    # Создание объекта сообщения
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipient_emails)  # Список адресов получателей
    msg["Cc"] = ", ".join(cc_emails)  # Список адресов копии
    msg["Subject"] = subject

    # Добавление текста сообщения
    msg.attach(MIMEText(message, "plain"))

    try:
        # Установка соединения с SMTP-сервером Яндекса
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        # Формирование списка всех адресов получателей (To + Cc)
        all_recipients = recipient_emails + cc_emails

        # Отправка сообщения
        server.sendmail(sender_email, all_recipients, msg.as_string())
        print("Уведомления успешно отправлены по электронной почте!")
    except Exception as e:
        print("Ошибка при отправке уведомлений:", str(e))
    finally:
        # Закрытие соединения с SMTP-сервером
        server.quit()


def check_result_and_send_email():
    """Проверяет, пустой файл или нет, если нет, то добавляет заголовок и отправляем письмо"""
    sender_email = "AutoNotice.Amtelsoft@yandex.ru"
    sender_password = yandex_password
    # Список адресов получателей
    recipient_email = [
        "A.Yakimov@amtelsoft.ru",
        'V.Kozhevnikova@amtelsoft.ru',
        'S.Konkovskii@amtelsoft.ru',
        'Aleksandra.Kochubei@softwarecom.ru',
        'Olga.Popova@softwarecom.ru',
        'Aleksandr.Pushkin@softwarecom.ru',
        'nataly.bakaeva@softwarecom.ru',
        'Vadim.Taranovsky@softwarecom.ru',
        'Anastasiya.Korotkova@softwarecom.ru',
        'Timur.Ibragimov@softwarecom.ru',
        'Markushin.Andrey@software.com',
        'Tatyana.Churakova@softwarecom.ru'
    ]

    cc_emails = [
        'k.Ignatiev@softwarecom.ru',
    ]

    subject = "Уведомление о статусах рабочих задач"

    text_to_prepend = "Уважаемые коллеги!\n\n" \
                      "Данная рассылка уведомляет вас, " \
                      "что следующие рабочие задания (по которым вы назначены исполнителем в JIRA) " \
                      "находятся в статусе 'В работе':\n" \
                      "Просьба передать информацию от инициатора на третью линию или наоборот\n\n"

    # Чтение данных из файла
    with open('result.txt', 'r', encoding='utf-8') as file:
        message = file.read()

    # Проверим, пустой ли файл, если нет, то добавим text_to_prepend сверху
    if not message:
        print('Нет рабочих задач в статусе "В работе"')
    else:
        message = text_to_prepend + message
        send_email(sender_email, sender_password, recipient_email, cc_emails, subject, message)


if __name__ == '__main__':
    check_result_and_send_email()
