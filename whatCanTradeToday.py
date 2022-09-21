import matplotlib
import requests as req
import pandas as pd
import numpy as np
# import urllib.request as req
# https://blog.csdn.net/weixin_42213622/article/details/105852794
import os
import json
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

path, filename = os.path.split(os.path.abspath(__file__))  # 當前路徑及py檔名
save_file_dir = path + "\\"


# 這是為了整理etoro格式寫的，for OneDay，for 50筆
def get_price_etoro(i, candle):
    url = "https://candle.etoro.com/candles/desc.json/OneDay/" + str(candle) + "/%s" % i
    r_data = req.get(url)
    print(url + " get")
    print("------------------------------------------------------")
    # print(r.headers["content-type"])發現這也是json
    r_edit = r_data.text
    front_key = "Candles"
    back_key = "RangeOpen"
    r_spliced = r_edit[(59 + len(i)):((r_edit.find(back_key)) - 2)]
    with open(save_file_dir + 'etoro_price\\' + "_spliced.txt", mode="w") as file:
        file.write(r_spliced)


# 這是為了用json看etoro檔案寫的
def etoro_to_json(i):
    input = open(save_file_dir + 'etoro_price\\' + "_spliced.txt", mode="r")
    output = open(save_file_dir + 'etoro_price\\' + "_spliced_dict.txt", mode="w")
    for line in input:
        output.write(line.replace("},{", "},\n{"))
    input.close()
    output.close()


# 這是為了把json變成matrix
def etoro_to_matrix(i):
    x = open(save_file_dir + 'etoro_price\\' + "_spliced_dict.txt", mode="r")
    # output1=open(Save_file_dir+'etoro_price\\'+"_matrix.txt"%i,mode="w")
    xr = json.loads(x.read())
    Date = []
    Open = []
    High = []
    Low = []
    Close = []
    for i in range(len(xr)):  # len(x)可以知道list有幾個i
        Date.append(xr[-i - 1]['FromDate'][0:10])
        # 指第i個list裡的FromDate元素，因為不需要分秒資訊所以只切0~10出來
        Open.append(xr[-i - 1]['Open'])
        # -i-1是因為etoro的資料是最新排到最舊，畫圖的時候要最舊排到最新
        High.append(xr[-i - 1]['High'])
        Low.append(xr[-i - 1]['Low'])
        Close.append(xr[-i - 1]['Close'])
    date_x = pd.DataFrame(Date).rename(columns={0: 'Date'})
    open_x = pd.DataFrame(Open).rename(columns={0: 'Open'})
    high_x = pd.DataFrame(High).rename(columns={0: 'High'})
    low_x = pd.DataFrame(Low).rename(columns={0: 'Low'})
    close_x = pd.DataFrame(Close).rename(columns={0: 'Close'})
    frames = [date_x, open_x, high_x, low_x, close_x]
    fin = pd.concat(frames, axis=1, join='inner')
    # print(fin)
    return fin


# 這是為了畫sma
def sma(data, window):
    sma = data.rolling(window=window).mean()
    # sma = data.rolling(window).mean()這樣寫似乎也可
    return sma


# 這是為了畫bb(20日)
def bb(data, sma, window):
    std = data.rolling(window=window).std()
    upper_bb = sma + std * 2
    lower_bb = sma - std * 2
    return upper_bb, lower_bb


