from DabBoard import DabBoard
import numpy as np
from copy import deepcopy

class DabEnv:

    '''
    Default constructor, create an environment with intial state of the game.
    The constructor takes in 2 parameters: # of boxes in one row and # of boxes in one columns
    '''
    def __init__(self, rows, columns):

        # Board dimension of rows x columns boxes
        self.rows = rows
        self.columns = columns

        # Calculate the # of lines the player can make
        self.lines = self.rows * self.columns + (self.rows+1) * (self.columns + 1) - 1

        # Create an intial board of rows x columns boxes
        self.state = DabBoard(rows=self.rows, columns=self.columns)

    def copy(self, ev):
        self.rows = ev.rows
        self.columns = ev.columns
        self.lines = ev.lines
        self.state = deepcopy(ev.state)

    '''
    Execute an action and return a new board game and a boolean value indicates if it's next player's move
    and return the reward for such action
    '''
    def play(self, action, willPrint):
        # Perform cut action
        current_state_id, reward, new_state_id, has_ended, who_scored = self.state.cut(action, willPrint)

        return current_state_id, reward, new_state_id, has_ended

    '''
    Display the game in console
    '''
    def render(self, mode='human'):
        e = 0
        # simple print for a given board size only; need to add checks for cut edges as well
        for i in range (2 * self.rows + 1):
            lineTP = ""
            if i % 2 == 0:
                for j in range (self.columns):
                    if self.state.edges[e].cut == False:
                        lineTP += "   |"
                    else:
                        lineTP += "    "
                    e += 1
            else:
                for j in range (self.columns):
                    if self.state.edges[e].cut == False:
                        lineTP += "---o"
                    else:
                        lineTP += "   o"
                    e += 1
                if self.state.edges[e].cut == False:
                    lineTP += "---"
                else:
                    lineTP += "   "
                e += 1

            print(lineTP)
