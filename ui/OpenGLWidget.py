import json
import os
import time

import matplotlib.pyplot as plt
import numpy as np
import pyrr
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QOpenGLWidget

from tools.DrawFunctions import DrawFunctions as DF


class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None, obj_path=None, road_dots_path=None):
        super(OpenGLWidget, self).__init__(parent)

       
        self.dot_dict = {
                    '0' : 'g_side', # side
                    '1' : 'g_crosswalk', # crosswalk
                    '2' : 'g_roadline'  # roadline
                    }
      
        self.obj_dict = {
            # nuscenes classes
            'car' : ["modern_car.obj", "modern_car.jpg"],
            'pedestrian' : ["walking_person.obj", "scooter_.jpg"], 
            'motorcycle' : ["scooter.obj", "scooter.jpg"],
            'truck' : ["truck.obj", "truck.jpg"],
            'bus' : ["bus.obj", "bus.jpg"],
            'traffic_cone' : ["cone.obj", "cone.png"],
            # others
            'ego_car' : ["SUV.obj", "SUV.jpg"],
            'cone' : ["cone.obj", "cone.png"],
            'g_crosswalk' : ["cube.obj", "crossroad.png"], 
            'g_roadline' : ["cube.obj", "roadline.png"], 
            'g_side' : ["cube.obj", "side.png"], 
            'sign_60' : ["sign_60.obj", "sign_60.png"],
            'sign_ped' : ["sign_ped.obj", "sign_ped.png"], 
            'front_arrow' : ["front_arrow.obj", "white.png"],
            'front_left_arrow' : ["front_left_arrow.obj", "white.png"],
            'front_right_arrow' : ["front_right_arrow.obj", "white.png"]
        }
        
        self.idx = 0
        self.peek = 0
     
        self.map_draw_mode = 'vec'
        self.cur_frame_data = {}
        self.speed_limit_60 = False

        self.color_pal = plt.cm.plasma(range(256)) * 255

        self.color_pal = np.round(self.color_pal).astype(np.uint8).tolist()


    def initializeGL(self):

        glClearColor(0.0, 0.0, 0.0, 1)

        self.view = pyrr.matrix44.create_look_at(pyrr.Vector3([0, 3, 20]), 
                                                 pyrr.Vector3([0, -1, 0]), 
                                                 pyrr.Vector3([0, 1, 0]))
        
        self.projection = pyrr.matrix44.create_perspective_projection_matrix(45, 800 / 600, 0.1, 100)

        self.obj_models, _, self.view_loc = DF.get_model_info(self.obj_dict,
                                        self.view, self.projection)  

        self.color_textures = DF.get_colors(self.color_pal)
        
    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        
    def set_view(self, view):
        self.view = pyrr.matrix44.create_look_at(pyrr.Vector3((view[0])), pyrr.Vector3(view[1]), pyrr.Vector3(view[2]))
    
    def paintGL(self):    

        if self.cur_frame_data:
            
            t0 = time.time()
            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.view)
            DF.draw_model(self.obj_models['ego_car'], 180, [0, -5, 0])
            self.idx += 1

            # 繪製道路地圖
            
            

            glBindVertexArray(self.obj_models['g_crosswalk']['VAO'])

            if self.map_draw_mode == 'seg':

                for dot in self.cur_frame_data['dot']:
                    x = dot['x'] * 70 - 35
                    y = dot['y'] * 70 - 35

                    DF.draw_dot(self.obj_models[self.dot_dict[str(int(dot['cls']))]], [x, -5, y])

            elif self.map_draw_mode == 'vec':
                
                if 'traj' in self.cur_frame_data.keys():

                    glLineWidth(50)

                    traj = self.cur_frame_data['traj']
                    
                    # glBindTexture(GL_TEXTURE_2D, self.color_textures[0])

                    x = np.array(traj)[:, 0] 
                    y = np.array(traj)[:, 1] 
                    x = x.tolist()
                    y = y.tolist()
                
        
                    z = [0 for _ in range(len(x))]
                    DF.draw_traj_pred(self.obj_models[self.dot_dict['0']], self.color_textures, x, z, y)


                glLineWidth(5)
                
                for lines in self.cur_frame_data['dot']:
                    
                    x = [dot_x * 70 - 35 for dot_x in lines['x']]
                    y = [dot_y * 70 - 35 for dot_y in lines['y']]
                    z = [0 for _ in range(len(x))]
                    DF.draw_line(self.obj_models[self.dot_dict[str(lines['cls'])]], x, z, y)


                # # DEBUG 畫前後偵測區域
                # line_1 = [int(l1 / 682 * 70 - 35) for l1 in [395, 415]] # front
                # line_2 = [int(l1 / 682 * 70 - 35) for l1 in [265, 305]] # back
               
                # # draw_line(self.obj_models[self.dot_dict['1']], [-5, 5], [-5, -5], [10, 10])
                # draw_line(self.obj_models[self.dot_dict['1']], [-100, -100, 100, 100, -100], [0 for _ in range(5)], [line_1[0], line_1[1], line_1[1], line_1[0], line_1[0]])
                # draw_line(self.obj_models[self.dot_dict['1']], [-100, -100, 100, 100, -100], [0 for _ in range(5)], [line_2[0], line_2[1], line_2[1], line_2[0], line_2[0]])
                

            

            # print('draw dot time : ', round((time.time() - t0) * 1000, 4), 'ms')

            # draw scene objects
         
            # 繪製道路物件
            for obj in self.cur_frame_data['obj']:
                
                if obj['cls'] not in self.obj_dict.keys():
                        continue
                
                c_x = obj['x']
                c_y = obj['y']

                if self.map_draw_mode == 'seg':

                    x = c_x / 682 * 100 - 50
                    y = c_y / 682 * 100 - 50

                elif self.map_draw_mode == 'vec':
                    
                    # 使用 DataSender_TCP_vec.py 來傳送資料的話 x, y 要設定成 * 100 - 50
                    x = c_x * 70 - 35
                    y = c_y * 70 - 35
          
                # TODO : optimize speed limit sign determine

                if obj['cls'] == 'sign_60':
                    self.speed_limit_60 = True

                DF.draw_model(self.obj_models[obj['cls']], obj['ang'], [x, -5, y])   
            
            # t1 = time.time()
            # if t1 - t0 > self.peek:
            #     self.peek = t1 - t0
            # print('peek : ', round(self.peek * 1000, 4), 'ms')