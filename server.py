import socket
import cv2
import pynput
from pynput.mouse import Button as but, Controller
import numpy as np
import threading
import pyautogui
import keyboard 
import win32api
import pickle
import tkinter.messagebox as mess
import os
import time
import struct
from pynput import keyboard
from tkinter import filedialog
import pygetwindow as gw
import pytesseract


#Set Tesseract path (Modify for Windows if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:/Users/ashis/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"

#Define Sensitive Words to Detect
SENSITIVE_WORDS = ["password", "ssn", "credit card", "confidential", "bank", "secret"]


def get_ip_address():
    """Fetches the WiFi (WLAN) IP instead of Ethernet IP"""
    try:
        #Connect to an external server (Google DNS) to get the WLAN IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        wlan_ip = s.getsockname()[0]
        s.close()
        return wlan_ip
    except Exception as e:
        return "127.0.0.1" 

def detect_sensitive_lines(image, window_width):
    """Finds entire lines that contain sensitive words and returns their bounding box regions."""
    ocr_data = extract_text_with_positions(image)
    blur_regions = []

    for i, word in enumerate(ocr_data["text"]):
        if any(sensitive.lower() in word.lower() for sensitive in SENSITIVE_WORDS):
            print(f" Found Sensitive Word: {word} at Line {ocr_data['line_num'][i]}")

            y, h = ocr_data["top"][i], ocr_data["height"][i]  # Get line position
            blur_regions.append((0, y, window_width, y + h))  # Blur entire line width

    return blur_regions  # Return list of full-line regions to blur

def extract_text_with_positions(image):
    """Extracts text with word bounding boxes from an image."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    d = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)  # OCR with positions
    return d  # Returns dictionary with words & positions

def detect_sensitive_regions(image):
    """Finds words that need blurring and their bounding boxes."""
    ocr_data = extract_text_with_positions(image)
    blur_regions = []

    for i, word in enumerate(ocr_data["text"]):
        if any(sensitive.lower() in word.lower() for sensitive in SENSITIVE_WORDS):
            print(f" Found Sensitive Word: {word} at ({ocr_data['left'][i]}, {ocr_data['top'][i]})")
            x, y, w, h = ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i]
            blur_regions.append((x, y, x + w, y + h))  # Store bounding box

    return blur_regions 

def extract_text_from_image(image):
    """Extracts text from an image using OCR"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    text = pytesseract.image_to_string(gray)  # OCR processing
    return text
'''
def detect_sensitive_lines2(image):
    """Finds lines with sensitive words and returns their positions"""
    text = extract_text_from_image(image)
    lines = text.split("\n")  # Split into individual lines
    blur_regions = []

    for idx, line in enumerate(lines):
        if any(word.lower() in line.lower() for word in SENSITIVE_WORDS):  
            print(f" Sensitive Word Found: {line}")  # Debugging
            y_start = idx * 30  # Approximate y position (tweak as needed)
            blur_regions.append((y_start, y_start + 30))  # Save line position

    return blur_regions'''

def is_sensitive_file_open():
    """Check if a sensitive file type (.txt, .docx, .pdf) is open"""
    active_window = gw.getActiveWindow()
    
    if active_window:
        window_title = active_window.title.lower()  # Convert to lowercase
        
        #Check for specific file extensions
        sensitive_extensions = [".txt", ".docx", ".pdf", ".xlsx", ".pptx"]
        return any(ext in window_title for ext in sensitive_extensions)

    return False

def get_active_window_region():
    """Get the position & size of the active window"""
    try:
        active_window = gw.getActiveWindow()  #Get active window
        if active_window:
            x, y, width, height = (
                active_window.left, active_window.top,
                active_window.width, active_window.height
            )
            return x, y, width, height
    except:
        return None
    
def apply_blur(frame):
        """Applies a Gaussian blur effect to the frame"""
        return cv2.GaussianBlur(frame, (21, 21), 30)

def is_text_editor_active():
        """Checks if a text editor like Notepad or Word is active"""
        active_window = pyautogui.getActiveWindow()
        if active_window:
            text_apps = ["Notepad", "Word", "Google Docs", "Text", "LibreOffice", "WPS Office"]
            return any(app in active_window.title for app in text_apps)
        return False

