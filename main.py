import time

import schedule

from distribution import check_result_and_send_email
from parse_data import webscrapper


def assemblage():
    webscrapper()
    check_result_and_send_email()


manual_start = True
schedule.every(59).minutes.do(assemblage)

while True:
    if manual_start:  # Если ручной старт, то запустить код сразу
        assemblage()
        manual_start = False
    schedule.run_pending()
    time.sleep(1)
