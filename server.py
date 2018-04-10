import socketserver
from blockchain import Block,BlockChain
import _thread
bchain=BlockChain('Votes')
tally=[0]*10
class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        votes=str(self.data, "utf-8").split(',')
        bchain.addBlock(votes)
        for vote in votes:
            temp=int(vote.split(':')[1])
            if temp<10 and temp>=0:
                tally[temp]+=1
        self.request.sendall(bytes('current tally: {}'.format(str(tally)),"utf-8"))
        
def listen():
    HOST, PORT = "localhost", 9999
    # Create the server, binding to localhost on port 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        for i in range(0,7):
            server.handle_request()
        print(bchain)
        print(tally)
        print(max(tally))
        #server.serve_forever()

listen()
#_thread.start_new_thread(listen,())
