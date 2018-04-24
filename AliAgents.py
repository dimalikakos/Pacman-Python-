from pacman import Directions
from game import Agent
import api
import random
import game
import util
import copy
import math

#obstacleY = False
#obstacleX = False



#def find_closest_food(pac_pos,food_list):



class GoWestAgent(Agent):

    def getAction(self, state):
        # Get the actions we can try, and remove "STOP" if that is one of them.
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        if Directions.EAST in legal:
            legal.remove(Directions.EAST)



        if Directions.WEST in legal:

            return api.makeMove(Directions.WEST, legal)
        else:
            return api.makeMove(random.choice(legal), legal)

class HungryTrackerAgent(Agent):

    def __init__(self):
        self.last = Directions.STOP
        self.backsteps = 0
        self.backstep_direction = None
        self.most_recent_direction = None

    #def select_target(self, food_locations,current_direction):
     #   for a_food_location in food_locations:

    def getAction(self, state):

        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        target = (1, 1)
        print target

        print "Food locations: "
        print len(api.food(state))

        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman
        if self.backsteps == 0:
            if pacman[0] >= target[0]:
                if Directions.WEST in legal:
                    return api.makeMove(Directions.WEST, legal)
            else:
                if Directions.EAST in legal:
                    return api.makeMove(Directions.EAST, legal)

            if pacman[1] >= target[1]:
                if Directions.SOUTH in legal:
                    return api.makeMove(Directions.SOUTH, legal)
            else:
                if Directions.NORTH in legal:
                    return api.makeMove(Directions.NORTH, legal)
            self.backsteps = 2
            self.backstep_direction = random.choice(legal)

        self.backsteps -= 1
        return api.makeMove(self.backstep_direction, legal)


class HungryTracker2Agent(Agent):


    def __init__(self):
        self.obstacle_Y = False
        self.obstacle_Y_direction = None
        self.obstacle_X = False
        self.variable_N = Directions.NORTH
        self.variable_W = Directions.WEST



    def move_pacman(self,pac_dir,axis,legal,pacman,target):
        if pacman[axis] > target[axis]:
            if pac_dir in legal:
                return api.makeMove(pac_dir, legal)
        elif pacman[axis] < target[axis]:
            if pac_dir in legal:
                return api.makeMove(pac_dir.REVERSE, legal)

    def getAction(self, state):

        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        target = (1, 1)
        print target

        print "Food locations: "
        print len(api.food(state))

        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman

        self.move_pacman(self.variable_W, 0, legal, pacman, target)
        self.move_pacman(self.variable_N, 1, legal, pacman, target)

        if pacman[0] is target[0] and pacman[1] < target[1] and Directions.NORTH not in legal and not self.obstacle_Y:
            self.obstacle_Y = True
            legal.remove(Directions.SOUTH)
            self.obstacle_Y_direction = random.choice(legal)






