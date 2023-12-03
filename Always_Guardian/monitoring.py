import cv2
import platform
import threading


def stream_camera():
    src = "rtsp://admin:Itg8Ulds@192.168.10.108:554/live/ch00_1"
    if platform.system() == 'Windows':
        cap = cv2.VideoCapture(src)
    else:
        cap = cv2.VideoCapture(src)
    while cap.isOpened():
        grabbed, frame = cap.read()
        frame = frame.reshape(360, 640, 3)
        frame = cv2.transpose(frame)
        frame = cv2.flip(frame, 0)

        if grabbed:
            cv2.imshow('Sunglasses Monitoring', frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()


cam_thread = threading.Thread(target=stream_camera)
cam_thread.start()
