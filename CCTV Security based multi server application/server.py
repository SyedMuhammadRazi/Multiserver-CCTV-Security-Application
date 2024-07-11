import socket
import cv2
import pickle
import struct
import threading
import tkinter as tk
from tkinter import messagebox  # Import messagebox submodule separately

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
print('HOST IP:', host_ip)
port = 9999
socket_address = (host_ip, port)
server_socket.bind(socket_address)
server_socket.listen()
print("Listening at", socket_address)

connected_clients = {}  # Dictionary to store connected clients

def show_client(addr, client_socket, thread_num):
    try:
        print('CLIENT {} CONNECTED!'.format(addr))
        if client_socket:
            data = b""
            payload_size = struct.calcsize("Q")
            while True:
                while len(data) < payload_size:
                    packet = client_socket.recv(4 * 1024)  # 4K
                    if not packet:
                        break
                    data += packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q", packed_msg_size)[0]

                while len(data) < msg_size:
                    data += client_socket.recv(4 * 1024)
                frame_data = data[:msg_size]
                data = data[msg_size:]
                
                # Process video frames as usual
                frame = pickle.loads(frame_data)
                cv2.imshow(f"FROM {addr}", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            
            client_socket.close()
    except Exception as e:
        print(f"CLIENT {addr} DISCONNECTED")
        pass

def terminate_client(client_socket):
    try:
        client_socket.sendall(b"terminate")  # Send termination message
        client_socket.close()  # Close the client's socket
    except Exception as e:
        print("Error terminating client:", e)

def update_clients_list():
    clients_listbox.delete(0, tk.END)
    for transaction_id in connected_clients.keys():
        clients_listbox.insert(tk.END, transaction_id)

def accept_clients():
    while True:
        client_socket, addr = server_socket.accept()
        if len(connected_clients) >= 2:
            oldest_client, oldest_thread = connected_clients.popitem()
            terminate_client(oldest_client)
            print(f"Client {oldest_thread[0]} terminated due to queue limit reached.")
        
        transaction_id = addr[1]  # Use port number as transaction ID
        connected_clients[transaction_id] = (client_socket, addr) 
        thread = threading.Thread(target=show_client, args=(addr, client_socket, len(connected_clients)))
        thread.start()
        update_clients_list()
        print("TOTAL CLIENTS ", len(connected_clients))
        print(connected_clients)

def disconnect_by_transaction_id():
    transaction_id = transaction_id_entry.get()
    client_data = connected_clients.get(transaction_id)
    print(client_data)
    print(transaction_id)
    if client_data:
        client_socket, _ = client_data
        terminate_client(client_socket)
        del connected_clients[transaction_id]
        update_clients_list()
    else:
        messagebox.showerror("Error", f"Client not found for transaction ID: {transaction_id}")  # Use messagebox submodule

root = tk.Tk()
root.title("Connected Clients")
root.geometry("400x200")

clients_label = tk.Label(root, text="Connected Clients:")
clients_label.pack()

clients_listbox = tk.Listbox(root)
clients_listbox.pack()

# Input field for transaction ID
transaction_id_label = tk.Label(root, text="Enter Transaction ID:")
transaction_id_label.pack()

transaction_id_entry = tk.Entry(root)
transaction_id_entry.pack()

# Button to disconnect by transaction ID
disconnect_by_transaction_id_button = tk.Button(root, text="Disconnect by Transaction ID", command=disconnect_by_transaction_id)
disconnect_by_transaction_id_button.pack()

accept_thread = threading.Thread(target=accept_clients)
accept_thread.start()

root.mainloop()
