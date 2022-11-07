#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import threading
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
from flask import render_template
import logging
from time import strftime
from logging.config import dictConfig
import os
from redisService import Redis
import jobService

tw = pytz.timezone('Asia/Taipei')
now = datetime.now(tw)

sched = BackgroundScheduler(timezone="Asia/Taipei", daemon=True)
# # 正式用如下
if os.getenv('ENVIRONMENT')=='master':
    sched.add_job(jobService.job_in_master, 'cron', day_of_week='mon-fri', hour='21,4', minute=31)
elif os.getenv('ENVIRONMENT')=='slave':
    sched.add_job(jobService.job_in_slave, 'cron', day_of_week='mon-fri', hour='21,4', minute=31)
sched.add_job(Redis.initialize_state_of_num_and_ticker_pairs_in_redis, 'cron', day_of_week='mon-fri', hour='19,23', minute=59, id='my_job_re')

# 測試用如下
# sched.add_job(jobService.job_in_master, 'cron', day_of_week='mon-fri',hour='16,21,22,4', minute=35, id='my_job_test')
# sched.add_job(Redis.initialize_state_of_num_and_ticker_pairs_in_redis, 'cron', day_of_week='mon-fri', hour='16,19,23', minute=59, id='my_job_re')


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


logging.config.dictConfig(dictConfig)
logger = logging.getLogger("file")
logger.info('info message')


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

@app.route('/')
def hello_world():
    return render_template('panel.html', system_datetime=datetime.now(), taipei_datetime=datetime.now(tw))


@app.route('/tool',methods=['GET'])
def sent_manually():
    environment = request.values.get('env')
    print(environment)
    if environment=='master':
        jobService.job_in_master()
    elif environment=='slave':
        jobService.job_in_slave()
    return "images sent"


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
    Redis.initialize_state_of_num_and_ticker_pairs_in_redis()
    return 'done'


@app.route('/redis-test')
def redis_connection_test():
    conn=Redis.get_redis_connection()
    return f'ping is {conn.ping()}'


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
