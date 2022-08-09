import configparser
import json
import math
import random
from pprint import pprint

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

# LINE bot 的連線設定
config = configparser.ConfigParser()
config.read("config.ini")

app = Flask(__name__)
handler = WebhookHandler(config["line-bot"]["channel_secret"])
line_bot_api = LineBotApi(config["line-bot"]["channel_access_token"])

# 接收LINE的資訊
@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    # app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# 處理機器人被加入的事件
@handler.add(JoinEvent)
def handle_join(event):
    template_linebot_join = json.load(
        open("Templates/template_linebot_join.json", "r", encoding="utf-8")
    )
    line_bot_api.reply_message(
        event.reply_token, FlexSendMessage("加入群組", template_linebot_join)
    )


# 處理文字訊息的事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global is_ask_blanker, is_game_start, is_describing, is_voting, player_now_describing
    global vote_container, players

    profile = line_bot_api.get_profile(event.source.user_id)
    player_name = profile.display_name

    if (
        event.message.text == "開啟遊戲"
        and is_game_start == False
        and event.source.type == "group"
    ):
        # 初始化
        players.clear()
        template_open_game = json.load(
            open("Templates/template_open_game.json", "r", encoding="utf-8")
        )
        line_bot_api.reply_message(
            event.reply_token, FlexSendMessage("開啟遊戲", template_open_game)
        )
    elif event.message.text == "遊戲規則" and event.source.type == "group":
        template_rules = json.load(
            open("Templates/template_game_rules.json", "r", encoding="utf-8")
        )
        line_bot_api.reply_message(
            event.reply_token, FlexSendMessage("遊戲規則", template_rules)
        )
    elif (
        event.message.text == "我要參加"
        and is_game_start == False
        and event.source.type == "group"
    ):
        if len(players) >= 16:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="人數已達 16 人上限囉~")
            )
            return

        # 當玩家不存在於列表中，且是群組訊息就加入到玩家列表
        if player_name not in players:
            # 將參加人放到玩家列表中
            player_id = profile.user_id
            players[player_name] = {
                "role": "",
                "describe": False,
                "vote": False,
                "id": player_id,
            }
            # 推播新的玩家列表，會隨著參加人數增加而增加
            template_join_member = json.load(
                open("Templates/template_join_member.json", "r", encoding="utf-8")
            )
            for idx, player_name in enumerate(players):  # 將玩家動態插入到 template
                template_join_member["body"]["contents"].extend(
                    [
                        {"type": "separator", "margin": "md"},
                        {
                            "type": "text",
                            "text": str(idx + 1) + ". " + str(player_name),
                            "margin": "sm",
                        },
                    ]
                )
            line_bot_api.reply_message(
                event.reply_token, FlexSendMessage("我要參加", template_join_member)
            )
            print(player_name, "加入遊戲")
            print("現在玩家列表" + str(players))
    elif (
        event.message.text == "開始遊戲"
        and is_game_start == False
        and event.source.type == "group"
    ):
        if len(players) > 4:  # 如果參加人數大於 4 人，詢問白板是否開啟
            template_blanker_confirm = json.load(
                open("Templates/template_blanker_confirm.json", "r", encoding="utf-8")
            )
            line_bot_api.reply_message(
                event.reply_token, FlexSendMessage("白板詢問", template_blanker_confirm)
            )
            is_game_start = True
            is_ask_blanker = True
        elif len(players) == 4:  # 如果參加人數等於 4 人，直接分配角色詞並開始遊戲
            start_game(players, False, event)
        elif len(players) < 4:
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text="人數未達 4 人，無法開始遊戲唷～")
            )
            return
    elif (
        event.message.text == "是"
        and is_ask_blanker == True
        and event.source.type == "group"
    ):
        is_ask_blanker = False
        start_game(players, True, event)
    elif (
        event.message.text == "否"
        and is_ask_blanker == True
        and event.source.type == "group"
    ):
        is_ask_blanker = False
        start_game(players, False, event)
    elif (
        event.message.text == "我的角色詞"
        and event.source.type == "user"
        and is_game_start == True
    ):
        if profile.display_name in players:
            role = players[profile.display_name]["role"]
            if role == "臥底":
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text=f"你的角色詞為 {spy_word}")
                )
            elif role == "平民":
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text=f"你的角色詞為 {civilian_word}")
                )
            elif role == "白板":
                line_bot_api.reply_message(
                    event.reply_token, TextSendMessage(text="這裡什麼都沒有，請努力瞎掰於遊戲中存活唷 ⌓‿⌓")
                )
    elif (
        is_game_start
        and is_describing
        and "回答" in event.message.text[:2]
        and event.source.type == "group"
    ):
        if players[player_name]["describe"] == True:  # 確認是否描述過了
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=str(player_name) + " 已經描述過囉")
            )
            return
        
        if player_name == player_now_describing:  # 確認是否為當前指定描述者
            players[player_name]["describe"] = True  # 將他的 describe 標記為 True

            # 確認還有沒有玩家還沒描述過
            for player_name, player_info in players.items():
                if player_info["describe"] == False:
                    template_turn_describe["body"]["contents"][0]["text"] = (
                        "請玩家 " + str(player_name) + " 開始描述角色詞"
                    )
                    line_bot_api.reply_message(
                        event.reply_token,
                        FlexSendMessage("輪流描述", template_turn_describe),
                    )
                    player_now_describing = player_name  # 將這個還沒描述過的玩家設定為當前指定描述者
                    return

            # 如果離開 for 迴圈，表示所有人都描述過了，進入下一階段
            # 關閉描述流程，這是全域變數
            print("結束描述")
            is_describing = False
            init_players_info()
            
            # 開始投票流程，這是全域變數
            is_voting = True
            # 設定投票箱
            vote_container.clear()
            for player_name in players.keys():
                vote_container[player_name] = 0
            show_vote_page(event, False)
   
