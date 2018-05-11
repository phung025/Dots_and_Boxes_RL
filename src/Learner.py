from DabEnv import DabEnv

import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import random

def td0_learning(s_table, episodes, steps):

    # Learning rate
    alpha = 0.0001

    # Discount rate
    gamma = 0.9

    for episode in range(0, episodes):

        # Initialize new environment
        env = DabEnv(6,6)

        for step in range(0, steps):
            # Take a random action a
            available_chains = env.state.chains
            #env.state.getAvailableEdges()

            if len(available_chains) == 0:
                continue

            # Pick a random chain to cut an edge from
            c = [chain for chain in available_chains if chain.chain_type != -1]
            c = c[random.randint(0, len(c)-1)]

            if len(c.candEdges) == 0:
                continue

            # pick an edge (randomly) from the chain to cut
            a = c.candEdges[random.randint(0, len(c.candEdges) - 1)]

            # Do the move
            current_state_id, reward, new_state_id, has_ended = env.play(a, False)

            # Update the value of the state prior to taking action a
            # Initialize the value if it not exists before
            if current_state_id not in s_table:
                s_table[current_state_id] = {}
            if new_state_id not in s_table:
                s_table[new_state_id] = {}

            if a not in s_table[current_state_id]:
                s_table[current_state_id][a] = 0
            if a not in s_table[new_state_id]:
                s_table[new_state_id][a] = 0

            # Access the q table of the next state s_prime
            max_q = s_table[new_state_id].values()
            q_vals = []
            move_id = []
            for key in s_table[new_state_id]:
                q_vals.append(s_table[new_state_id][key])
                move_id.append(key)

            # Find the max value of Q(S')
            q_table = DataFrame(q_vals, index=move_id).sort_values(0, ascending=0)
            max_q = q_table.iloc[0].values[0]

            # Update the q-table
            s_table[current_state_id][a] = s_table[current_state_id][a] + alpha * (reward + gamma * max_q - s_table[current_state_id][a])

        print("Score 1:", env.state.score1, " --- Score 2:", env.state.score2)
        print("States explored:", len(s_table))
        print("")

    # Return the approximation of the value of states
    return s_table

# Try loading the state value table
table_name = 'qtable.npy'
table = {}
try:
    table = np.load(table_name).item()
except:
    table = {}

print("Start learning...")
table = td0_learning(table, 1000, 84)

# Save the state value table to file
np.save(table_name, table)
