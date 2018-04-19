from hashlib import sha512

class Block:    
    hashpointer=None   #assigned in form of (pointer,hash) of previous block   
    data=list()    
    block_num=0
    
    #input is string x
    #output is 512 bit hash
    @staticmethod
    def hash(x):
        return sha512(str.encode(x)).hexdigest()

    #takes an object and returns hash of its contents
    @staticmethod
    def hash_obj(x):
        return Block.hash(str(vars(x)))
    
    def __init__(self,info,previous_block):
        if previous_block is not None:
            self.hashpointer=(previous_block,Block.hash_obj(previous_block))
            self.block_num=previous_block.block_num+1
        if not isinstance(info,list):
            info=[info]
        self.data=info

    #returns the previous block it points to if that block's hash is the same as the one recorded
    def getPrevious(self):
        if self.hashpointer is None:
            return None
        if Block.hash_obj(self.hashpointer[0])==self.hashpointer[1]:
            return self.hashpointer[0]
        else:
            #print('chain tampered!')
            return None

    #boolean, returns True if this block is genesis block     
    def isGenesis(self):
        return (self.hashpointer is None)

    #returns hash of itself
    def getHash(self):
        return Block.hash_obj(self)

    #prints out contents in readable? format
    def __str__(self):
        response='\nBlock number {}\n'.format(self.block_num)
        if self.hashpointer is not None:
           response+='Pointing to Block {} with hash:\n'.format(self.hashpointer[0].block_num)
           response+=self.hashpointer[1]
        response+='\n\nContaining Following Data: \n'
        response+=str(self.data)+'\n'
        return response

class BlockChain:
    name=None
    genesisHash=None
    head=None
    size=1

    #initializes by creating a genesis block (hardcoded)
    def __init__(self,chain_name=None):
        self.name=chain_name
        genesis=Block(['Genesis'],None) #genesis block
        self.head=genesis
        self.genesisHash=Block.hash_obj(genesis)

    #adds a new block to chain
    def addBlock(self,data):
        new_block=Block(data,self.head)
        self.head=new_block
        self.size+=1

    #returns block where param index == Block.block_num
    def getBlock(self,index):
        temp=self.head
        if index>=self.size or index<0:
            return None
        while temp.block_num!=index:
            temp=temp.getPrevious()
        return temp

    #starting at the head, tries to verify by traversing back to genesis block and verifying genesis block
    def verify(self):
        temp=self.head
        while not temp.isGenesis():
            temp=temp.getPrevious()
            if temp is None:
                return False
        return self.genesisHash==Block.hash_obj(temp)

    #returns human readable? format of contents
    def __str__(self):
        response='BlockChain'
        if self.name:
            response='BlockChain {}'.format(self.name)
        temp=self.head
        while not temp.isGenesis():
            response+=str(temp)
            temp=temp.getPrevious()
        response+='\nGenesis Block: \n'
        response+=str(temp)
        return response
    
class Test:
    def __init__(self,x):
        self.x=x

a=Test('red')
b=Block(a,None)
t1=b.getHash()
print(t1)
a.x='blue'
t2=b.getHash()
print(t2)
print(t1==t2)

'''
a=Block(['cat','dog'],None)
b=Block(['jelly','jello'],a)
c=Block(['red','blue','green'],b)
#b.data[0]='not jello'
#c.getPrevious()
print(a)
print(b)
print(c)
'''
'''a=BlockChain('Colors')
a.addBlock(['red'])
a.addBlock(['blu'])
a.addBlock(['green'])
a.addBlock(['cyan'])
#print(a)
print('verifying')
print(a.verify())
print("changing block #2's contents")
a.getBlock(2).data=['whoops']
print('verifying')
print(a.verify())'''

