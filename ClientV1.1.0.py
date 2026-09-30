import customtkinter as ctk
import socket
import threading # 多线程模块
import time

def add_message_user(chat_box,text):
    print("add_messager被调用:", text)
    chat_box.configure(state="normal")
    chat_box.insert(ctk.END, f"{text}\n")
    chat_box.configure(state="disabled")

def switch_page(target,pagelist):
    for page in pagelist:
        page.pack_forget()
    target.pack(fill="both", expand=True)

def receive_message(client_socket,chat_box):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("[连接断开]与服务器断开连接") #之后加个as e
                break
            chat_box.after(0, lambda d=data: add_message_user(chat_box,d.decode("utf-8")) )
        except Exception as e:
            print("接收出错:", e)
            break

def log_in(entryH,entryP,entryN,sock):
    HOST = entryH.get()
    PORT = int(entryP.get())
    nickname = entryN.get()
    if HOST and PORT:
        try:
            print("准备连接服务端")
            sock.connect((HOST,PORT))
            print("连接成功")
            sock.sendall(nickname.encode("utf-8"))
            entryH.delete(0,ctk.END)
            entryP.delete(0,ctk.END)
            entryN.delete(0,ctk.END)
        except ConnectionRefusedError:
            print("无法连接到服务器：连接被拒绝")
            return
    
def send_message(sock, entry):
    """
    读取输入框内容并发送。
    发送成功后清空输入框，方便输入下一条。
    """
    message = entry.get()                                   # 取出输入框里的文字
    print("准备发送:", message)
    if message:                                             # 如果非空才发送，防止发空消息
        try:        
            sock.sendall(message.encode('utf-8'))                       # 编译并发送
            print("发送成功")
            entry.delete(0, ctk.END)                         # 如果非空才发送，防止发空消息
        except Exception as e:
            print(f"发送失败: {e}")
       
def start_ui():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # 创建 TCP socket(客户端)
    root = ctk.CTk()
    root.title("ChatAmongUsClient")
    page1 = ctk.CTkFrame(root)
    page2 = ctk.CTkFrame(root)
    lable1 = ctk.CTkLabel(page1, text="输入ip:")
    lable1.pack()
    entry1 = ctk.CTkEntry(page1, width=50)
    entry1.pack()
    lable2 = ctk.CTkLabel(page1, text="输入端口:")
    lable2.pack()
    entry2 = ctk.CTkEntry(page1, width=50)
    entry2.pack()
    lable3 = ctk.CTkLabel(page1,text="输入昵称")
    lable3.pack()
    entry3 = ctk.CTkEntry(page1,width=50)
    entry3.pack()
    send_address_btn = ctk.CTkButton(page1, text="登录", command=lambda:(log_in(entry1,entry2,entry3,client),switch_page(page2,pagelist),threading.Thread(target=receive_message, args=(client,chat_box), daemon=True).start()))
    send_address_btn.pack()
    
    chat_box = ctk.CTkTextbox(page2, state="disabled")
    chat_box.pack()
    ctk.CTkLabel(page2, text="输入消息:").pack()
    entry = ctk.CTkEntry(page2, width=50)
    entry.pack()
    entry.bind("<Return>", lambda event: send_message(client, entry))
    send_btn = ctk.CTkButton(page2, text="发送", command=lambda: send_message(client, entry))
    send_btn.pack()

    pagelist = [page1,page2]
    page1.pack(fill="both", expand=True)

    root.mainloop()                

if __name__ == "__main__":
    start_ui()


"""
HOST,PORT =  addr_input.split(":")
addr=str(HOST),int(PORT)  #addr: ( , )元组 
client.connect(addr)

nickname = input("输入名称（按回车默认随机名称）") or "sb"   # nicknamesend
client.sendall(nickname.encode('utf-8'))

threading.Thread(target=receive_message, args=(client,), daemon=True).start()  # 给receive_message多开一个线程

print("成功进入通讯室！(/quit推出)")
while True:
    msg = input()

    # if not msg:
    #     continue

    client.sendall(msg.encode('utf-8'))
    if msg == "/quit":
        break

client.close()
print("已退出聊天室,3秒后自动关闭窗口")

time.sleep(2)
print("bye")
time.sleep(1)  
"""