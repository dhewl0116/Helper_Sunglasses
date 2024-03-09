import os
import time
import cv2
import json
import subprocess
import uvicorn as uvicorn
from fastapi import FastAPI
from multiprocessing import Process
from ultralytics import YOLO
from urllib.parse import quote
from pymongo import MongoClient
from connect.db import mart_dic


mongo_uri = "mongodb://always:" + quote("always") + "@192.168.10.189:27017/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri)
database = client['always']
dataset = database.dataset
app = FastAPI()
proc = 0


@app.get("/start")
def start():
    global proc
    if proc:
        proc.kill()
    dataset.update_one({"id": "1"}, {"$set": {"pick": "", "goods": "", "flag": False}})
    proc = Process(target=webcam_server)
    proc.start()
    print('시작')
    return "YOLOv8 서버 가동 시작"


@app.get("/stop")
def stop():
    proc.kill()
    dataset.update_one({"id": "1"}, {"$set": {"pick": "", "goods": "", "flag": True}})
    os.system('rm -rf output.avi')
    return "서버 가동 중지"


def webcam_server():
    cap = cv2.VideoCapture('rtsp://admin:Itg8Ulds@192.168.10.108:554/live/ch00_1')     # 'rtsp://admin:Itg8Ulds@192.168.10.108:554/live/ch00_1'

    # fourcc = cv2.VideoWriter_fourcc(*"DIVX")
    # out = cv2.VideoWriter('output.avi', fourcc, 25.0, (640, 360))

    model = YOLO("sunglasses.pt")

    cnt = 0
    while True:
        cnt += 1
        ret, frame = cap.read()
        frame = frame.reshape(360, 640, 3)
        img = cv2.transpose(frame)
        img = cv2.flip(img, 0)
        cv2.imshow("frame", img)

        if cnt % 50 == 0:
            results = model(img, conf=0.85)
            label = []
            xyxy = []
            right, left = None, None
            for b in results[0].boxes:
                cls = model.names[int(b.cls)]
                print(cls)
                if cls == 'mart_board':
                    cv2.imwrite('ocr.png', img)
                    # out.write(img)
                    ocr_list = []
                    ocr_str = ""
                    for cmd in [""" curl --location --request POST 'https://52695d72-4503-4abf-86a9-51f019cbaf0c.api.kr-central-1.kakaoi.io/ai/ocr/d813f986abd441fdb8b99addccadb811' \
                                --header 'x-api-key: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' \
                                --header 'Content-Type: multipart/form-data' \
                                --form 'image=@"ocr.png"' """]:
                        ocr = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
                    json_list = json.loads(ocr)

                    for json_obj in json_list["responses"]:
                        for json_word in json_obj["results"]:
                            ocr_list += json_word["recognized_word"]

                    for x in ocr_list:
                        ocr_str += x + ","

                    print(ocr_str)
                    if ocr_str:
                        ocr_array = ['글자는,'+ocr_str, '입니다.']
                        dataset.update_one({"id": "1"}, {"$set": {"pick": ocr_array, "goods": mart_dic, "flag": False}})
                        time.sleep(5)
                        continue
                elif cls == 'myright':
                    if right:
                        raise Exception('오른쪽 팔이 이미 감지되어있습니다.')
                    else:
                        right = tuple(map(int, b.xyxy[0]))
                elif cls == 'myleft':
                    if left:
                        raise Exception('왼쪽 팔이 이미 감지되어있습니다.')
                    else:
                        left = tuple(map(int, b.xyxy[0]))
                else:
                    xyxy.append([cls] + list(map(int, b.xyxy[0])))

            for b in xyxy:
                cls, x1, y1, x2, y2 = b
                cls = mart_dic[cls]
                if right and (x1 < right[0] < right[2] < x2) + (y1 < right[1] < right[3]) < y2 + (
                        right[0] < x1 < x2 < right[2]) + (right[1] < y1 < y2 < right[3]) + (
                        right[0] < x1 < right[2] < x2) + (right[1] < y1 < right[3] < y2) + (
                        x1 < right[0] < x2 < right[2]) + (y1 < right[1] < y2 < right[3]) >= 2:
                    label += [cls, 'in_hand']
                elif left and (x1 < left[0] < left[2] < x2) + (y1 < left[1] < left[3]) < y2 + (
                        left[0] < x1 < x2 < left[2]) + (left[1] < y1 < y2 < left[3]) + (
                        left[0] < x1 < left[2] < x2) + (left[1] < y1 < left[3] < y2) + (
                        x1 < left[0] < x2 < left[2]) + (y1 < left[1] < y2 < left[3]) >= 2:
                    label += [cls, 'in_hand']
                else:
                    label += [cls, 'out_hand']
            print(label)
            dataset.update_one({"id": "1"}, {"$set": {"pick": label, "goods": mart_dic, "flag": False}})

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


if __name__ == "__main__":
    uvicorn.run(app="server:app", host="0.0.0.0", port=8000, reload=False, workers=1)

