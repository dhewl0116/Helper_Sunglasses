import subprocess
import sys
import multiprocessing as mp
import datetime
import time
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox, QTextBrowser
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon
from multiprocessing import Process, Queue


class Communicate(QObject):
    closeApp = pyqtSignal()


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowIcon(QIcon('icon.png'))
        self.btn1 = QPushButton('딥러닝 서버 시작', self)
        self.btn1.setEnabled(True)
        self.btn1.clicked.connect(self.server_start)

        self.btn2 = QPushButton('딥러닝 서버 중지', self)
        self.btn2.setEnabled(True)
        self.btn2.clicked.connect(self.server_stop)

        self.btn3 = QPushButton('모니터링 [중지: ESC 키]', self)
        self.btn3.setEnabled(True)
        self.btn3.clicked.connect(self.monitoring)

        self.btn4 = QPushButton('음성 채팅 시작', self)
        self.btn4.setEnabled(True)
        self.btn4.clicked.connect(self.voice_start)

        self.btn5 = QPushButton('음성 채팅 중지', self)
        self.btn5.setEnabled(True)
        self.btn5.clicked.connect(self.voice_stop)

        self.tb = QTextBrowser()
        self.tb.setAcceptRichText(True)
        self.tb.setOpenExternalLinks(True)

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.btn1)
        self.vbox.addWidget(self.btn2)
        self.vbox.addWidget(self.btn3)
        self.vbox.addWidget(self.btn4)
        self.vbox.addWidget(self.btn5)
        self.vbox.addWidget(self.tb)

        self.setLayout(self.vbox)
        self.setWindowTitle('시각장애인 보호자 프로그램')
        self.setGeometry(300, 300, 400, 300)
        self.show()

    def server_start(self, e):
        res = go_server_start()
        self.tb.clear()
        self.tb.append(res)

    def server_stop(self, e):
        res = go_server_stop()
        self.tb.clear()
        self.tb.append(res)

    def monitoring(self, e):
        self.p = Process(name="monitoring", target=go_monitoring, args=(q,), daemon=True)
        self.p.start()
        self.tb.clear()
        self.tb.append('모니터링 시작')

    def voice_start(self, e):
        self.p = Process(name="voice_start", target=go_voice_start, args=(q,), daemon=True)
        self.p.start()
        self.tb.clear()
        self.tb.append('음성 채팅 시작')

    def voice_stop(self, e):
        self.p = Process(name="voice_stop", target=go_voice_stop, args=(q,), daemon=True)
        self.p.start()
        self.tb.clear()
        self.tb.append('음성 채팅 중지')

    def closeEvent(self, event):
        reply = QMessageBox.question(self, '프로그램 종료', 'Are you sure to quit?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def go_server_start():
    response = requests.get('http://192.168.10.189:8000/start')
    if str(response) == '<Response [200]>':
        return '서버 시작 성공'
    else:
        return str(response)


def go_server_stop():
    response = requests.get('http://192.168.10.189:8000/stop')
    if str(response) == '<Response [200]>':
        return '서버 중지 성공'
    else:
        return str(response)


def go_monitoring(q):
    proc = mp.current_process()
    print(proc.name)
    subprocess.run('./monitoring.exe')

    while True:
        now = datetime.datetime.now()
        data = str(now)
        q.put(data)
        time.sleep(1)


def go_voice_start(q):
    proc = mp.current_process()
    print(proc.name)
    subprocess.run('./voice_start.exe')

    while True:
        now = datetime.datetime.now()
        data = str(now)
        q.put(data)
        time.sleep(1)


def go_voice_stop(q):
    proc = mp.current_process()
    print(proc.name)
    subprocess.run('./voice_stop.exe')

    while True:
        now = datetime.datetime.now()
        data = str(now)
        q.put(data)
        time.sleep(1)


if __name__ == '__main__':
    q = Queue()
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
