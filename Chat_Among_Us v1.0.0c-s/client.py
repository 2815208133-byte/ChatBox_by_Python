import socket
import threading # 多线程模块
import time

def receive_message(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                print("[连接断开]与服务器断开连接") #之后加个as e
                break
            
            print(data.decode('utf-8'))
        except:
            break


client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # 创建ipv4 tcp的socket
addr_input = input("输入你要连接的ip与端口号 格式:HOST:PORT \n(按enter使用默认127.0.0.1:9178)") or "127.0.0.1:9178"
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
print("已退出聊天室，3秒后自动关闭窗口")

time.sleep(2)
print("bye")
time.sleep(1)  