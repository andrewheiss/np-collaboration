#!/usr/bin/env python
import random

#------------------------
# Set up the simulation
#------------------------

# Type the number of simulated players
num_players = 16

# Type the names of the simulated resources
resources = ['A', 'B', 'C', 'D']

# Type the quantities of each resource
# `quantities` must equal the number of players
quantities = [6, 6, 2, 2]

# Turn on random allocation
shuffle = False



#---------------------------------------------------
# Run the simulation. Do not edit below this line.
#---------------------------------------------------

# Build the players list
players = range(num_players)

# Shuffle the lists if shuffling enabled
if shuffle == True:
    random.shuffle(players)
    random.shuffle(quantities)
    random.shuffle(resources)

# Build the resource pool dictionary
# e.g.: {'A': 6, 'C': 2, 'B': 6, 'D': 2}
resource_pool = dict(zip(resources, quantities))

# Initialize empty combined dictionary
combined = {}

# `count` keeps track of the number of times a resource is allocated to a player. It should only ever go up to `num_players` as long as the quantities of resources are set correctly
count = 0

# Loop through `resource_pool` and assign resources to each player. 
# Player numbers are assigned using `count` as an index to `combined`
for resource, quantity in resource_pool.items():
    for i in range(quantity):
        combined[players[count]] = resource
        count += 1

print combined