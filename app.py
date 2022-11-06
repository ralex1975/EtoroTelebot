#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, g, request
from flask import render_template
import sendPhotoByTelegram
import whatCanTradeToday
import logging
from logging.handlers import RotatingFileHandler
import traceback
from time import strftime
from logging.config import dictConfig
import os
# t1 = threading.Thread(target=telegramBot.main(), daemon=True)
# t1.start()  # start the bot in a thread instead
import redisService

tw = pytz.timezone('Asia/Taipei')
now = datetime.now(tw)
print(now)


def reportByBot():
    print('job in')

    # open0930pm = now
    # close0430am = now
    # if 5 >= now.hour >= 0:  # 過夜了
    #     open0930pm = now.replace(day=now.day - 1, hour=21, minute=30, second=0, microsecond=0)
    #     close0430am = now.replace(hour=4, minute=30, second=0, microsecond=0)
    # elif 24 >= now.hour >= 21:  # 未過夜
    #     open0930pm = now.replace(hour=21, minute=30, second=0, microsecond=0)
    #     close0430am = now.replace(day=now.day + 1, hour=4, minute=30, second=0, microsecond=0)
    # else:  # 不行運作的時候
    #     pass
    # if close0430am > now > open0930pm:
    #     watchListToday = whatCanTradeToday.main()
    #     for i in watchListToday:
    #         sendPhotoByTelegram.main(i)

    ticker = ['27', '28', '29', '1002', '1003', '18', '3025', '3246', '3163', '3306',
              '4465', '4459', '3008', '1467', '45', '63', '1111', '3006', '1951',
              '5968', '1588', '93', '6357', '3024', '3019', '4269', '3004', '1118',
              '2316', '4463', '4251', '100000']

    nameList = ['spx500', 'nsdq100', 'dj30', 'goog', 'fb', 'gold', 'gld', 'uvxy', 'vix',
                'qqq', 'tqqq', 'sqqq', 'xle', 'gs', 'usd_cnh', 'usd_mxn', 'tsla', 'ma',
                'swn', 'tdoc', 'x', 'cotton', 'smh', 'xly', 'xli', 'iwd', 'xlf', 'brk_b',
                '2318_hk', 'soxx', 'isrg', 'btc']

    # 範例：myList=['8887,FOXF', '8888,PNFP', '8889,PNW', '8890,WWD', '8891,BL']

    # ['27,spx500', '28,nsdq100', '29,dj30', '1002,goog', '1003,fb', '18,gold', '3025,gld', '3246,uvxy', '3163,vix',
    #  '3306,qqq', '4465,tqqq', '4459,sqqq', '3008,xle', '1467,gs', '45,usd_cnh', '63,usd_mxn', '1111,tsla', '3006,ma',
    #  '1951,swn', '5968,tdoc', '1588,x', '93,cotton', '6357,smh', '3024,xly', '3019,xli', '4269,iwd', '3004,xlf',
    #  '1118,brk_b', '2316,2318_hk', '4463,soxx', '4251,isrg', '100000,btc']

    myList = list()
    for i, j in zip(ticker, nameList):
        items = str(i) + ',' + str(j)
        myList.append(items)

    watchListToday = whatCanTradeToday.main(myList, bb_range=2)
    for i in watchListToday:
        sendPhotoByTelegram.main(i)


sched = BackgroundScheduler(timezone="Asia/Taipei", daemon=True)
# https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html?highlight=interval
# sched.add_job(reportByBot, 'interval', minutes=30)
# https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html?highlight=cron
# sched.add_job(reportByBot, 'cron', day_of_week='mon-fri', hour=5, minute=30, end_date='2017-10-30')
# 正式用如下
sched.add_job(reportByBot, 'cron', day_of_week='mon-fri', hour='21,4', minute=31)
# 測試用如下
# sched.add_job(reportByBot, 'cron', day_of_week='mon-sun',
#               hour='21,22,4', minute=26)

sched.start()

app = Flask(__name__)

dir_path = os.path.dirname(os.path.realpath(__file__))

