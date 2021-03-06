__author__ = 'Owner'
import random
import math
import sys
sys.path.append("/Users/Chris/Programming/AIA/up-antics_02Sep2013/Antics")
from Player import *
from Constants import *
from Construction import CONSTR_STATS
from Ant import *
from AIPlayerUtils import *
from Move import Move
from Building import *
from GameState import *
from Location import *
import sys

##
#StateNode
#Description: A node for a tree that describes a given state for Antics
#
#Variables:
# parent - the parent node of this StateNode
# children - a list of all of this node's children
# arrivalMove - the move that brought the game to this state
# newState - the state that arrival move would produce, based on its parent
# evaluation - the score [0,1] that represents newState
#
#NOTE: This is an anonymous class
#
##
class StateNode:
        ##
        #__init__
        #Description: Initializes the StateNode object
        #
        #Parameters:
        # parentNode - the node that is indended to be the new node's parent
        # move - the move that will be used to create the new state
        #
        #
        ##
        def __init__(self, move, newState, qualOfState, parentNode):
            #save the parameters for later reference
            self.parent = parentNode
            self.arrivalMove = move
            #create and evaluate the state that will be represented by this node
            self.currentState = newState
            self.evaluation = qualOfState
            #initialize the array for children
            self.children = []
            #go and put self in parent's children list, if it has a parent
            if not parentNode == None:
                self.parent.children.append(self)

