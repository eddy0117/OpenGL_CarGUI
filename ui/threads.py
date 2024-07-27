from PyQt5.QtCore import pyqtSignal, QObject
import os
import time
import socket
import json


class DataRecievedThread(QObject):

    data_recieved_signal = pyqtSignal(dict)

    def __init__(self):
        super(DataRecievedThread, self).__init__()
        # # 创建一个UDP套接字
        # self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # # 绑定套接字到本地地址和端口
        # self.server_socket.bind(('localhost', 65432))
        # # 设置套接字为非阻塞模式
        # self.server_socket.setblocking(False)

        # 创建一个TCP套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定套接字到本地地址和端口
        self.server_socket.bind(('localhost', 65432))
        
        self.server_socket.listen(1)
        
        

    def run(self):
        conn, _ = self.server_socket.accept()
        whole_data = b''
        while True:
            
            data = conn.recv(5000)
            # print(data.__len__())
            
            if not data:
                self.server_socket.close()
                break

            if data[-3:] == b'end': # end of a package
                whole_data += data[:-3]
                data = json.loads(whole_data.decode('utf-8'))
                self.data_recieved_signal.emit(data)
                whole_data = b''
            else:
                whole_data += data
       # try:

            #     data, addr = self.server_socket.recvfrom(100000)
            #     data = json.loads(data.decode('utf-8'))
            #     self.data_recieved_signal.emit(data)

            # except BlockingIOError:
            #     pass
            


