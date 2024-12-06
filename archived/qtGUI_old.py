
import base64
import json
import os
import sys

import cv2
import numpy as np
from OpenGL.GL import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

from ui.threads import DataRecievedThread
from ui.UIPrototype import Ui_MainWindow


class Car_MainWindow(Ui_MainWindow):
    def __init__(self):
        super(Car_MainWindow, self).__init__()

        self.img_arr = {}
        self.speed_arr = []
        self.img_idx = 0
        self.cam_path_arr = ['CAM_FRONT', 'CAM_BACK']
        self.display_tl = False
        self.tl_dire = 'left'
        self.isLightOn = False

        self.thread_data = QThread()
        self.datathread = DataRecievedThread()
        self.datathread.moveToThread(self.thread_data)
        self.thread_data.started.connect(self.datathread.run)
        self.datathread.data_recieved_signal.connect(self.updateUI)
        self.thread_data.start()
        

        with open('json/speeds.txt', 'r') as f:
            self.speed_arr = f.readlines()
        
        with open('json/vehicle_monitor.json', 'r') as f:
            self.vehicle_monitor_arr = json.load(f)

        for cam_path in self.cam_path_arr:
            img_paths = sorted(os.listdir(os.path.join('dummy_imgs', cam_path)), key=lambda x: int(x.split('.')[0].split('_')[-1]))
            self.img_arr[cam_path] = []
            for img_path in img_paths:
                img = cv2.imread(os.path.join('dummy_imgs', cam_path, img_path))
                img = cv2.resize(img, (470, 264))
                self.img_arr[cam_path].append(img)


    # updating frame
    def update_img(self, data_rec):

        # self.img_idx += 1

        # if self.img_idx < len(self.img_arr['CAM_FRONT']):
        #     self.img_front.setPixmap(self.convert_cv_qt(self.img_arr['CAM_FRONT'][self.img_idx]))
        #     self.img_back.setPixmap(self.convert_cv_qt(self.img_arr['CAM_BACK'][self.img_idx]))
        #     self.speedometer.display(round(float(self.speed_arr[self.img_idx].strip()), 1))
        #     steering = round(float(self.vehicle_monitor_arr[self.img_idx]['steering']),2)
        #     # self.speedometer_2.display(steering)
        #     if steering > 60:
        #         self.display_tl = True
        #         self.tl_dire = 'left'
        #     elif steering < -60:
        #         self.display_tl = True
        #         self.tl_dire = 'right'
        #     else:
        #         self.display_tl = False
    
        #     if self.openGLWidget.speed_limit_60:
        #         self.img_speed_limit.setPixmap(QPixmap('imgs/spd_limit_60.png'))
        for cam, img_data in data_rec['img'].items():

            img_data = base64.b64decode(img_data) # -> bytes
            img = np.frombuffer(img_data, np.uint8) # -> numpy array, shape = (N,)
            img = cv2.imdecode(img, cv2.IMREAD_COLOR) # -> numpy array, shape = (H, W, C)
            if cam == 'CAM_FRONT':
                self.img_front.setPixmap(self.convert_cv_qt(img))
            elif cam == 'CAM_BACK':
                self.img_back.setPixmap(self.convert_cv_qt(img))

        self.speedometer.display(round(float(data_rec['speed']), 1))
        steering = round(float(data_rec['steering']),2)
        if steering > 60:
            self.display_tl = True
            self.tl_dire = 'left'
        elif steering < -60:
            self.display_tl = True
            self.tl_dire = 'right'
        else:
            self.display_tl = False

        if self.openGLWidget.speed_limit_60:
            self.img_speed_limit.setPixmap(QPixmap('imgs/spd_limit_60.png'))

    def turn_light(self):
        if self.display_tl:
            if self.isLightOn:
                self.isLightOn = False
                if self.tl_dire == 'left':
                    self.img_steer_left.setPixmap(QPixmap('imgs/green_arrow_left.png'))
                elif self.tl_dire == 'right':
                    self.img_steer_right.setPixmap(QPixmap('imgs/green_arrow_right.png'))
            else:
                if self.tl_dire == 'left':
                    self.img_steer_left.setPixmap(QPixmap('imgs/green_arrow_left_dark.png'))
                elif self.tl_dire == 'right':
                    self.img_steer_right.setPixmap(QPixmap('imgs/green_arrow_right_dark.png'))
                self.isLightOn = True
        else:
            self.img_steer_left.setPixmap(QPixmap('imgs/green_arrow_left_dark.png'))
            self.img_steer_right.setPixmap(QPixmap('imgs/green_arrow_right_dark.png'))

    def convert_cv_qt(self, cv_img):
        
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(convert_to_Qt_format)

    def setupUi(self, MainWindow): 
        super(Car_MainWindow,self).setupUi(MainWindow)

        # self.img_front.setPixmap(self.convert_cv_qt(self.img_arr['CAM_FRONT'][self.img_idx]))
        # self.img_back.setPixmap(self.convert_cv_qt(self.img_arr['CAM_BACK'][self.img_idx]))
        self.img_front.setPixmap(self.convert_cv_qt(np.zeros((264, 470, 3), np.uint8)))
        self.img_back.setPixmap(self.convert_cv_qt(np.zeros((264, 470, 3), np.uint8)))
        
        self.speedometer.display(0)

       
        self.img_steer_left.setScaledContents(True)
        self.img_steer_right.setScaledContents(True)
        self.img_speed_limit.setScaledContents(True)
        self.img_steer_left.setPixmap(QPixmap('imgs/green_arrow_left_dark.png'))
        self.img_steer_right.setPixmap(QPixmap('imgs/green_arrow_right_dark.png'))

    def setupTimer(self):
        self.timer_frame = QTimer()
        # self.timer_frame.timeout.connect(self.openGLWidget.update)
        # self.timer_frame.timeout.connect(self.gl_update)
        # self.timer_frame.timeout.connect(self.update_img)
        # self.timer_frame.start(33)

        self.timer_turnlight = QTimer()
        self.timer_turnlight.timeout.connect(self.turn_light)
        self.timer_turnlight.start(300)
        
    
    def updateUI(self, data_rec : dict):
 
        self.openGLWidget.cur_frame_data = data_rec
        self.openGLWidget.update()
        self.update_img(data_rec)


if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Car_MainWindow()
    ui.setupUi(window)
    window.show()
    ui.setupTimer()
    sys.exit(app.exec_())
