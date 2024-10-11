import time

import matplotlib.pyplot as plt
import numpy as np
import pyrr
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtWidgets import QOpenGLWidget
from tools.utils import twoD_2_threeD, rotate_2d_point
from tools.DrawFunctions import DrawFunctions as DF
import joblib
# 從檔案載入模型





class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None, obj_path=None, road_dots_path=None):
        super(OpenGLWidget, self).__init__(parent)

        self.dot_dict = {
            "0": "g_side",  # side
            "1": "g_crosswalk",  # crosswalk
            "2": "g_roadline",  # roadline
        }

        self.obj_dict = {
            # nuscenes classes
            "car": ["modern_car.obj", "modern_car.jpg"],
            "pedestrian": ["walking_person.obj", "scooter_.jpg"],
            "motorcycle": ["scooter.obj", "scooter.jpg"],
            "truck": ["truck.obj", "truck.jpg"],
            "bus": ["bus.obj", "bus.jpg"],
            "traffic_cone": ["cone.obj", "cone.png"],
            # others
            "ego_car": ["SUV.obj", "SUV.jpg"],
            "car_stop": ["modern_car.obj", "modern_car_stop_2.jpg"],
            "cone": ["cone.obj", "cone.png"],
            "g_crosswalk": ["cube.obj", "crossroad.png"],
            "g_roadline": ["cube.obj", "roadline.png"],
            "g_side": ["cube.obj", "side.png"],
            "sign_60": ["sign_60.obj", "sign_60.png"],
            "sign_ped": ["sign_ped.obj", "sign_ped.png"],
            "front_arrow": ["front_arrow.obj", "white.png"],
            "front_left_arrow": ["front_left_arrow.obj", "white.png"],
            "front_right_arrow": ["front_right_arrow.obj", "white.png"],
        }

        self.idx = 0
        self.peek = 0

        self.map_draw_mode = "vec"
        self.cur_frame_data = {}
        self.speed_limit_60 = False

        self.color_pal = plt.cm.plasma(range(256, 0, -1)) * 255
        self.color_pal = np.round(self.color_pal).astype(np.uint8).tolist()

        # 載入預測 distance 模型
        self.svg_reg = joblib.load('tools/svr_rbf_model.joblib')
        
        # nuscenes 某幀內參
        self.intrinsic = np.array([[1.26641720e+03, 0.00000000e+00, 8.16267020e+02],
                                    [0.00000000e+00, 1.26641720e+03, 4.91507066e+02],
                                    [0.00000000e+00, 0.00000000e+00, 1.00000000e+00]])

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1)

        self.view = pyrr.matrix44.create_look_at(
            pyrr.Vector3([0, 3, 20]), pyrr.Vector3([0, -1, 0]), pyrr.Vector3([0, 1, 0])
        )

        self.projection = pyrr.matrix44.create_perspective_projection_matrix(
            45, 800 / 600, 0.1, 100
        )

        self.obj_models, _, self.view_loc = DF.get_model_info(
            self.obj_dict, self.view, self.projection
        )

        self.color_textures = DF.get_colors(self.color_pal)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

    def set_view(self, view):
        self.view = pyrr.matrix44.create_look_at(
            pyrr.Vector3((view[0])), pyrr.Vector3(view[1]), pyrr.Vector3(view[2])
        )

    def paintGL(self):
        if self.cur_frame_data:
            t0 = time.time()
            glUniformMatrix4fv(self.view_loc, 1, GL_FALSE, self.view)
            DF.draw_model(self.obj_models["ego_car"], 180, [0, -5, 0])
            self.idx += 1

            # 繪製道路地圖

            if self.map_draw_mode == "seg":
                for dot in self.cur_frame_data["dot"]:
                    x = dot["x"] * 70 - 35
                    y = dot["y"] * 70 - 35

                    DF.draw_dot(
                        self.obj_models[self.dot_dict[str(int(dot["cls"]))]], [x, -5, y]
                    )

            elif self.map_draw_mode == "vec":
                if "traj" in self.cur_frame_data.keys():
                    glLineWidth(50)

                    traj = self.cur_frame_data["traj"]

                    x = np.array(traj)[:, 0]
                    y = np.array(traj)[:, 1]
                    x = x.tolist()
                    y = y.tolist()

                    z = [0 for _ in range(len(x))]
                    DF.draw_traj_pred(self.color_textures, x, z, y)

                glLineWidth(5)

                for lines in self.cur_frame_data["dot"]:
                    x = [dot_x * 70 - 35 for dot_x in lines["x"]]
                    y = [dot_y * 70 - 35 for dot_y in lines["y"]]
                    z = [0 for _ in range(len(x))]
                    DF.draw_line(
                        self.obj_models[self.dot_dict[str(lines["cls"])]], x, z, y
                    )

                # # DEBUG 畫前後偵測區域
                # line_1 = [int(l1 / 682 * 70 - 35) for l1 in [395, 415]] # front
                # line_2 = [int(l1 / 682 * 70 - 35) for l1 in [265, 305]] # back

                # # draw_line(self.obj_models[self.dot_dict['1']], [-5, 5], [-5, -5], [10, 10])
                # draw_line(self.obj_models[self.dot_dict['1']], [-100, -100, 100, 100, -100], [0 for _ in range(5)], [line_1[0], line_1[1], line_1[1], line_1[0], line_1[0]])
                # draw_line(self.obj_models[self.dot_dict['1']], [-100, -100, 100, 100, -100], [0 for _ in range(5)], [line_2[0], line_2[1], line_2[1], line_2[0], line_2[0]])

            # print('draw dot time : ', round((time.time() - t0) * 1000, 4), 'ms')



            # 2d 模式下將 box_h 輸入模型預測 distance
            if self.map_draw_mode == "2d":
                # 取得所有車輛的 box_h
                inputs = np.array([it['h'] for it in self.cur_frame_data["obj"] if it['cls'] == 'car'])
                if inputs.shape[0] != 0:
                    distance_arr = self.svg_reg.predict(inputs.reshape(-1, 1)).flatten()
                    


            # 繪製道路物件
            car_idx = 0
            for idx, obj in enumerate(self.cur_frame_data["obj"]):
                if obj["cls"] not in self.obj_dict.keys():
                    continue

                c_x = obj["x"]
                c_y = obj["y"]
                cls = obj["cls"]
                ang = obj["ang"]
                x, y = None, None

                if self.map_draw_mode == "3d":
                    scale = 70
                    x = c_x * scale - scale / 2
                    y = c_y * scale - scale / 2

                elif self.map_draw_mode == "seg":
                    scale = 100
                    x = c_x / 682 * scale - scale / 2
                    y = c_y / 682 * scale - scale / 2

                elif self.map_draw_mode == "vec":
                    # 使用 DataSender_TCP_vec.py 來傳送資料的話 x, y 要設定成 * 100 - 50
                    scale = 70
                    x = c_x * scale - scale / 2
                    y = c_y * scale - scale / 2

                    # is_stop只有在vec(SparseDrive)模式下才會有，有煞車燈
                    if (obj["is_stop"] == 1) and (cls == "car"):
                        cls = "car_stop"

                # 2d 模式目前只顯示車輛
                elif self.map_draw_mode == "2d" and obj["cls"] == 'car':
                    # 中心線座標 x 軸為 800 (nuscene圖片為 1600x900)
                    # 這裡的 x, y 指的是 2d bbox 在畫面上的左上角座標
           
                    w = obj["w"]
                    h = obj["h"]
                    x = c_x + w // 2
                    y = c_y + h

                    x, y, z = twoD_2_threeD((x + w) // 2, y + h, distance_arr[car_idx] / 8, self.intrinsic)
                    # y = -z 
                    # x = x
                    x, y = rotate_2d_point(x, -z, 20)
                    x = x * 1.2 - 3
                    y = y * 1.2 - 5
             
                    car_idx += 1
                
                    if c_y + h > 900:
                        continue

                # TODO : optimize speed limit sign determine

                if obj["cls"] == "sign_60":
                    self.speed_limit_60 = True

                # 為了2d模式只顯示車輛
                if not x or not y:
                    continue

                DF.draw_model(self.obj_models[cls], ang, [x, -5, y])

            # t1 = time.time()
            # if t1 - t0 > self.peek:
            #     self.peek = t1 - t0
            # print('peek : ', round(self.peek * 1000, 4), 'ms')
