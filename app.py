from __future__ import unicode_literals
from flask import Flask, request, abort, render_template
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests
import json
import configparser
import os
from urllib import parse

import time
import pymysql


app = Flask(__name__, static_url_path='/static')
UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])


config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))
my_line_id = config.get('line-bot', 'my_line_id')
end_point = config.get('line-bot', 'end_point')
line_login_id = config.get('line-bot', 'line_login_id')
line_login_secret = config.get('line-bot', 'line_login_secret')
my_phone = config.get('line-bot', 'my_phone')
HEADER = {
    'Content-type': 'application/json',
    'Authorization': F'Bearer {config.get("line-bot", "channel_access_token")}'
}


@app.route("/", methods=['POST', 'GET'])
def index():
    if request.method == 'GET':
        return 'ok'
    body = request.json
    events = body["events"]
    print(body)
    if "replyToken" in events[0]:
        payload = dict()
        replyToken = events[0]["replyToken"]
        payload["replyToken"] = replyToken
        if events[0]["type"] == "message":
            if events[0]["message"]["type"] == "text":
                text = events[0]["message"]["text"]

                if text == "一般使用者":
                    payload["messages"] = [
                                            {
                                            "type":"text",
                                            "text":"Hello, user"
                                            },
                                            {
                                                "type": "template",
                                                "altText": "This is a buttons template",
                                                "template": {
                                                    "type": "buttons",
                                                    "title": "Menu",
                                                    "text": "Please select",
                                                    "actions": [
                                                        {
                                                            "type": "message",
                                                            "label": "cfi-102",
                                                            "text": "cfi-102"
                                                        },
                                                        {
                                                            "type": "message",
                                                            "label": "cfi-103",
                                                            "text": "cfi-103"
                                                        },
                                                        {
                                                            "type": "message",
                                                            "label": "cfi-888",
                                                            "text": "cfi-888"
                                                        }
                                                    ]
                                                }
                                            }
                                          ]
                elif text == "打卡":
                    daka()

                    payload["messages"] = [getPlayStickerMessage()]
                elif text == "cfi-102":
                    a = data()[0]
                    b = data()[1]
                    c = data()[2]
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"您好:{a} "
                                    f"在{b} "
                                    f"人流量為{c}"
                        }
                    ]

                else:
                    payload["messages"] = [
                            {
                                "type": "text",
                                "text": text
                            }
                        ]
                replyMessage(payload)

    return 'OK'


def getNameEmojiMessage():
    lookUpStr = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    productId = "5ac21a8c040ab15980c9b43f"
    name = "Jason"
    message = dict()
    message["type"] = "text"
    message["text"] = "".join("$" for r in range(len(name)))
    emojis_list = list()
    for i, nChar in enumerate(name):
        emojis_list.append(
            {
                "index": i,
                "productId": productId,
                "emojiId": f"{lookUpStr.index(nChar) + 1 :03}"
            }
        )
    message["emojis"] = emojis_list
    return message


def getPlayStickerMessage():
    message = dict()
    message["type"] = "sticker"
    message["packageId"] = "6325"
    message["stickerId"] = "10979904"
    return message


def replyMessage(payload):
    response = requests.post("https://api.line.me/v2/bot/message/reply",headers=HEADER,data=json.dumps(payload))
    return 'OK'


def pushMessage(payload):
    response = requests.post("https://api.line.me/v2/bot/message/push",headers=HEADER,data=json.dumps(payload))
    return 'OK'


def getTotalSentMessageCount():
    response = requests.get("https://api.line.me/v2/bot/message/quota/consumption",headers=HEADER)
    return response.json()["totalUsage"]

def daka():
    connection = pymysql.connect(host="us-cdbr-east-05.cleardb.net",
                                 user="b809ff374c792c",
                                 password="bbc8de98",
                                 database="heroku_9a97caadd884ab8")

    cursor = connection.cursor()
    create_date = time.strftime('%Y-%m-%d')  # 得到當前日期
    create_time = time.strftime('%H:%M:%S')  # 得到當前時間
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號
    sql = f"insert into wlog (EMPNO , CREATE_DATE, CREATE_TIME) values ('{216}', '{create_date}', '{create_time}')"
    cursor.execute(sql)

    connection.commit()
    cursor.close()
    connection.close()

def data():
    connection = pymysql.connect(host="us-cdbr-east-05.cleardb.net",
                                 user="b809ff374c792c",
                                 password="bbc8de98",
                                 database="heroku_9a97caadd884ab8")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號
    sql = f"""select RDATE, NOWIN, LOCATION
            from slog  join aiot on slog.AIOTNO = aiot.AIOTNO
            where AIOTNO = cfi-102
            order by RDATE desc
            limit 1;"""
    cursor.execute(sql)
    result = cursor.fetchone()
    # result["RDATE"] = str(result["RDATE"])

    connection.commit()
    cursor.close()
    connection.close()
    return result


if __name__ == "__main__":
    app.debug = True
    app.run()
