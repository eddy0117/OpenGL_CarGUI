import json
import os
import socket
import time

from PyQt5.QtCore import QObject, pyqtSignal


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

