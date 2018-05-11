from copy import deepcopy

class Edge:
    def __init__(self, name, n1, n2, edgeID):
        self.cand = True
        self.cut = False
        self.chain = name
        self.chain_pos = 0
        self.node1 = n1
        self.node2 = n2
        self.edgeID = edgeID
    
    def updateCand(self, cand, pos, ch):
        self.cand = cand
        self.chain = ch
        self.chain_pos = pos
    
    # n is the array of nodes from the board. After a string is cut, each node
    # in this edge loses a valency 
    def cutString(self,n):
        self.cut = True
        if(self.node1 != -1):
            n[self.node1] -= 1
        if(self.node2 != -1):
            n[self.node2] -= 1
        
    def updateChain(self, ch):
        self.chain = ch
        
    def printEdge(self):
        print(self.cand, self.cut, self.chain, self.chain_pos, self.node1, self.node2)
    
