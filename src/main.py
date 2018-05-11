from DabEnv import DabEnv
from Agent import Agent

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import random

# Player 1: human
# Player 2: computer

# Create environment (a 6x6 board game)
env = DabEnv(6,6)

# Create computer player
computer_player = Agent(2)

# Boolean variable indicating game ended or not
has_ended = False
while has_ended == False and len(env.state.getAvailableEdges()) != 0:
    if env.player == 1:
        available_moves = env.state.getAvailableEdges()

        '''
        # Prompt for input & check if valid
        print(available_moves)
        val = input("Enter a legal move:")
        player_move = int(val)
        if player_move not in available_moves:
            continue
        '''
        
        # Execute player's move                                                                                                                                               
        current_state_id, reward, new_state_id, has_ended = env.play(player_move, False)
        
    else:
        reward, has_ended = computer_player.make_move(env)
        print(reward)
        rewards = np.append(rewards, reward)
