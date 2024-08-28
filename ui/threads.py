from PyQt5.QtCore import pyqtSignal, QObject
import os
import time
import socket
import json


class DataRecievedThread(QObject):

    data_recieved_signal = pyqtSignal(dict)

    def __init__(self):
        super(DataRecievedThread, self).__init__()
        
        # Set the maximum size of the message that can be received one time
        self.MAX_CHUNK_SIZE = 5000
        
        

    def run(self):
        while True:
            
            # Create a TCP socket
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind the socket to the address and port
            self.server_socket.bind(('localhost', 65432))
            
            # Setup the socket to listen for incoming connections
            self.server_socket.listen(1)

            conn, _ = self.server_socket.accept()
            
            whole_data = b''
            data_cat = b''
            while True:
                
                data = conn.recv(self.MAX_CHUNK_SIZE)
                data = data_cat + data  # add the rest of the data from last frame
                if data_cat:
                    print('data concat!')
                if not data:
                    self.server_socket.close()
                    print('Connection closed')
                    break

                data_split = data.split(b'\0')
                if len(data_split) > 1: # End of a package
                    data_cat = data_split[1] # Preserve the rest of the data (a part of next frame first chunk)
                    whole_data += data_split[0]
                    data = json.loads(whole_data.strip(b'\0').decode('utf-8'))
                    self.data_recieved_signal.emit(data)
                    whole_data = b''
                    
                else:
                    data_cat = b''
                    whole_data += data_split[0]



            # try:
            #     if b'\0' in data: # end of a package
                    
            #         print(data.index(b'\0'), data.__len__())

            #         t1 = time.time()
            #         whole_data += data
            #         # print(data[-30:], 'data len : ' , data.decode('utf-8').__len__(), 'whole data len : ' , whole_data.decode('utf-8').__len__())
            #         data = json.loads(whole_data.strip(b'\0').decode('utf-8'))
            #         self.data_recieved_signal.emit(data)
            #         whole_data = b''
            #         print('takes time : ', round((time.time() - t1) * 1000, 4), 'ms')
            #     else:
            #         whole_data += data
            # except json.JSONDecodeError:
            #     print('===========json decode error===========')
            #     print(data[-10:])
            #     break
                
            # if chunk_idx == 3:
            #     whole_data += data
            #     print(whole_data.__len__(), whole_data.strip(b'\0').__len__())
            #     data = json.loads(whole_data.strip(b'\0').decode('utf-8'))
            #     self.data_recieved_signal.emit(data)
            #     chunk_idx = 0
            #     whole_data = b''
            # else:
            #     whole_data += data
            #     chunk_idx += 1

       # try:

            #     data, addr = self.server_socket.recvfrom(100000)
            #     data = json.loads(data.decode('utf-8'))
            #     self.data_recieved_signal.emit(data)

            # except BlockingIOError:
            #     pass
            


