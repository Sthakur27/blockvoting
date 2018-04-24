#raft implementation
import random
import time
import socketserver
import threading
import json
import socket

        
class Node:
    def __init__(self,contact=None,HOST="localhost",PORT=9999,name=''):
        self.name=name
        self.host=HOST
        self.port=PORT      
        self.term=0
        self.contacts=[]
        self.send_q=[]

        
        
        print('\nnode {} instansiated on {}:{}\n'.format(self.name,self.host,self.port))
        
        if contact is not None:
            contact_host,contact_port=contact.split(':')
            self.contacts.append([contact_host,int(contact_port),time.time()])
            self.send(self.contacts[0],'5',[self.host,self.port])
            self.status='follower'
        else:
            self.leader=[self.host,self.port,time.time()]
            self.status='leader'

            
        self.time_out=3+4*random.random()
        self.vote=None      
        self.logs=[]
        self.last_msg=time.time()
        self.cmd=''


       

        self.main_threads=[]

        send_msg_t=threading.Thread(target=self.send_msg)
        recieve_msg_t=threading.Thread(target=self.recieve_msg)


        self.main_threads.append(send_msg_t)
        self.main_threads.append(recieve_msg_t)
        
        for t in self.main_threads:
            t.start()

    class MyTCPHandler(socketserver.BaseRequestHandler):
        """
        The request handler class for our server.

        It is instantiated once per connection to the server, and must
        override the handle() method to implement communication to the
        client.
        """

        def handle(self):
            data_and_label = str(self.request.recv(1024).strip(),"utf-8")
            print("Undecoded msg: {}".format(data_and_label))
            label=data_and_label[0]
            data=json.loads(data_and_label[1:])
            print("\nrecieving a msg".format(self.node.name))
            print("{}:{} wrote: {}".format(self.client_address[0],self.client_address[1],data))
            if label=='1':
                self.recieve_msg(data)
            elif label=='2':
                self.vote_and_tally()
            elif label=='3':
                #for leader
                self.recieve_cmd(data)
            elif label=='4':
                #for connecting with new nodes
                self.node.connect(data)
            elif label=='5':
                #for recieving new node's first connection
                self.node.first_connect(data)
            elif label=='6':
                #for recieving multiple contact cards
                print('added new contacts')
                print('contacting new contacts')
                print(data)
                for address in data:
                    self.node.send(address,'4',[self.node.host,self.node.port])
                self.node.leader=data[0]
                data=data[1:]
                if len(data)>0:
                    self.node.contacts=self.node.contacts+data
                print("Leader: {}".format(self.node.leader))
                print("My contacts: {}".format(self.node.contacts))
                
            else:
                #acknowledgment or error
                print(data)
                
    def recieve_msg(self):
        #socket set up
        with socketserver.TCPServer((self.host, self.port), Node.MyTCPHandler) as server:
            server.RequestHandlerClass.node=self
            server.serve_forever()
                
    def send(self,contact,label,msg):
        self.send_q.append([contact[0],contact[1],label+json.dumps(msg)])
        
    def send_msg(self):
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                #print('checking if msgs to be send')
                if len(self.send_q)>0:
                    # Connect to server and send data
                    print("Current send queue: {}".format(self.send_q))
                    print('\nsending a msg to {}:{}'.format(self.send_q[0][0], self.send_q[0][1]))
                    sock.connect((self.send_q[0][0], self.send_q[0][1]))
                    sock.sendall(bytes(self.send_q[0][2] + "\n", "utf-8"))
                    del(self.send_q[0])
    #for reciever
    def connect(self,contact):
        contact.append(time.time())
        self.contacts.append(contact)
        print('appended contact {}'.format(contact))
        self.send(contact,'A',[self.host,self.port,'contact acknowledged'])

    #for reciever
    def first_connect(self,address):
        print("recieving contact card:")
        #print("address {}".format(address))
        address.append(time.time())
        print(address)
        
        print('returning contacts {}'.format(self.contacts))
        self.send(address,'6',[self.leader]+self.contacts)
        
        print("Added new contact")
        self.contacts.append(address)
        return
    
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

'''
name=input('name?')
contact=input('contact?')
if contact == '':
    contact=None
else:
    contact='127.0.0.1:999'+contact
port=int('999'+input('Port?'))

mynode=Node(name=name,PORT=port,contact=contact)

'''

choice=int(input('node num'))
if choice<=1:
    mynode=Node(name=chr(96+choice),PORT=10000-choice,contact=None)
else:
    mynode=Node(name=chr(96+choice),PORT=10000-choice,contact='127.0.0.1:'+str(10001-choice))

    

    
    
