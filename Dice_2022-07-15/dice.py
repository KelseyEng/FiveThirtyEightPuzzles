import numpy as np
from itertools import product

# This program solves the FiveThirtyEight puzzle titled "How Many Ways Can you
# Cast A Die", which was published on July 15,2022. The puzzle can be found at:
# https://fivethirtyeight.com/features/how-many-ways-can-you-cast-a-die/
# The text is posted here in case the link is broken:
# I have an unlabeled, six-sided die. I make a single mark on the middle of each
# face that is parallel to one pair of that face’s four edges.
# How many unique ways are there for me to mark the die? (Note: If two ways can
# be rotated so that they appear the same, then they are considered to be the
# same marking.)
# Extra credit: Suppose you can also mark a face along one of its two diagonals.
# Now how many unique ways are there to mark the die?



## Gameplan
# If we ignored rotations, then this would be relatively straight forward. Each
# face could have 2 possibilties, so the number of possibilities would be
# 2^6, or 64. With the extra credit, that grows to 4^6, or 4096. Both are easily
# solved with brute force. So, the strategy is to weed out rotations. 
# This also sets our bounds. For the first section, our answer should be
# between 1 and 64. For the extra credit, between 1 and 4096.

# 1. We will create a virtual die whose markings will be either -1 or 1. These
# can change due to rotation. 
# 2. So, we will work out the different rotations and how they move the faces 
# and change the markings. 
# 3. Go through all combinations and weed out copies.
# 4. For extra credit, just add -2 and 2 as possibilities. Rotations are same.

# Note die reference frame: if die is sitting on a table, the x-y plan sits on
# the table and the z axis is perpindicular to the table. Right hand rule applies.


def initialdie():
    pos = np.arange(6, dtype=int)
    mod = np.ones(6, dtype=int)
    return [pos, mod]


def twistdie(pos, mod):
    # Rotates die around z axis in the counter-clockwise direction (positive z)

    # Move Location of Squares
    idx = np.array([0, 2, 3, 4, 1, 5])
    pos = pos[idx]

    # Account for rotation of symbols
    mod = mod * [-1, 1, 1, 1, 1, -1]
    mod = mod[idx]
    return [pos, mod]


def flipdie(pos, mod):
    # Rotates die around the x axis (positive x)

    # Move Location of Squares
    idx = np.array([3, 0, 2, 5, 4, 1], dtype=int)
    pos = pos[idx]

    # Account for rotation of symbols
    mod = mod * [1, 1, -1, 1, -1, 1]
    mod = mod[idx]
    return [pos, mod]


def die_perms(position,mod):
    positionlist = np.zeros([24,6], dtype=int)
    modlist = np.zeros([24,6], dtype=int)
    count = 0
    for i in range(6):
        #Rotate die into correct position (Number on Top)
        if position[0] != i: 
            if position[5] == i:
                [position, mod] = flipdie(position, mod)
                [position, mod] = flipdie(position, mod)
            else:
                while position[3] != i:
                    [position, mod] = twistdie(position, mod)
                [position, mod] = flipdie(position, mod)
        
        # Get 4 unique configurations with Number on Top
        for j in range(4):
            positionlist[count,] = position
            modlist[count,] = mod
            count +=1
            [position, mod] = twistdie(position, mod)
    
    return [positionlist, modlist]

def possible_combos(a):
    
    possible_list = product(a,a,a,a,a,a)
    possible_list = np.fromiter(possible_list, dtype=np.dtype((int, 6)))
    return possible_list


def all_die_rotations(current_val,positionlist,modlist):
    all_vals = []
    for i in range(len(positionlist)):
        all_vals.append(current_val[positionlist[i]] * modlist[i])
    all_vals = np.array(all_vals)
    return all_vals
    

def find_unique(possible_list,positionlist,modlist):
    combo_history = np.empty([0,6])
    for i in range(len(possible_list)):
        found_match = 0
        current_val = possible_list[i]
        if np.any(np.all(combo_history == current_val, axis = 1)):
            print('skip')
            continue
        else:
            all_vals = all_die_rotations(current_val,positionlist,modlist)
            for rotated_val in all_vals:
                #rotated_val = rotated_val.reshape([1,6])
                if np.any(np.all(rotated_val == combo_history,axis = 1)):
                    found_match = 1
                    break
            if found_match == 1:
                continue
            else: 
                current_val = current_val.reshape([1,6])
                combo_history = np.append(combo_history,current_val,axis=0)
    return combo_history

# Regular
[pos, mod] = initialdie()
[poslist, modlist] = die_perms(pos,mod)
possible_list = possible_combos([-1,1])

combo_history = find_unique(possible_list,poslist,modlist)
print(combo_history)
print(len(combo_history))

# Extra Credit
possible_list = possible_combos([-2,-1,1,2])

combo_history = find_unique(possible_list,poslist,modlist)
print(combo_history)
print(len(combo_history))