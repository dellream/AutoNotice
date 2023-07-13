import time
import unittest
from unittest.mock import patch

from main import assemblage


class MainTestCase(unittest.TestCase):

    def test_assemblage(self):
        # Имитируем функции `webscrapper` и `check_result_and_send_email`
        with patch('main.webscrapper') as mock_webscrapper, \
             patch('main.check_result_and_send_email') as mock_check_result_and_send_email:
            assemblage()  # Вызываем функцию, которую мы тестируем

            # Проверяем, что функции `webscrapper` и `check_result_and_send_email` были вызваны
            self.assertTrue(mock_webscrapper.called)
            self.assertTrue(mock_check_result_and_send_email.called)


if __name__ == '__main__':
    unittest.main()
