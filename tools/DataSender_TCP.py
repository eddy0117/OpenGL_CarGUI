import socket
import os
import json
import time
import base64
import cv2
import random

MAX_CHUNK_SIZE = 5000

def send_udp_message():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 65432))
    # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 50000)
    # client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 5000)
    # server_address = ('localhost', 65432)
 
    try:
        
        obj_path = 'result2ue5_add.json'
        road_dots_path = 'coord.json'
        cam_path_arr = ['CAM_FRONT', 'CAM_BACK']
        img_arr = {}


        data_send = {}

        with open(os.path.join('json', obj_path), 'r') as f:
            data = json.load(f)

        with open(os.path.join('json', road_dots_path), 'r') as f:
            coord = json.load(f)

        with open('json/speeds.txt', 'r') as f:
            speed_arr = f.readlines()
        
        with open('json/vehicle_monitor.json', 'r') as f:
            vehicle_monitor_arr = json.load(f)

        for cam_path in cam_path_arr:
            img_paths = sorted(os.listdir(os.path.join('dummy_imgs', cam_path)), key=lambda x: int(x.split('.')[0].split('_')[-1]))
            img_arr[cam_path] = []
            for img_path in img_paths:
                img = cv2.imread(os.path.join('dummy_imgs', cam_path, img_path))
                img = cv2.resize(img, (470, 264))
                img_arr[cam_path].append(img)

        bev_img_paths = sorted(os.listdir(os.path.join('dummy_imgs', 'gt_t')), key=lambda x: int(x.split('.')[0]))
        img_arr['bev_img'] = []
        for img_path in bev_img_paths:
            img = cv2.imread(os.path.join('dummy_imgs', 'gt_t', img_path))
            img_arr['bev_img'].append(img)

        idx = 0
        t0 = time.time()
        while True:

            data_send = {} # reset data_send for new frame

            if idx > len(list(data.keys())) - 1:
                break
            
            cur_obj_data = data[list(data.keys())[idx]]
            cur_coord_data = coord[list(coord.keys())[idx]]
                

            # send speed and steering
            cur_speed = speed_arr[idx]
            cur_steering = vehicle_monitor_arr[idx]['steering']

            data_send['speed'] = cur_speed
            data_send['steering'] = cur_steering

            # send images
            data_send['img'] = {}
            for cam_path in cam_path_arr:
                cur_img = img_arr[cam_path][idx]
                # base64 encode image
                _, cur_img = cv2.imencode('.jpg', cur_img)
                cur_img = base64.b64encode(cur_img).decode('utf-8')  # decode bytes to string
      
                data_send['img'][cam_path] = cur_img

            # send bev image
            
            cur_img = img_arr['bev_img'][idx]
            # base64 encode image
            _, cur_img = cv2.imencode('.jpg', cur_img)
            cur_img = base64.b64encode(cur_img).decode('utf-8')  # decode bytes to string
    
            data_send['img']['BEV'] = cur_img

            # send dots       
            # data_dot = []

            # for dot in cur_coord_data:
            #     data_dot.append({'x' : dot[1], 
            #                      'y' : dot[0],
            #                      'cls' : dot[2]})
            # data_send['dot'] = data_dot

            # send objects
            data_obj = []
            for obj_idx in list(cur_obj_data.keys()):
                obj = cur_obj_data[obj_idx]
                data_obj.append({'x' : obj['x'], 
                                 'y' : obj['y'], 
                                 'cls' : obj['class'], 
                                 'ang' : obj['distance_ang'] + 90})
           

            
            data_send['obj'] = data_obj

            # send data_send to server

            data_send = json.dumps(data_send).encode('utf-8')
            
            # UDP
            # client_socket.sendto(data_send, server_address)

            # TCP
            # client_socket.sendall(data_send)

            data_send += ('\0').encode('utf-8')
            print('send length : ',len(data_send))
            for i in range(0, len(data_send), MAX_CHUNK_SIZE):
                # print('segment length : ',len(data_send[i:i+MAX_CHUNK_SIZE]))
                client_socket.sendall(data_send[i:i+MAX_CHUNK_SIZE])


            # if len(data_send) < MAX_CHUNK_SIZE * 4:
            #     data_send_padd = data_send + b'\0' * (MAX_CHUNK_SIZE * 4 - len(data_send))
            # print('send length : ',len(data_send), ', padd length : ', len(data_send_padd))
            # for i in range(0, len(data_send_padd), MAX_CHUNK_SIZE):
            #     # print('segment length : ',len(data_send[i:i+MAX_CHUNK_SIZE]))
            #     client_socket.sendall(data_send_padd[i:i+MAX_CHUNK_SIZE])
              


            # client_socket.sendall('end'.encode('utf-8'))
            # delay = random.uniform(0.03, 0.08)
            delay = 0.1

            time.sleep(delay)
            idx += 1
        print(f'{idx} samples take time : ', round((time.time() - t0), 4), 's')
    finally:
        client_socket.close()

if __name__ == "__main__":
    send_udp_message()