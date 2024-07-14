
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
from ui.UIPrototype import Ui_MainWindow
from PyQt5.QtGui import QImage, QPixmap
import sys
import os
import cv2


class Car_MainWindow(Ui_MainWindow):
    def __init__(self):
        super(Car_MainWindow, self).__init__()

        self.img_arr = {}
        self.speed_arr = []
        self.img_idx = 0
        self.cam_path_arr = ['CAM_FRONT', 'CAM_BACK']

        with open('json/speeds.txt', 'r') as f:
            self.speed_arr = f.readlines()

        for cam_path in self.cam_path_arr:
            img_paths = sorted(os.listdir(os.path.join('dummy_imgs', cam_path)), key=lambda x: int(x.split('.')[0].split('_')[-1]))
            self.img_arr[cam_path] = []
            for img_path in img_paths:
                img = cv2.imread(os.path.join('dummy_imgs', cam_path, img_path))
                img = cv2.resize(img, (450, 253))
                self.img_arr[cam_path].append(img)

    def update_img(self):

        self.img_idx += 1

        if self.img_idx < len(self.img_arr['CAM_FRONT']):
            self.img_front.setPixmap(self.convert_cv_qt(self.img_arr['CAM_FRONT'][self.img_idx]))
            self.img_back.setPixmap(self.convert_cv_qt(self.img_arr['CAM_BACK'][self.img_idx]))
            self.speedometer.display(round(float(self.speed_arr[self.img_idx].strip()), 1))


    def convert_cv_qt(self, cv_img):
        
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        return QPixmap.fromImage(convert_to_Qt_format)

    def setupUi(self, MainWindow): 
        super(Car_MainWindow,self).setupUi(MainWindow)

        self.img_front.setPixmap(self.convert_cv_qt(self.img_arr['CAM_FRONT'][self.img_idx]))
        self.img_back.setPixmap(self.convert_cv_qt(self.img_arr['CAM_BACK'][self.img_idx]))
        
        self.speedometer.display(round(float(self.speed_arr[self.img_idx].strip()), 1))


    def setupTimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.openGLWidget.update)
        self.timer.timeout.connect(self.update_img)
        self.timer.start(1000 // 8)
        
    



if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Car_MainWindow()
    ui.setupUi(window)
    window.show()
    ui.setupTimer()
    sys.exit(app.exec_())
