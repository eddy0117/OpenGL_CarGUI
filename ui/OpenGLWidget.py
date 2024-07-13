from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
import pyrr
import json
import os
from tools.DrawFunctions import get_model_info, draw_model

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super(OpenGLWidget, self).__init__(parent)

       
        self.dot_dict = {
                    '0' : 4, # side
                    '1' : 2, # crossroad
                    '2' : 3  # roadline
                    }

        self.obj_dict = {
                    'car' : 0,
                    'pedestrian' : 1,
                    'motorcycle' : 5,
                    'sign_60' : 6,
                    'sign_ped' : 7,
                    'cone' : 8
                    }

        self.t1 = None
        self.idx = 0
        

        obj_path = 'result2ue5_add.json'
        road_dots_path = 'coord.json'


        with open(os.path.join('JSONfiles', obj_path), 'r') as f:
            self.data = json.load(f)

        with open(os.path.join('JSONfiles', road_dots_path), 'r') as f:
            self.coord = json.load(f)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1000 // 5)

    def initializeGL(self):
        # glClearColor(0.0, 0.0, 0.0, 1.0)

        
        glClearColor(0.1, 0.1, 0.1, 1)

        self.view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 3, 20]), pyrr.Vector3([0, -1, 0]), pyrr.Vector3([0, 1, 0]))
        self.projection = pyrr.matrix44.create_perspective_projection_matrix(45, 800 / 600, 0.1, 100)

        self.model, _ = get_model_info(["models/SUV.obj", "models/MasCasual3.obj", "models/cube.obj", "models/cube.obj", "models/cube.obj", "models/scooter.obj", "models/sign_60.obj", "models/sign_ped.obj", "models/cone.obj"], 
                                        ["textures/SUV.jpg", "textures/ManCasual3.png", "textures/crossroad.png", "textures/roadline.png", "textures/side.png", "textures/gray_2.jpg", "textures/sign_60.png", "textures/sign_ped.png", "textures/cone.png"],
                                        self.view, self.projection)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def paintGL(self):

        if self.idx > len(list(self.data.keys())) - 1:
            return
        
        cur_frame_data = self.data[list(self.data.keys())[self.idx]]
        cur_coord_data = self.coord[list(self.coord.keys())[self.idx]]
          
        self.idx += 1

        draw_model(self.model[0], 180, [0, -5, 0])

        # draw floor dots
        for dot in cur_coord_data:
            x = dot[1] / 682 * 70 - 35
            y = dot[0] / 682 * 70 - 35
        
            draw_model(self.model[self.dot_dict[str(dot[2])]], 90, [x, -5, y])


        # draw scene objects
        for obj_idx in list(cur_frame_data.keys()):
            obj = cur_frame_data[obj_idx]
            if obj['class'] not in self.obj_dict.keys():
                continue
            c_x = obj['x']
            c_y = obj['y']
            x = c_x / 682 * 100 - 50
            y = c_y / 682 * 100 - 50

            draw_model(self.model[self.obj_dict[obj['class']]], obj['distance_ang'] + 90, [x, -5, y])

        # self.update()