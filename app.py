import os
from datetime import datetime
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask import render_template
import sendPhotoByTelegram
import whatCanTradeToday

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
sched.add_job(reportByBot, 'cron', day_of_week='mon-fri', hour='21,23,4', minute=3)
sched.start()

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('panel.html', system_datetime=datetime.now(), taipei_datetime=datetime.now(tw))


#
# @app.route('/about.html')
# def about():
#     return render_template('about.html')
#
#
# @app.route('/index.html')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/blog.html')
# def blog():
#     return render_template('blog.html')
#
#
# @app.route('/sidebar-left.html')
# def sidebar_left():
#     return render_template('sidebar-left.html')
#
#
# @app.route('/sidebar-right.html')
# def sidebar_right():
#     return render_template('sidebar-right.html')
#
#
# @app.route('/single.html')
# def single():
#     return render_template('single.html')

if __name__ == '__main__':
    # flask重啟時會有兩條執行續，不能讓他們都跑，不然會有兩張圖
    # app.run(debug=True, use_reloader=False)
    # app.run(debug=False, port=os.getenv("PORT", default=5000))
    app.run(debug=True, port=os.getenv("PORT", default=5000))
