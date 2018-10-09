#client.py
from socket import *
import getpass
from multiprocessing import Process
from time import sleep
import sys


class Murder_Client(object):
    def __init__(self,ADDR):
        self.s = socket(AF_INET,SOCK_STREAM)
        self.s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)          
        self.ADDR = ADDR   

    def MainServer(self):
        
        self.s.connect((self.ADDR))
        # add a new process to send message       
        
        print("1 注册：")
        print("2 登陆：")
        print("3 退出：")       
        while True:
            num = int(input("num:"))        
            if num == 1:
                self.do_register(self.s)
                continue
            elif num == 2 :
                self.do_login(self.s)
                continue
            elif num ==  3:
                self.s.send(b"Q^Q^Q")
                print("谢谢使用")
                sys.exit()

    def do_register(self,s):
        print("register")
        data = self.input_key('R')        
        if data =="Y":            
            print("Registtered successfully")
            self.do_chat(s)
        else:
            print("The username already exists")
        
            

    def do_login(self,s):
        print("Login ...")
        data = self.input_key('L')
        if data =="Y":
            print("Login successfully")
            self.do_chat(s)
        elif data == "UN":
            print("Incorrect username,please re-enter")
        else:
            print("Incorrect password,please re-enter")

    def input_key(self,z):
        while True:
            msg = input("user:")
            passwd = getpass.getpass(stream=None)
            if z =='R':
                passwd1 = getpass.getpass(stream=None)
                if passwd != passwd:
                    print("The two passwords do not match,re-enter")       
                    continue
            msg_send = z+"^"+msg+"^"+passwd
            self.s.send(msg_send.encode())
            print(msg_send,"msg_send")
            data = self.s.recv(128).decode()
            print(data,"input_key")
            return data

    def do_chat(self,s): 
        # create child process to send msg
        # parent process receive msg from server
        print("in chat")
        p = Process(target = self.to_send,args=(s,))
        p.start()
        sleep(0.2)
        print("father process")
        while True:              
            msg = input("消息：")            
            msg = 'C'+'^'+msg
            s.send(msg.encode())
            if msg =="C^exit":                
                sleep(0.1)
                p.join()
                s.close()        
                sys.exit()

    def to_send(self,s):
        print("this is child process")
        while True:            
            data = s.recv(4096).decode()
            print("\n"+data+"\n消息:",end="")            
            if data == "^^exit":
                print('child EXIT')                
                sys.exit()
     
        
        
        
        

if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 8000
    ADDR = (HOST,PORT)
    m = Murder_Client(ADDR)
    m.MainServer()
    