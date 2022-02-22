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

from datetime import datetime
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
                    x = events[0]['source']['userId']
                    daka(x)
                    payload["messages"] = [getPlayStickerMessage()]

                elif text == "打卡查詢":
                    payload["messages"] = [dakaSearch()]

                elif text == "cfi-102":
                    x = 'cfi-102'
                    a = data(x)[0]
                    b = data(x)[1]
                    c = data(x)[2]
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"您好:{a} "
                                    f"在{c} "
                                    f"人流量為{b}"
                        }
                    ]
                elif text == "cfi-103":
                    x = 'cfi-103'
                    a = data(x)[0]
                    b = data(x)[1]
                    c = data(x)[2]
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"您好:{a} "
                                    f"在{c} "
                                    f"人流量為{b}"
                        }
                    ]
                elif text == "cfi-888":
                    x = 'cfi-888'
                    a = data(x)[0]
                    b = data(x)[1]
                    c = data(x)[2]
                    payload["messages"] = [
                        {
                            "type": "text",
                            "text": f"您好:{a} "
                                    f"在{c} "
                                    f"人流量為{b}"
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

        elif events[0]["type"] == "postback":
            if "params" in events[0]["postback"]:
                x = events[0]["postback"]["params"]["date"]
                y = events[0]['source']['userId']
                a = showDakaSearchFirst(x, y)[0][0]
                b = showDakaSearchFirst(x, y)[0][1]
                c = showDakaSearchlast(x, y)[0][0]
                d = showDakaSearchlast(x, y)[0][1]
                payload["messages"] = [
                    {
                        "type": "text",
                        "text": f"{a} {b}\n{c} {d}"
                    }]

                replyMessage(payload)
            
    return 'OK'

def getPlayStickerMessage(): #標示打卡成功用的
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


def daka(x):  # 打卡功能
    connection = pymysql.connect(host="us-cdbr-east-05.cleardb.net",
                                 user="b809ff374c792c",
                                 password="bbc8de98",
                                 database="heroku_9a97caadd884ab8")


    cursor = connection.cursor()
    create_date = datetime.today().strftime('%Y-%m-%d')  # 得到當前日期
    create_time = datetime.today().strftime('%H:%M:%S')  # 得到當前時間
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號
    sql = f"insert into wlog (EMPNO , CREATE_DATE, CREATE_TIME) values ('{x}', '{create_date}', '{create_time}')"
    cursor.execute(sql)

    connection.commit()
    cursor.close()
    connection.close()

def data(x):  # 人流查詢功能
    connection = pymysql.connect(host="us-cdbr-east-05.cleardb.net",
                                 user="b809ff374c792c",
                                 password="bbc8de98",
                                 database="heroku_9a97caadd884ab8")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號
    a = 'cfi-102'
    b = 'cfi-103'
    c = 'cfi-888'
    if x == a:
        sql = f"""select RDATE, NOWIN, LOCATION
                    from slog s  join aiot a on s.AIOTNO = a.AIOTNO
                    where s.AIOTNO = 'cfi-102'
                    order by RDATE desc
                    limit 1"""
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    elif x == b:
        sql = f"""select RDATE, NOWIN, LOCATION
                    from slog s  join aiot a on s.AIOTNO = a.AIOTNO
                    where s.AIOTNO = 'cfi-103'
                    order by RDATE desc
                    limit 1"""
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    elif x == c:
        sql = f"""select RDATE, NOWIN, LOCATION
                    from slog s  join aiot a on s.AIOTNO = a.AIOTNO
                    where s.AIOTNO = 'cfi-888'
                    order by RDATE desc
                    limit 1"""
        cursor.execute(sql)
        result = cursor.fetchone()
        return result
    # result["RDATE"] = str(result["RDATE"])

    connection.commit()
    cursor.close()
    connection.close()


def dakaSearch(): #打卡時間選擇
    message = {
                "type": "template",
                "altText": "this is a template",
                "template": {
                    "type": "buttons",
                    "text": "請選擇查詢時間",
                    "actions": [
                        {
                            "type": "datetimepicker",
                            "label": "Select date",
                            "data": "storeId=12345",
                            "mode": "date"
                        }
                    ]
                }
            }
    return message


def showDakaSearchFirst(x, y):  # 打卡查詢功能
    connection = pymysql.connect(host="us-cdbr-east-05.cleardb.net",
                                 user="b809ff374c792c",
                                 password="bbc8de98",
                                 database="heroku_9a97caadd884ab8")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號

    sql = f"""select CREATE_DATE, CREATE_TIME 
                from wlog
                where CREATE_DATE ='{x}' and EMPNO = '{y}'
                order by CREATE_TIME 
                limit 1;
                """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return result


def showDakaSearchlast(x, y):  # 打卡查詢功能
    connection = pymysql.connect(host="us-cdbr-east-05.cleardb.net",
                                 user="b809ff374c792c",
                                 password="bbc8de98",
                                 database="heroku_9a97caadd884ab8")

    cursor = connection.cursor()
    # 在mysql中，時間資料也是字串，故create_date和create_time還要有一組雙引號

    sql = f"""select CREATE_DATE, CREATE_TIME 
                from wlog
                where CREATE_DATE ='{x}' and EMPNO = '{y}'
                order by CREATE_TIME desc 
                limit 1;
                """
    cursor.execute(sql)
    result = cursor.fetchall()
    connection.commit()
    cursor.close()
    connection.close()
    return result


if __name__ == "__main__":
    app.debug = True
    app.run()
