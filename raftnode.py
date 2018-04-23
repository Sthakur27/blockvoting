#raft implementation
import random
import time
import socketserver
import threading
import json
import socket

        
class Node:
    def __init__(self,contact=None,HOST="localhost",PORT=9999):
        self.host=HOST
        self.port=PORT      
        self.term=0
        self.leader=self
        self.contacts=[]
        self.send_q=[]

        
        
        print('hello?')
        
        if contact is not None:
            contact_host,contact_port=contact.split(':')
            self.contacts.append([contact_host,int(contact_port),time.time()])
            self.send(self.contacts[0],'5')

            
        self.time_out=3+4*random.random()
        self.vote=None
        self.status='follower'
        self.logs=[]
        self.last_msg=time.time()
        self.cmd=''


       

        self.main_threads=[]

        send_msg_t=threading.Thread(target=self.send_msg)
        recieve_msg_t=threading.Thread(target=self.recieve_msg)
        #camp_t=threading.Thread(target=self.campaign)
        #rec_msg_t=threading.Thread(target=self.recieve_msg)
        #heart_beat_t=threading.Thread(target=self.heart_beat)
        #recieve_cmd_t=threading.Thread(target=self.recieve_cmd)


        self.main_threads.append(send_msg_t)
        self.main_threads.append(recieve_msg_t)
        #self.main_threads.append(camp_t)
        #self.main_threads.append(rec_msg_t)
        #self.main_threads.append(heart_beat_t)
        #self.main_threads.append(recieve_cmd_t)
        
        for t in self.main_threads:
            t.start()

    class MyTCPHandler(socketserver.BaseRequestHandler):
        """
        The request handler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
        """
        def __init__(self,node):
            self.node=node

        def handle(self):
            data = str(self.request.recv(1024).strip(),"utf-8")
            print("{} wrote: {}".format(self.client_address[0],data))
            if data[0]=='1':
                self.recieve_msg(data)
            elif data[0]=='2':
                self.vote_and_tally()
            elif data[0]=='3':
                #for leader
                self.recieve_cmd(data)
            elif data[0]=='4':
                #for connecting with new nodes
                self.connect(self.client_address)
            elif data[0]=='5':
                #for new node's first connection
                node.first_connect(self.client_address)
            else:
                #acknowledgment or error
                print(data)
                
    def recieve_msg(self):
        #socket set up
        with socketserver.TCPServer((self.host, self.port), Node.MyTCPHandler) as server:
            server.serve_forever()
                
    def send(self,contact,msg):
        self.send_q.append([contact[0],contact[1],msg])
        
    def send_msg(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            while True:
                #print('checking if msgs to be send')
                if len(self.send_q)>0:
                    # Connect to server and send data
                    sock.connect((self.send_q[0][0], self.send_q[0][1]))
                    sock.sendall(bytes(self.send_q[0][2] + "\n", "utf-8"))
                    del(self.send_q[0])

    def connect(self,address):
        contact=address
        contact.append(time.time())
        self.contacts.append(contact)
        print('appended contact {}'.format(contact))
        self.send_q.append([contact[0],contact[1],'ack'])

    def first_connect(self,address):
        print("address {}".format(address))
        contact=address
        self.contacts.append(contact)
        
        print('returning contacts {}'.format(self.contacts))
    
    def campaign(self):
        while True:
            if self.status=='follower' and time.time()-self.last_msg>=self.time_out:
                print('campaigning')
                self.status='candidate'
                self.term=self.term+1
                self.vote=self
                votes=len(self.contacts)/2
                for contact in self.contacts:
                    if contact.term>=self.term:
                        self.status='follower'
                        self.leader=contact.leader
                        self.vote=None
                        return
                    if contact.vote==None:
                        contact.vote=self
                        votes-=1
                if votes<=0:
                    self.status='leader'
                    print('campaign won')
                    self.vote=None
                else:
                    self.vote=None
                    self.status='follower'
                    self.last_msg=time.time()
                
        
    def recieve_cmd(self,data):
        send_msgs_t=threading.Thread(target=self.send_all,args=(data,))
        send_msgs_t.start()
        print("send msg '{}' to followers".format(data))


    def send_all(self,msg):
        for follower in self.contacts:
            self.seng_msg(msg,follower)
        self.last_msg=time.time()




    def heart_beat(self):
        
        while True:
            if self.status=='leader':
                time.sleep(0.5)
                if time.time()-self.last_msg>2:
                    send_all('')
                    self.last_msg=time.time()



a=Node()
print('a created')
b=Node(PORT=9998,contact="localhost:9999")

    

    
    
