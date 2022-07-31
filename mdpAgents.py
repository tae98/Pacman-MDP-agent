# mdpAgents.py
# parsons/20-nov-2017
#
# Version 1
#
# The starting point for CW2.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class Grid:

    # To draw a grid for the mapping of the pacman environment(from lecture)

    def __init__(self, width, height):
        self.width = width
        self.height = height
        subgrid = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(0)
            subgrid.append(row)

        self.grid = subgrid

    def setValue(self, x, y, value):
        self.grid[y][x] = value

    def getValue(self, x, y):
        return self.grid[y][x]

    def getHeight(self):
        return self.height

    def getWidth(self):
        return self.width

    # To disply grid
    def display(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[i][j],
            print
        print

    def prettyDisplay(self):
        for i in range(self.height):
            for j in range(self.width):
                # print grid elements with no newline
                print self.grid[self.height - (i + 1)][j],
            print
        print


class MDPAgent(Agent):
    """
    The MDP Agent is one that calculates utilities for the map and for pacman's location
    In order to gain the best movement policy for every state of the map
    It updates every time a move is made (i.e. when a food is eaten, or a ghost moves)
    (i.e. recalculates using valueIteration)
    Number of loops in valueIteration depends on map size for efficiency. The smaller the map is,
    the lower the number of loops required.
    """

    # Constructor: this gets run when we first invoke pacman.py
    def __init__(self):
        print "Starting up MDPAgent!"
        name = "Pacman"
        self.trackList = {'visited': [], 'foodPos': [], 'wallPos': [], 'capsulePos': []}
        self.map = []

    # Gets run after an MDPAgent object is created and once there is
    # game state to access.
    def registerInitialState(self, state):
        print "Running registerInitialState for MDPAgent!"
        print "I'm at:"
        print api.whereAmI(state)

        # creates the map
        self.makeMap(state)

    def final(self, state):
        print "Looks like the game just ended!"
        # Initialize tracklist after each games are played
        keys = self.trackList.keys()
        for each in keys:
            self.trackList[each] = []

    # To make the map from the grid
    def makeMap(self, state):
        w, h = self.getWH(state)
        self.map = Grid(w + 1, h + 1)

        walls = api.walls(state)
        for i in range(len(walls)):
            self.map.setValue(walls[i][0], walls[i][1], "%")

    # Getting Width and Height for the map

    def getWH(self, state):
        ys = [each[1] for each in api.corners(state)]
        xs = [each[0] for each in api.corners(state)]
        height = max(ys) - min(ys)
        width = max(xs) - min(xs)

        return width, height

    # Putting the variable for the map

    def createValMap(self, state):

        if api.whereAmI(state) not in self.trackList['visited']:
            self.trackList['visited'].append(api.whereAmI(state))

        for each in api.food(state):
            if each not in self.trackList['foodPos']:
                list.append(self.trackList['foodPos'], each)

        for each in api.walls(state):
            if each not in self.trackList['wallPos']:
                list.append(self.trackList['wallPos'], each)

        for each in api.capsules(state):
            if each not in self.trackList['capsulePos']:
                list.append(self.trackList['capsulePos'], each)

        return self.createRewardMap(api.corners(state), state)
    # Giving the reward values for the rewards of food = 7 wall =% capsule=7
    def createRewardMap(self, corners, state):
        rewardMap = dict()
        dict.update(rewardMap, dict.fromkeys(self.trackList['foodPos'], 7))
        dict.update(rewardMap, dict.fromkeys(self.trackList['wallPos'], '%'))
        dict.update(rewardMap, dict.fromkeys(self.trackList['capsulePos'], 7))

        w, h = self.getWH(state)
        for i in range(w):
            for j in range(h):
                if (i, j) not in rewardMap.keys():
                    rewardMap[(i, j)] = 0
        # If the food or capsules has been visited by the pacman the reward is set to 0
        for i in self.trackList['foodPos']:
            if i in self.trackList['visited']:
                rewardMap[i] = 0

        for i in self.trackList['capsulePos']:
            if i in self.trackList['visited']:
                rewardMap[i] = 0
        # Setting Reward value for the ghost as -10
        ghosts = api.ghosts(state)
        for i in rewardMap.keys():
            for j in range(len(ghosts)):
                if ((int(ghosts[j][0])), (int(ghosts[j][1]))) == i:
                    rewardMap[i] = -10

        return rewardMap

    def valueIterationCalc(self, state, reward, gamma, val):
        # Get max width and height
        maxWidth, maxHeight = self.getWH(state)
        ghosts = api.ghosts(state)
        foodToCalculate = []
        # Listing the coordinates within range from the ghost's NSWE position
        for each in range(5):
            for x in range(len(ghosts)):
                if (int(ghosts[x][0] + each), int(ghosts[x][1])) not in foodToCalculate:
                    foodToCalculate.append((int(ghosts[x][0] + each), int(ghosts[x][1])))
                if (int(ghosts[x][0] - each), int(ghosts[x][1])) not in foodToCalculate:
                    foodToCalculate.append((int(ghosts[x][0] - each), int(ghosts[x][1])))
                if (int(ghosts[x][0]), int(ghosts[x][1] + 1)) not in foodToCalculate:
                    foodToCalculate.append((int(ghosts[x][0]), int(ghosts[x][1] + each)))
                if (int(ghosts[x][0]), int(ghosts[x][1] - 1)) not in foodToCalculate:
                    foodToCalculate.append((int(ghosts[x][0]), int(ghosts[x][1] - each)))


        noCalculation = []
        for i in api.food(state):
            if i not in foodToCalculate:
                noCalculation.append(i)

        if not (0 < gamma <= 1):
            raise ValueError("gamma out of the range.")
        # Variable to keep track of the old values
        loops = 200
        while loops > 0:
            oldVal = val.copy()
            for i in range(maxWidth):
                for j in range(maxHeight):
                    if (i, j) not in api.walls(state) and (i, j) not in noCalculation and (i, j) not in ghosts and (
                    i, j) not in api.capsules(state):
                        val[(i, j)] = reward + gamma * self.transitionCalc(i, j, oldVal)
            loops -= 1
    # Different iteration method for map with smaller grid
    def smallGridValueIterationCalc(self, state, reward, gamma, val):

        walls = api.walls(state)
        food = api.food(state)
        ghosts = api.ghosts(state)
        capsules = api.capsules(state)

        maxWidth, maxHeight = self.getWH(state)

        if not (0 < gamma <= 1):
            raise ValueError("Gamma out of the range.")

        # Smaller grid goes through lesser iteration of 10 times compared to larger grid
        # oldVal stores the older value
        loops = 100
        while loops > 0:
            oldVal = val.copy()
            for i in range(maxWidth):
                for j in range(maxHeight):
                    if (i, j) not in walls and (i, j) not in food and (i, j) not in ghosts and (i, j) not in capsules:
                        val[(i, j)] = reward + gamma * self.transitionCalc(i, j, oldVal)
            loops -= 1
    # Calculating the transition probability of the pacman
    def transitionCalc(self, x, y, valueMap):
        valueMap[(x, y)] = self.getMax(x, y, valueMap)

        return valueMap[(x, y)]
    # Calculating the policy of the iterated map by updating the ghost movement
    def policyCalc(self, x, y, valueMap):
        util_dict = {"North": 0.0, "South": 0.0, "East": 0.0, "West": 0.0}
        direction = {'North': (x, y + 1), 'South': (x, y - 1), 'East': (x + 1, y), 'West': (x - 1, y)}
        perpen = {'North': ('East', 'West'), 'East': ('North', 'South'), 'South': ('East', 'West'),
                  'West': ('North', 'South')}

        for each in direction.keys():
            if valueMap[direction[each]] != '%':
                util_dict[each] = 0.8 * valueMap[direction[each]]
            else:
                util_dict[each] = 0.8 * valueMap[(x, y)]
            option = perpen[each]
            for op in option:
                if valueMap[direction[op]] != '%':
                    util_dict[each] += 0.1 * valueMap[direction[op]]
                else:
                    util_dict[each] += 0.1 * valueMap[(x, y)]
        # Getting the max value of the utility
        maxMEU = max(util_dict.values())

        return util_dict.keys()[util_dict.values().index(maxMEU)]


    def getMax(self, x, y, valueMap):
        util_dict = {"North": 0.0, "South": 0.0, "East": 0.0, "West": 0.0}
        direction = {'North': (x, y + 1), 'South': (x, y - 1), 'East': (x + 1, y), 'West': (x - 1, y)}
        perpen = {'North': ('East', 'West'), 'East': ('North', 'South'), 'South': ('East', 'West'),
                  'West': ('North', 'South')}

        for each in direction.keys():
            if valueMap[direction[each]] != '%':
                util_dict[each] = 0.8 * valueMap[direction[each]]
            else:
                util_dict[each] = 0.8 * valueMap[(x, y)]
            option = perpen[each]
            for op in option:
                if valueMap[direction[op]] != '%':
                    util_dict[each] += 0.1 * valueMap[direction[op]]
                else:
                    util_dict[each] += 0.1 * valueMap[(x, y)]
        # Calculating the action that will allow the pacman to move for the maximum utility
        self.action = util_dict.keys()[util_dict.values().index(max(util_dict.values()))]
        return max(util_dict.values())


    def getAction(self, state):
        # To create a map environment for pacman to calculate its movement
        maxWidth, maxHeight = self.getWH(state)
        valueMap = self.createValMap(state)
        x, y = api.whereAmI(state)
        # Choosing which iteration to use according to the size of the map
        if maxHeight >= 10 and maxWidth >= 10:
            self.valueIterationCalc(state, 0, 0.625, valueMap)
        else:
            self.smallGridValueIterationCalc(state, 0.2, 0.732, valueMap)

        # Map values are updated with the values obtained from iteration
        for i in range(self.map.getWidth()):
            for j in range(self.map.getHeight()):
                if self.map.getValue(i, j) != "%":
                    self.map.setValue(i, j, valueMap[(i, j)])

        self.map.prettyDisplay()

        return api.makeMove(self.policyCalc(x, y, valueMap), api.legalActions(state))