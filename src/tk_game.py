"""
TK frontend to Dots-And-Boxes by Gregor Lingl
From a mailing list posting:
    Until now I didn't know "The Dots and Boxes" Game, but Dannies
    program made me interested in it.
    So I wrote the beginning of a gui version. I tried hard to use
    Dannies code as is - so the gui code is (nearly) completely
    separated from the game machinery. I consider this a proof for
    the exceptionally good design of Dannies program (imho).
    O.k., maybe my extension of the program still needs some more
    buttons or textfields or so, but perhaps it could be a starting
    point.
"""


from tkinter import *
#from Canvas import Rectangle

from DabEnv import DabEnv
from Agent import Agent

import numpy as np

def cartesian( v1, v2 ):
    """ Helper function
    returns cartesian product of the two
    'sets' v1, v2"""
    return tuple([(x,y) for x in v1 for y in v2])


def right(x):
    """Helper function: argument x must be a dot.
    Returns dot right of x."""
    return (x[0]+1,x[1])


def upper(x):
    """Helper function: argument x must be a dot.
    Returns dot above (actually below) x."""
    return (x[0], x[1]+1)


class GameGUI:
    def __init__(self, env, computer_player):
        """Initializes graphic display of a rectangular gameboard."""
        self.tmp = 0
        # AI Player
        self.computer_player = computer_player

        # Properties of gameboard
        dw = self.dotwidth = 6
        sw = self.squarewidth = 60
        sk = self.skip = 4
        fw = self.fieldwidth = dw + sw + 2*sk
        ins = self.inset = sw/2
        self.barcolors = ['blue','red']
        self.squarecolors = ['lightblue','orange']

        # Construct Canvas
        self.env = env
        width, height = env.columns+1, env.rows+1

        # compute size of canvas:
        w = width * fw
        h = height * fw
        self.root = Tk()
        cv = self.cv = Canvas(self.root, width=w, height=h, bg='white')
        cv.bind('<Button-1>', self._callback)
        cv.pack()

        # Put geometrical objects - dots, bars and squares - on canvas
        self.bars = {}
        self.squares = {}
        for dot in cartesian(range(width), range(height)):
            # dots. Never used again
            Canvas.create_rectangle(cv, ins+dot[0]*fw, ins+dot[1]*fw,
                           ins+dot[0]*fw + dw, ins+dot[1]*fw + dw, fill='black', outline='' )
            # horizontal bars
            if dot[0] < width - 1:
                x0 = ins+dot[0]*fw+dw+sk
                y0 = ins+dot[1]*fw
                self.bars[(dot,right(dot))] = Canvas.create_rectangle(cv,x0,y0,x0+sw,y0+dw,fill='lightgray',outline='')
            # vertical bars
            if dot[1] < height - 1:
                x0 = ins+dot[0]*fw
                y0 = ins+dot[1]*fw + dw + sk
                self.bars[(dot,upper(dot))] = Canvas.create_rectangle(cv,x0,y0,x0+dw,y0+sw,fill='lightgray',outline='')
            # squares
            if (dot[0] < width - 1) and (dot[1] < height - 1):
                x0 =ins+dot[0]*fw + dw + sk
                y0 =ins+dot[1]*fw + dw + sk
                self.squares[dot] = Canvas.create_rectangle(cv,x0,y0,x0+sw,y0+sw,fill='lightyellow',outline='')
        cv.update()
        self.root.mainloop()

    def _coord(self,x):
        """returns pixel-coordinate corresponding to
        a dot-coordinate x"""
        return self.inset + self.dotwidth/2 + self.fieldwidth*x

    def _find_bar(self,event):
        """returns bar next to mouse-position when clicked,
        if applicable, otherwise None"""
        ex, ey = event.x, event.y
        for bar in self.bars:
            ((x1,y1),(x2,y2))=bar
            mx, my = ( (self._coord(x1)+self._coord(x2))/2,
                       (self._coord(y1)+self._coord(y2))/2 )
            if abs(ex-mx)+abs(ey-my) < self.squarewidth/2:
                return bar

    def _callback(self, event):

        """Action following a mouse-click"""
        hit = self._find_bar(event)

        # Convert the coordinate into the edge id
        vertical = (6+hit[1][0])+ 13*(hit[1][1]-1)
        horizontal = (hit[0][1]*10)+hit[0][0] + hit[1][1]*3
        edge_id = -1
        if abs(hit[0][0] - hit[1][0]) == 1:
            edge_id = horizontal
        elif abs(hit[0][1] - hit[1][1]) == 1:
            edge_id = vertical

        # A little bit redudant
        if not hit or self.env.state.curr_player == 2 or edge_id not in self.env.state.getAvailableEdges():
            return

        # Do a move
        player = self.env.state.curr_player
        has_ended = False

        if player == 1: # Human player
            available_moves = self.env.state.getAvailableEdges()
            if edge_id in available_moves and has_ended == False:

                # Color the player's move
                self.cv.itemconfig(self.bars[hit], fill=self.barcolors[player-1])

                current_state_id, reward, new_state_id, has_ended = self.env.play(edge_id, False)
                self.computer_player.update_table(edge_id, current_state_id, new_state_id, reward)

                # Color the boxes
                self.color_square(1)

            # Computer player turn right after
            while self.env.state.curr_player == 2 and has_ended == False:
                self.computer_move(hit, player)

        if has_ended:
            print("Game over!")
            print("Final score:\n\tPlayer 1: %s\n\tPlayer 2: %s" % (self.env.state.score1, self.env.state.score2))
            print("Updating state-value table...")
            self.computer_player.save_table()

    def color_square(self, player):
        # Colorize the box
        for i in range(0, len(self.env.state.nodes)):
            node_valency = self.env.state.nodes[i]
            node_coord = (i%6, int(i/6))
            if node_valency == 0 and self.squares[node_coord] != None:
                self.cv.itemconfig(self.squares[node_coord], fill=self.squarecolors[player-1])
                self.squares[node_coord] = None

    def computer_move(self, hit, player):
        vertical = (6+hit[1][0])+ 13*(hit[1][1]-1)
        horizontal = (hit[0][1]*10)+hit[0][0] + hit[1][1]*3
        edge_id = -1
        if abs(hit[0][0] - hit[1][0]) == 1:
            edge_id = horizontal
        elif abs(hit[0][1] - hit[1][1]) == 1:
            edge_id = vertical

        ai_move, reward, has_ended = self.computer_player.make_move(self.env)

        # Colorize the computer's move
        target = None
        for coord in self.bars.keys():
            vertical = (6+coord[1][0])+ 13*(coord[1][1]-1)
            horizontal = (coord[0][1]*10)+coord[0][0] + coord[1][1]*3
            index = -1
            if abs(coord[0][0] - coord[1][0]) == 1:
                index = horizontal
            elif abs(coord[0][1] - coord[1][1]) == 1:
                index = vertical

            if index == ai_move:
                target = coord
                break
        self.cv.itemconfig(self.bars[target], fill=self.barcolors[3-player-1])

        # Color the box if computer gain any score
        self.color_square(2)

def _gtest(width, height):
    """A small driver to make sure that the board works.  It's not
    safe to use this test function in production, because it uses
    input()."""
    print("Running _gtest... ")

    # Create environment & agent
    env = DabEnv(height, width)

    table_name = 'qtable.npy'
    state_value_table = np.load(table_name).item()
    computer_player = Agent(2, state_value_table, table_name)

    gui = GameGUI(env, computer_player)

if __name__ == '__main__':
    # graphics mode
    if len(sys.argv[1:]) == 2:
        _gtest(int(sys.argv[1]), int(sys.argv[2]))
    elif len(sys.argv[1:]) == 1:
        _gtest(int(sys.argv[1]), int(sys.argv[1]))
    else:
        _gtest(6, 6)