@handler.add(PostbackEvent)
def handle_postback(event):
    global is_voting, alive_role_last_game
    profile = line_bot_api.get_profile(event.source.user_id)
    player_name = profile.display_name

    if (is_voting 
        and "vote_to" in event.postback.data 
        and player_name in players
       ):
        if players[player_name]["vote"] == True:  # 如果點擊的人已經投過票了
            return
        voted_player = event.postback.data.split("=")[1]
        vote_container[voted_player] += 1
        players[player_name]["vote"] = True

        show_vote_page(event, False)  # 每次有人投票成功就顯示投票的狀態
        
        # 確認還有沒有玩家還沒投票過
        for player_name, player_info in players.items():
            if player_info["vote"] == False:
                return
        # 如果離開 for 迴圈，表示所有玩家都投過了

        # 找出最高票有哪些人
        vote_count_max = max(vote_container.values())
        vote_again = []
        for name, vote_count in vote_container.items():
            if vote_count == vote_count_max:
                vote_again.append(name)

        if len(vote_again) == 1:  # 最高票只有一人的話
            is_voting = False  # 關閉投票流程，這是全域變數
            max_vote_name = vote_again[0]
            max_vote_role = players[max_vote_name]["role"]
            players.pop(max_vote_name)
            print("最高票者為: " + str(max_vote_name))
            print("現存活玩家: " + str(players.keys()))
            pprint(players)
            check_end_game(event, max_vote_name, max_vote_role)
        elif len(vote_again) > 1:  # 最高票有多人的話
            # 清空投票箱，加入所有平票者
            vote_container.clear()
            for name in vote_again:
                vote_container[name] = 0
            # 將玩家的標記為未投票
            init_players_info()
            print("再投一次")
            show_vote_page(event, True)

    elif "誰沒投票" == event.postback.data and is_voting:
        unvote_list = []
        for player_name, player_info in players.items():
            if player_info["vote"] == False:
                unvote_list.append(player_name)
        if len(unvote_list) != 0:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=", ".join(unvote_list) + " 尚未投票唷。"),
            )

    elif "角色揭曉" == event.postback.data and is_game_start == False:
        role_list = {"臥底": [], "平民": [], "白板": []}
        for player_name, player_info in players_last_game.items():
            role_list[player_info["role"]].append(player_name)
        print("上一局的角色列表如下")
        pprint(role_list)
        result = ""
        for role, player_list in role_list.items():
            if len(player_list) != 0:
                result += str(role) + "： " + ", ".join(player_list) + "\n"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=result[:-1]))

    elif "角色詞揭曉" == event.postback.data and is_game_start == False:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f"平民的角色詞：{civilian_word}\n" + f"臥底的角色詞：{spy_word}"),
        )


