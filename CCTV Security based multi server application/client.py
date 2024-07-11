import socket
import cv2
import pickle
import struct
import sys
import imutils
import tkinter as tk
import threading

camera = True
streaming = False  # Flag to track if stream is running
client_socket = None

if camera:
    vid = cv2.VideoCapture('sample.mp4')
    # vid = cv2.VideoCapture(0)
else:
    vid = cv2.VideoCapture('sample.mp4')

def connect_to_server():
    global client_socket
    if not client_socket:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_ip = '192.168.100.44'  # Replace this with your server's IP address
        port = 9999
        try:
            client_socket.connect((host_ip, port))
            return True
        except Exception as e:
            print("Error connecting to server:", e)
            return False
    return True

def start_stream():
    global streaming
    if not streaming:  # Check if stream is not already running
        if connect_to_server():  # Check if connected to server
            streaming = True
            threading.Thread(target=stream_video).start()  # Start streaming in a new thread
            
        else:
            sys.exit()

def stream_video():
    global streaming
    while vid.isOpened() and streaming:  # Check if streaming flag is True
        try:
            _, frame = vid.read()
            frame = imutils.resize(frame, width=380)
            serialized_frame = pickle.dumps(frame)
            message = struct.pack("Q", len(serialized_frame)) + serialized_frame
            client_socket.sendall(message)
        except:
            print('VIDEO FINISHED!')
            break

def stop_stream():
    global streaming
    if streaming:  # Check if stream is currently running
        streaming = False

def disconnect():
    global client_socket
    global streaming
    if client_socket:
        client_socket.close()
        client_socket = None  # Reset client_socket to allow reconnection
        streaming = False  # Reset streaming flag

# GUI
root = tk.Tk()
root.title("Cool Video Stream Controller")
root.geometry("300x200")  # Set initial window size
root.configure(bg="#2C3E50")  # Set background color

# Button styles
button_style = {"font": ("Arial", 12), "height": 2, "width": 15, "bg": "#3498DB", "fg": "white"}

start_button = tk.Button(root, text="Start Stream", command=start_stream, **button_style)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop Stream", command=stop_stream, **button_style)
stop_button.pack(pady=5)

disconnect_button = tk.Button(root, text="Disconnect", command=disconnect, **button_style)
disconnect_button.pack(pady=5)

root.mainloop()
