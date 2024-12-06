import base64
import json
import os
import random
import socket
import time
from nuscenes.nuscenes import NuScenes
import cv2
import numpy as np

MAX_CHUNK_SIZE = 5000

def send_udp_message():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65432))




    try:
        
        obj_path = 'carla_2d_bbox_new.json'
        cam_path_arr = ['CAM_FRONT', 'CAM_BACK']
        img_arr = {
            'CAM_FRONT' : [],
            'CAM_BACK' : [],
        }


        data_send = {}

        carla_img_paths = sorted(os.listdir('data/carla/img'), key=lambda x: int(x.split('.')[0]))

        with open(os.path.join('json', obj_path), 'r') as f:
            data = json.load(f)


        for i in range(0, len(data)):

            cam_front_path = os.path.join('data/carla/img', carla_img_paths[i])

            img = cv2.imread(cam_front_path)
            img = cv2.resize(img, (470, 264))
            img_fake = np.ones_like(img) * 128
            img_arr['CAM_FRONT'].append(img)
            img_arr['CAM_BACK'].append(img_fake)
        

        idx = 0
        t0 = time.time()
        while True:

            data_send = {} # reset data_send for new frame

            if idx > len(list(data.keys())) - 1:
                break
            
            cur_obj_data = data[list(data.keys())[idx]]
                
            data_send['speed'] = 0
            data_send['steering'] = 0

            # send images
            data_send['img'] = {}
            for cam_path in cam_path_arr:
                cur_img = img_arr[cam_path][idx]
                # base64 encode image
                _, cur_img = cv2.imencode('.jpg', cur_img)
                cur_img = base64.b64encode(cur_img).decode('utf-8')  # decode bytes to string
      
                data_send['img'][cam_path] = cur_img


            # send objects
            data_obj = []
            for obj_idx in list(cur_obj_data.keys()):
                obj = cur_obj_data[obj_idx]
                data_obj.append({'x' : obj['x'], 
                                 'y' : obj['y'], 
                                 'w' : obj['w'],
                                 'h' : obj['h'],
                                 'cls' : obj['cls'], 
                                 'ang' : 180})
           

            
            data_send['obj'] = data_obj
 
            # send data_send to server

            data_send = json.dumps(data_send).encode('utf-8')
            

            data_send += ('\0').encode('utf-8')
            print('send length : ',len(data_send))
            for i in range(0, len(data_send), MAX_CHUNK_SIZE):
                # print('segment length : ',len(data_send[i:i+MAX_CHUNK_SIZE]))
                client_socket.sendall(data_send[i:i+MAX_CHUNK_SIZE])

            delay = 0.2

            time.sleep(delay)
            idx += 1
        print(f'{idx} samples take time : ', round((time.time() - t0), 4), 's')
    finally:
        client_socket.close()

if __name__ == "__main__":
    send_udp_message()