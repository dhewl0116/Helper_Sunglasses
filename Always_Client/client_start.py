import os
import time
import threading
import datetime
import requests
from urllib.parse import quote
from pymongo import MongoClient


mongo_uri = "mongodb://always:" + quote("always") + "@192.168.10.189:27017/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
database = client['always']
dataset = database.dataset
dataset.update_one({"id": "1"}, {"$set": {"pick": "", "goods": "", "flag": False}})

sData = ''
overlap = 0
fn = 0
tmp = None
tm = time.localtime()
event = threading.Event()


def speak(add_str):
    global sData, overlap, tmp
    if overlap == 1:
        print(sData+add_str)
        voice = """ curl -v \
                  -H "x-api-key: XXXXXXXXXXXXXXXXXXXXXXXXXX" \
                  -H "Content-Type: application/xml" \
                  -H "X-TTS-Engine: deep" \
                  -d '<speak>
                      <voice name="Summer">{0}</voice>
                      </speak>' \
                  https://94a32363-bfe6-4c43-8cd5-0ecb45a376e6.api.kr-central-1.kakaoi.io/ai/text-to-speech/d7504f19ae0e4390b7c790dc2e2d4226 > /home/pi/CodeFair_Always/sound/sound.mp3 && mpg123 /home/pi/CodeFair_Always/sound/sound.mp3 """.format(sData+add_str)
        os.system(voice)
        time.sleep(1)
        tmp = None
    elif overlap == 0:
        print(sData)
        


def client_cam():
    global sData, tmp, overlap, fn
    
    os.system("mpg123 /home/pi/CodeFair_Always/sound/start.mp3")
    start = time.time()
    
    while True:
        row = dataset.find_one({"id": "1"})
        result = row['pick']
        goods = row['goods']
        flags = row['flag']
        if flags:
            sData = ''
        print(result)

        if result != tmp:
            for x in result:
                if len(x) == 1:
                    overlap = 0
                else:
                    overlap = 1
                    sData = result[0]
                    #print(sData)
            end = time.time()
            sec = (end - start)
            result_list = str(datetime.timedelta(seconds=sec)).split(".")
            time_str = result_list[0]
            td = int(time_str[5:7])
            if td % 1 == 0 and fn % 1 == 0:
                if sData in goods:
                    if 'in_hand' in result:
                        #print(result[0] + '잡기성공')
                        thread = threading.Thread(target=speak(',잡기성공'))
                        thread.start()
                        overlap = 0
                    elif 'out_hand' in result:
                        #print(result[0])
                        thread = threading.Thread(target=speak(''))
                        thread.start()
                        overlap = 0
                else:
                    thread = threading.Thread(target=speak(''))
                    thread.start()
                    overlap = 0
            fn = td + 1
        tmp = result


if __name__ == "__main__":
    try:
        requests.get('http://192.168.10.189:8000/start')
        client_cam()
    except AttributeError:
        event.set()
        client_cam()