##
#AIPlayer
#Description: The responsbility of this class is to interact with the game by
#deciding a valid move based on a given game state. This class has methods that
#will be implemented by students in Dr. Nuxoll's AI course.
#
#Variables:
#   playerId - The id of the player.
##
class AIPlayer(Player):

    #__init__
    #Description: Creates a new Player
    #
    #Parameters:
    #   inputPlayerId - The id to give the new player (int)
    ##
    def __init__(self, inputPlayerId):
        super(AIPlayer,self).__init__(inputPlayerId, "The Hard Easy")
        self.foodSwitch = False
        self.chosenFoodCoords = None

    ##
    # distance
    #
    # Description: calculates the length between coordinates by sum of deltaX and deltaY of two
    # coordinates on the board (not the hypotenuse)
    #
    # Parameters:
    #   tuple1, tuple2 - coordinates between which distance is measured (tuple), (tuple)
    #
    # Return: the sum distance of the two legs between the coordinates(int)
    #
    def distance(self, tuple1, tuple2):
        return int(math.fabs(tuple1[0]-tuple2[0]) + math.fabs(tuple1[1]-tuple2[1]))

    ##
    #bestNode
    #Description: Determines the best node from a selection of nodes
    #
    #Parameters:
    #   nodeList: a list of nodes
    #
    #Return Value: returns the node with the highest score
    #
    ##
    def bestNode(self, nodeList):
        #Initialize variables that will determine the best node
        highestEval = 0
        bestNode = None
        #counter is used to ensure that initial values are put in bestNode
        #and highestEval
        counter = 0

        #determine the best node
        for node in nodeList:
            if counter == 0:
                bestNode = node
                highestEval = node.evaluation

            elif node.evaluation >= highestEval:
                bestNode = node
                highestEval = node.evaluation

            counter+=1

        return bestNode

    ##
    #exploreTree
    #Description: Explores the tree and searches for the best node
    #
    #Parameters:
    #   currentState - The state that the move will be applied to
    #   PID - The current Player's ID
    #   depth - the current depth of the search
    #   depthLimit - the furthest down that the search will look to find the best move
    #   parentNode - the node that represents currentState's game state
    #
    #Return Value: the highest scoring node found
    ##
    def exploreTree(self, currentState, PID = 0, depth = 0, depthLimit = 1, parentNode = None):
        enoughIsEnough = 1
        bestSeen = parentNode
        #base Case
        if depth == depthLimit:
            #look at all the pretty nodes on this level
            nodesToChooseFrom = []
            for move in listAllLegalMoves(currentState):
                newState = self.simulateMove(move, currentState.fastclone())
                qualOfState = self.stateQuality(newState)
                if qualOfState > parentNode.evaluation and qualOfState > bestSeen.evaluation:
                    bestSeen = StateNode(move, newState, qualOfState, parentNode)
            bestTuple = (bestSeen, bestSeen.evaluation)
            return bestTuple
        #recursive Case
        else:
            depth += 1
            nodeList = []
            for move in listAllLegalMoves(currentState):
                newState = self.simulateMove(move, currentState.fastclone())
                qualOfState = self.stateQuality(newState)
                if qualOfState > parentNode.evaluation and qualOfState > bestSeen.evaluation:
                    bestSuccessor = self.exploreTree(bestSeen.currentState, self.playerId, depth, depthLimit, bestSeen)
                    if bestSuccessor[1] > bestSeen.evaluation:
                        bestSeen = bestSuccessor[0]

            bestTuple = bestSeen, bestSeen.evaluation
            return bestTuple


    ##
    #getMove
    #Description: Gets the next move from the Player.
    #
    #Parameters:
    #   currentState - The state of the current game waiting for the player's move (GameState)
    #
    #Return: The Move to be made
    ##
    def getMove(self, currentState):
        move = None
        qualOfState = 0
        parentNode = None
        node = StateNode(move, currentState, qualOfState, parentNode)
        resultantTuple = self.exploreTree(currentState, self.playerId, 0, 2, node)
        return resultantTuple[0].arrivalMove


    ##
    #simulateMove
    #
    #Description: takes a single move and a copy of the gameState and reflects the details of the
    #  move onto the new gameState
    #
    #Parameters:
    #   move: the move that is affecting the gameState (Move)
    #   newState: a copy of the state of the game, which is being changed by the move (GameState)
    #
    #Return: newState, a copy of the gameState that has been altered as per the move
    #
    def simulateMove(self, move, newState):

       #designating the inventories to variables
        for inv in newState.inventories:
            if inv.player == newState.whoseTurn:
                myInv = inv
            else:
                theirInv = inv
        #if an ant is moved
        if move.moveType == MOVE_ANT:
            #clarifying where the ant is and where its going
            src = move.coordList[0]
            dst = move.coordList[-1]
            #assigns the ant to myAnt and changes its coords in the inventory
            for ant in myInv.ants:
                if ant.coords == src:
                    ant.coords = dst
                    myAnt = ant
            #Prepare to attack an enemy
            enemyAnts = getAntList(newState, PLAYER_ONE, (QUEEN, WORKER, DRONE, SOLDIER, R_SOLDIER))
            enemyAntsCoords = []
            for ant in enemyAnts:
                enemyAntsCoords.append(ant.coords)
            inRange = self.getAttack(newState, myAnt, enemyAntsCoords)
            #attacks the inRange ant by lowering its health by one
            if inRange is not None:
                #lowers ant health by attack power of myAnt
                attackPower = UNIT_STATS[myAnt.type][ATTACK]
                for ant in theirInv.ants:
                    if ant.coords == inRange:
                        ant.health -= attackPower
                #removes the ant if its health is 0
                if getAntAt(newState, inRange).health <= 0:
                    deadAnt = getAntAt(newState, inRange)
                    theirInv.ants.remove(deadAnt)

            #finds rules for ants sitting on food, tunnels or anthills
            for ant in myInv.ants:
                constr = getConstrAt(newState, ant.coords)
                #narrows rule to apply only for workers sitting on a construction
                if ant.type == WORKER and constr is not None:
                    #if on my side of the board, compensate for food transportation
                    if ant.coords[1] < 4:
                        if constr.type == FOOD and not ant.carrying:
                            ant.carrying = True
                        elif constr.type == (TUNNEL or ANTHILL) and ant.carrying:
                            ant.carrying = False
                            inv.foodCount += 1
                    #if the worker is sitting on an anthill or tunnel on the other side of the
                    #board, modify capture health
                    elif constr.type == (TUNNEL or ANTHILL):
                        if constr.captureHealth > 1:
                            constr.captureHealth -= 1
                        #remove if the constr is at health one
                        else:
                            theirInv.constrs.remove(constr)

        #deals with build actions
        if move.moveType == BUILD:
            loc = move.coordList[0]
            #deals with building a tunnel
            if move.buildType == TUNNEL and myInv.foodCount >= 10:
                #adjusts food count
                myInv.foodCount -= CONSTR_STATS[TUNNEL][COST]
                #creates the new building as per specified
                newBuilding = Building(loc, TUNNEL, newState.whoseTurn)
                #fits newBuilding into the board and inventory
                myInv.constrs.append(newBuilding)
            #deals with building an ant, works the same as tunnel except with ant objects
            else:
                myInv.foodCount -= UNIT_STATS[move.buildType][COST]
                newAnt = Ant(loc, move.buildType, newState.whoseTurn)
                #newState.board[loc[1]][loc[1]].ant = newAnt
                myInv.ants.append(newAnt)
        #update the inventories and return the state
        for inv in newState.inventories:
            if inv.player == newState.whoseTurn:
                inv = myInv
            else:
                inv = theirInv

        for inv in newState.inventories:
            if inv.player == newState.whoseTurn:
                myInv = inv

        for ant in myInv.ants:
            ant.hasMoved = False
        return newState


    ##
    #stateQuality
    #
    #Description: Decided the "quality" of a state
    #
    #Parameters:
    #   newState - a copy of the state after a move that might be taken
    #
    #Return: a value quantifying the quality of the state <= 1 and >= 0 (double)
    #
    ##
    def stateQuality(self, newState):
        #The quality of the state is defined as the average distance to the enemy anthill
        return self.distToEnemyQueen(newState)

    ##
    #distToEnemyQueen
    #
    #Description: using the distance to the enemy anthill, determines a score
    #
    #Parameters:
    #   currentState - the state to be evaluated
    #
    #Return Value: a score, as a float
    #
    ##
    def distToEnemyQueen(self, currentState):
        #Retrieve the inventories of each player
        for inv in currentState.inventories:
            if inv.player == currentState.whoseTurn:
                myInv = inv
            elif inv.player == PLAYER_ONE:
                theirInv = inv

        #Get DAT ANTHILL
        eneQueen = theirInv.getQueen()

        #Check the number of spaces to reach the enemy anthill
        distances = []
        for ant in myInv.ants:
            distances.append(stepsToReach(currentState, ant.coords, eneQueen.coords))

        #Convert that distance into points
        points = 0
        for dist in distances:
            points += (1.0-(dist/20.0))
        totalPoints = points/len(myInv.ants)
        #don't build ants brah.
        if len(myInv.ants) > 2:
            totalPoints *= .5
        return totalPoints

    ##
    #getPlacement
    #
    #Description: called during setup phase for each Construction that
    #   must be placed by the player.  These items are: 1 Anthill on
    #   the player's side; 1 tunnel on player's side; 9 grass on the
    #   player's side; and 2 food on the enemy's side.
    #
    #Parameters:
    #   construction - the Construction to be placed.
    #   currentState - the state of the game at this point in time.
    #
    #Return: The coordinates of where the construction is to be placed
    ##
    def getPlacement(self, currentState):
        numToPlace = 0
        #implemented by students to return their next move
        if currentState.phase == SETUP_PHASE_1:    #stuff on my side
            numToPlace = 11
            moves = []
            for i in range(0, numToPlace):
                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on your side of the board
                    y = random.randint(0, 3)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        elif currentState.phase == SETUP_PHASE_2:   #stuff on foe's side
            numToPlace = 2
            moves = []
            for i in range(0, numToPlace):

                move = None
                while move == None:
                    #Choose any x location
                    x = random.randint(0, 9)
                    #Choose any y location on enemy side of the board
                    y = random.randint(6, 9)
                    #Set the move if this space is empty
                    if currentState.board[x][y].constr == None and (x, y) not in moves:
                        move = (x, y)
                        #Just need to make the space non-empty. So I threw whatever I felt like in there.
                        currentState.board[x][y].constr == True
                moves.append(move)
            return moves
        else:
            return [(0, 0)]


    ##
    #getAttack
    #Description: Gets the attack to be made from the Player
    #
    #Parameters:
    #   currentState - A clone of the current state (GameState)
    #   attackingAnt - The ant currently making the attack (Ant)
    #   enemyLocation - The Locations of the Enemies that can be attacked (Location[])
    ##
    def getAttack(self, currentState, attackingAnt, enemyLocations):
        #Attack a random enemy
        return enemyLocations[random.randint(0, len(enemyLocations) - 1)]