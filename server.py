 #server.py
from socket import *
from select import *
from threading import Thread
from time import sleep
import sys
import os
import pdb

class Murder(object):
    def __init__(self,ADDR,file_name):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.s.bind(ADDR)        
        self.s.listen(10)
        self.file_name = file_name
        self.addr = ADDR
        
    # 主程序
    def MainServer(self):

        # get user info include username and passwd
        # 获取用户信息
        user_list = self.get_user_list(self.file_name)
        for key,item in user_list.items():
            print(key, item)

        # 获取用户名和套接字
        addr_list = {'admini':self.addr}      

        # set IO multiplexing(io 多路复用)
        rlist = [self.s]
        wlist = []
        elist = [self.s]
        BUFFER = 4096        
        print("waitint for connect")
        
        while True: 
            print("IO conplexing")           
            rl,wl,el = select(rlist, wlist, elist)            
            for i in rl:
                if i == self.s:
                    print("it's s")
                    c,addr = self.s.accept()
                    rlist.append(c)
                    print("connect successfully")
                else:
                    try:
                        data = i.recv(4096).decode()
                    except Exception as e:
                        i.close()
                        print(e)
                        continue
                    
                    # 判断消息归属注册、登陆还是退出
                    flag = data.split("^")[0]
                    if flag == "C" :
                        content = data.split("^")[1]
                        self.send_2_all(content,user_list,i,addr_list)
                    elif flag =="G":
                        self.send_2_player()
                    else:
                        sig = data.split("^")[0]
                        user = data.split("^")[1]
                        passwd = data.split("^")[2]
                        if sig == "R":                        
                            self.do_register(user,passwd,self.file_name,
                                             user_list,i,rlist,wlist,addr_list)
                        elif sig == "L":                        
                            self.do_login(user,passwd,user_list,i,
                                          rlist,wlist,addr_list)
                        elif sig == "Q" or "^":
                            i.send(b'^^exit')

                            c.close()           
            for i in wl:
                print("it's c")
                print(i)
                data = i.recv(4096).decode()
                print("sd")
                print(data,'in wlist')                
                sig = data.split("^")[0]
                content = data.split("^")[1]
                if sig =="C":
                    self.send_2_all(nt,user_list,c,addr_list)
                elif sig =="G":
                    self.send_2_player()

                # sig_w is begin Game
                elif sig =="BG":
                    c.send(b"ok")
                    print("ok is sended")
       
                    

    # 注册
    def do_register(self,user,passwd,file_name,user_list,c,
                    rlist,wlist,addr_list):
        print(user,passwd)
        if user not in user_list:
            user_list[user] = passwd
            addr_list[user] = c
            c.send(b"Y")
            try:
                with open(file_name,'w') as f:
                    for key,item in user_list.items():                        
                        data = key+' '+ item+'\n'                    
                        f.write(data)                    
            except Exception as e:
                print(e,"raise a error")
        else:
            c.send(b"N")
            rlist.append(c)

    # 登陆
    def do_login(self,user,passwd,user_list,c,
                 rlist,wlist,addr_list):            
        if user in user_list:
            if passwd == user_list.get(user):
                addr_list[user] = c
                c.send(b'Y')                
                print('Login successfully')
                
            else:
                c.send(b"PN")
                rlist.append(c)
        else:
            c.send(b"UN")
            rlist.append(c)

    # 接收客户端信息发送给其他用户
    def send_2_all(self,data,user_list,c,addr_list):        
        error_list = []   
        for m,n in addr_list.items():
            if n == c:
                user = m
                break
        print(data)
        data = user+":\n"+data
        
        for key in addr_list.keys():            
            print(key,"in for ")
            if key != user and key != 'admini':
                try:
                    print(key,'in try')
                    addr_list[key].send(data.encode())                    
                except Exception:
                    print('raise a exception in send to all')
                    error_list.append(key)
                    addr_list[key].close()
        # delete socket which pipe is broken
        # 删除连接断开的套接字
        for i in error_list:
            del addr_list[i]

        
            
            
     
    # 此方法用以发送信息给游戏参与者，也可用采用其他方法
    def send_2_player(self):        
        pass

    # 获取返回用户信息列表
    def get_user_list(self,file_name):
        # create a list to content username and assword
        user_list = {}
        with open(file_name) as f:        
            while True:
                for info in f:                    
                    info = info[:-1]
                    info = info.split(" ")                
                    user_list[info[0]] = info[1]
                    continue                
                return user_list

    # 管理员喊话功能
    def admini_send(self):
        global addr_list
        while True:
            # add conditons of send
            if True:
                msg = input("msg to send>>>")
                for key,item in addr_list.items():
                    if key != "admini":
                        try:
                            addr_list[1].send(msg.decode())                
                        except:
                            del addr_list[key]
                            continue
            
      

if __name__ == "__main__":
    # if len(sys.argv) < 3:
    # 	print("请输入正确格式的HOST和PORT")
    # 	sys.exit()
    # HOST = sys.argv[1]
    # PORT = sys.argv[2]
    HOST = "127.0.0.1"
    PORT = 8000
    ADDR = (HOST,PORT)    
    file_name = r"F:\project\user_info.txt.txt"
    m = Murder(ADDR,file_name)
    m.MainServer()