dictConfig = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s | %(module)s >>> %(message)s",
            "datefmt": "%B %d, %Y %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": f'{dir_path}\\flask.log',
            "formatter": "default",
        },
    },
    "loggers": {
        "console_logger": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "file_logger": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": False,
        }
    },
    "root": {"level": "DEBUG", "handlers": ["console", "file"]},
}

# timezone取消，會有編碼問題
# "datefmt": "%B %d, %Y %H:%M:%S %Z",
# "encoding": "utf-8"

logging.config.dictConfig(dictConfig)
logger = logging.getLogger("file")
logger.info('info message')


# # 註冊一個函數，在處理第一個請求之前執行
# @app.before_first_request
# def before_request():
#     print('before request started:'+request.url)

# # 註冊一個函數，在每次請求之前執行
# @app.before_request
# def before_request():
#     print('before request started:'+request.url)

# 註冊一個函數，如果沒有未處理的異常拋出，在每次請求之後執行
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    ##有dictConfig後就都不需要這些app.logger了
    app.logger.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme,
                    request.full_path, response.status)
    print('after request finished:' + request.url)
    response.headers['key'] = 'value'
    return response


# # 註冊一個函數，如果有未處理的異常拋出，在每次請求之後執行
# @app.teardown_request
# def teardown_request(exception):
#     print('teardown request:'+request.url)


# @app.errorhandler(Exception)
# def exceptions(e):
#     tb = traceback.format_exc()
#     timestamp = strftime('[%Y-%b-%d %H:%M]')
#     app.logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, tb)
#     return e.status_code


@app.route('/')
def hello_world():
    return render_template('panel.html', system_datetime=datetime.now(), taipei_datetime=datetime.now(tw))


@app.route('/tool')
def sent_manually():
    conn = redisService.get_redis_connection("localhost", 6379, "")
    remaining = len(redisService.get_member_in_initial_state(conn, redisService.ETORO_DICT_KEY_NAME))
    # print(remaining)
    while remaining > 0:
        threads = []
        for i in range(5):  # 五條(太多條會429 too many request)
            # 啟動執行續前取出要執行的ticker，並在啟動下一條執行續前把狀態從未取用(111)改成已取用(999)，避免重複取
            num_ticker = redisService.get_member_in_initial_state(conn, redisService.ETORO_DICT_KEY_NAME)
            for ticker in num_ticker:
                redisService.change_state_of_num_and_ticker_pairs_in_redis_when_finish(conn, ticker)
            # 啟動執行續
            threads.append(threading.Thread(name=f'{i}', target=job, args=(num_ticker, str(i))))
            threads[i].start()
        # 五條都做完再做下一批
        for i in range(5):
            threads[i].join()
        print("Done.")
        remaining = len(redisService.get_member_in_initial_state(conn, redisService.ETORO_DICT_KEY_NAME))
    return "images sent"


def job(num_ticker, thread_number: str = ""):
    watchListToday = whatCanTradeToday.main(num_ticker, thread_number,3)
    for i in watchListToday:
        try:
            sendPhotoByTelegram.main(i)
        except Exception as e:
            print(e)


@app.route('/log')
def show_log():
    text = ""
    with open(dir_path + "\\flask.log", mode="r") as log:
        # text=log
        for i in log.readlines():
            # print(i)
            # print(type(i))
            text += i
            text += '<br>'
    return text


@app.route('/re')
def initialize_state_of_num_and_ticker_pairs_in_redis():
    conn = redisService.get_redis_connection("localhost", 6379, "")
    redisService.initialize_state_of_num_and_ticker_pairs_in_redis(conn)
    return 'done'


if __name__ == '__main__':
    # # 記log
    # handler = RotatingFileHandler('app.log', maxBytes=100000, backupCount=3)
    # app.logger = logging.getLogger('tdm')
    # app.logger.setLevel(logging.ERROR)
    # app.logger.addHandler(handler)

    # flask重啟時會有兩條執行續，不能讓他們都跑，不然會有兩張圖(use_reloader=False)
    # app.run(debug=True, use_reloader=False)
    # app.run(debug=False, port=os.getenv("PORT", default=5000))
    app.run(use_reloader=False, debug=False,
            port=os.getenv("PORT", default=5000))
    # app.run(debug=True, port=os.getenv("PORT", default=5000))
