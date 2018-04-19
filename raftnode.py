#raft implementation
import random
import time
class Node:
    def __init__(self,contact=None):
        self.term=0
        self.leader=self
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

    def campaign():
        if time.time()-self.last_msg>=self.time_out:
            self.status='candidate'
            vote=self
            #ask for votes
            #etc
    def recieve_msg():
        self.last_msg=time.time()
        

    def send_all(msg):
        if self.status='leader':
            for follower in self.contacts:
                seng_msg(msg,follower)
            self.last_msg=time.time()
        else:
            return None

    def seng_msg(msg,follower):
        return None

    def heart_beat():
        while True:
            if time.time()-self.last_msg>2:
                send_all('')
    
    def listen():
        #for leader
        return None
