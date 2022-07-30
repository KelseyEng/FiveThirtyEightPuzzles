from unittest import result
import numpy as np
import matplotlib.pyplot as plt
import time

# This program solves the FiveThirtyEight puzzle titled "Can You Beat The Shell
# Game...Quantum-Style: Riddler Express", which was published on July 29,2022.
# The puzzle can be found at:
# https://fivethirtyeight.com/features/can-you-beat-the-shell-game-quantum-style/
# The text is posted here in case the link is broken:

# While walking down the street one day, you notice people gathering around a
# woman playing the shell game. With each game, she places a ball under one of
# three cups, and then swaps the positions of pairs of cups several times
# before asking passersby which cup they think the ball is now under.

# You have it on good authority that she is playing fairly, performing all the
# moves in plain sight, albeit too fast for you to track precisely which cups
# she’s moving. However, you do have one additional key piece of information —
# every time she swaps cups, one of them has the ball. In other words, she
# never swaps the two empty cups.

# When it’s your turn to guess, you note which cup she initially places the
# ball under. Then, as she begins to swap cups, you close your eyes and count
# the number of swaps. Once she is done, you open your eyes again. What is
# your best strategy for guessing which cup has the ball?


# Assumption
# 1. One crucial assumption that is not stated in the puzzle is that she
#   switches the cup with the ball to one of the random two empty slots.
#   Without this assumption, I don't think the problem is tractable.

# Gameplan
# Since we don't have any information about where the ball is moved, we can
# divide the possible guesses into either 1) original location or 2) alternate
# location. There will be no way of distinguishing between a guess of one of
# the two alternate locations. Originally, the ball is in the original
# location. After one move, it must be in one of the two alternate locations.
# After 2 moves, it has a 50% chance of being in the original, and 50% chance
# of being in one of the two alternates. So, our expectation for the answer is
# that the probability will alternate back and forth while decaying to zero
# knowledge (equal probability of being in any of the 3 locations).

# As is often the case with these puzzles, they are easier if you know a math
# or statistics trick. In this case, the probability can be calculated using
# Markov chains. However, to highlight other methods of solving this problem,
# I will demonstrate 3 different methods:
# 1. Markov Chains for exact calculations
# 2. Branching node calcuations that would run into space issues as the number
#   of moves (m) approaches infinity.
# 3. Monte Carlo approach that overcomes space issue for large m but only
#   approximates the solution for small m.

# Written in python version 3.10.5. See requirements.txt for package dependencies


# 1. Markov Chains (Transition Matrix)

def calcprob(m):
    tic = time.perf_counter()
    # define probability matrix of where the ball goes based on current location.
    P = np.array([[0, 0.5, 0.5],
                  [0.5, 0, 0.5],
                  [0.5, 0.5, 0]])

    # define original known location:
    location = np.array([1, 0, 0])

    # Calculate probably after each move up to m by multiplying
    loc_prob = np.zeros([m, 3])
    time_count = np.zeros(m)
    for i in range(m):
        loc_prob[i,:] = location
        location = np.matmul(P, location)
        toc = time.perf_counter()
        time_count[i] = toc-tic
    return (loc_prob,time_count)


# Set number of moves that you want to calculate out to
m = 20
(loc_prob_markov,time_count_markov) = calcprob(m)
print(time_count_markov)
print(loc_prob_markov)

# Note that our expectation was correct. If the number of moves is odd, select
# one of the alternate locations. If it is even, select the original location.
# After about 8 moves, the information has decayed to equal 1/3 probabilities.


# 2. Branching Structure
# because this structure has memory limits, lets collapse the location
# information into two states: original location, or one of the alternate
# locations. This allows us to represent the information as a boolean
# variable  of true (at original location) and false (at alternate location).
# The size of the branching array will be 2^m. Here, we selected m = 20, so 
# the array will be a bit over a million points. Manageable, although run time 
# will be much slower than Markov chains.

def format_results(results_in):
    results = np.zeros((results_in.shape[0],3))
    results[:,0] = results_in
    results[:,1] = (1-results_in)/2
    results[:,2] = (1-results_in)/2
    return results


def calc_branch(max_m):
    tic = time.perf_counter()
    time_count = np.zeros(max_m)
    loc_prob_branching = np.array(True, dtype=bool,ndmin=1)
    branch = np.copy(loc_prob_branching)
    for m in range(max_m-1):
        print(m)
        for i in range(branch.size):
            if branch[i] == True:
                branch[i] = False
                branch = np.append(branch,False)
            else:
                branch = np.append(branch,True)
        loc_prob_branching = np.append(loc_prob_branching,np.mean(branch))
        toc = time.perf_counter()
        time_count[m+1] = toc-tic
    loc_prob_branching = format_results(loc_prob_branching)
    return (loc_prob_branching,time_count)





(loc_prob_branching,time_count_branching) = calc_branch(m)


# As can be seen, it gets the exact same answer as the Markov chain method,
# but takes significantly longer to run. Furthermore, the time scales to m^3 
# rather than m in the Markov case



# 3. Monte Carlo
# We can also create an estimate of the answer using a Monte Carlo approach. 
# This will not give an exact answer, but would be able to make estimates for 
# higher values of m, something that the braching system cannot do. Here we 
# will keep the binary system introduced in the braching version.

def montecarlo(max_m,n):
    tic = time.perf_counter()
    time_count = np.zeros(max_m)
    location = np.ones((max_m,n))
    for m in range(1,max_m):
        locTemp = location[m-1,:] + np.random.randint(2,size=n)
        location[m,:] = locTemp < 1
        toc = time.perf_counter()
        time_count[m] = toc-tic
    loc_prob_montecarlo = np.mean(location,axis=1)
    loc_prob_montecarlo = format_results(loc_prob_montecarlo)

    return (loc_prob_montecarlo,time_count)


n = 1000

(loc_prob_montecarlo,time_count_montecarlo) = montecarlo(m,n)

print(loc_prob_montecarlo)


# Plot results

def plotprob(loc_prob,time_count,title):
    fig, axs = plt.subplots(nrows=3,ncols=3, sharey=True, sharex=True)
    m = loc_prob.shape[0]
    for j in range(3):
        axs[0,j].set_title(title[j])
        for i in range(3):
            axs[i,j].plot(range(m), loc_prob[:, i])
            axs[i,j].set_ylim([0, 1])
            axs[i,j].set_xticks(range(0, m))
            if i == 0:
                axs[i,j].set(ylabel='Original Location Probability')
            else:
                axs[i,j].set(ylabel=f'Alt Location {i} Probability')
        axs[-1,j].set(xlabel = 'Number of Moves')
    fig2, axs2 = plt.subplots(nrows=1,ncols=3, sharey=True, sharex=True)    
    for j in range(3):
        axs2[j].semilogy(range(m),time_count[:,j])
        axs2[j].set(ylabel='Run Time (s)')
        axs2[j].set(xlabel = 'Number of Moves')
        axs2[j].set_title(title[j])
    plt.show()
    return

loc_prob = np.concatenate((loc_prob_markov,
    loc_prob_branching,
    loc_prob_montecarlo),axis=1)
time_count = np.concatenate((time_count_markov.reshape([m,1]),
    time_count_branching.reshape([m,1]),
    time_count_montecarlo.reshape([m,1])),axis = 1)
print(time_count)
title_list = ["Markov Chain","Branching Structure","Monte Carlo"]
plotprob(loc_prob,time_count,title_list)