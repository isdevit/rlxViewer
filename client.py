import socket
import pyautogui
from threading import Thread
import threading
import cv2
import struct
from pynput import keyboard
import pickle
import tkinter.messagebox as mess
import numpy as np
import os
import time
from tkinter import filedialog

class Client:
    def __init__(self):
        self.host = ""
        self.my_host = socket.gethostbyname(socket.gethostname())
        # self.my_host = "26.151.58.139"
        self.port = 4444 #port 
        self.click_count = 0
        self.client_socket = None
        self.running = False
        self.window = "Remote Desktop"
        self.focus_window = False
        self.record = False
        self.width_window = 1920
        self.height_window = 1080
        self.filename_record =""
    def handle_error(self, error):
        mess.showerror(title = "Error",
                             message = error)
        self.running = False
    def send_size_window(self):  #Package Window SIze
        width= str(1920)
        height= str(1080)
        time.sleep(3)
        try:
            client_host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client_host.connect((self.host,self.port))
            mess = str(self.width_window)  + ' ' + str(self.height_window)
            client_host.send(mess.encode('utf-8'))
            client_host.close()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                self.handle_error(e)
    def send_client_ip(self): #client ip addrs
        try:
            client_host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            client_host.connect((self.host,self.port))
            print(self.my_host)
            client_host.send(self.my_host.encode("utf-8"))
            client_host.close()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                self.handle_error(e)
    def send_mouse(self,data):
        try:#send mouse data
            message =  {
                'type_data': 'mouse',
                'data': data
            }
            mess = pickle.dumps(message)
            packet = struct.pack('Q',len(mess)) + mess
            self.client_socket.sendall(packet)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                self.handle_error(e)
    def mouse_event(self,event, x, y, flags,param): #mouse listener
            if event == cv2.EVENT_MOUSEMOVE:
                message = f'mouse_move {x} {y}'
                self.send_mouse(message)
            elif event == cv2.EVENT_LBUTTONDOWN:
                self.click_count = 1
                message = f'left_click_and_hold {x} {y}'
                self.send_mouse(message)
            elif event == cv2.EVENT_LBUTTONUP:
                if self.click_count == 1:
                    message = f'left_release {x} {y}' 
                    self.send_mouse(message)
                    self.click_count = 0
            elif event == cv2.EVENT_LBUTTONDBLCLK:
                message = f'left_double_click {x} {y}'
                self.send_mouse(message)
            elif event == cv2.EVENT_RBUTTONDOWN:
                message = f'right_click {x} {y}'
                self.send_mouse(message)
            elif event == cv2.EVENT_MBUTTONDOWN:
                message = f'middle_click {x} {y}'
                self.send_mouse(message)
            elif event == cv2.EVENT_MOUSEWHEEL:
                if flags > 0:
                    self.send_mouse('scroll up')
                else:
                    self.send_mouse('scroll down')
    def send_key(self,key):
        try:
            message = pickle.dumps(key)
            packet = struct.pack('Q',len(message)) + message
            self.client_socket.sendall(packet)
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                self.handle_error(e)   
    def on_press(self,key):
        data = {
            'type_data' : 'key',
            'type' : 'down',
            'key' : key
        }
        if(self.focus_window):
            self.send_key(data)  
    def on_release(self,key):
        data = {
            'type_data' : 'key',
            'type' : 'up',
            'key' : key
        }
        if(self.focus_window):
            self.send_key(data)        
    def listen_keyboard(self):
        while self.running:
            with keyboard.Listener(on_press = self.on_press, on_release = self.on_release) as listener:
                listener.join()
    def receive_screen(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #get the screen
        server_socket.bind((self.my_host, self.port))
        server_socket.listen()
        connection, address = server_socket.accept()
        file_record = None
        try:
            if self.record:
                x = int(self.width_window)
                y = int(self.height_window)
                resolution = tuple((x, y))
                codec = cv2.VideoWriter_fourcc(*"XVID")
                fps = 12.0
                file_record = cv2.VideoWriter(self.filename_record, codec, fps, resolution)
                print(f"Recording started: {self.filename_record}")

            payload_size = struct.calcsize('>L')
            data = b""
            while self.running:
                try:
                    break_loop = False
                    while len(data) < payload_size:
                        received = connection.recv(4096)
                        if received == b'':
                            connection.close()
                            break_loop = True
                            break
                        data += received
                    if break_loop:
                        break
                    packed_msg_size = data[:payload_size]
                    
                    data = data[payload_size:]
                    
                    msg_size = struct.unpack(">L", packed_msg_size)[0]
                    while len(data) < msg_size:
                        data += connection.recv(4096)
                        
                    frame_data = data[:msg_size]
                    data = data[msg_size:]
                    
                    frame = pickle.loads(frame_data, fix_imports = True, encoding = "bytes")
                    frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
                    
                    if self.record and file_record is not None:
                        file_record.write(frame)  # Write frame to video file
                        
                    cv2.namedWindow(self.window, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(self.window, frame.shape[1], frame.shape[0])
                    cv2.imshow(self.window, frame)
                    
                    if (pyautogui.getActiveWindowTitle() == self.window):
                        self.focus_window = True
                    else:
                        self.focus_window = False
                    cv2.setMouseCallback(self.window, self.mouse_event)
                    cv2.waitKey(1)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                    connection.close()
                    cv2.destroyAllWindows()
                    self.handle_error(e)
                    break
        finally:
            if file_record is not None:
                file_record.release()
                print(f"Recording saved: {self.filename_record}")
            server_socket.close()
            cv2.destroyAllWindows()
    def choose_file(self):
        # Display file selection window
        file_path = os.path.realpath(
        filedialog.askopenfilename(title="Select File"))
        file_path = file_path.replace("\\", "/")
        # Print the file to selected path
        return file_path
    def send_filename(self, sck, filename):
        message = os.path.split(filename)[1]
        message_length = len(message)
        packed_message = struct.pack("<I", message_length)
        sck.sendall(packed_message)
        sck.send(message.encode('utf-8'))
    def send_file(self):
        try:
            new_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_client.connect((self.host, self.port + 5))
            filename = self.choose_file()
            if not filename:  # User cancelled file selection
                new_client.close()
                return
                
            print(f"Sending file: {filename}")
            self.send_filename(new_client, filename)
            time.sleep(0.5)
            
            filesize = os.path.getsize(filename)
            new_client.sendall(struct.pack("<Q", filesize))
            
            bytes_sent = 0
            with open(filename, "rb") as f:
                while bytes_sent < filesize:
                    chunk = f.read(8192)  # Increased buffer size for better performance
                    if not chunk:
                        break
                    new_client.sendall(chunk)
                    bytes_sent += len(chunk)
                    print(f"Progress: {bytes_sent}/{filesize} bytes ({(bytes_sent/filesize)*100:.1f}%)")
            
            print(f"File sent successfully: {filename}")
            new_client.close()
        except Exception as e:
            print(f"Error sending file: {str(e)}")
            mess.showerror(title="Error", message=f"Failed to send file: {str(e)}")
    def start_sendfile(self):
        message =  {
        'type_data': 'sendfile',
        'data': 'sendfile'
        }
        mess = pickle.dumps(message)
        packet = struct.pack('Q',len(mess)) + mess
        self.client_socket.sendall(packet)
        time.sleep(1)
        ##send file
        sendfile_thread = Thread(target= self.send_file)
        sendfile_thread.start()
    def start_client(self):
        self.running = True
        self.send_client_ip()
        if (self.running):
            self.send_size_window()
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #capture movement
            self.client_socket.connect((self.host, self.port))
            t1  = threading.Thread(target = self.receive_screen) #Receive Screen
            t2  = threading.Thread(target = self.listen_keyboard)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            self.client_socket.close()
# if __name__ == "__main__":
#     client = Client()
#     client.start_client()