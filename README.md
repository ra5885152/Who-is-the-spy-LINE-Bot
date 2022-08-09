# Who is the spy (LINE Bot)

## Introduction

「誰是間諜」為趣味的陣營類遊戲，而 Who is the spy 則可以透過 LINE Bot 與朋友們來遊玩這款遊戲，在 LINE 打造一個類桌遊的玩樂空間。

## Game flow

<img src="https://user-images.githubusercontent.com/106053450/183679000-5c2c5ea2-8ed9-49fe-acf7-14e06f9ab570.png">

## Setting of players

<img src="https://user-images.githubusercontent.com/106053450/183679047-b9c2623f-d985-4e08-a6dd-0989b7cac7cb.png">

## Prerequisites

1. A LINE Bot on [LINE Developers Console](https://developers.line.biz/console/)
2. Modify `config.ini`

	<img src="https://user-images.githubusercontent.com/106053450/183679086-dff98a5e-d6e2-432d-9c52-96c5e81e9d5e.png">
  
3. A avaliable web hook service (such as [ngrok](https://ngrok.com/))
4. Python virtualenv 
    ```bash
    python -m venv venv
    ./venv/Scripts/activate
    pip install -r requirements.txt
    ```

## Run

```python
python main.py
```

1. 將 LINE Bot 加入群組。

	<img src="https://user-images.githubusercontent.com/106053450/183679180-512830ef-53ce-49c5-b2c6-c8a77708019e.png" width="350">

2. 點擊【開啟遊戲】後，提示可遊玩人數。

	<img src="https://user-images.githubusercontent.com/106053450/183679249-e390562b-882b-4d8a-a653-179e42782d5c.png" width="350">

3. 點擊【遊戲規則】，提供遊戲規則及勝利條件。

	<img src="https://user-images.githubusercontent.com/106053450/183679289-24ad2b6b-215d-4e76-872c-c3bd00a91c9c.png" width="350">

4. 點擊【我要參加】，即可參加遊戲。

	<img src="https://user-images.githubusercontent.com/106053450/183679313-40116bf9-34ca-478c-a19e-abd54bafd25d.png" width="350">

5. 當玩家報名結束，點擊【開始遊戲】，LINE Bot 詢問是否開啟白板。

	<img src="https://user-images.githubusercontent.com/106053450/183679529-65a17619-8d43-4862-ad3e-c4b01ebed739.png" width="350">

6. 玩家們討論是否開啟白板，並點擊【是】或【否】，LINE Bot 通知遊戲資訊。

	<img src="https://user-images.githubusercontent.com/106053450/183679553-c78ff985-cac7-4ec6-9096-a8c4d7e4a77c.png" width="350">

7. 點擊群組的【我的角色詞】，自動轉跳至與 LINE Bot 的一對一聊天室，並點擊【我的角色詞】，即獲取角色詞。

	<img src="https://user-images.githubusercontent.com/106053450/183690238-1f45ea40-0e48-4cb2-8f78-cca663c87ee8.jpg" width="350">

	<img src="https://user-images.githubusercontent.com/106053450/183689842-747ca8ff-eb16-447e-bbe1-4194ff7e0e16.jpg" height="175.84">

8. LINE Bot 會輪流請玩家描述角色詞，當玩家進行描述時，必須在描述最前面加上**回答**。

	<img src="https://user-images.githubusercontent.com/106053450/183679675-e1c58303-88b8-4a8b-82cf-196f18d13412.png" width="350">

9. 當玩家們皆已描述角色詞，LINE Bot 開啟投票板，玩家們可以點擊【玩家名稱】進行投票。

	<img src="https://user-images.githubusercontent.com/106053450/183679746-4e1e8f18-951f-466b-a619-81a65d759e3f.png" width="350">

10. 若發生平票的情況，LINE Bot 再次開啟投票版，並只對平票者再次投票，可點擊【誰沒投票】，確認尚未投票者。

	<img src="https://user-images.githubusercontent.com/106053450/183679834-210814fe-9db0-4758-a025-e195ce11af0e.png" width="350">

11. 當確定有出局玩家，LINE Bot 提供戰況回報，若本局尚未有勝負，LINE Bot 會輪流請存活玩家描述角色詞，遊戲繼續！

	<img src="https://user-images.githubusercontent.com/106053450/183679927-d1a9ecc3-24d1-4843-b8c7-fc3337d14e05.png" width="350">

12. 若遊戲分出勝負，LINE Bot 宣布遊戲結束，並可點擊【角色揭曉】、【角色詞揭曉】，及【再來一局】開啟遊戲。

	<img src="https://user-images.githubusercontent.com/106053450/183679985-fd50ad6e-dbba-4c16-8683-0d1c0506ac2c.png" width="350">

## Notice

LINE Bot 有每月免費訊息的限制，如果 LINE Bot 為免費版 (輕用量)，則每月 push message 只能推播 500 則訊息。

<img src="https://user-images.githubusercontent.com/106053450/183680062-600b34a7-f823-44c0-be29-5b4108ea5297.png">

## Reference

- [line-bot-sdk-python](https://github.com/line/line-bot-sdk-python)
- [LINE Developers](https://developers.line.biz/en/docs/messaging-api/)
- [ngrok](https://ngrok.com/)
- [Image source from spy-family](https://spy-family.net/)

## ****Contributors****

[ra5885152](https://github.com/ra5885152)

[chen810405](https://github.com/chen810405)