class HungryTracker3Agent(Agent):

    def __init__(self):
        self.trapped = False
        self.backsteps = 0
        self.backstep_direction = None
        self.obstacle_in_direction_X = 0
        self.obstacle_in_direction_Y = 0
        self.target_direction_Y = None
        self.target_direction_X = None
        self.obstacle_Y_direction = None
        self.obstacle_X_direction = None
        self.find_corners = False
        self.corner_mode = False
        self.map_mode = False
        self.non_wall_coordinates = []
        self.corners = []
        self.corners_backup = []
        self.target = (10, 1)
        self.escape_mode = False
        self.escape_corners = []
        self.escape_steps = 0

    def final(self, state):
        self.trapped = False
        self.backsteps = 0
        self.backstep_direction = None
        self.obstacle_in_direction_X = 0
        self.obstacle_in_direction_Y = 0
        self.target_direction_Y = None
        self.target_direction_X = None
        self.obstacle_Y_direction = None
        self.obstacle_X_direction = None
        self.find_corners = False
        self.corner_mode = False
        self.map_mode = False
        self.non_wall_coordinates = []
        self.corners = []
        self.corners_backup = []
        self.target = (10, 1)
        self.escape_mode = False
        self.escape_corners = []
        self.escape_steps = 0



    def find_closest_coordinate_to_pacman(self,state,pacman,list):
        print "FOUND"
        shortest_distance = None
        for list_item in list:
            distance = util.manhattanDistance(pacman, list_item)
            if distance <= shortest_distance or shortest_distance is None:
                shortest_distance = distance
                closest_point = list_item
        if 'closest_point' in locals():
            self.target = closest_point
        else:
            self.target = random.choice(self.corners_backup)
        print 'HERE IS NEW CALCULATED TARGET', self.target

    def initialize_map(self, walls, min_x, max_x, min_y, max_y):
        coordinate = []
        for i in range(min_x, max_x):
            for y in range(min_y, max_y):

                if (i, y) not in walls:
                    self.non_wall_coordinates.append((i, y))
                else:
                    print "this coordinate: ", coordinate
                coordinate = []

        print "HERE ARE ALL THE NON WALL COORDINATES", self.non_wall_coordinates

    def initialize_waypoints(self,walls):
        # IF ALL MAPS HAVE 4 CORNERS, THIS WILL WORK
        max_x = min_x = max_y = min_y = None
        for coordinate in walls:
            if max_x is None or coordinate[0] > max_x:
                max_x = coordinate[0]
            if min_x is None or coordinate[0] < min_x:
                min_x = coordinate[0]
            if max_y is None or coordinate[1] > max_y:
                max_y = coordinate[0]
            if min_y is None or coordinate[1] < min_y:
                min_y = coordinate[0]
        min_x += 1
        min_y += 1
        max_x -= 1
        max_y -= 1
        self.corners.append((int(min_x), int(min_y)))
        self.corners.append((int(min_x), int(max_y)))
        self.corners.append((int(max_x), int(min_y)))
        self.corners.append((int(max_x), int(max_y)))
        self.corners_backup = list(self.corners)
        self.find_corners = True

        self.initialize_map(walls, min_x, max_x, min_y, max_y)

    def get_escape_routes(self, legal, pacman,ghost_positions):
        escape_routes = list(legal)
        for i in range(0, 1):
            if pacman[0] < ghost_positions[0][0] and Directions.EAST in legal:
                escape_routes.remove(Directions.EAST)
            elif pacman[0] > ghost_positions[0][0] and Directions.WEST in legal:
                escape_routes.remove(Directions.WEST)
            if pacman[1] > ghost_positions[0][1] and Directions.SOUTH in legal:
                escape_routes.remove(Directions.SOUTH)
            elif pacman[1] < ghost_positions[0][1] and Directions.NORTH in legal:
                escape_routes.remove(Directions.NORTH)
            return escape_routes

    def make_escape_target_list(self,index1,index2): # REMOVES FROM ESCAPE CORNERS THE CORNERS THAT PACMAN SHOULD NOT RUN TOWARDS
        if self.corners_backup[index1] in self.escape_corners:
            self.escape_corners.remove(self.corners_backup[index1])
        if self.corners_backup[index2] in self.escape_corners:
            self.escape_corners.remove(self.corners_backup[index2])


    def get_escape_routes_V2(self, legal, pacman,ghost_positions):
        escape_routes = list(legal)
        print "ESCAPE CORNERS", self.escape_corners
        for i in range(0, 1):
            if pacman[0] < ghost_positions[0][0] and Directions.EAST in legal:
                escape_routes.remove(Directions.EAST)
                self.make_escape_target_list(2, 3)
            elif pacman[0] > ghost_positions[0][0] and Directions.WEST in legal:
                escape_routes.remove(Directions.WEST)
                self.make_escape_target_list(0, 1)
            if pacman[1] > ghost_positions[0][1] and Directions.SOUTH in legal:
                escape_routes.remove(Directions.SOUTH)
                self.make_escape_target_list(0, 2)
            elif pacman[1] < ghost_positions[0][1] and Directions.NORTH in legal:
                escape_routes.remove(Directions.NORTH)
                self.make_escape_target_list(1, 3)
            return escape_routes

    def getAction(self, state):
        legal = api.legalActions(state)

        if not self.find_corners:
            self.initialize_waypoints(api.walls(state))

        if Directions.STOP in legal:
            legal.remove(Directions.STOP)
        #print "TARGET:", self.target
        #print "LEGAL: ", legal
        #print "Food locations: "
        #print food_locations
        pacman = api.whereAmI(state)
        #print "Pacman position: ", pacman
        ghost_positions = api.ghosts(state)
        print "Ghost positions:", ghost_positions

        if pacman in self.non_wall_coordinates:
            self.non_wall_coordinates.remove(pacman)
        print "HERE ARE COORDINATES LEFT:", len(self.non_wall_coordinates)

        #print "HERE IS TARGET:", self.target

        #print "HERE ARE WALLS:",api.walls(state)
        #print "HERE ARE CORNERS:", self.corners

        if self.escape_mode:
            self.escape_steps -= 1
            print "ESCAPE STEPS ARE: ", self.escape_steps
            if self.escape_steps == 0:
                self.escape_mode = False
                self.corner_mode = True



        if len(ghost_positions) > 0: #IF IT SENSES TWO GHOSTS AND IS MOVING, ONE IS VERY CLOSE< THE OTHER IS FAR AWAY. PACMAN ALWAYS FACES A CORNER WHEN HE GOES IN IT
            self.backsteps = 0  #STOP BACKSTEP MODE
            self.obstacle_in_direction_X = False  # IGNORE FINDING OBSTACLE TO TARGET
            self.obstacle_in_direction_Y = False  # IGNORE FINDING OBSTACLE TO TARGET
            self.escape_mode = True
            self.escape_corners = list(self.corners_backup)
            self.escape_steps = 4

            escape_routes = list(self.get_escape_routes_V2(legal, pacman, ghost_positions))
            escape_corner = random.choice(self.escape_corners)
            self.escape_corners.remove(escape_corner)
            self.target = escape_corner
            if escape_routes:
                return api.makeMove(random.choice(escape_routes), legal)
            else:
                print "MAKING RANDOM MOVE"
                return api.makeMove(random.choice(legal), legal)








        if len(api.food(state)) > 0 and (self.map_mode or self.corner_mode):
            self.corner_mode = False
            self.map_mode = False
            self.find_closest_coordinate_to_pacman(state, pacman, api.food(state))

        if pacman[0] is self.target[0] and pacman[1] is self.target[1]:
            if len(api.food(state)) > 0:
                self.find_closest_coordinate_to_pacman(state, pacman, api.food(state))
            elif self.corners:
                if pacman in self.corners and self.corner_mode:
                    self.corners.remove(pacman)
                    print "REMOVED CORNER"
                self.corner_mode = True
                if self.corners:
                    self.target = random.choice(self.corners)
                else:
                    print "MAP MODE ON"
                    self.map_mode = True
                    self.find_closest_coordinate_to_pacman(state, pacman, self.non_wall_coordinates)
            else:
                print "MAP MODE ON"
                self.map_mode = True
                self.find_closest_coordinate_to_pacman(state, pacman, self.non_wall_coordinates)

        if pacman[1] < self.target[1]:
            self.target_direction_X = Directions.NORTH
        else:
            self.target_direction_X = Directions.SOUTH
        if pacman[0] < self.target[0]:
            self.target_direction_Y = Directions.EAST
        else:
            self.target_direction_Y = Directions.WEST

        #IF TRAPPED, GET OUT OF TRAPPED, WE ARE ASSUMING THAT THAT NORTH IS ALWAYS WAY OUT OF TRAP.
        if self.trapped:
            self.trapped = False
            self.target = random.choice(self.corners_backup)
            self.corner_mode = True
            return api.makeMove(Directions.NORTH, legal)

        #CONTINUE BACKSTEPPING TO RECALCULATE OBSTACLE ROUTE
        if self.backsteps is not 0 and self.backstep_direction in legal:
            self.backsteps -= 1
            return api.makeMove(self.backstep_direction, legal)

        #OBSTACLE MODE MOVEMENT HERE
        if self.obstacle_in_direction_X:
            print "LOOKING FOR DIRECTION: ", self.target_direction_X
            if self.target_direction_X in legal:
                self.obstacle_in_direction_X = False
                return api.makeMove(self.target_direction_X, legal)
            else:
                if self.obstacle_Y_direction in legal:
                    return api.makeMove(self.obstacle_Y_direction, legal)
        elif self.obstacle_in_direction_Y:
            print "OBSTACLE IN DIRECTION Y MODE ON. WAITING FOR: ", self.target_direction_Y
            if self.target_direction_Y in legal:
                self.obstacle_in_direction_Y = False
                print "OBSTACLE OVERCOME"
                return api.makeMove(self.target_direction_Y, legal)
            else:
                if self.obstacle_X_direction in legal:
                    return api.makeMove(self.obstacle_X_direction, legal)
        else:
            #NORMAL MOVEMENT HERE
            if pacman[0] > self.target[0]:  # X IS HERE
                self.target_direction_X = Directions.WEST
                if self.target_direction_X in legal:
                    return api.makeMove(self.target_direction_X, legal)
            elif pacman[0] < self.target[0]:
                self.target_direction_X = Directions.EAST
                if self.target_direction_X in legal:
                    return api.makeMove(self.target_direction_X, legal)
            if pacman[1] > self.target[1]:  # Y IS HERE
                self.target_direction_Y = Directions.SOUTH
                if self.target_direction_Y in legal:
                    return api.makeMove(self.target_direction_Y, legal)
            elif pacman[1] < self.target[1]:
                self.target_direction_Y = Directions.NORTH
                if self.target_direction_Y in legal:
                    return api.makeMove(self.target_direction_Y, legal)


        #BELOW IS THE OBSTACLE BYPASS CODE
        temp_legal = copy.copy(legal)
        if pacman[0] is self.target[0] and self.target_direction_X not in legal and self.target_direction_X:
            self.obstacle_in_direction_X = True
            if self.target_direction_X is Directions.NORTH and Directions.SOUTH in temp_legal:
                temp_legal.remove(Directions.SOUTH)
            elif Directions.NORTH in temp_legal:
                temp_legal.remove(Directions.NORTH)
            self.obstacle_Y_direction = random.choice(temp_legal)
            return api.makeMove(self.obstacle_Y_direction, legal)
        elif pacman[1] is self.target[1] and self.target_direction_Y not in legal and self.target_direction_Y:
            self.obstacle_in_direction_Y = True
            if self.target_direction_Y is Directions.EAST and Directions.WEST in temp_legal:
                temp_legal.remove(Directions.WEST)
            elif Directions.EAST in temp_legal:
                temp_legal.remove(Directions.EAST)
            self.obstacle_X_direction = random.choice(temp_legal)
            return api.makeMove(self.obstacle_X_direction, legal)

        if len(legal) > 1:
            self.backsteps = 1
            self.backstep_direction = random.choice(legal)
            print "BACKSTEPPING", 60*"="
            return api.makeMove(self.backstep_direction, legal)
        else:
            self.trapped = 2
            return api.makeMove(random.choice(legal), legal)


