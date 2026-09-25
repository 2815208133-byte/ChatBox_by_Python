"""服务端程序
运行:终端中运行:python server.py
"""
import socket   #通信模块（套接字）
import threading #多线程
import sys #防报错
from datetime import datetime 

# 网络配置
HOST = '0.0.0.0'

PORT = 9178

# 用字典存储全局状态
clients = {}
clients_lock = threading.Lock() #限制字典的读取修改 同一时刻只能有一个线程 不能同时修改 排队修改


def get_current_time():
    return datetime.now().strftime("%H:%M:%S")

def broadcast(message: str, sender_socket=None): #
    """
    将一条信息广播给所有在线客户端
    sender_socket: 发送者的socket 


    """
    # if not message.endswith('\n'):
    #     message = message + '\n'

    '''用encode()打包把要发送的信息打包为二进制'''
    encoded_message = message.encode('utf-8')


    with clients_lock:  # 加锁，保证同一时刻只有一个线程操作 clients
        # 用 list(clients.keys()) 是为了防止在遍历时有客户端退出导致字典大小改变报错
        for client_socket in list(clients.keys()): 
            try:
                # 调用sendall()确保发送所有完整字节
                client_socket.sendall(encoded_message)
            except Exception as e:
                print(f"[{get_current_time()}]消息发送失败，可能是客户端异常断开:{e}")


def handle_client(client_socket, client_address):
    """
    - client_socket: 客户端的socket对象
    - client_address: 客户端的地址信息 (ip, port)

    当一个用户连接时，服务端给他单独开一个线程（这个函数）来处理这个用户的收发消息。
    """
    print(f"[{get_current_time()}][新连接] 来自IP: {client_address[0]} 端口：{client_address[1]}")
    nickname = "未知用户"

    try:
        # 约定：客户端连接成功后的第一条消息，是发送他自己的'昵称'
        nickname = client_socket.recv(1024).decode('utf-8').strip()
        # 接收昵称，并删除前后空格
        if not nickname:
            nickname = f"用户_{client_address[1]}"
        
        with clients_lock: #将用户加入到在线用户字典中(加锁保护)
            clients[client_socket] = nickname

        join_notice = f"[系统通知][{nickname}]加入了通讯室!(当前在线:{len(clients)}人)"
        print(f"[{get_current_time()}] {join_notice}")
        broadcast(f"[{get_current_time()}]{join_notice}")
        
        '''循环监听客户端消息,并广播'''
        while True:

            data = client_socket.recv(1024)
            # 等待client_socket这个“人”发的内容 存到data里

         
            if not data:
                break
            
            text= data.decode('utf-8').strip() # 解码用户发的正文


            if text == "/quit":
                break


            chat_msg = f"[{get_current_time()}] {nickname}:{text}"
            print(chat_msg) #方便控制台排查
            broadcast(chat_msg)
        
    except ConnectionResetError:
        
        print(f"[{get_current_time()}][断开连接] {nickname} 强制断开了连接")
    except Exception as e:
        print(f"[{get_current_time()}][发生异常] {nickname} 通信出错:{e}")
    finally: #清理与收尾 函数结束时触发finally
        with clients_lock:
            if client_socket in clients:
                del clients[client_socket]

        try:
            client_socket.close()
        except:
            pass

        #广播clients离开的消息
        leave_notice = f"[系统通知][{nickname}]离开了通讯室(当前在线：{len(clients)}人)"
        print(f"[{get_current_time()}]{leave_notice}")
        broadcast(f"[{get_current_time()}]{leave_notice}")    
    

def start_server():
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 创建socket
    # socket.AF_INET 代表使用 IPv4 协议族
    # socket.SOCK_STREAM 代表使用 TCP 协议

    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 设置端口可复用
    
    server_socket.bind((HOST,PORT))
    # 绑定IP和端口

    server_socket.listen(5)
    # 开始监听 默认5

    print("="* 60)
    print(f"通讯室服务端已启动成功")
    print(f"正在监听:{HOST}:{PORT}")
    print(f"本机测试请用 127.0.0.1，联机请用公网ip或同一局域网")
    print(f"tips:按Ctrl + C 可以停止该服务端")
    print("="*60)    
    
    try:
        while True:


            client_socket,client_address = server_socket.accept()


            thread = threading.Thread(
                target=handle_client,
                args=(client_socket, client_address),
                daemon=True
            )
            thread.start()
    
    except KeyboardInterrupt:

        print(f"\n\n[!]客户端正在关闭...")
    finally:
        #关闭主服务端 socket
        server_socket.close()
        print("[+]服务端安全已关闭seccessfully!")

if __name__=='__main__':
    start_server()