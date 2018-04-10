import socket
import random
from time import sleep
import _thread
#import sys
ballots=[]

HOST, PORT = "localhost", 9999
def generate_data():
    social_sec_num=random.randint(10**8,10**9-1)
    vote=random.randint(0,9)
    return('{}:{}'.format(social_sec_num,vote))


def simulate():
    while True:
       sleep(0.05)
       ballots.append(generate_data())

def keep_sending():
    while True:
        sleep(0.05)
        #print('test')
        if(len(ballots)>70):
            data_block=','.join(ballots[0:70])
            send_data(data_block)
            del(ballots[0:70])
       

#data='987654321:01,'
# Create a socket (SOCK_STREAM means a TCP socket)
def send_data(block):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Connect to server and send data
        sock.connect((HOST, PORT))
        sock.sendall(bytes(block + "\n", "utf-8"))

        # Receive data from the server and shut down
        received = str(sock.recv(1024), "utf-8")
        #received = sock.recv(1024)
    #print("Sent:     {}".format(len(data)))
    print("Received: {}".format(received))

_thread.start_new_thread( simulate,() )
_thread.start_new_thread( keep_sending,() )
while 1:
    pass

