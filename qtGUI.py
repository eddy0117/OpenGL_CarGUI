
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QThread
from OpenGL.GL import *
from ui.UIPrototype import Ui_MainWindow
from PyQt5.QtGui import QImage, QPixmap
from ui.threads import DataRecievedThread

from easing_functions import *
import sys
import numpy as np
import os
import cv2
import json
import base64
import time
from numba import jit

@jit
def process_bev_data(img):
    dot_data = []

    for i in range(0, img.shape[0], 3):
        for j in range(0, img.shape[1], 3):
     
            pixel = img[i, j]
            if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
                dot_data.append({'x': j, 'y': i, 'cls': 0})
            elif pixel[0] == 255 and pixel[1] == 0 and pixel[2] == 0:
                dot_data.append({'x': j, 'y': i, 'cls': 1})
            elif pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 255:
                dot_data.append({'x': j, 'y': i, 'cls': 2})

    return dot_data

class Car_MainWindow(Ui_MainWindow):
    def __init__(self):
        super(Car_MainWindow, self).__init__()

        self.bev_map_mode = 'vec'

        self.cur_frame_data = {}

        self.idx_data = 0
        self.idx_cam_rise = 0
        self.idx_cam_down = 0

        self.flag_cam_rised = False
        self.flag_cam_lock = False

        
        self.queue_inter = []
        self.tl_dire = 'left'
        self.isLightOn = False
        self.display_tl = False
        self.flag_frame_changed = False



        self.thread_data = QThread()
        self.datathread = DataRecievedThread()
        self.datathread.moveToThread(self.thread_data)
        self.thread_data.started.connect(self.datathread.run)
        self.datathread.data_recieved_signal.connect(self.recv_data)
        self.thread_data.start()

        self.arr_cam_ease = list(map(CubicEaseInOut(start=0, end=25),np.arange(0, 1, 0.1))) 
        
    
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
    
    
    # def process_bev_data(self):
    #     img = cv2.cvtColor(self.img_bev_data, cv2.COLOR_BGR2RGB)
    #     img = cv2.resize(img, (200, 200))
    #     img = np.rot90(img, 1)
        
    #     # Cut car img in the middle of BEV map
    #     img[(img.shape[0] // 2 - 8):(img.shape[0] // 2 + 8), (img.shape[1] // 2 - 4):(img.shape[1] // 2 + 3)] = 255
    #     img = cv2.threshold(img, 105, 255, cv2.THRESH_BINARY)[1]
        
 
    #     for i in range(0, img.shape[0], 3):
    #         for j in range(0, img.shape[1], 3):
    #             pixel = img[i, j]
    #             if pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 0:
    #                 self.cur_frame_data['dot'].append({'x': j, 'y': i, 'cls': 0})
    #             elif pixel[0] == 255 and pixel[1] == 0 and pixel[2] == 0:
    #                 self.cur_frame_data['dot'].append({'x': j, 'y': i, 'cls': 1})
    #             elif pixel[0] == 0 and pixel[1] == 0 and pixel[2] == 255:
    #                 self.cur_frame_data['dot'].append({'x': j, 'y': i, 'cls': 2})

    def recv_data(self, data_rec):
        self.cur_frame_data = data_rec
        self.flag_frame_changed = True
        # t0 = time.time()
        for cam, img_data in data_rec['img'].items():

            img_data = base64.b64decode(img_data) # -> bytes
            img = np.frombuffer(img_data, np.uint8) # -> numpy array, shape = (N,)
            img = cv2.imdecode(img, cv2.IMREAD_COLOR) # -> numpy array, shape = (H, W, C)
            
            if cam == 'CAM_FRONT':
                self.img_front_data = self.convert_cv_qt(img)
            elif cam == 'CAM_BACK':
                self.img_back_data = self.convert_cv_qt(img)
            elif cam == 'BEV':
                self.img_bev_data = img       

        self.cur_frame_data['dot'] = []

        t0 = time.time()

        if self.bev_map_mode == 'seg':

            img = cv2.cvtColor(self.img_bev_data, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (200, 200))
            img = np.rot90(img, 1)
            
            img[(img.shape[0] // 2 - 8):(img.shape[0] // 2 + 8), (img.shape[1] // 2 - 4):(img.shape[1] // 2 + 3)] = 255
            img = cv2.threshold(img, 105, 255, cv2.THRESH_BINARY)[1]

            self.cur_frame_data['dot'] = process_bev_data(img)
            
        elif self.bev_map_mode == 'vec':
            pass

            print('==== bev img time ==== : ', round((time.time() - t0) * 1000, 4), 'ms')
    

    def isIntersection(self):
        dots_data = self.cur_frame_data['dot']

        # 定義車前，後的偵測線
        line_1 = [245 // 3.41, 275 // 3.41]
        line_2 = [395 // 3.41, 452 // 3.41]
        in_dot_sum = 0
        out_dot_sum = 0
        thr = 2
        
        for dot in dots_data:
            if dot['cls'] == 1:
                if dot['y'] > line_1[0] and dot['y'] < line_1[1]:
                    in_dot_sum += 1
                if dot['y'] > line_2[0] and dot['y'] < line_2[1]:
                    out_dot_sum += 1

        if self.flag_frame_changed:
            if in_dot_sum > thr:
                if not self.queue_inter:
                    self.queue_inter.append('in')
                else:
                    if self.queue_inter[-1] != 'in':
                        self.queue_inter.append('in')
                        
            if out_dot_sum > thr:
                if not self.queue_inter:
                    self.queue_inter.append('out')
                else: 
                    if self.queue_inter[-1] != 'out':
                        self.queue_inter.append('out')
  
            self.flag_frame_changed = False

    def cam_rise(self):
        if not self.flag_cam_rised:
            if self.idx_cam_rise < 10:
                self.openGLWidget.set_view([[0, 3 + self.arr_cam_ease[self.idx_cam_rise], 20], [0, -1, 0], [0, 1, 0]])
                self.idx_cam_rise += 1
                self.flag_cam_lock = True
            else:
                self.flag_cam_rised = True
                self.flag_cam_lock = False
                self.idx_cam_rise = 0

    def cam_down(self):
        if self.flag_cam_rised:
            if self.idx_cam_down < 10:
                self.openGLWidget.set_view([[0, 3 + 25 - self.arr_cam_ease[self.idx_cam_down], 20], [0, -1, 0], [0, 1, 0]])
                self.idx_cam_down += 1
                self.flag_cam_lock = True
            else:
                self.flag_cam_rised = False
                self.flag_cam_lock = False
                self.idx_cam_down = 0
    
       

    def setupUi(self, MainWindow): 
        super(Car_MainWindow,self).setupUi(MainWindow)

        # OpenGLWidget 設定道路線繪製模式
        self.openGLWidget.map_draw_mode = self.bev_map_mode

        # 前後鏡頭RGB畫面顯示
        self.img_front.setPixmap(self.convert_cv_qt(np.zeros((264, 470, 3), np.uint8)))
        self.img_back.setPixmap(self.convert_cv_qt(np.zeros((264, 470, 3), np.uint8)))
        
        # 時速表顯示
        self.speedometer.display(0)

        # 方向燈顯示
        self.img_steer_left.setScaledContents(True)
        self.img_steer_right.setScaledContents(True)
        self.img_speed_limit.setScaledContents(True)
        self.img_steer_left.setPixmap(QPixmap('imgs/green_arrow_left_dark.png'))
        self.img_steer_right.setPixmap(QPixmap('imgs/green_arrow_right_dark.png'))

    def setupTimer(self):
        self.timer_frame = QTimer()

        # Setup timer for turning light
        self.timer_turnlight = QTimer()
        self.timer_turnlight.timeout.connect(self.turn_light)
        self.timer_turnlight.start(300)

        # Setup timer for updating UI
        self.timer_updateUI = QTimer()
        self.timer_updateUI.timeout.connect(self.updateUI)
        self.timer_updateUI.start(33)
        
    
    def updateUI(self):
        
        # Update UI after received first frame data
        # t0 = time.time()
        if self.cur_frame_data:       
             
            self.openGLWidget.cur_frame_data = self.cur_frame_data
            self.openGLWidget.update()
           
            self.update_img(self.cur_frame_data)
            
            if self.bev_map_mode == 'seg':
                self.isIntersection()

            if self.queue_inter:
                if self.queue_inter[0] == 'in':
                    self.cam_rise()
                    if not self.flag_cam_lock:
                        self.queue_inter.pop(0)
                elif self.queue_inter[0] == 'out':
                    self.cam_down()
                    if not self.flag_cam_lock:
                        self.queue_inter.pop(0)

        # print('==== update UI time ==== : ', round((time.time() - t0) * 1000, 4), 'ms') 
            
    # Updating frame
    def update_img(self, data_rec):
        
        self.img_front.setPixmap(self.img_front_data)
        self.img_back.setPixmap(self.img_back_data)
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

if __name__ == '__main__':

    # Dummy function to warm up the numba jit
    process_bev_data(np.zeros((200, 200, 3), np.uint8))

    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Car_MainWindow()
    ui.setupUi(window)
    window.show()
    ui.setupTimer()
    sys.exit(app.exec_())