def start_game(players, has_blanker, event):
    global civilian_word, spy_word, is_game_start, is_describing, player_now_describing
    global vote_container, is_voting, is_ask_blanker, players_last_game

    # 設定角色數量
    blanker_count = 1 if has_blanker else 0
    spy_count = math.ceil(len(players) / 4) - blanker_count
    civilian_count = len(players) - spy_count - blanker_count

    # 隨機分配角色給目前參加的玩家
    drawer = (
        ["臥底"] * spy_count + ["平民"] * civilian_count + ["白板"] * blanker_count
    )  # 建立角色池
    random.shuffle(drawer)  # 打亂角色池
    names = list(players.keys())
    for idx, role in enumerate(drawer):
        players[names[idx]]["role"] = role

    # 設定該局的臥底與平民詞，這是全域變數
    civilian_word, spy_word = word_pool[random.randint(0, len(word_pool) - 1)]

    # 推播遊戲開始訊息
    template_game_start = json.load(
        open("Templates/template_game_start.json", "r", encoding="utf-8")
    )
    template_game_start["body"]["contents"][2]["contents"][1][
        "text"
    ] = "本局有 %d 位平民，%d 位臥底，%d 位白板。" % (
        civilian_count,
        spy_count,
        blanker_count,
    )
    line_bot_api.reply_message(
        event.reply_token, FlexSendMessage("Game start", template_game_start)
    )

    # 同時私訊角色詞按鈕給所有參與的玩家
    player_push_list = list(
        set([player_info["id"] for player_info in players.values()])
    )
    print(player_push_list)
    template_get_self_role = json.load(
        open("Templates/template_get_self_role.json", "r", encoding="utf-8")
    )
    line_bot_api.multicast(
        player_push_list, FlexSendMessage("取得角色詞", template_get_self_role)
    )

    # 開始遊戲流程，這是全域變數
    is_game_start = True
    # 開始描述流程，這是全域變數
    is_describing = True
    # 關閉其他流程，這些是全域變數
    is_voting = False
    is_ask_blanker = False

    # 暫存所有參加遊戲的玩家，
    # 用來在結束遊戲時，輸出角色揭曉 (players 會在遊戲進行減少)
    players_last_game = players.copy()

    print("遊戲建立成功，本局角色資訊如下")
    pprint(players)

    set_first_player_start_describing(event)


def show_vote_page(event, vote_again=False):
    template_vote = json.load(
        open("Templates/template_vote_page.json", "r", encoding="utf-8")
    )
    if vote_again == True:  # 如果是再次投票的話，替換文字
        template_vote["body"]["contents"][1]["text"] = "尚未決定最高票者\n請再對以下玩家進行投票"
    for name, vote_count in vote_container.items():
        template_vote["body"]["contents"].append(
            {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                    {
                        "type": "text",
                        "text": f"{name}",
                        "action": {
                            "type": "postback",
                            "label": f"{name}",
                            "data": f"vote_to={name}",
                        },
                        "flex": 7,
                        "align": "center",
                    },
                    {
                        "type": "text",
                        "text": f"{vote_count}",
                        "align": "center",
                        "gravity": "center",
                        "flex": 3,
                    },
                ],
                "paddingAll": "sm",
            }
        )
    line_bot_api.push_message(
        event.source.group_id, FlexSendMessage("投票", template_vote)
    )


