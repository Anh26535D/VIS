# %%
import sys
sys.path.insert(0, '/VIS_3TH/')

import numpy as np
from numba import njit

from setup import SHORT_PATH
import importlib.util
game_name = 'Splendor_v3'

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

# %%
@njit()
def valueOf(card, pGemTokens, pGoldTokens, pDevCards, adjust=0):
    if np.sum(card) == 0:
        return -1
    cost = card[-5:]
    score = card[0]
    needs = cost - pDevCards - pGemTokens
    needs[needs < 0] = 0
    needs[needs > 0] = 1
    if adjust == 1:
        return 1/((score + 1)*(np.sum(needs) + 1))
    return (score + 1)/(np.sum(needs) + 1)

@njit()
def player(state, per):
    pGemTokens = state[6:11]
    pGoldTokens = state[11]
    pDevCards = state[12:17]

    adjust = 0
    if state[17] <= 8:
        adjust = 1
    
    faceupCards = state[18:150]
    facedownCards = state[175:208]
    cards = np.append(faceupCards, facedownCards).reshape(15, -1)
    valueOfCards = np.array([valueOf(card, pGemTokens, pGoldTokens, pDevCards, adjust) for card in cards])
    mostValuableCards = (-valueOfCards).argsort()[:1]
    action = mostValuableCards[np.random.randint(len(mostValuableCards))]
    return action, per

# %%
win, per = numba_main_2(player, 100000, np.array([]), 1)
win


