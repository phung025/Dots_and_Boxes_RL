from copy import deepcopy

class Chain:
    # e is the initial chain edge ID
    def __init__(self, e):
        self.chainEdges = list()
        self.candEdges = list()
        self.chainEdges.append(e)
        self.candEdges.append(e)
        self.chainID = e
        self.chain_type = 8
        self.length = 0
        self.unionTable = self.ut()
        
    def copy(self, ch):
        self.chainEdges = deepcopy(ch.chainEdges)
        self.candEdges = deepcopy(ch.candEdges)
        self.chainID = ch.chainID
        self.chain_type = ch.chain_type
        self.length = ch.length
        self.unionTable = self.ut()
        
    # be sure to call clear before updating candidate edges otherwise you will overwrite it the edge     
    def clear(self, edges):
        while len(self.candEdges) > 0:
            oldC = self.candEdges.pop()
            edges[oldC].updateCand(False, -1, self.chainID)
        self.chainEdges = list()
        self.candEdges = list()
        self.chain_type = -1
        self.length = -1
      
    # checks if element e is in chainEdges
    def contains(self, e):
        try:
            self.chainEdges.index(e)
            return True
        except ValueError:
            return False
    
    # c2 is some other chain
    # el is the edge list from the board
    def addEdges(self, c2, el):
        edges = c2.chainEdges
        for i in range(0, len(edges)):
            self.chainEdges.append(edges.pop(0))
            self.length += 1
        c2.clear(el)
        
    # appends e to end of chainEdges
    def appendEdge(self, e):
        self.chainEdges.append(e)
        self.length += 1
        
    # inserts edge ID e at i
    def insertEdge(self,e,i):
        self.chainEdges.insert(i,e)
        self.length += 1
        
    # e is an edge ID, -1 if not found
    def getIndex(self, e):
        try:
            i = self.chainEdges.index(e)
            return i
        except ValueError:
            return -1
    
    # this function is meant to be used to calculate the new length
    # after the chain has been modified
    def updateLength(self):
        cl = len(self.chainEdges)
        if self.chain_type == 12:
            self.length = cl
        else:
            self.length = cl - 1
            
            
    # updates the candidate edges based on whatever the current type is
    # e is the list of edges from the board
    # n is the list of nodes from the board
    def updateCandidates(self,e,n):
        c = 0
        while len(self.candEdges) > 0:
            oldC = self.candEdges.pop()
            e[oldC].updateCand(False, -1, self.chainID)
        if self.chain_type == 3 or self.chain_type == 7 or self.chain_type == 10:
            c = 1
        if self.chain_type == 2:
            edge = e[self.chainEdges[0]]
            if n[edge.node1] < 3 and n[edge.node2] < 3:
                e[self.chainEdges[0]].updateCand(True, 0, self.chainID)
                self.candEdges.append(self.chainEdges[0])
            else:
                e[self.chainEdges[self.length]].updateCand(True, 0, self.chainID)
                self.candEdges.append(self.chainEdges[self.length])
        else:
            while c >= 0:
                e[self.chainEdges[c]].updateCand(True, c, self.chainID)
                self.candEdges.append(self.chainEdges[c])
                c -= 1
            
    
    # pops off from this chain to c2 chainEdges until it hits index i
    # precondition: c2 is an empty list
    # note: the result of the edges in c2 will be reveresed from the original order
    def popOff(self, c2, i):
        while len(self.chainEdges) != i+1:
            c2.appendEdge(self.chainEdges.pop())
            self.length -= 1
        self.chainEdges.pop()
        self.updateLength()
        
    # sets the new type after a union with type
    def unionLookup(self, ctype):
        if self.chain_type < 4:
            t1 = self.chain_type - 1
        else:
            t1 = self.chain_type - 5
        if ctype < 4:
            t2 = ctype - 1
        else:
            t2 = ctype - 5
                        
        if t2 < t1:
            tmp = t2
            t2 = t1
            t1 = tmp
        self.chain_type = self.unionTable[t1][t2]
            
    
    # Checks what type the chain currently is
    # e is an edge (should be -1 if there is no edge to remove)
    # n is the list of node valencies
    # el is the edgelist from the board
    # isCl boolean for if the chain is type 12 (is circle loop)
    def evaluateChange(self, e, n, el, isCl):
        sc = 0 #square count
        if isCl == True:
            self.length -= 2
            if self.chainEdges[0] != e and self.chainEdges[-1] != e:
                self.shiftEdge(e)
            self.chainEdges.remove(e)
        elif e != -1:
            self.chainEdges.remove(e)
            self.length -= 1
        if self.length > 0:
            front = el[self.chainEdges[0]]
            back = el[self.chainEdges[self.length]]
            try:
                if n[front.node1] > 2 or n[front.node2] > 2:
                    sc += 1
            except ValueError:
                sc += 1
            try:
                if n[back.node1] > 2 or n[back.node2] > 2:
                    sc += 1
            except ValueError:
                sc += 1
        else:
            edge = el[self.chainEdges[0]]
            try: 
                if n[edge.node1] > 2:
                    sc += 1
                if n[edge.node2] > 2:
                    sc += 1
            except ValueError:
                sc += 1
        
        self.chainTable(self.length, sc)
        self.updateCandidates(el,n)

    # Shifts the edges until they are in a valid position for a new chain.
    # e: an edge that needs to be on the end of the chain
    def shiftEdge(self,e):
        while self.chainEdges[0] != e:
            for i in range (0, len(self.chainEdges)-1):
                tmp = self.chainEdges[i]
                self.chainEdges[i] = self.chainEdges[i+1]
                self.chainEdges[i+1] = tmp
    
    # does not work for 11b and 12 at the moment
    def chainTable(self, length, numSquares):
        if length > 3:
            length = 3
        if numSquares == 0:
            self.chain_type = {
                -1:-1,
                0 : 4,
                1 : 5,
                2 : 7,
                3 : 6
            }[length]
        elif numSquares == 1:
            self.chain_type = {
                -1:-1,
                0 : 1,
                1 : 3,
                2 : 2,
                3 : 2
            }[length]
        elif numSquares == 2:
            self.chain_type = {
                -1:-1,
                0 : 8,
                1 : 9,
                2 : 10,
                3 : 11
            }[length]
        else:
            self.chain_type = -1
            
    def ut(self):
        unionTable = [[0 for i in range(7)] for j in range(7)]
        unionTable[0][0] = 5
        unionTable[0][1] = 6
        unionTable[0][2] = 7
        unionTable[0][3] = 3
        unionTable[0][4] = 2
        unionTable[0][5] = 2
        unionTable[0][6] = 2
        unionTable[1][1] = 6
        unionTable[1][2] = 6
        unionTable[1][3] = 2
        unionTable[1][4] = 2
        unionTable[1][5] = 2
        unionTable[1][6] = 2
        unionTable[2][2] = 6
        unionTable[2][3] = 2
        unionTable[2][4] = 2
        unionTable[2][5] = 2
        unionTable[2][6] = 2
        unionTable[3][3] = 9
        unionTable[3][4] = 10
        unionTable[3][5] = 11
        unionTable[3][6] = 11
        unionTable[4][4] = 11
        unionTable[4][5] = 11
        unionTable[4][6] = 11
        unionTable[5][5] = 11
        unionTable[5][6] = 11
        unionTable[6][6] = 11
        return unionTable
