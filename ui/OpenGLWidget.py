from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
import pyrr
import json
import os
import time
from tools.DrawFunctions import *

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None, obj_path=None, road_dots_path=None):
        super(OpenGLWidget, self).__init__(parent)

       
        self.dot_dict = {
                    '0' : 4, # side
                    '1' : 2, # crossroad
                    '2' : 3  # roadline
                    }

        self.obj_dict = {
                    'car' : 0,
                    'bus' : 0,
                    'pedestrian' : 1,
                    'motorcycle' : 5,
                    'sign_60' : 6,
                    'sign_ped' : 7,
                    'cone' : 8,
                    'truck' : 9,
                    'front_arrow' : 10,
                    'front_left_arrow' : 11,
                    'front_right_arrow' : 12,
                    }

        self.idx = 0
        
        # TODO : move this to main
        obj_path = 'result2ue5_add.json'
        road_dots_path = 'coord.json'


        self.cur_frame_data = {}
        self.speed_limit_60 = False


        # with open(os.path.join('json', obj_path), 'r') as f:
        #     self.data = json.load(f)

        # with open(os.path.join('json', road_dots_path), 'r') as f:
        #     self.coord = json.load(f)


    def initializeGL(self):
        # glClearColor(0.0, 0.0, 0.0, 1.0)

        
        glClearColor(0.0, 0.0, 0.0, 1)

        self.view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 3, 20]), 
                                                 pyrr.Vector3([0, -1, 0]), 
                                                 pyrr.Vector3([0, 1, 0]))
        
        self.projection = pyrr.matrix44.create_perspective_projection_matrix(45, 800 / 600, 0.1, 100)

        self.model, _, self.view_loc = get_model_info(["models/SUV.obj", "models/MasCasual3.obj", "models/cube.obj", "models/cube.obj", "models/cube.obj", "models/scooter.obj", "models/sign_60.obj", "models/sign_ped.obj", "models/cone.obj", "models/truck.obj", "models/front_arrow.obj", "models/front_left_arrow.obj", "models/front_right_arrow.obj"], 
                                        ["textures/SUV.jpg", "textures/ManCasual3.png", "textures/crossroad.png", "textures/roadline.png", "textures/side.png", "textures/scooter.jpg", "textures/sign_60.png", "textures/sign_ped.png", "textures/cone.png", "textures/truck.png", "textures/white.png", "textures/white.png", "textures/white.png"],
                                        self.view, self.projection)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        
    def set_view(self, view):
        self.view = pyrr.matrix44.create_look_at(pyrr.Vector3((view[0])), pyrr.Vector3(view[1]), pyrr.Vector3(view[2]))

    def paintGL(self):    
        if self.cur_frame_data:
            

            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.view)
            draw_model(self.model[0], 180, [0, -5, 0])
            self.idx += 1
            # draw floor dots
            t0 = time.time()
            for dot in self.cur_frame_data['dot']:
                x = dot['x'] / 200 * 70 - 35
                y = dot['y'] / 200 * 70 - 35
            
                draw_model(self.model[self.dot_dict[str(dot['cls'])]], 90, [x, -5, y])
                
            print('draw dot time : ', round((time.time() - t0) * 1000, 4), 'ms')

            # draw scene objects
            t0 = time.time()
            for obj in self.cur_frame_data['obj']:
                if obj['cls'] not in self.obj_dict.keys():
                    continue
                c_x = obj['x']
                c_y = obj['y']
                x = c_x / 682 * 100 - 50
                y = c_y / 682 * 100 - 50
                
                # TODO : optimize speed limit sign determine

                if obj['cls'] == 'sign_60':
                    self.speed_limit_60 = True

                draw_model(self.model[self.obj_dict[obj['cls']]], obj['ang'], [x, -5, y])   
            
            print('draw obj time : ', round((time.time() - t0) * 1000, 4), 'ms')