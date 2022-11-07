# Etoro X Telebot 
## Auto-Login-and-Buy (run locally)
###### Etoro frequently changes their UI/UX, so it might not work now
### Features：
1. auto login your Etoro account
2. switch to virtual portfolio
3. open positions
#### Demo Locally
    https://drive.google.com/file/d/1a5LGwJYYAsmHQJFpWiJyKPtz2ni_J-fg/view?usp=sharing
## What-Can-Trade-Today (run in [Heroku app](https://etorotelebot.herokuapp.com/) and backup with [Railway app](https://etorotelebot-production.up.railway.app/))
### Features：
1. use BB strategy to check tickers
2. BB strategy demo clip is on Google Drive now :
#### Demo Locally
    https://drive.google.com/file/d/1WIVBSOXXoSdfN-0M6hUhFN8FWXoG8EcR/view?usp=sharing
#### Demo in Heroku app with telegram bot
    https://drive.google.com/file/d/1ZQqjkHx6O02Nn7fkRiaDMwwxnQw-4pbd/view?usp=sharing
#### Demo screenshot on mobile device
<img src="https://github.com/winterdrive/EtoroTelebot/blob/master/screenshot1.jpg" width="480" alt="screenshot1">
<img src="https://github.com/winterdrive/EtoroTelebot/blob/master/screenshot2.jpg" width="480" alt="screenshot2">

## Possible Features (if I'm not busy in the future)
1. create a main page
2. open position with a click 
3. close position with a click 
4. check positions with a click



## 效能提升
2022/11/06 in localhost
- V1 
  - 4845個ticker, ticker number in each batch=10, thread number=1, bb std=2, 
  - 結果：~=90分鐘(600張圖)
  - 改善方向： 
    - [x] std=2條件過於寬鬆，執行交易也不一定會賺，可以考慮設更嚴格一點
    - [x] thread number=1，可以考慮多執行續處理
- V2 
  - 4845個ticker, ticker number in each batch=10, thread number=3, bb std=2,
  - 結果：~=47分鐘(600張圖)，圖片異常，resp:429
  - 改善方向：
    - [ ] matplotlib非線程安全，所以會有Race Condition，圖片才會異常，須逐個製圖(by queue)
      - https://matplotlib.org/3.1.0/faq/howto_faq.html?fbclid=IwAR3RjWyVS2fjFR9iLRiZvpfVcuQhPewDX3JK8ndRFDG7RwKqqoZ0FYzdVZM#working-with-threads
    - [ ] telegram 會擋過於頻繁的request，須穩定依次發圖
- V3
  - 4845個ticker, ticker number in batch=100, thread number=5, bb std=3,
  - 結果： ~=15分鐘(50張圖)
  - 改善方向：
    - [x] 429及製圖缺失已無再現，因為每批次執行數量提升，且bb std拉高，需製作及傳送的圖已大量減少，但仍需使用queue使系統更robust
    - [ ] 尚須考慮多主機執行時redis的上鎖問題
      - https://developer.aliyun.com/article/677797
      - https://blog.csdn.net/weixin_41754309/article/details/121419465
      - https://cloud.tencent.com/developer/article/1574207
      - https://zhuanlan.zhihu.com/p/112016634
      - https://zhuanlan.zhihu.com/p/258890196
    - [ ] 多主機任務分派(免費版只執行選定ticker，自己的主機再執行所有ticker)
      - railway測試，單次花費

2022/11/07 in localhost connect remote redis
- V4 
  - 4845個ticker, ticker number in batch=100, thread number=5, bb std=3,
  - 結果：時間拉長，因為Redis連線次數增加
  - 改善方向： 
    - [ ] Lua腳本處理狀態值改變(111->999)，減少連線次數，並保證atomic，避免多執行續Race Condition產生的髒資料