class CornerSeekingAgent(Agent):

    def __init__(self):
        self.last = Directions.STOP
        self.backsteps = 0
        self.backstep_direction

    def getAction(self, state):
        legal = api.legalActions(state)
        if Directions.STOP in legal:
            legal.remove(Directions.STOP)

        #SELECT TARGET
        target = api.food(state)[0]
        print target

        pacman = api.whereAmI(state)
        print "Pacman position: ", pacman
        if self.backsteps == 0:
            if pacman[0] >= target[0]:
                if Directions.WEST in legal:
                    return api.makeMove(Directions.WEST, legal)
            else:
                if Directions.EAST in legal:
                    return api.makeMove(Directions.EAST, legal)

            if pacman[1] >= target[1]:
                if Directions.SOUTH in legal:
                    return api.makeMove(Directions.SOUTH, legal)
            else:
                if Directions.NORTH in legal:
                    return api.makeMove(Directions.NORTH, legal)
            self.backsteps = 2                                      #IT REACHES HERE ONLY ONCE BOTH DIRECTIONS IT WANTS TO GO ARE ILLEGAL, SO: BACKSTEP 2 STOPS TOWARDS RANDOM LEGAL DIRECTION
            self.backstep_direction = random.choice(legal)

        self.backsteps -= 1
        return api.makeMove(self.backstep_direction, legal)
