# 這是為了回測
def implement_bb_strategy(data, lower_bb, upper_bb):
    buy_price = []
    sell_price = []
    bb_signal = []
    signal = 0
    for i in range(len(data)):
        if data[i - 1] > lower_bb[i - 1] and data[i] < lower_bb[i]:
            if signal != 1:
                buy_price.append(data[i])
                sell_price.append(np.nan)
                signal = 1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        elif data[i - 1] < upper_bb[i - 1] and data[i] > upper_bb[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(data[i])
                signal = -1
                bb_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                bb_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            bb_signal.append(0)
    return buy_price, sell_price, bb_signal


def main():
    try:
        os.mkdir(save_file_dir + 'etoro_price')
    except FileExistsError:
        pass
    try:
        os.mkdir(save_file_dir + 'etoro_price/' + 'png')
    except FileExistsError:
        pass

    candle = 50

    ticker = ['27', '28', '29', '1002', '1003', '18', '3025', '3246', '3163', '3306',
              '4465', '4459', '3008', '1467', '45', '63', '1111', '3006', '1951',
              '5968', '1588', '93', '6357', '3024', '3019', '4269', '3004', '1118',
              '2316', '4463', '4251', '100000']
    nameList = ['spx500', 'nsdq100', 'dj30', 'goog', 'fb', 'gold', 'gld', 'uvxy', 'vix',
                'qqq', 'tqqq', 'sqqq', 'xle', 'gs', 'usd_cnh', 'usd_mxn', 'tsla', 'ma',
                'swn', 'tdoc', 'x', 'cotton', 'smh', 'xly', 'xli', 'iwd', 'xlf', 'brk_b',
                '2318_hk', 'soxx', 'isrg', 'btc']
    failList = []
    watchListToday = []

    print('------------開始運行------------')
    for i, j in zip(ticker, range(0, len(ticker))):
        try:
            # 資料前處理
            name = 'temp'
            get_price_etoro(i, candle)
            etoro_to_json(i)
            ticker_matrix = etoro_to_matrix(i)
            duration = ticker_matrix.set_index('Date')
            # duration = duration[duration.index >= '2019-01-01']#時間區段可改
            duration.to_csv(save_file_dir + 'etoro_price\\' + str(name) + ".csv")
            ticker_fine_matrix = pd.read_csv(save_file_dir + 'etoro_price\\' + '%s' % name + ".csv").set_index('Date')
            ticker_fine_matrix["SMA"] = sma(ticker_fine_matrix["Close"], 20)
            ticker_fine_matrix['upper_bb'], ticker_fine_matrix['lower_bb'] = bb(ticker_fine_matrix['Close'],
                                                                                ticker_fine_matrix['SMA'], 20)
            buy_price, sell_price, bb_signal = implement_bb_strategy(ticker_fine_matrix['Close'],
                                                                     ticker_fine_matrix['lower_bb'],
                                                                     ticker_fine_matrix['upper_bb'])
            ticker_fine_matrix.to_csv(save_file_dir + 'etoro_price\\' + str(name) + "_fine.csv")

            # 落到布林外的，請考慮交易
            if (ticker_fine_matrix['upper_bb'][-1] < ticker_fine_matrix['Close'][-1]) or (
                    ticker_fine_matrix['lower_bb'][-1] > ticker_fine_matrix['Close'][-1]):
                watchListToday.append(nameList[j])
                # 接著畫圖
                ticker_fine_matrix['Close'].plot(label='CLOSE PRICES', alpha=0.3)
                ticker_fine_matrix['upper_bb'].plot(label='UPPER BB', linestyle='--', linewidth=1, color='black')
                ticker_fine_matrix['SMA'].plot(label='MIDDLE BB', linestyle='--', linewidth=1.2, color='grey')
                ticker_fine_matrix['lower_bb'].plot(label='LOWER BB', linestyle='--', linewidth=1, color='black')
                plt.scatter(ticker_fine_matrix.index, buy_price, marker='^', color='green', label='BUY', s=200)
                plt.scatter(ticker_fine_matrix.index, sell_price, marker='v', color='red', label='SELL', s=200)
                plt.title('%s BB STRATEGY TRADING SIGNALS' % nameList[j])
                plt.legend(loc='upper left')
                plt.savefig(save_file_dir + 'etoro_price\\' + 'png\\' + '%s_BBplot' % nameList[j])
                # print(ticker_fine_matrix)
                print("------------------------------------------------------")
                # 記得清畫板
                plt.cla()
                print("success")
            else:
                # 因為要上線，所以沒過的就不畫了
                continue
        except Exception as e:
            print(e)
            failList.append(nameList[j])
            print("failList:", failList)
            pass
    print("failList:", failList)
    if len(watchListToday) > 0:
        print("請考慮交易:", watchListToday)
    else:
        print("本日不建議交易")
    # input()
    return watchListToday


if __name__ == '__main__':
    main()
