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
objectives = ['a1', 'a2', 'b1', 'b2', 'c1', 'c2', 'd1', 'd2']

objective_quantities = [15, 15, 5, 5, 15, 15, 5, 5]
objective_values = [20, 10, 20, 10, 20, 10, 20, 10]


# Turn on random allocation
shuffle = False



#---------------------------------------------------
# Run the simulation. Do not edit below this line.
#---------------------------------------------------

# Build the players list
num_players = sum(resource_quantities)
players = range(num_players)

# Shuffle the lists if shuffling is enabled
if shuffle == True:
    random.shuffle(players)
    random.shuffle(resource_quantities)
    random.shuffle(resources)

# Build the resource pool dictionary
# e.g.: {'A': 6, 'C': 2, 'B': 6, 'D': 2}
resource_pool = dict(zip(resources, resource_quantities))

# Initialize empty combined dictionary
combined = {}

# `count` keeps track of the number of times a resource is allocated to a player. It should only ever go up to `num_players` as long as the quantities of resources are set correctly
count = 0

# Loop through `resource_pool` and assign resources to each player. 
# Player numbers are assigned using `count` as an index to `combined`
for resource, quantity in sorted(resource_pool.items()):
    for i in range(quantity):
        combined[players[count]] = resource
        count += 1

print combined