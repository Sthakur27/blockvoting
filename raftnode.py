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
            self.send([contact_host,int(contact_port)],'LS',[self.host,self.port])
            self.status='follower'
            self.leader=None
        else:
            self.leader=[self.host,self.port,time.time()]
            self.contacts=[[self.host,self.port,time.time()]]
            self.status='leader'

            
        self.time_out=3+4*random.random()
        self.vote=None      
        self.logs=[]
        self.last_msg=time.time()
        self.cmd=''


       

        self.main_threads=[]

        send_msg_t=threading.Thread(target=self.send_msg)
        recieve_msg_t=threading.Thread(target=self.recieve_msg)
        idle_time_out_t=threading.Thread(target=self.idle_time_out)


        self.main_threads.append(send_msg_t)
        self.main_threads.append(recieve_msg_t)
        self.main_threads.append(idle_time_out_t)
        
        for t in self.main_threads:
            t.start()

    class MyTCPHandler(socketserver.BaseRequestHandler):
        """
        The request handler class for  server.

        It is instantiated once per connection to the server
        """

        def handle(self):
            data_and_label = str(self.request.recv(1024).strip(),"utf-8")
            label=data_and_label[:2]
            data=data_and_label[2:]
            #print("\nrecieving a msg")
            #print("{}:{} wrote: {}".format(self.client_address[0],self.client_address[1],data))
            if label=='HS':
                print("Recieved Heart Beat")
                self.last_msg=time.time()
                
            #leader info recieve/send
            elif label=='LS':
                data=json.loads(data)
                self.node.send(data,'LR',self.node.leader)
                
            elif label=='LR':
                #new node receiving leader info from follower
                data=json.loads(data)
                self.node.leader=data
                self.node.send(self.node.leader,'AS',[self.node.host,self.node.port])
                
            elif label=='AS':
                data=json.loads(data)
                #leader recieving a rqst from new node to be added to network
                self.node.add_contact(data)
                self.node.send_all('AR',self.node.contacts)

            #all contacts recieve
            elif label=='AR':
                #for recieving multiple contact cards
                data=json.loads(data)
                print('updating contacts')
                self.node.contacts=data
                print("My contacts: {}".format(self.node.contacts))
                
            else:
                pass
                
    def recieve_msg(self):
        #socket set up
        with socketserver.TCPServer((self.host, self.port), Node.MyTCPHandler) as server:
            server.RequestHandlerClass.node=self
            server.serve_forever()
                
    def send(self,contact,label,msg):
        if len(label)==2:
            self.send_q.append([contact[0],contact[1],label+json.dumps(msg)])
        
    def send_msg(self):
        while True:
            if len(self.send_q)>0:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                        # Connect to server and send data
                        #print('\nsending {} to {}:{}'.format(self.send_q[0][2],self.send_q[0][0], self.send_q[0][1]))
                        sock.connect((self.send_q[0][0], self.send_q[0][1]))
                        sock.sendall(bytes(self.send_q[0][2] + "\n", "utf-8"))
                except:
                    pass
                del(self.send_q[0])
                
    #for leader
    def add_contact(self,address):
        host,port=address
        unique=True
        for i in range(0,len(self.contacts)):
            if self.contacts[i][0]==host and self.contacts[i][1]==port:
                self.contacts[i][2]=time.time()
                unique=False
        if(unique):
            self.contacts.append([host,port,time.time()])
    
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


    #for leader
    def send_all(self,label,msg):
        for follower in self.contacts:
            self.send(follower,label,msg)
        self.last_msg=time.time()




    def idle_time_out(self):
        
        while True:
            if self.status=='leader':
                #send heart beat
                time.sleep(2.5)
                print(self.contacts)
                self.send_all('HS','')
            elif self.status=='follower':
                #wait and campaign
                if time.time()-self.last_msg>=self.time_out:
                    #campaign
                    pass
                else:
                    time.sleep(1)

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

    

    
    