def check_end_game(event, vote_name, vote_role):
    global is_game_start, player_now_describing, is_describing, players
    civilian_count = sum(
        1 for player_info in players.values() if player_info["role"] == "平民"
    )
    spy_count = sum(
        1 for player_info in players.values() if player_info["role"] == "臥底"
    )
    blanker_count = sum(
        1 for player_info in players.values() if player_info["role"] == "白板"
    )
    # 進行戰況回報
    show_game_report(
        event, vote_name, vote_role, civilian_count, spy_count, blanker_count
    )

    # 臥底勝利: 臥底與平民均為一人 或 臥底人數大於平民
    if (spy_count == 1 and civilian_count == 1) or (spy_count > civilian_count):
        template_end_game = json.load(
            open("Templates/template_win_spy.json", "r", encoding="utf-8")
        )
        line_bot_api.push_message(
            event.source.group_id, FlexSendMessage("臥底勝利", template_end_game)
        )
        print("遊戲結束")
        is_game_start = False
        players.clear()
    # 平民勝利: 臥底全數出局
    elif spy_count == 0:
        template_end_game = json.load(
            open("Templates/template_win_civilian.json", "r", encoding="utf-8")
        )
        line_bot_api.push_message(
            event.source.group_id, FlexSendMessage("平民勝利", template_end_game)
        )
        print("遊戲結束")
        is_game_start = False
        players.clear()
    # 未分出勝負，繼續遊戲
    else:
        init_players_info()  # 初始化所有玩家的描述和投票狀態
        set_first_player_start_describing(event)

def show_game_report(
    event, vote_name, vote_role, civilian_count, spy_count, blanker_count
):
    template_game_report = json.load(
        open("Templates/template_vote_report.json", "r", encoding="utf-8")
    )
    template_game_report["body"]["contents"][1]["contents"][1]["contents"][0][
        "text"
    ] = vote_name
    template_game_report["body"]["contents"][1]["contents"][1]["contents"][1][
        "text"
    ] = vote_role
    template_game_report["body"]["contents"][2]["contents"][1]["contents"][1][
        "text"
    ] = str(civilian_count)
    template_game_report["body"]["contents"][2]["contents"][2]["contents"][1][
        "text"
    ] = str(spy_count)
    template_game_report["body"]["contents"][2]["contents"][3]["contents"][1][
        "text"
    ] = str(blanker_count)
    line_bot_api.push_message(
        event.source.group_id, FlexSendMessage("戰況回報", template_game_report)
    )


def init_players_info():
    for player_info in players.values():
        player_info["describe"] = False
        player_info["vote"] = False


def get_word_pool():
    word_pool = []
    with open("word_pool.txt", "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()  # to remove space char
            word_pool.append(line.split(","))
    return word_pool


def set_first_player_start_describing(event):
    global player_now_describing, is_describing
    
    # 開始描述流程
    is_describing = True
    # 請第一位玩家出來描述
    player_now_describing = list(players.keys())[0]  # 將第一位玩家設定為當前指定描述者
    template_turn_describe["body"]["contents"][0]["text"] = (
        "請玩家 " + str(player_now_describing) + " 開始描述角色詞"
    )
    line_bot_api.push_message(
        event.source.group_id, FlexSendMessage("輪流描述", template_turn_describe)
    )


def init():
    global players, players_last_game, is_ask_blanker, is_game_start, is_describing, is_voting
    global player_now_describing, vote_container, word_pool, civilian_word, spy_word
    global template_turn_describe

    # 變數
    players = {}
    players_last_game = {}
    is_ask_blanker = False
    is_game_start = False
    is_describing = False
    is_voting = False
    player_now_describing = ""
    vote_container = {}

    template_turn_describe = json.load(
        open("Templates/template_turn_describe.json", "r", encoding="utf-8")
    )
    word_pool = get_word_pool()
    civilian_word = ""
    spy_word = ""


if __name__ == "__main__":
    init()
    app.run()



