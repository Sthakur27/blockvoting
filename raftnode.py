#raft implementation
import random
class Node:
    def __init__(self,contact=None):
        self.term=0
        if contact is not None:
            self.contacts=contact.contacts
            self.contacts.append(contact)
            self.term=contact.term
        self.timeout=3+4*random.random()
        self.vote=None
