import time
import sys
from parcer import *
from connection_to_db import Database
import datetime

from threading import Thread
import asyncio

db = Database()
db.set_db()


def parcing_event(db):
    while True:
        begin = datetime.datetime.now().timestamp()
        db.connect_to_db()
        cursor, existing_tasks = db.cursor, db.existing_tasks
        url = 'https://codeforces.com/problemset/page/1?order=BY_SOLVED_DESC&locale=ru'
        HEADERS = ({'User-Agent':
                        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36', \
                    'Accept-Language': 'en-US, en;q=0.5'})
        number_of_pages = number_of_pages_count(url, HEADERS)
        for num in range(1, number_of_pages + 1):
            url = f'https://codeforces.com/problemset/page/{num}?order=BY_SOLVED_DESC&locale=ru'
            print(f'--- parsing of page number {num} ---')
            parce_page(url, HEADERS, cursor, existing_tasks)
        db.close_connection()
        end = datetime.datetime.now().timestamp()
        time_to_next_parce = int(3600 - (end - begin))
        tt = int(time_to_next_parce)
        for i in range(time_to_next_parce):
            tt -= 1
            sys.stdout.write("\r")
            sys.stdout.write(f"time to next parce: {tt} seconds...")
            sys.stdout.flush()
            time.sleep(1)


from telegram_bot import main


def bot_event():
    asyncio.run(main())


thread1 = Thread(target=parcing_event, args=(db,))
thread2 = Thread(target=bot_event)

thread1.start()
thread2.start()
thread1.join()
thread2.join()
