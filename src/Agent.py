from DabEnv import DabEnv
import numpy as np
import random
import pandas as pd
from pandas import DataFrame

class Agent:
    def __init__(self, player_id, table, file_name):
        self.player_id = player_id

        # Load the state value table
        self.s_table = table

        self.file_name = file_name

    def save_table(self):
        np.save(self.file_name, self.s_table)

    def update_table(self, best_move, current_state_id, new_state_id, reward):

        gamma = 0.9
        alpha = 0.0001

        # Update the state-value table
        # Update the value of the state prior to taking action a
        # Initialize the value if it not exists before
        if current_state_id not in self.s_table:
            self.s_table[current_state_id] = {}
        if new_state_id not in self.s_table:
            self.s_table[new_state_id] = {}

        if best_move not in self.s_table[current_state_id]:
            self.s_table[current_state_id][best_move] = 0
        if best_move not in self.s_table[new_state_id]:
            self.s_table[new_state_id][best_move] = 0

        # Access the q table of the next state s_prime
        max_q = self.s_table[new_state_id].values()
        q_vals = []
        move_id = []
        for key in self.s_table[new_state_id]:
            q_vals.append(self.s_table[new_state_id][key])
            move_id.append(key)

        # Find the max value of Q(S')
        q_table = DataFrame(q_vals, index=move_id).sort_values(0, ascending=0)
        max_q = q_table.iloc[0].values[0]

        # Update the q-table
        self.s_table[current_state_id][best_move] = self.s_table[current_state_id][best_move] + alpha * (reward + gamma * max_q - self.s_table[current_state_id][best_move])

    def make_move(self, env):

        gamma = 0.9

        # Get available chains
        available_chains = env.state.chains
        if len(available_chains) == 0:
            return

        c = [chain for chain in available_chains if chain.chain_type != -1]
        #c = c[random.randint(0, len(c)-1)]
        candEdges = []
        for chain in c:
            tmp = chain.candEdges
            for edge in tmp:
                if edge not in candEdges:
                    candEdges.append(edge)

        available_actions = candEdges
        pi_s = np.array([0]*len(available_actions))
        reward_list = np.array([0]*len(available_actions))

        # Do a Q-Learning to find the best move
        for action in available_actions:
            copied_env = DabEnv(6,6)
            copied_env.copy(env)

            current_state_id, reward, new_state_id, has_ended = copied_env.play(action, False)

            if (new_state_id not in self.s_table):
                self.s_table[new_state_id] = {}
            if action not in self.s_table[new_state_id]:
                self.s_table[new_state_id][action] = 0

            pi_s[available_actions.index(action)] = reward + gamma * self.s_table[new_state_id][action]
            reward_list[available_actions.index(action)] = reward

        # Choose best move
        move_index = np.argmax(pi_s)
        best_move = available_actions[move_index]

        # Make the move
        current_state_id, reward, new_state_id, has_ended = env.play(best_move, False)

        self.update_table(best_move, current_state_id, new_state_id, reward)

        return best_move, reward, has_ended
