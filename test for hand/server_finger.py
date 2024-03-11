import os
import time
import cv2
import json
import subprocess
import uvicorn as uvicorn
from fastapi import FastAPI
from multiprocessing import Process, Manager
from ultralytics import YOLO
import mediapipe as mp
import math
import numpy as np

cls = ""
app = FastAPI()
proc = None
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

def calculate_distance(x1, y1, x2, y2):
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return distance

def finger_capture(frame):
    height, width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            return int(index_tip.x*width), int(index_tip.y*height)
    return None

@app.get("/start")
def start():
    global proc
    if proc:
        proc.kill()
    proc = Process(target=webcam_server, args=(Manager().Value(str, cls),))
    proc.start()
    print('시작')
    return "YOLOv8 서버 가동 시작"

@app.get("/stop")
def stop():
    proc.kill()
    os.system('rm -rf output.avi')
    return "서버 가동 중지"

@app.get("/get")
def get_result(cls_manager: Manager().Value):
    global cls
    cls = cls_manager.value
    print(cls)
    return cls

def webcam_server(cls_manager: Manager().Value):
    global cls
    cap = cv2.VideoCapture(0)

    model = YOLO("C:/Users/leejimin/Desktop/2023 코드페어/sunglasses_back7.pt")

    cnt = 0
    while True:
        cnt += 1
        ret, img = cap.read()
        cv2.imshow("frame", img)
        if cnt % 100 == 0:
            results = model(img, conf=0.60)
            annotated_frame = results[0].plot()
            finger = finger_capture(img)
            if finger:
                print("손이 감지되었습니다")
                detected_item = []
                finger_x, finger_y = finger
                for b in results[0].boxes:
                    item = model.names[int(b.cls)]
                    xyxy = b.xyxy[0]
                    x_avg = int((xyxy[0] + xyxy[2]) / 2)
                    y_avg = int((xyxy[1] + xyxy[3]) / 2)
                    detected_item.append(((x_avg, y_avg), item))

                short_dis = 10000
                for loc, cls_name in detected_item:
                    ob_x, ob_y = loc
                    calculated_dis = calculate_distance(finger_x, finger_y, ob_x, ob_y)
                    if calculated_dis < short_dis:
                        short_dis = calculated_dis
                        cls = cls_name
                    annotated_frame = cv2.line(annotated_frame, (finger_x, finger_y), (ob_x, ob_y), (0, 0, 255), 5)
                cls_manager.value = cls
                cv2.imshow("yes finger", annotated_frame)
                if cls == 'mart_board':
                    cv2.imwrite('ocr.png', img)
                    ocr_list = []
                    ocr_str = ""
                    for cmd in [""" curl --location --request POST 'https://52695d72-4503-4abf-86a9-51f019cbaf0c.api.kr-central-1.kakaoi.io/ai/ocr/d813f986abd441fdb8b99addccadb811' \
                                --header 'x-api-key: ' \
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
                        ocr_array = ['글자는,' + ocr_str, '입니다.']
                        print(ocr_array)
                        cls_manager.value = ocr_array
                        time.sleep(5)
                        continue
                print(cls)
            else:
                print("손이 감지되지 않았습니다.")
                for b in results[0].boxes:
                    cls = model.names[int(b.cls)]
                    if cls == 'mart_board':
                        cv2.imwrite('ocr.png', img)
                        ocr_list = []
                        ocr_str = ""
                        for cmd in [""" curl --location --request POST 'https://52695d72-4503-4abf-86a9-51f019cbaf0c.api.kr-central-1.kakaoi.io/ai/ocr/d813f986abd441fdb8b99addccadb811' \
                                    --header 'x-api-key: ' \
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
                            ocr_array = ['글자는,' + ocr_str, '입니다.']
                            print(ocr_array)
                            cls_manager.value = ocr_array
                            time.sleep(5)
                            continue
                print(cls)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

if __name__ == "__main__":
    uvicorn.run(app="server_finger:app", host="localhost", port=8000, reload=False, workers=1)
