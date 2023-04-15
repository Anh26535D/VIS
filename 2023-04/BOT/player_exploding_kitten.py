import sys
sys.path.insert(0, '/VIS_3TH/')

import numpy as np
from numba import njit

from setup import SHORT_PATH
import importlib.util
game_name = 'Exploding_Kitten'

def add_game_to_syspath(game_name):
    if len(sys.argv) >= 2:
        sys.argv = [sys.argv[0]]
    sys.argv.append(game_name)

def setup_game(game_name):
    spec = importlib.util.spec_from_file_location('env', f"{SHORT_PATH}Base/{game_name}/env.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module 
    spec.loader.exec_module(module)
    return module

add_game_to_syspath(game_name)
env = setup_game(game_name)

getActionSize = env.getActionSize
getStateSize = env.getStateSize
getAgentSize = env.getAgentSize

getValidActions = env.getValidActions
getReward = env.getReward
numba_main_2 = env.numba_main_2

# (34, 10, 50, 7, 3, 0, 5, 9, 40, 18, 28, 1, 25, 21, 36, 11, 47, 38, 26, 15, 29, 35, 13, 23, 20, 32, 19, 30, 2, 44, 42, 31, 12, 17, 22, 46, 14, 39, 49, 8, 27, 16, 43, 6, 33, 24, 37, 45, 41, 4, 48):


def DataAgent():
    return np.array([0])

@njit()
def Test(state, per):
    validActions = getValidActions(state) 
    validActions = np.where(validActions == 1)[0]
    if np.argmax(state[87:91])+11 in validActions:
        return np.argmax(state[87:91])+11, per
    for i in (10, 9, 8, 7, 6, 1, 2, 4, 5, 3, 0, 11):
        if i+15 in validActions:
            return i+15, per
    for i in (11, 0, 3, 5, 4, 2, 1, 6, 7, 8, 9, 10):
        if i+27 in validActions:
            return i+27, per
    for i in (11, 0, 3, 5, 4, 2, 1, 6, 7, 8, 9, 10):
        if i+39 in validActions:
            return i+39, per
    for i in (9, 7, 8):
        if i in validActions:
            return i, per
    if 10 in validActions:
        return 10, per
    for i in (3, 0, 6, 5, 4, 2, 1):
        if i in validActions:
            return i, per
    action = np.random.choice(validActions)
    return action, per


