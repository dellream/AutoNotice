import unittest
from unittest import mock
from outlook_jira_notifications.distribution import check_result_and_send_email, send_email


class SendEmailTestCase(unittest.TestCase):
    @mock.patch('smtplib.SMTP')
    def test_send_email(self, mock_smtp):
        sender_email = 'sender@example.com'
        sender_password = 'password'
        recipient_emails = ['recipient1@example.com', 'recipient2@example.com']
        cc_emails = ['cc1@example.com', 'cc2@example.com']
        subject = 'Test Subject'
        message = 'Test Message'

        # Создание экземпляра SMTP мока
        mock_smtp_instance = mock_smtp.return_value

        # Запуск тестируемой функции
        send_email(sender_email, sender_password, recipient_emails, cc_emails, subject, message)

        # Проверка вызовов методов на моке SMTP
        mock_smtp.assert_called_once_with('smtp.yandex.com', 587)
        mock_smtp_instance.starttls.assert_called_once()
        mock_smtp_instance.login.assert_called_once_with(sender_email, sender_password)
        mock_smtp_instance.sendmail.assert_called_once()
        mock_smtp_instance.quit.assert_called_once()


class CheckResultAndSendEmailTestCase(unittest.TestCase):
    @mock.patch('distribution.send_email')
    @mock.patch('builtins.open')
    def test_check_result_and_send_email(self, mock_open, mock_send_email):
        # Задаем мок-объект для функции send_email()
        mock_send_email.return_value = None

        # Задаем возвращаемое значение метода read()
        mock_open.return_value.__enter__.return_value.read.return_value = 'Рабочие задачи'

        # Запуск тестируемой функции
        check_result_and_send_email()

        # Проверка вызовов методов на количество вызовов
        mock_send_email.assert_called_once()
        mock_open.assert_called_once_with('result.txt', 'r', encoding='utf-8')
        mock_open.return_value.__enter__.return_value.read.assert_called_once()


if __name__ == '__main__':
    unittest.main()
