## 이성준, 박재동 ##
## 2019 - 07 - 10 ##
#   웹 테이터 크롤링 & 파싱
#   ngrok 서버 연결
#   Flask 프레임워크
#   슬렉 클라이언트 제어
#----------------------------#
#                            #
#    슬렉 챗봇 프로젝트      #
#                            #
#----------------------------#

# -*- coding: utf-8 -*-
import re

import urllib.request
import bs4

from flask import Flask
from slack import WebClient
from slackeventsapi import SlackEventAdapter
from slack.web.classes import extract_json
from slack.web.classes.blocks import *
from datetime import datetime
import json
import re
import requests
import urllib.request
import urllib.parse

from bs4 import BeautifulSoup
from flask import Flask, request
from slack import WebClient
from slack.web.classes import extract_json
from slack.web.classes.blocks import *
from slack.web.classes.elements import *
from slack.web.classes.interactions import MessageInteractiveEvent
from slackeventsapi import SlackEventAdapter

## 토큰 ##
SLACK_TOKEN = "xoxb-689656827440-683311242321-rB50u6qbT7ZW3Bi9NI1NvsUx"
SLACK_SIGNING_SECRET = "0a83257813fb5e283d52bdfa5a8f7a85"


## listening 반응 ##
app = Flask(__name__)
# /listening 으로 슬랙 이벤트를 받습니다.
slack_events_adaptor = SlackEventAdapter(SLACK_SIGNING_SECRET, "/listening", app)
slack_web_client = WebClient(token=SLACK_TOKEN)



## 테스팅 프린터 ##
def printing():
    print("###############################################################################################")
    print("################################                                ###############################")
    print("################################                                ###############################")
    print("################################        테스팅 프리터           ###############################")
    print("################################                                ###############################")
    print("################################                                ###############################")
    print("###############################################################################################")


    ########################################################################
    ##########################                       #######################
    ############          LUNCH TITLE,ITEM,IMG CRAWLING           ##########
    ##########################                       #######################
    ########################################################################

## 크롤링 함수 구현하기 ##
def crawlig(urlAddText):
    url = "http://welfoodstory.azurewebsites.net/?category=2%EC%BA%A0%ED%8D%BC%EC%8A%A4-3&date=2019-07-" + urlAddText
    html = urllib.request.urlopen(url)
    soup = bs4.BeautifulSoup(html, "html.parser")

    count = 27      # 삼성 식당 # 점심 인덱스 ( 2~3 )
    lunchObjs = []  # ( 2~3 ) 점심 인스턴스 리스트


    printing()

    ## 파싱 ##
    divTitles = soup.findAll("div", {"class": "menu-item-title"})
    divContents = soup.findAll("div", {"class": "menu-item-contents"})

    for i in range(count, count + 3):
        print("TEST Title name : ", divTitles[i].getText())
        if "셰프" in divTitles[i].getText() :
            divSplitContents = divContents[i].getText().split("\r\n")
            imgContent = divContents[i].find("img")["src"]
            divTitle = divTitles[i].getText()
            lunchObj = Menu(divTitle, divSplitContents, imgContent)
            lunchObjs.append(lunchObj)

    for tmpObj in lunchObjs:
        tmpObj.info()

    return lunchObjs



# 메뉴 클래스
class Menu:
    title = ""  #   메뉴 타이틀
    foods = []  #   식단 리스트
    img = ""    #   대표 메뉴 이미지
    def __init__(self):
        self.title = ""
        self.foods = []
        self.img = ""
    def __init__(self , _title , _foods , _img):
        self.title = _title
        self.foods = _foods
        self.img = _img
    def __del__(self):
        print("소멸!!")

    ## 프린팅 테스트 입니다.. ##
    def info(self):
        print("<><><><><><><><><><><><><><><><><><>")
        print("오늘은 메뉴", self.title ,"입니다.")
        print("<><><><><><><><><><><><><><><><><><>")
        print("img : ",self.img)
        count = 1
        for food in self.foods:
            print(count,". ",food)
            count += 1
        print("<><><><><><><><><><><><><><><><><><>")

