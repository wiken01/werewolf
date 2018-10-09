 #server.py
from socket import *
from select import *
from threading import Thread
from time import sleep
import requests
import sys,os



class Murder(object):
    def __init__(self,ADDR,file_name,R):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
        self.s.bind(ADDR)        
        self.s.listen(10)
        self.file_name = file_name
        self.addr = ADDR
        self.R = R
        
    # 主程序
    def MainServer(self):

        '''用户信息存储在数据库，包括
        id name password              
        '''
        user_list = self.get_user_list(self.file_name)
        for key,item in user_list.items():
            print(key, item)

        # 获取用户名和套接字
        addr_list = {'admini':self.addr}      
        # robot 标志位        

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
                        rlist.remove(i)
                        print(e)
                        continue
                    
                    # 判断消息归属注册、登陆还是退出
                    flag = data.split("^")[0]                    
                    if flag == "C" :
                        content = data.split("^")[1]
                        self.send_2_all(content,user_list,i,addr_list)
                        if data == "C^exit":
                            i.send(b"^^exit")
                            sleep(0.1)
                            i.close()
                            rlist.remove(i)
                    elif flag =="G":
                        self.send_2_player()
                    elif data =="":                        
                        i.close()
                        rlist.remove(i) 
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
                            i.close()
                            rlist.remove(i)
         
                    

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
        
        # data for ai_robot  
        msg = data      
        data = user+":\n"+data
        
        for key in addr_list.keys():
            if key != user and key != 'admini':
                try:                    
                    addr_list[key].send(data.encode())                    
                except Exception:
                    print('raise a exception in send to all')
                    error_list.append(key)
                    addr_list[key].close()
        self.ai_robot(msg,addr_list,error_list)

        # delete socket which pipe is broken
        # 删除连接断开的套接字
        for i in error_list:
            del addr_list[i]

    # add robot module 
    def ai_robot(self,msg,addr_list,error_list):
        # set status of robot        
        if msg =="hello robot":
            self.R = 1            
        elif msg =="bye robot":
            self.R = 0
        if self.R:                    
            api_url = "http://www.tuling123.com/openapi/api"
            data = {
                'key':'cfa3da11ea2245ff9775de478a2b84de',
                'info':msg,
                'userid':"wiken"            
                    }
            # send data to tuling 
            r = requests.post(api_url,data=data).json()
            # get response from tuling
            r_data = r.get("text") 
            # set robot name                               
            r_data = "ai_robot"+":\n"+r_data

            for key in addr_list.keys():
                if key != 'admini': 
                    # send msg to client
                    try:                    
                        addr_list[key].send(r_dat.encode())                    
                    except Exception:
                        print('raise a exception in robot send to all')
                        error_list.append(key)
                        addr_list[key].close()            
     
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
    file_name = r"./user_info.txt"    
    m = Murder(ADDR,file_name,R)
    m.MainServer()
