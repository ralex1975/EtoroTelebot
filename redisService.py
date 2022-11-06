# https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments
import requests as req
import json
import redis

# 簡易結構(詳細結構參考"20221105etoroTickers.txt")
# myJson={"InstrumentDisplayDatas": [
#   {
#     "InstrumentID": 100342,
#     "InstrumentDisplayName": "CryptoOps55",
#     "InstrumentTypeID": 10,
#     "ExchangeID": 8,
#     "Images": [
#       {
#         "InstrumentID": 100342,
#         "Width": 35,
#         "Height": 35,
#         "Uri": "https://etoro-cdn.etorostatic.com/market-avatars/100342/35x35.png"
#       },
#       {
#         "InstrumentID": 100342,
#         "Width": 50,
#         "Height": 50,
#         "Uri": "https://etoro-cdn.etorostatic.com/market-avatars/100342/50x50.png"
#       },
#       {
#         "InstrumentID": 100342,
#         "Width": 150,
#         "Height": 150,
#         "Uri": "https://etoro-cdn.etorostatic.com/market-avatars/100342/150x150.png"
#       }
#     ],
#     "SymbolFull": "CryptoOps55",
#     "InstrumentTypeSubCategoryID": 1001,
#     "PriceSource": "eToro",
#     "HasExpirationDate": false,
#     "IsInternalInstrument": true
#   },
#   {
#     "InstrumentID": 100342,
#     "InstrumentDisplayName": "CryptoOps55",
#     "InstrumentTypeID": 10,
#     "ExchangeID": 8,
#     "Images": [
#       {
#         "InstrumentID": 100342,
#         "Width": 35,
#         "Height": 35,
#         "Uri": "https://etoro-cdn.etorostatic.com/market-avatars/100342/35x35.png"
#       },
#       {
#         "InstrumentID": 100342,
#         "Width": 50,
#         "Height": 50,
#         "Uri": "https://etoro-cdn.etorostatic.com/market-avatars/100342/50x50.png"
#       },
#       {
#         "InstrumentID": 100342,
#         "Width": 150,
#         "Height": 150,
#         "Uri": "https://etoro-cdn.etorostatic.com/market-avatars/100342/150x150.png"
#       }
#     ],
#     "SymbolFull": "CryptoOps55",
#     "InstrumentTypeSubCategoryID": 1001,
#     "PriceSource": "eToro",
#     "HasExpirationDate": false,
#     "IsInternalInstrument": true
#   }
# ]
# }

ETORO_DICT_KEY_NAME = "etoroDict"


def get_redis_connection(hostnameStr, portNumber, passwordStr=""):
    return redis.Redis(host=hostnameStr, port=portNumber, password=passwordStr,charset="utf-8", decode_responses=True)


def initialize_state_of_num_and_ticker_pairs_in_redis(conn):
    resp = req.get("https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments")
    data = resp.text
    myJsonList = json.loads(data)["InstrumentDisplayDatas"]
    myEtoroList = list()
    for i in myJsonList:
        # print(i["InstrumentID"])
        # print(i["SymbolFull"])
        myEtoroList.append(",".join([str(i["InstrumentID"]), str(i["SymbolFull"]).replace('.', '_')]))
    # print(len(myEtoroList))
    # print(myEtoroList[0])
    myRedisScoreDict = dict()
    for i in myEtoroList:
        myRedisScoreDict[i] = 111
    conn.zadd(ETORO_DICT_KEY_NAME, myRedisScoreDict)
    # 最終結構是etoroDict(zset)內有4845條類似111:1,EURUSD的結構
    return


def change_state_of_num_and_ticker_pairs_in_redis_when_finish(conn, member: str):
    conn.zadd(ETORO_DICT_KEY_NAME, {member: 999})
    return


def get_member_in_initial_state(conn, keyName: str):
    myList = conn.zrangebyscore(keyName, '100', '120', start=0, num=100)
    return myList


def get_member_in_finish_state(conn, keyName: str):
    myList = conn.zrangebyscore(keyName, '888', '1000', start=0, num=100)
    return myList


# conn = get_redis_connection("localhost", 6379, "")
# initialize_state_of_num_and_ticker_pairs_in_redis(conn)
# change_state_of_num_and_ticker_pairs_in_redis_when_finish(conn, "1,EURUSD")
# get_member_in_initial_state(conn, ETORO_DICT_KEY_NAME)
# get_member_in_finish_state(conn, ETORO_DICT_KEY_NAME)
