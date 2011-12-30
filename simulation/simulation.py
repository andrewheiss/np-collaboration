#!/usr/bin/env python
#
# Nonprofit collaboration simulation
#-------------------------------------
# Copyright 2011-12
# Eva Witesman and Andrew Heiss
# Romney Institute of Public Management
# Brigham Young University
#

import random

#------------------------
# Set up the simulation
#------------------------

# Type the names of the simulated resources
resources = ['A', 'B', 'C', 'D']

# Type the quantities of each resource
resource_quantities = [6, 6, 2, 2]

# Objectives
objs_per_player = 5

# Pseudo database of objectives
objective_names = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2']
objective_quantities = [15, 15, 5, 5, 15, 15, 5, 5]
objective_values = [20, 10, 20, 10, 20, 10, 20, 10]

# Turn on random allocation
shuffle = False


#---------------------------------------------------
# Run the simulation. Do not edit below this line.
#---------------------------------------------------

class Player:
    """A player is the primary element of the simulation and is responsible for maximizing its personal or societal value by trading objectives with other players
    
    Attributes:
        name: The player's name
        resource: The name of a resource (i.e. "A")
        objectives: A dictionary of lists, correposnding to the objective index, objective name, and objective value. (i.e. {0: ['a1', 20], 1: ['a1', 20], 2: ['a1', 20], 3: ['a1', 20], 4: ['a1', 20]})
    
    Returns:
        A new player object
    """
    
    def __init__(self, name, resource, objectives):
        """Creates a new Player object
        
        Creates a player based on resources and objectives created beforehand (i.e. players should be created as part of a loop that allocates resources and objectives).
        
        Args:
            name: The player's name
            resource: The name of a resource (i.e. "A")
            objectives: A list of objective indicies (i.e. [1, 2, 3, 4, 5])
        
        Raises:
            No errors yet... I should probably build some sort of error handling eventually...
        """
        self.name = name
        self.resource = resource
        
        # Build the dictionary of lists
        # {`index`: [`objective name`, `objective value`]}
        self.objectives = {}
        for i in objectives:
            self.objectives[i] = [objs_table[i]['name'], objs_table[i]['value']]
    
    def currentTotal(self):
        """Sum the values of all objectives that match a player's assigned resource"""
        total = 0
        for index, details in self.objectives.items():
            if self.resource == details[0][0].upper():
                total += details[1]
        return total
    
    def dropObjective(self):
        """docstring for dropObjective"""
        pass
    

def listPlayers():
    """Print a list of all the players, their resources, objectives, and scores"""
    print '----- Players -----'
    for i, player in players.items():
        print "Name:", player.name
        print "Points:", player.currentTotal()
        print "Resource:", player.resource
        print "Objectives (index [objective name, objective value]):", "\n\t", player.objectives, "\n"

def listPlayersPseudoTable():
    """Print a list of all the players, their resources, objectives, and scores in a table-like format"""
    print '----- Players -----'
    for i, player in players.items():
        print player.name, player.resource, player.objectives, player.currentTotal()

def printObjectivesPool():
    """List all the objectives and their corresponding value"""
    print '----- Objective pool -----'
    count = 0
    for row in objs_table:
        print "%02d"%count, row['name'], row['value']
        count += 1


# Set up other variables
num_players = sum(resource_quantities)
total_objs = objs_per_player * num_players

# Build the players list and index of objectives
players_list = range(num_players)
objs_index = range(total_objs)

objs_table = []
for i in range(len(objective_names)):
    for j in range(objective_quantities[i]):
        objs_table.append({'name':objective_names[i], 'value':objective_values[i]})


# Initialize empty players dictionary (only a dictionary so it can be indexed)
players = {}

# Shuffle the lists if shuffling is enabled
if shuffle == True:
    random.shuffle(players_list)
    random.shuffle(objs_index)
    random.shuffle(resource_quantities)
    random.shuffle(resources)

# Build the resource pool dictionary
# e.g.: {'A': 6, 'C': 2, 'B': 6, 'D': 2}
resource_pool = dict(zip(resources, resource_quantities))

# `count` keeps track of the number of times a resource is allocated to a player. It will only ever go up to `num_players`
count = 0

# Initialize starting and stopping variables for slicing the objectives list
start = 0
stop = objs_per_player


# Loop through `resource_pool` and assign resources to each player. 
# Player numbers are assigned using `count` as an index to `combined`
for resource, quantity in sorted(resource_pool.items()):
    for i in range(quantity):
        # Create a new player and add it to the players dictionary
        players[players_list[count]] = Player(name="Player %02d"%players_list[count],
                                              resource=resource, 
                                              objectives=objs_index[start:stop:1])
        
        # Increment everything
        count += 1
        start += objs_per_player
        stop += objs_per_player


# Print out players
listPlayers()