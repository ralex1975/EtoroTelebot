#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
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

# t1 = threading.Thread(target=telegramBot.main(), daemon=True)
# t1.start()  # start the bot in a thread instead

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
    watchListToday = whatCanTradeToday.main()
    for i in watchListToday:
        sendPhotoByTelegram.main(i)


sched = BackgroundScheduler(timezone="Asia/Taipei", daemon=True)
# https://apscheduler.readthedocs.io/en/3.x/modules/triggers/interval.html?highlight=interval
# sched.add_job(reportByBot, 'interval', minutes=30)
# https://apscheduler.readthedocs.io/en/3.x/modules/triggers/cron.html?highlight=cron
# sched.add_job(reportByBot, 'cron', day_of_week='mon-fri', hour=5, minute=30, end_date='2017-10-30')
# 正式用如下
# sched.add_job(reportByBot, 'cron', day_of_week='mon-fri', hour='21,4', minute=31)
# 測試用如下
sched.add_job(reportByBot, 'cron', day_of_week='mon-fri',
              hour='11,12,21,4', minute=4)

sched.start()

app = Flask(__name__)


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
            "filename": "flask.log",
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
    app.logger.info('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    print('after request finished:'+request.url)
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
    watchListToday = whatCanTradeToday.main()
    for i in watchListToday:
        sendPhotoByTelegram.main(i)
    return "images sent"


@app.route('/log')
def show_log():
    text = ""
    with open("flask.log", mode="r") as log:
        # text=log
        for i in log.readlines():
            # print(i)
            # print(type(i))
            text += i
            text += '<br>'
    return text


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
