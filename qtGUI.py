
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer
from OpenGL.GL import *
import sys
import os
from ui.UIPrototype import Ui_MainWindow


class Car_MainWindow(Ui_MainWindow):
    def __init__(self):
        super(Car_MainWindow, self).__init__()


    def setupUi(self, MainWindow): 
        super(Car_MainWindow,self).setupUi(MainWindow)
        
        
if __name__ == '__main__':
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    app = QApplication(sys.argv)
    window = QMainWindow()
    ui = Car_MainWindow()
    ui.setupUi(window)
    window.show()
    sys.exit(app.exec_())
