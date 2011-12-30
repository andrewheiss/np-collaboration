#!/usr/bin/env python
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
    """docstring for Player"""
    def __init__(self, name, resource, objectives):
        self.name = name
        self.resource = resource
        self.objectives = objectives
        
        # Build the dictionary of lists
        # {`index`: [`objective name`, `objective value`]}
        self.objectives = {}
        for i in objectives:
            self.objectives[i] = [objs_table[i]['name'], objs_table[i]['value']]
    
    def currentTotal(self):
        """docstring for currentTotal"""
        pass
    
    def dropObjective(self):
        """docstring for dropObjective"""
        pass

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

# print objs_table[0]['name']
# for row in objs_table:
#     print row['name'], row['value']



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



# Print out players and their assignments
print '----- Players -----'
for i, p in players.items():
    total = 0
    obj_names = []
    for i in p.objectives:
        total += objs_table[i]['value']
        obj_names.append(objs_table[i]['name'])
    print p.name, p.resource, p.objectives, obj_names, total