class Server:
    def __init__(self):
        self.x_res,self.y_res = int(pyautogui.size()[0]), int(pyautogui.size()[1])
        self.width,self.height = int(pyautogui.size()[0]), int(pyautogui.size()[1])
        self.host = ""
        #self.my_host = socket.gethostbyname(socket.gethostname()) this returns ethernet ipv4
        #self.my_host = get_ip_address()
        #self.my_host = "192.168.66.20"
        self.my_host = "10.4.132.137"
        self.running = False
        self.port = 4444
        self.server_socket = None
        self.screen_quality = 45
        self.is_auto_blur = False
        self.is_auto_blurwin = False
        self.mouse = Controller()
        self.server_host = None
    def handle_error(self, error):
        mess.showerror(title = "Error",
                             message = error)
        print("Closing connection")
        self.running = False
    def receive_client_ip(self): #get client ip addrs
        server_host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            server_host.bind((self.my_host, self.port))
            server_host.settimeout(10)
            server_host.listen()
            conn, addr = server_host.accept()
            self.host = conn.recv(1024)
            self.host = str(self.host.decode("utf-8"))
            conn.close()
            server_host.close()
        except socket.timeout as e:
                server_host.close()
                self.handle_error(e)
            
    def recv_size_window(self):   #get window size
        try:
            server_host = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_host.bind((self.my_host, self.port))
            server_host.listen()
            conn, addr = server_host.accept()
            size = conn.recv(1024).decode("utf-8")
            size = size.split(' ')
            self.x_res,self.y_res = int(size[0]),int(size[1])
            print(self.x_res,self.y_res)
            conn.close()
            server_host.close()
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                self.handle_error(e)
    
    def get_frame(self):  #screenshot
        screen = pyautogui.screenshot()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (self.x_res,self.y_res), interpolation=cv2.INTER_AREA)
        return frame
    
    def send_display(self):
        """Captures the screen, detects sensitive words, and blurs the entire line."""
        socket_screen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_screen.connect((self.host, self.port))
        
        while self.running:
            frame = self.get_frame()

            if self.is_auto_blur and is_text_editor_active():
                print(" Scanning for Sensitive Words...")

                # Get active window region
                region = get_active_window_region()

                if region:
                    x, y, width, height = region
                    window_area = frame[y:y+height, x:x+width]  # Extract window area
                    
                    # Detect full lines containing sensitive words
                    blur_regions = detect_sensitive_lines(window_area, width)

                    # Apply blur to detected full lines
                    for (x1, y1, x2, y2) in blur_regions:
                        frame[y + y1:y + y2, x + x1:x + x2] = cv2.GaussianBlur(frame[y + y1:y + y2, x + x1:x + x2], (21, 21), 30)

            result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.screen_quality])
            data = pickle.dumps(frame, 0)

            try:
                socket_screen.sendall(struct.pack('>L', len(data)) + data)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, TimeoutError) as e:
                self.handle_error(e)
                break
        
    '''def send_display(self):
        """Captures the screen, detects sensitive words, and blurs only them."""
        socket_screen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_screen.connect((self.host, self.port))
        
        while self.running:
            frame = self.get_frame()

            if self.is_auto_blur and is_text_editor_active():
                print(" Scanning for Sensitive Words...")

                # Get active window region
                region = get_active_window_region()

                if region:
                    x, y, width, height = region
                    window_area = frame[y:y+height, x:x+width]  # Extract window area
                    
                    # Detect exact word positions
                    blur_regions = detect_sensitive_regions(window_area)

                    # Apply blur only to detected words
                    for (x1, y1, x2, y2) in blur_regions:
                        frame[y + y1:y + y2, x + x1:x + x2] = cv2.GaussianBlur(frame[y + y1:y + y2, x + x1:x + x2], (21, 21), 30)

            result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.screen_quality])
            data = pickle.dumps(frame, 0)

            try:
                socket_screen.sendall(struct.pack('>L', len(data)) + data)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, TimeoutError) as e:
                self.handle_error(e)
                break'''

    def send_display2(self):
            """Captures the screen and sends it to the client"""
            socket_screen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_screen.connect((self.host, self.port))
            
            while self.running:
                frame = self.get_frame()

                if self.is_auto_blurwin and is_sensitive_file_open():
                    print(" Blurring Sensitive File: ", gw.getActiveWindow().title)
                    region = get_active_window_region()

                    if region:
                        x, y, width, height = region

                        #Extract the window area
                        window_area = frame[y:y+height, x:x+width]

                        #Apply blur ONLY to the window area
                        blurred_area = cv2.GaussianBlur(window_area, (21, 21), 30)

                        #Replace the original area with the blurred version
                        frame[y:y+height, x:x+width] = blurred_area

                result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.screen_quality])
                data = pickle.dumps(frame, 0)

                try:
                    socket_screen.sendall(struct.pack('>L', len(data)) + data)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, TimeoutError) as e:
                    self.handle_error(e)
                    break
    
    '''def send_display(self):
            """Captures the screen, detects sensitive words, and blurs only those lines"""
            socket_screen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_screen.connect((self.host, self.port))
            
            while self.running:
                frame = self.get_frame()

                if self.is_auto_blur and is_text_editor_active():
                    print(" Scanning for Sensitive Information...")

                    #Get active window region
                    region = get_active_window_region()

                    if region:
                        x, y, width, height = region
                        window_area = frame[y:y+height, x:x+width]  # Extract window area
                        
                        #Detect lines that need blurring
                        blur_regions = detect_sensitive_lines(window_area)

                        #Apply blur only to detected lines
                        for (y1, y2) in blur_regions:
                            frame[y + y1:y + y2, x:x+width] = cv2.GaussianBlur(frame[y + y1:y + y2, x:x+width], (21, 21), 30)

                result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.screen_quality])
                data = pickle.dumps(frame, 0)

                try:
                    socket_screen.sendall(struct.pack('>L', len(data)) + data)
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                    self.handle_error(e)
                    break'''
            
    '''def send_display(self):
        """Captures the screen and sends it to the client"""
        socket_screen = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_screen.connect((self.host, self.port))
        
        while self.running:
            frame = self.get_frame()

            # Apply blur if Auto Blur is enabled and a text editor is open
            if self.is_auto_blur and self.is_text_editor_active():
                frame = apply_blur(frame)

            result, frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), self.screen_quality])
            data = pickle.dumps(frame, 0)

            try:
                socket_screen.sendall(struct.pack('>L', len(data)) + data)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, TimeoutError) as e:
                self.handle_error(e)
                break
        socket_screen.close()'''
    
    def get_keyboard(self,key):
        controller = keyboard.Controller()
        if key['type'] == 'down':
            controller.press(key['key'])
        else:
            controller.release(key['key'])
            
    def receive_filename(self, sck):
        
        # Get 4 bytes from the connection
        received_data = sck.recv(4)

        # Check if enough data has been receiver
        while len(received_data) < 4:
            received_data += sck.recv(4 - len(received_data))

        # Data extraction using little-endian and unsigned int types
        message_length= struct.unpack("<I", received_data)[0]
        
        #message_length = struct.unpack("<I", sck.recv(4))[0]
        message = sck.recv(message_length)
        message = message.decode('utf-8')
        return message
    
    def choose_folder(self):
        # Display folder selection window
        folder_path = os.path.realpath(
            filedialog.askdirectory(title="Select Folder"))
        # Print the path to the selected folder
        folder_path = folder_path.replace("\\", "/")
        return folder_path
        
    
    def receive_file_size(self, sck):
        fmt = "<Q"
        expected_bytes = struct.calcsize(fmt)
        received_bytes = 0
        stream = bytes()
        while received_bytes < expected_bytes:
            chunk = sck.recv(expected_bytes - received_bytes)
            stream += chunk
            received_bytes += len(chunk)
        filesize = struct.unpack(fmt, stream)[0]
        return filesize

    def receive_file(self):
        try:
            new_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            new_server.bind((self.my_host, self.port + 5))
            new_server.listen(1)
            print("Waiting for file transfer...")
            new_socket, client_addr = new_server.accept()
            
            # Get save location from user
            source = self.choose_folder()
            if not source:  # User cancelled folder selection
                new_socket.close()
                new_server.close()
                return
                
            # Get filename length (4 bytes)
            received_data = new_socket.recv(4)
            while len(received_data) < 4:
                chunk = new_socket.recv(4 - len(received_data))
                if not chunk:
                    raise Exception("Connection closed while receiving filename length")
                received_data += chunk

            # Get filename
            message_length = struct.unpack("<I", received_data)[0]
            message = new_socket.recv(message_length).decode('utf-8')
            filename = os.path.join(source, "receive_" + message)
            
            # Get file size
            filesize = self.receive_file_size(new_socket)
            print(f"Receiving file: {filename} ({filesize} bytes)")
            
            # Receive file data
            with open(filename, "wb") as f:
                received_bytes = 0
                while received_bytes < filesize:
                    chunk = new_socket.recv(min(8192, filesize - received_bytes))
                    if not chunk:
                        break
                    f.write(chunk)
                    received_bytes += len(chunk)
                    print(f"Progress: {received_bytes}/{filesize} bytes ({(received_bytes/filesize)*100:.1f}%)")
            
            print(f"File received successfully: {filename}")
            
        except Exception as e:
            print(f"Error receiving file: {str(e)}")
            mess.showerror(title="Error", message=f"Failed to receive file: {str(e)}")
        finally:
            if 'new_socket' in locals():
                new_socket.close()
            if 'new_server' in locals():
                new_server.close()
    
    def recv_control(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #using UDP to receive mouse data
        self.server_socket.bind((self.my_host,self.port))
        hold = 0
        header = struct.calcsize('Q')
        data = b''
        while self.running:
            try:
                while len(data) < header:
                    data += self.server_socket.recv(1024)
                mess_size = struct.unpack('Q',data[:header])[0]
                data = data[header:]
                while len(data) < mess_size:
                    data += self.server_socket.recv(1024)
                resquest = data[:mess_size]
                data = data[mess_size:]
                key = pickle.loads(resquest)
                if(key['type_data'] == 'mouse'):
                    if(key['data']!=""):
                        datagram = key['data']
                        datagram = datagram.split()
                        if(len(datagram) == 3):
                            if(datagram[0] == 'mouse_move'):
                                x,y = int(int(datagram[1])*self.width/self.x_res), int(int(datagram[2])*self.height/self.y_res)
                                win32api.SetCursorPos((x,y))
                            elif(datagram[0] == 'left_click_and_hold' and hold==0):
                                pyautogui.mouseDown()
                                hold = 1
                            elif(datagram[0] == 'left_release' and hold ==1):
                                pyautogui.mouseUp()
                                hold=0
                            elif(datagram[0] == 'left_double_click'):
                                pyautogui.doubleClick()
                            elif(datagram[0] == 'right_click'):
                                pyautogui.rightClick()
                            elif(datagram[0] == 'middle_click'):
                                pyautogui.middleClick()
                        elif(len(datagram) == 2):
                            if(datagram[0] == 'scroll' and datagram[1] == 'up'):
                                self.mouse.scroll(0,1)
                            elif(datagram[0] == 'scroll' and datagram[1] == 'down'):
                                self.mouse.scroll(0,-1)    
                
                elif(key['type_data'] == 'sendfile'):
                    recvfile_thread= threading.Thread(target=self.receive_file)
                    recvfile_thread.start()
                    #recvfile_thread.daemon = True
                    #recvfile_thread.join()
                    
                
                else:
                    self.get_keyboard(key)
            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError,TimeoutError) as e:
                self.handle_error(e)
                break
        self.server_socket.close()
    

    def start_server(self):
        self.running=True 
        self.receive_client_ip()
        if self.running:
            print(self.host)
            self.recv_size_window ()
            print(self.width, self.height)
            t2= threading.Thread(target = self.recv_control) #get mouse
            if(self.is_auto_blur==True):
                t1= threading.Thread(target = self.send_display) #send screen
            else : 
                t1= threading.Thread(target = self.send_display2) #send screen
            t1.daemon = True
            t2.daemon = True
            t2.start()
            t1.start()
            t2.join()
            t1.join()
# if __name__ == "__main__":
#     server_run = Server()
#     server_run.start_server()