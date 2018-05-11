#######################################
# Dots and boxes state and environment
# Author: Andrew Miller
# Author: Dale Dowling
# Author: Nam Phung
# Date created: Jan 25, 2018
#######################################

import numpy as np

from Edge import Edge
from Chain import Chain

from copy import deepcopy

class DabBoard:


    '''
    Hash the DabBoard and return a string value represent the
    object. This function is used to classify different states
    '''
    def hash(self):

        c = [0] * 13

        # Get ID of all chain objects in chains
        for chain in self.chains:
            if chain.chain_type != -1:
                c[chain.chain_type] = c[chain.chain_type] + 1

        # Turn to a string
        return ''.join(map(str, c))

    '''
    Default constructor to create an empty board
    Arguments:
        + rows: number of coins in a row
        + columns: number of coins in a column
    '''
    def __init__(self, rows, columns):

        # Get arguments
        self.rows = rows
        self.columns = columns

        # Set initial scores of player 1, 2 = 0
        self.score1 = 0
        self.score2 = 0

        # Set current player to 1
        self.curr_player = 1

        # Numpy array holding the information about the valency of the nodes(coins)
        self.nodes = np.array([4]*((self.rows)*(self.columns)))

        # Numpy array of each edge. They are indexed from left to right starting from the top
        # The ID of a given edge is its index in the array
        self.num_edges = self.rows*self.columns + (self.rows + 1)*(self.columns + 1) - 1
        # the array
        self.edges = np.array([Edge(-1,-1,-1,-1)]*self.num_edges)

        # chains. uses num_edges because the number of edges is the max number of chains
        self.chains = np.array([Chain(-1)]*self.num_edges)

        num_col = self.columns + self.columns + 1 #the number of columns of edges
        num_edge_rows = self.rows + self.rows + 1 #the number of rows of edges
        cur_edge = 0
        ix = 0 #horizontal row count
        iy = 0 #vertical row count

        # Initialize the edge array
        for i in range(0, num_edge_rows):
            #horizontal row
            if i % 2 == 1:
                for j in range(0, self.columns+1):

                    if j == 0:
                        left_node = -1
                    else:
                        left_node = cur_edge - (self.rows + 1) - (2*self.rows + 1)*ix + self.rows*ix

                    if j == columns:
                        right_node = -1
                    else:
                        right_node = cur_edge - (self.rows) - (2*self.rows + 1)*ix + self.rows*ix

                    self.chains[cur_edge] = Chain(cur_edge)
                    self.edges[cur_edge] = Edge(cur_edge, left_node, right_node, cur_edge)
                    cur_edge += 1
                ix += 1
            #vertical row
            else:
                for j in range(0, self.columns):
                    if i == 0:
                        top_node = -1
                    else:
                        top_node = cur_edge - self.rows - (self.rows + 1)*iy
                    if i == num_edge_rows-1:
                        bot_node = -1
                    else:
                        bot_node = cur_edge - (self.rows + 1)*iy

                    self.chains[cur_edge] = Chain(cur_edge)
                    self.edges[cur_edge] = Edge(cur_edge, top_node, bot_node, cur_edge)
                    cur_edge += 1
                iy += 1

    def copy(self, db):

        # Copy chains list
        self.chains = np.array([Chain(-1)]*db.num_edges)
        for i in range (0, len(db.chains)):
            self.chains[i].copy(db.chains[i])

        # Copy edges list
        self.edges = deepcopy(db.edges)

        # Copy nodes list
        self.nodes = deepcopy(db.nodes)

        self.num_edges = db.num_edges
        self.rows = db.rows
        self.columns = db.columns
        self.score1 = db.score1
        self.score2 = db.score2
        self.curr_player = db.curr_player

    '''
    Checks if an edge is already cut, if not, it's sent to cutFlow. Returns
    a numerical value as a reward for cutting an edge
    Arguments:
        + edge: the edge being cut
        + willPrint: boolean value to enable/disable test mode
    '''
    def cut(self, edge, willPrint):
        e = self.edges[edge]
        current_state_id = self.hash()
        if e.cut != True:

            # Check the chain type BEFORE cutting the edge
            chain_type = self.chains[e.edgeID].chain_type

            # Cut the edge
            has_ended, who_scored, reward = self.cutFlow(e,willPrint)

            # Return reward based on the chain type
            if 1 <= chain_type <= 2 or 4 <= chain_type <= 6: # Edge category 0
                reward += 1
            elif chain_type == 3 or chain_type == 7: # Edge category 2
                reward += 0.5
            elif 8 <= chain_type <= 9: # Edge category 1
                reward += 0
            else: # Edge category 3
                reward += -1

            return current_state_id, reward, self.hash(), has_ended, who_scored

        else:
            print("That edge is already cut!")

    '''
    Decides what to do when an edge is cut.
    Arguments:
        + e: an edge being cut
    '''
    def cutFlow(self, e, willPrint):

        # Cut the string
        e.cutString(self.nodes)

        # Update the score and get boolean value check game ended?
        has_ended, who_scored, reward = self.updateScore(e, willPrint)

        if willPrint:
            print('isCand:', e.cand)
        if e.cand == False:
            self.findInChains(e.edgeID)

        n1 = 4
        n2 = 4
        if(e.node1 != -1):
            n1 = self.nodes[e.node1]
        if(e.node2 != -1):
            n2 = self.nodes[e.node2]

        if n1 == 1 and n2 == 1:
            if willPrint:
                print('splitting')
            self.split(e)
        elif n1 == 2 and n2 == 2:
            if willPrint:
                print('union both')
            self.union(e.node1)
            self.union(e.node2)
            self.chains[e.chain].clear(self.edges)
        elif n1 == 2:
            if willPrint:
                print('union n1')
                print('change')
            self.change(e)
            self.union(e.node1)
        elif n2 == 2:
            if willPrint:
                print('union n2')
                print('change')
            self.change(e)
            self.union(e.node2)
        else:
            if willPrint:
                print('change')
            self.change(e)

        return has_ended, who_scored, reward
    '''
    Checks if points were scored or game is finished
    Arguments:
        + e: edge being cut
        + willPrint: boolean value to enable/disable test mode
    '''
    def updateScore(self, e, willPrint):

        # Integer value indicating which player just makes
        # a box in this turn, 0 if none of them
        who_scored = 0

        v1 = self.nodes[e.node1]
        v2 = self.nodes[e.node2]

        if e.node1 == -1:
            v1 = 4
        if e.node2 == -1:
            v2 = 4

        if  v1 == 0:
            if self.curr_player == 1:
                self.score1 += 1
                who_scored = 1
            else:
                self.score2 += 1
                who_scored = 2
        if  v2 == 0:
            if self.curr_player == 1:
                self.score1 += 1
                who_scored = 1
            else:
                self.score2 += 1
                who_scored = 2

        # If no body make a box, switch player
        reward = 0
        if who_scored == 0:
            self.curr_player = 3 - self.curr_player
        else:
            reward = 2

        if (self.score1 + self.score2) == len(self.nodes):
            if willPrint:
                print("Game over.")
                print("Player 1 scored:")
                print(self.score1)
                print("Player 2 scored:")
                print(self.score2)
            return True, who_scored, reward # End game
        else:
            if willPrint:
                print("Player 1 score:")
                print(self.score1)
                print("Player 2 score:")
                print(self.score2)
            return False, who_scored, reward # Game is not over

    '''
    Facilitates a change after a qualifying cut
    Arguments:
        + e: the edge that was cut
    '''
    def change(self, e):
        ch = self.chains[e.chain]
        ch.updateLength()
        if ch.length == 0:
            ch.clear(self.edges)
        else:
            ch.evaluateChange(e.edgeID,self.nodes,self.edges,False)

    '''
    Facilitates a split after cutting the edge of a chain that qualifies
    Arguments:
        + e: the edge that was cut
    '''
    def split(self, e):
        c2 = self.chains[self.findEmptyChain()]
        c1 = self.chains[e.chain]
        if c1.chain_type == 12:
            self.chains[e.chain].evaluateChange(e.edgeID,self.nodes,self.edges,True)
        else:
            i = c1.getIndex(e.edgeID)
            c1.popOff(c2,i)
            c1.evaluateChange(-1,self.nodes,self.edges,False)
            c2.evaluateChange(-1,self.nodes,self.edges,False)

    '''
    Facilitates a union between two chains after a cut
    Arguments:
        + n: the ID of the node connecting the two chains
    '''
    def union(self,n):
        et = self.getEdges(n)
        e1 = self.edges[et[0]]
        e2 = self.edges[et[1]]
        if e1.cand == False:
            self.findInChains(e1.edgeID)
        if e2.cand == False:
            self.findInChains(e2.edgeID)

        c1 = self.chains[e1.chain]
        c2 = self.chains[e2.chain]

        if c1.chainEdges[-1] == et[0] and c2.chainEdges[0] == et[1]:
            self.performUnion(self.chains[e1.chain],self.chains[e2.chain],False,False)
        elif c1.chainEdges[-1] == et[0] and c2.chainEdges[-1] == et[1]:
            self.performUnion(self.chains[e1.chain],self.chains[e2.chain],False,True)
        elif c1.chainEdges[0] == et[0] and c2.chainEdges[-1] == et[1]:
            self.performUnion(self.chains[e2.chain],self.chains[e1.chain],False,False)
        elif c1.chainEdges[0] == et[0] and c2.chainEdges[0] == et[1]:
            self.performUnion(self.chains[e2.chain],self.chains[e1.chain],True,False)
        else:
            print("ERROR", "Should not reach this point.")

    '''
    Perform union operation to add chain c2 to the end of chain c1
    Arguments:
        + c1: main chain
        + c2: the chain being added to c1
        + backToBack: ?
    '''
    def performUnion(self,c1,c2,revFirst, revSec):
        if c1.chainID == c2.chainID:
            c1.chain_type = 12
            c1.length += 1
        else:
            c1.unionLookup(c2.chain_type)
            for i in range (0,len(c2.candEdges)):
                self.edges[c2.chainEdges[i]].updateCand(False,-1,-1)
            if revFirst == True:
                c1.chainEdges.reverse()
                c1.addEdges(c2,self.edges)
            elif revSec == True:
                c2.chainEdges.reverse()
                c1.addEdges(c2,self.edges)
            else:
                c1.addEdges(c2,self.edges)
        c1.updateCandidates(self.edges,self.nodes)

    # returns the index of the first empty chain in the list of chains
    def findEmptyChain(self):
        i = 0
        for i in range(0,len(self.chains)):
            if self.chains[i].chain_type == -1:
                return i

    # returns an array with all uncut edges connected to the node
    def getEdges(self, n):
        i = int(n / self.rows)
        e = []
        left = n + self.rows + i*(2*self.rows + 1) - self.rows*i
        if self.edges[left].cut == False:
            e.append(left)
        right = n + (self.rows + 1) + i*(2*self.rows + 1) - self.rows*i
        if self.edges[right].cut == False:
            e.append(right)
        top = n + i*(self.rows + 1)
        if self.edges[top].cut == False:
            e.append(top)
        bottom = n + (self.rows + 1)*(i + 2) - 1
        if self.edges[bottom].cut == False:
            e.append(bottom)

        return e

    # if edge with ID e is not a candidate when cut, call this update its chain
    def findInChains(self, e):
        found = False
        i = 0
        while found != True:
            found = self.chains[i].contains(e)
            i += 1

        self.edges[e].updateChain(i-1)


    def printChains(self):
        for i in range(0,self.num_edges):
            print(self.chains[i].chainEdges)

    def printEdgeInfo(self):
        print('index','cut','cand','chain','node1','node2')
        for i in range(0,self.num_edges):
            print(i,self.edges[i].cut,self.edges[i].cand,self.edges[i].chain,self.edges[i].node1,self.edges[i].node2)


    '''
    Get the available edges that can be cut
    '''
    def getAvailableEdges(self):
        available_edges = []
        for edge in self.edges:
            if edge.cut == False:
                available_edges.append(edge.edgeID)
        return available_edges
