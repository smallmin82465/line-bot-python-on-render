from flask import Flask
app = Flask(__name__)

from flask import request, abort, render_template
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, BubbleContainer, ImageComponent, BoxComponent, TextComponent, IconComponent, ButtonComponent, SeparatorComponent, FlexSendMessage, URIAction
from typing import List
from linebot.models import (
    MessageEvent, TextMessage, StickerMessage, StickerSendMessage, ConfirmTemplate, TemplateSendMessage, MessageAction, URIAction, LocationMessage
 )
from linebot.models import *
import  json, ssl, urllib.request
import requests
import math

app = Flask(__name__)
line_bot_api = LineBotApi('jV4Wkcvst8hZ5a43IwzhffCtgcHbQlKqt7zkgb8enS+74HkXUZNJBd8L1x1ATdfVOXEAXxwjFQk5P1Vd+spjQXuy7wbJvF9iiRnerABpHBK+kCBqWopcWVKMZZcfBShC8NQipg0fDeRlJdsOwiDafgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7912d56d1a4ad693713b1e6f1b3d48f9')
###handler = WebhookHandler('81d02ef0bf37d4b7c516d81f76d8b5d8')
arlist = []
snalist = []
latlist = []
lnglist = []
bemplist = []
sbilist = []
tmplist = []
context = ssl._create_unverified_context()
url1 = 'https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json'  
url2 = 'https://data.tycg.gov.tw/opendata/datalist/datasetMeta/download?id=5ca2bfc7-9ace-4719-88ae-4034b9a5a55c&rid=a1b4714b-3b75-4ff8-a8f2-cc377e4eaa0f'  
cities = ['宜蘭縣', '花蓮縣', '臺東縣', '澎湖縣', '金門縣', '連江縣', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市', '基隆市', '新竹縣', '新竹市', '苗栗縣', '彰化縣', '南投縣', '雲林縣', '嘉義縣', '嘉義市', '屏東縣']


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

def get(city):
    token = 'CWB-F8BA9050-4549-48B8-9698-7BAC83C7DA63'
    url = 'https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=' + token + '&format=JSON&locationName=' + str(city)
    Data = requests.get(url)
    Data = (json.loads(Data.text,encoding='utf-8'))['records']['location'][0]['weatherElement']
    res = [[] , [] , []]
    for j in range(3):
        for i in Data:
            res[j].append(i['time'][j])
    return res


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    mtext = event.message.text
    message_type = event.message.type
    user_id = event.source.user_id
    reply_token = event.reply_token
    message = event.message.text
    if mtext[:7]== '@choice' and mtext[:7]!='':    
        city = message[7:]
        city = city.replace('台','臺')
        
        if mtext[7:]=='台北市':
            with urllib.request.urlopen(url1, context=context) as jsondata:
                data = json.loads(jsondata.read().decode('utf-8-sig'))        
            snalist.clear()
            arlist.clear() 
            latlist.clear()
            lnglist.clear()
            bemplist.clear()
            sbilist.clear()
                     
            for i in data:
                snalist.append((i['sna']))
                arlist.append(i['ar'])
                latlist.append(i['lat'])
                lnglist.append(i['lng'])
                bemplist.append(i['bemp'])
                sbilist.append(i['sbi'])
            #print(latlist)    
        if mtext[7:]=='桃園市':
            with urllib.request.urlopen(url2, context=context) as jsondata:
                data2 = json.loads(jsondata.read().decode('utf-8-sig'))
            snalist.clear()
            arlist.clear() 
            latlist.clear()
            lnglist.clear()
            bemplist.clear()
            sbilist.clear() 

            for i in data2['retVal']:
                snalist.append(data2['retVal'][i]['sna'])
                arlist.append(data2['retVal'][i]['ar'])            
                latlist.append(float(data2['retVal'][i]['lat']))
                lnglist.append(float(data2['retVal'][i]['lng']))
                bemplist.append(data2['retVal'][i]['bemp'])
                sbilist.append(data2['retVal'][i]['sbi'])
                
        if(not (city in cities)):
            line_bot_api.reply_message(reply_token,TextSendMessage(text="查詢格式為:@choice縣市"))
        else:
            res = get(city)
            line_bot_api.reply_message(reply_token, TemplateSendMessage(
                alt_text = 'Ubike站查詢範圍為'+city+',請分享您的位置訊息查詢最近的ubike站及空位,這邊附上未來 36 小時天氣預測',
                template = CarouselTemplate(
                    columns = [
                        CarouselColumn(
                            thumbnail_image_url = 'https://i.imgur.com/xjSwtFD.png',
                            title = '{} ~ {}'.format(res[0][0]['startTime'][5:-3],res[0][0]['endTime'][5:-3]),
                            text = '天氣狀況 {}\n溫度 {} ~ {} °C\n降雨機率 {}'.format(data[0]['parameter']['parameterName'],data[2]['parameter']['parameterName'],data[4]['parameter']['parameterName'],data[1]['parameter']['parameterName']),
                            actions = [
                                URIAction(
                                    label = '詳細內容',
                                    uri = 'https://www.cwb.gov.tw/V8/C/W/County/index.html'
                                )
                            ]
                        )for data in res
                    ]
                )
            ))

    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text=message))
   #----------------------------------------------------------------------------    

       
@handler.add(MessageEvent, message=LocationMessage)
def handle_location_message(event):
    #addr = event.message.address #地址
    lat = event.message.latitude  #緯度
    lng = event.message.longitude #緯度
    minDistance=getDistance(lat,lng,latlist[0],lnglist[0])
    for i in range(len(lnglist)):       
        if(getDistance(lat,lng,latlist[i],lnglist[i])<=minDistance):
            minDistance=getDistance(lat,lng,latlist[i],lnglist[i])
            tmpi=i
    ans=round(float(minDistance)*1000,4)
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text='最近的站: '+str(snalist[tmpi])+"\n"+'位置: '+str(arlist[tmpi])+"\n"+"目前可用車輛數: "+str(sbilist[tmpi])+"\n"+'目前空位數: '+str(bemplist[tmpi])+"\n"+'距離: '+str(ans)+'公尺')) 
    print(minDistance)
    
# 計算距離
def getDistance(latA, lonA, latB, lonB):
    ra = 6378140  # 赤道半徑
    rb = 6356755  # 極半徑
    flatten = (ra - rb) / ra  # Partial rate of the earth
    # change angle to radians
    radLatA = math.radians(latA)
    radLonA = math.radians(lonA)
    radLatB = math.radians(latB)
    radLonB = math.radians(lonB)

    pA = math.atan(rb / ra * math.tan(radLatA))
    pB = math.atan(rb / ra * math.tan(radLatB))
    x = math.acos(math.sin(pA) * math.sin(pB) + math.cos(pA) * math.cos(pB) * math.cos(radLonA - radLonB))
    c1 = (math.sin(x) - x) * (math.sin(pA) + math.sin(pB)) ** 2 / math.cos(x / 2) ** 2
    c2 = (math.sin(x) + x) * (math.sin(pA) - math.sin(pB)) ** 2 / math.sin(x / 2) ** 2
    dr = flatten / 8 * (c1 - c2)
    distance = ra * (x + dr)
    distance = round(distance/1000, 4)
    return f'{distance}'         

if __name__ == '__main__':
    app.run(debug=True)