## 챗봇에게 메시지 던짐 ##
def slackWebClient_toChatbotPostMsg(channel , my_blocks):
    slack_web_client.chat_postMessage(
        channel=channel,
        # text="반응해라",
        blocks=my_blocks
    )


## 챗봇이 멘션을 받았을 경우 ##
@slack_events_adaptor.on("app_mention")
def app_mentioned(event_data):
    channel = event_data["event"]["channel"]
    text = event_data["event"]["text"]
    # timeEvent = event_data["event_time"]      #   타임이벤트 발생 조건을 변경해 listening 반응을 제어


    ## 챗봇이 받은 메시지 파싱 ##
    split = []
    split = text.split(">")
    splitText = split[1]


    ## 초기 블록 생성 ##
    my_blocks = []
    contentBlockTmp = SectionBlock(
                text = "`****d*원하시는 날짜의 메뉴를 골라줭~!~!엉*****` "
    )
    button_actions = ActionsBlock(
        elements=[
            ButtonElement(
                text="어제",
                action_id="yesterday", value="0"
            ),
            ButtonElement(
                text="오늘", style="danger",
                action_id="today", value="1"
            ),
            ButtonElement(
                text="내일",
                action_id="tomorrow", value="2"
            ),
            ButtonElement(
                text="모레", style="primary",
                action_id="theDayAfterTomorrow", value="3"
            ),
        ]
    )
    my_blocks.append(contentBlockTmp)
    my_blocks.append(button_actions)



    ## Post message to Chatbot ##
    slackWebClient_toChatbotPostMsg(channel,extract_json(my_blocks))




# / 로 접속하면 서버가 준비되었다고 알려줍니다.
@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


# 사용자가 버튼을 클릭한 결과는 /click 으로 받습니다
# 이 기능을 사용하려면 앱 설정 페이지의 "Interactive Components"에서
# /click 이 포함된 링크를 입력해야 합니다.
@app.route("/click", methods=["GET","POST"])
def on_button_click():
    # 버튼 클릭은 SlackEventsApi에서 처리해주지 않으므로 직접 처리합니다
    payload = request.values["payload"]
    click_event = MessageInteractiveEvent(json.loads(payload))

    keyword = click_event.block_id
    dDay = int(click_event.value)

    yesterday = datetime.today().day -1
    yttt = []
    for i in range(4):
        tmpYttt = yesterday + i
        if int(tmpYttt) < 10:
            yttt.append("0" + str(tmpYttt))
        else :
            yttt.append(str(tmpYttt))

    dateData = ""
    if dDay == 0:
        dateData = yttt[0]
    elif dDay == 1:
        dateData = yttt[1]
    if dDay == 2:
        dateData = yttt[2]
    elif dDay == 3:
        dateData = yttt[3]

    objectList = []
    objectList = crawlig(dateData)

    # 블록 처리 ##
    my_blocks = []
    for i in range(len(objectList)):
        m = objectList[i]
        titleBlockTmp = SectionBlock(
            text="*`\\\\\\\\\\\\\\\\\\\\\\\\\t\t" + "Day " + dateData + ". "+ m.title +"\t\t///////////`*"
        )
        imgBlockTmp = ImageBlock(
            image_url = m.img,
            alt_text="이미지가 안보이면 어쩔수 없지...",
        )
        contentBlockTmp = SectionBlock(
            fields=m.foods
        )

        my_blocks.append(titleBlockTmp)
        my_blocks.append(imgBlockTmp)
        my_blocks.append(contentBlockTmp)

    ## Post message to Chatbot ##
    slackWebClient_toChatbotPostMsg(click_event.channel.id, extract_json(my_blocks))


    # Slack에게 클릭 이벤트를 확인했다고 알려줍니다
    return "OK", 200


if __name__ == '__main__':
    app.run('localhost', port=5000)
