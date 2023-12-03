import time
import os
from DFRobot_RaspberryPi_A02YYUW import DFRobot_A02_Distance as Board


board = Board()


def speak(distance):
    if distance <= 700:
        str = '바로 앞에 물체가 있습니다. 조심하세요.'
    else:
        distance /= 1000
        str = '전방 %.1f 미터 앞 물체 발견' % distance
    voice = """ curl -v \
              -H "x-api-key: 91ce013c97b577b8f4c8d354e675b883" \
              -H "Content-Type: application/xml" \
              -H "X-TTS-Engine: deep" \
              -d '<speak>
                  <voice name="Summer">{0}</voice>
                  </speak>' \
              https://94a32363-bfe6-4c43-8cd5-0ecb45a376e6.api.kr-central-1.kakaoi.io/ai/text-to-speech/d7504f19ae0e4390b7c790dc2e2d4226 > /home/pi/CodeFair_Always/sound/warn.mp3 && mpg123 /home/pi/CodeFair_Always/sound/warn.mp3 """.format(str)
    os.system(voice)
    time.sleep(1)


def print_distance(dis):
    if board.last_operate_status == board.STA_OK:
        print("Distance %d mm" %dis)
    elif board.last_operate_status == board.STA_ERR_CHECKSUM:
        print("ERROR")
    elif board.last_operate_status == board.STA_ERR_SERIAL:
        print("Serial open failed!")
    elif board.last_operate_status == board.STA_ERR_CHECK_OUT_LIMIT:
        print("Above the upper limit: %d" %dis)
    elif board.last_operate_status == board.STA_ERR_CHECK_LOW_LIMIT:
        print("Below the lower limit: %d" %dis)
    elif board.last_operate_status == board.STA_ERR_DATA:
        print("No data!")


if __name__ == "__main__":
  dis_min = 0   #Minimum ranging threshold: 0mm
  dis_max = 4500 #Highest ranging threshold: 4500mm
  board.set_dis_range(dis_min, dis_max)
  while True:
    distance = board.getDistance()
    print(distance)
    if board.last_operate_status != board.STA_ERR_DATA:
        speak(distance)
    time.sleep(0.6) #Delay time < 0.6s