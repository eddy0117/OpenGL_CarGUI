from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *
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
                    '1' : 2, # crosswalk
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
        self.peek = 0
     
        self.map_draw_mode = 'seg'
        self.cur_frame_data = {}
        self.speed_limit_60 = False


        # with open(os.path.join('json', obj_path), 'r') as f:
        #     self.data = json.load(f)

        # with open(os.path.join('json', road_dots_path), 'r') as f:
        #     self.coord = json.load(f)


    def initializeGL(self):
        # glClearColor(0.0, 0.0, 0.0, 1.0)

        glColor3f(1.0, 1.0, 1.0)  # 設置畫筆顏色為白色
        glPointSize(5.0)
        
        glClearColor(0.0, 0.0, 0.0, 1)

        self.view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 3, 20]), 
                                                 pyrr.Vector3([0, -1, 0]), 
                                                 pyrr.Vector3([0, 1, 0]))
        
        self.projection = pyrr.matrix44.create_perspective_projection_matrix(45, 800 / 600, 0.1, 100)

        self.model, _, self.view_loc = get_model_info(["models/SUV.obj", "models/walking_person.obj", "models/cube.obj", "models/cube.obj", "models/cube.obj", "models/scooter.obj", "models/sign_60.obj", "models/sign_ped.obj", "models/cone.obj", "models/truck.obj", "models/front_arrow.obj", "models/front_left_arrow.obj", "models/front_right_arrow.obj"], 
                                        ["textures/SUV.jpg", "textures/scooter.jpg", "textures/crossroad.png", "textures/roadline.png", "textures/side.png", "textures/scooter.jpg", "textures/sign_60.png", "textures/sign_ped.png", "textures/cone.png", "textures/truck.png", "textures/white.png", "textures/white.png", "textures/white.png"],
                                        self.view, self.projection)   

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        
    def set_view(self, view):
        self.view = pyrr.matrix44.create_look_at(pyrr.Vector3((view[0])), pyrr.Vector3(view[1]), pyrr.Vector3(view[2]))
    
    def paintGL(self):    

        glLineWidth(5)
        
        if self.cur_frame_data:
            

            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.view)
            draw_model(self.model[0], 180, [0, -5, 0])
            self.idx += 1
            # draw floor dots
            t0 = time.time()
            

            glBindVertexArray(self.model[2]['VAO'])

            if self.map_draw_mode == 'seg':

                for dot in self.cur_frame_data['dot']:
                    x = dot['x'] / 200 * 70 - 35
                    y = dot['y'] / 200 * 70 - 35

                    draw_dot(self.model[self.dot_dict[str(dot['cls'])]], [x, -5, y])

            elif self.map_draw_mode == 'vec':
                
                for lines in self.cur_frame_data['line']:
                    
                    x = [int(dot_x / 256 * 100 - 50) for dot_x in lines['x']]
                    y = [int(dot_y / 256 * 100 - 50) for dot_y in lines['y']]
                    z = [-5 for _ in range(len(x))]
                    draw_line(self.model[self.dot_dict[str(lines['cls'])]], x, z, y)

            t1 = time.time()
            if t1 - t0 > self.peek:
                self.peek = t1 - t0
            print('peek : ', round(self.peek * 1000, 4), 'ms')

            # print('draw dot time : ', round((time.time() - t0) * 1000, 4), 'ms')

            # draw scene objects
            # t0 = time.time()
            
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
            
            # print('draw obj time : ', round((time.time() - t0) * 1000, 4), 'ms')