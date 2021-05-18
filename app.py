from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from datetime import date
import configparser

import random

app = Flask(__name__)


config = configparser.ConfigParser()
config.read('config.ini')

line_bot_api = LineBotApi(config.get('line-bot', 'channel_access_token'))
handler = WebhookHandler(config.get('line-bot', 'channel_secret'))




# 接收 LINE 的資訊
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    try:
        print(body, signature)
        handler.handle(body, signature)
        
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 各群組的資訊互相獨立
    try:
        groupID = event.source.group_id
    except: # 此機器人設計給群組回報，單兵不可直接一對一回報給機器人
        message = TextSendMessage(text='我只接收群組內訊息，請先把我邀請到群組!')
        line_bot_api.reply_message(event.reply_token, message)
    else:
        if not reportData.get(groupID): # 如果此群組為新加入，會創立一個新的儲存區
            reportData[groupID]={}
        LineMessage = ''
        receivedmsg = event.message.text

        if receivedmsg[:5]=='/add ':
            content = receivedmsg[5:].split(' ')
            number = content[0]
            name = content[1]
            # phone = content[2]
            LineMessage = (
                number + ' ' + name + event.message.id

            )
        if receivedmsg[:5]=='1100\n' and len(receivedmsg)>7:
            stu_id = receivedmsg[5:8]
            title = '{} 11:00 安全回報'.format(today)
            reportData[groupID][title] = title
            reportData[groupID][stu_id] = receivedmsg
            LineMessage = stu_id+'，回報成功。'

        if receivedmsg[:5]=='1400\n' and len(receivedmsg)>7:
            stu_id = receivedmsg[5:8]
            reportData[groupID][title] = '{} 14:00 安全回報'.format(today)
            reportData[groupID][stu_id] = receivedmsg
            LineMessage = stu_id+'，回報成功。'

        if receivedmsg[:5]=='1900\n' and len(receivedmsg)>7:
            stu_id = receivedmsg[5:8]
            title = '{} 19:00 安全回報'.format(today)
            reportData[groupID][title] = title
            reportData[groupID][stu_id] = receivedmsg
            LineMessage = stu_id+'，回報成功。'

        elif ('-?' in receivedmsg or '-？' in receivedmsg) and len(receivedmsg)==2:
            try:
                LineMessage = (
                    '完成回報:\n'
                    +str([number for number in sorted(reportData[groupID].keys())]).strip('[]')
                )
            except BaseException as err:
                LineMessage = '錯誤原因: '+str(err)
        elif '回報' in receivedmsg and len(receivedmsg)==2:
            try:
                LineMessage = ''
                for data in [reportData[groupID][number] for number in sorted(reportData[groupID].keys())]:
                    LineMessage = reportData[groupID][title] + '\n' +data +'\n'
            except BaseException as err:
                LineMessage = '錯誤原因: '+str(err)
            else:
                reportData[groupID].clear()

        elif '格式' in receivedmsg and len(receivedmsg)==2:
            LineMessage = '學號 姓名：\n聯絡電話：\n緊急聯絡人：（）\n無返國人員接觸'

            # '''
            # 學號 姓名：
            # 聯絡電話：
            # 緊急聯絡人：（）
            # 無與返國人員接觸
            # '''
            #        
        elif '清除回報' in receivedmsg and len(receivedmsg)==4:
            reportData[groupID].clear()
            LineMessage = '已清除'
        
        if LineMessage :
            message = TextSendMessage(text=LineMessage)
            line_bot_api.reply_message(event.reply_token, message)


if __name__ == "__main__":
    global reportData
    reportData = {}
    today = date.today().strftime("%m/%d/%y")[:5]
    app.run()