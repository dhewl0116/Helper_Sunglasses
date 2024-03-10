import time
import os
from ult import DFRobot_A02_Distance as Board
import serial
board = Board()

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
    time.sleep(0.6) #Delay time < 0.6s