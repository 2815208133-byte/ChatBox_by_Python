import tkinter as tk
import socket
import threading

HOST_Sender = "frp-fun.com"
PORT_Sender = 39639
HOST_Receiver = "0.0.0.0"
PORT_Receiver = 39639

def btn_connect(s_sender):                              
    
    try:
        print("准备连接",HOST_Sender,PORT_Sender)
        s_sender.connect((HOST_Sender,PORT_Sender))
        print("连接成功")
    except ConnectionRefusedError:
        print("无法连接到服务器: 连接被拒绝")
        return
    

def send_message(sock, entry,chat_box):
    """
    读取输入框内容并发送。
    发送成功后清空输入框，方便输入下一条。
    """
    message = entry.get()                                   # 取出输入框里的文字
    print("准备发送:", message)
    if message:                                             # 如果非空才发送，防止发空消息
        try:        
            sock.sendall(message.encode('utf-8'))                       # 编译并发送
            chat_box.config(state="normal")
            chat_box.insert(tk.END, f"我:{message}\n")
            chat_box.config(state="disabled")
            print("发送成功")
            entry.delete(0, tk.END)                         # 如果非空才发送，防止发空消息
        except Exception as e:
            print(f"发送失败: {e}")

def add_message_sender(chat_box, text):
    print("add_message_sender 被调用:", text)
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"我:{text}\n")
    chat_box.config(state="disabled")

def add_message_receiver(chat_box, text):
    print("add_message_receiver 被调用:", text)
    chat_box.config(state="normal")
    chat_box.insert(tk.END, f"对面:{text}\n")
    chat_box.config(state="disabled")

def receive_data(conn, chat_box):
    while True:
        try:
            data = conn.recv(1024)
            print("收到原始数据:", data)
            if not data:                                     # 如果收到空 bytes，说明对方打完字了
                print("对方断开了")                                                        
                break
            chat_box.after(0, lambda d=data: add_message_receiver(chat_box,d.decode("utf-8")) )
            # lambda建立函数对象(包装)，after(0, func) 0毫秒后执行add_message_receiver，避免阻塞主线程
        except Exception as e:
            print("接收出错:", e)
            break

def wait_for_connection(s, chat_box):
    chat_box.after(0, lambda: add_message_sender(chat_box, "等待对面发送端连接..."))
    while True:
        conn, addr = s.accept()
        print("收到一个连接:", addr)
        chat_box.after(0, lambda: add_message_sender(chat_box, f"对面发送端 {addr} 已连接"))
        t = threading.Thread(target=receive_data, args=(conn, chat_box), daemon=True)
        t.start()

def start_ui():
    """
    启动接收端：先连接服务器，再创建界面。
    """
    s_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                           # 创建 TCP socket(接收端)
    s_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)                         # 允许端口重启后立刻复用
    s_receiver.bind((HOST_Receiver, PORT_Receiver))
    s_receiver.listen()   
    s_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 创建 TCP socket(发送端)
    root = tk.Tk()
    root.title("集合版聊天界面")
    
    chat_box = tk.Text(root, state="disabled")
    chat_box.pack()
        
    tk.Label(root, text="输入消息:").pack()
        
    entry = tk.Entry(root, width=50)
    entry.pack()
    entry.bind("<Return>", lambda event: send_message(s_sender, entry,chat_box))                       # 按回车键也发送
        
    send_btn = tk.Button(root, text="发送", command=lambda: send_message(s_sender, entry,chat_box))
    send_btn.pack()
    connect_btn = tk.Button(root,text="连接",command=lambda: btn_connect(s_sender))
    connect_btn.pack()
            
    threading.Thread(target=wait_for_connection, args=(s_receiver, chat_box), daemon=True).start()# 开始监听
    
    root.mainloop()

if __name__== "__main__":
    start_ui()                                                 
    
    