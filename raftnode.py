#raft implementation
import random
import time
import socketserver
import threading
class Node:
    def __init__(self,contact=None):
        self.term=0
        self.leader=self
        self.contacts=[]
        if contact is not None:
            self.contacts=contact.contacts
            for other_server in self.contacts:
                #give contact info to others
                pass
            self.contacts.append(contact)
            self.term=contact.term
            self.leader=contact.leader
        self.time_out=3+4*random.random()
        self.vote=None
        self.status='follower'
        self.logs=[]
        self.last_msg=time.time()
        self.cmd=''


        self.main_threads=[]

        
        camp_t=threading.Thread(target=self.campaign)
        rec_msg_t=threading.Thread(target=self.recieve_msg)
        heart_beat_t=threading.Thread(target=self.heart_beat)
        recieve_cmd_t=threading.Thread(target=self.recieve_cmd)

        self.main_threads.append(camp_t)
        self.main_threads.append(rec_msg_t)
        self.main_threads.append(heart_beat_t)
        self.main_threads.append(recieve_cmd_t)
        
        for t in self.main_threads:
            t.start()
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
                
    def recieve_msg(self):
        while True:
            if self.status=='follower':
                #if sender term is lower than current term then tell new leader
                #self.last_msg=time.time()
                time.sleep(0.5)
                print("{} till campaign".format(self.time_out-(time.time()-self.last_msg)))
        
    def recieve_cmd(self):
        while True:
            if self.status=='leader':
                cmd='example'
                send_msgs_t=threading.Thread(target=self.send_all,args=(cmd,))
                send_msgs_t.start()
                time.sleep(0.5)
                print('am leader')


    def send_all(self,msg):
        for follower in self.contacts:
            self.seng_msg(msg,follower)
        self.last_msg=time.time()


    def seng_msg(self,msg,follower):
        return None

    def heart_beat(self):
        while True:
            if self.status=='leader':
                time.sleep(0.5)
                if time.time()-self.last_msg>2:
                    send_all('')
                    self.last_msg=time.time()



a=Node()

    

    
    
