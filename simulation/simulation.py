#!/usr/bin/env python
# 
# Nonprofit collaboration simulation
#-------------------------------------
# Copyright 2011-12
# Eva Witesman and Andrew Heiss
# Romney Institute of Public Management
# Brigham Young University
#

import collections
import itertools
import string
import random

#------------------------
# Set up the simulation
#------------------------

num_players = 16
num_resources = 4
num_objs_per_player = 5
value_high = 20
value_low = 10
approximate_high_low_resource_ratio = 3
approximate_high_low_objective_ratio = 3

# Turn on random allocation
shuffle = True


#---------------------------------------------------
#---------------------------------------------------
# Run the simulation. Do not edit below this line.
#---------------------------------------------------
#---------------------------------------------------

#----------------------
# Objects and methods
#----------------------

class Player():
    """A player is the primary element of the simulation and is responsible for maximizing its personal or societal value by trading objectives with other players
    
    Attributes:
        name: The player's name
        resource: The name of a resource (i.e. "A")
        objectives: A dictionary of lists, correposnding to the objective index, objective name, and objective value. (i.e. {0: ['a1', 20], 1: ['a1', 20], 2: ['a1', 20], 3: ['a1', 20], 4: ['a1', 20]})
    
    Returns:
        A new player object
    """

    def __init__(self, sim, name, resource, objectives):
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
    
    def joinTeam(self, team):
        """Add a player to a team... eventually only after checking to see if the alliance is beneficial and after dropping an objective"""
        # Drop an objective
        self.team.removePlayer(self)    # Leave current team
        team.addPlayer(self)            # Join new team
        self.team = team                # Reassign new team to player attributes
    
    def setInitialTeam(self, team):
        self.team = team
    
    def report(self):        
        objectives = ', '.join('%s' % obj[0] for obj in self.objectives.values())
        print "I am %s; I have resource %s; I have objectives %s; I'm on team %s; and my total value is %s."%(self.name, self.resource, objectives, self.team.name, self.currentTotal()) 
        yield hold, self
        

class Community:
    """docstring for World"""
    def __init__(self, players):
        self.players = players
    
    def total(self):
        """docstring for globalTotal"""
        total = 0
        for i, player in players.items():
            total += player.currentTotal()
        return total


class ResourcePool:
    """Creates a pool of resources with high and low distributions according to the frequency in `approximate_high_low_resource_ratio`
    
    For example, if there are 16 players, with 4 different types of objectives, and an approximate ratio of 3:1, the pool will be a dictionary distributed like so:
    {'A': 6, 'B': 6, 'C': 2, 'D': 2}
    with A and B as high frequency resources and C and D as low frequency
    
    Attributes:
        high: A string of the high frequency resources (e.g. "AB")
        low: A string of the low frequency resources (e.g. "CD")
        pool: A dictionary structured like {'resource name': quantity, ...}
    
    Returns: 
        A resource pool object
    """
    def __init__(self, resources, players):
        """Create the resource pool object
        
        Args:
            resources: The number of resource types
            players: The number of players in the simulation
        """
        divided = self.divide_high_low(resources)
        self.high = divided.high
        self.low = divided.low
        r = self.create_distribution_ratios(divided.low, divided.high)
        self.pool = dict(sorted(collections.Counter(itertools.islice(r, players)).items()))

    def create_distribution_ratios(self, prop_low, prop_high):
        """Add a fraction priority to the given high frequency resources

        Args:
            prop_high: A string of letters that will have a high frequency distribution (e.g. "AB")
            prop_low: A string of letters that will have a low frequency distribution (e.g. "CDE")
        """
        prop_high_adjusted = prop_high * approximate_high_low_resource_ratio
        while True:
            for resource in prop_low:
                yield resource
            for resource in prop_high_adjusted:
                yield resource

    def divide_high_low(self, resources):
        """Divide the provided resources into high and low frequencies
        
        Args:
            resources: The number of resource types
        
        Returns:
            A named tuple of high and low frequency resources (e.g. (high='AB', low='CD'))
        """
        DivdedResources = collections.namedtuple('Resources', ['high', 'low'])
        letters = string.ascii_uppercase[:resources]
        high_count = resources // 2

        if shuffle == True:
            letters = ''.join(random.sample(letters, len(letters)))

        prop_high, prop_low = letters[:high_count], letters[high_count:]
        return DivdedResources(prop_high, prop_low)


class ObjectivePool:
    """Create a pool of objectives that corresponds to the distribution of the resource pool. 
    
    The objectives that correspond to the two frequencies of resources (high and low) are split into two types of prevalence (high and low). If there are two high frequency resources A and B, there will be four objectives: a1, a2, b1, and b2. 
    
    A subscript of 1 indicates high value, while a subscript of 2 indicates low value. 
    The objectives for resource A will be more prevalent than the objectives for resource B according to the ratio provided in `approximate_high_low_objective_ratio`
    
    For example, with a resource pool of {'A': 6, 'B': 6, 'C': 2, 'D': 2} and five objectives per player, the high frequency resources A and B will be split into highly prevalent objectives (15 a1s and a2s) and not-as-prevalent objectives (5 b1s and b2s). Low frequency resources will be split similarly (15 c1/2s, 5 d1/2s). 
    
    Attributes:
        num_objs: The total number of objectives in the pool (number of players * number of objectives per player)
        pool: A dictionary of objective distriubtions (e.g. {'a1': 15, 'a2': 15, 'b1': 5, 'b2': 5, 'c2': 15, 'c1': 15, 'd2': 5, 'd1': 5})
        table: A list of dictionaries with each objective name and value (e.g. [{'name': 'a1', 'value': 20},... {'name': 'c2', 'value': 10},...])
    
    Returns: 
        An objective pool object
    """
    def __init__(self, resource_pool):
        """Create the objective pool object
        
        Args:
            resource_pool: A ResourcePool object
        """
        self.num_objs = num_players * num_objs_per_player
        
        # Switch the first and last elements of the high and low frequency lists
        list_high = list(resource_pool.high)
        list_low = list(resource_pool.low)
        
        # Calculate half of list length
        temp1 = len(list_high)/2 
        temp2 = len(list_low)/2
        
        # Create new lists based on slices of the high and low lists
        new_high = list_high[:temp1] + list_low[:temp2]
        new_low = list_high[temp1:] + list_low[temp2:]

        # Split all the resources into two objectives
        # Converts "A" to "a1" and "a2"
        objectives_high = []
        for i in new_high:
            for j in range(1,3):
                objectives_high.append(i.lower() + str(j))

        objectives_low = []
        for i in new_low:
            for j in range(1,3):
                objectives_low.append(i.lower() + str(j))

        # Distribute the objectives to the newly created objectives
        o = self.create_distribution_ratios(objectives_low, objectives_high)
        self.pool = dict(sorted(collections.Counter(itertools.islice(o, self.num_objs)).items()))

        # Create a list of named dictionary pairs for each objective in the pool
        objs_table = []
        for i in self.pool.items():
            for j in range(i[1]):
                if int(i[0][1]) == 1: # if the objective's subscript is 1 (e.g. "a1")
                    value = value_high
                else:
                    value = value_low
                objs_table.append({'name':i[0], 'value':value})
        self.table = objs_table

    def create_distribution_ratios(self, prop_low, prop_high):
        """Add a fraction priority to the given high frequency resources

        Args:
            prop_high: A string of letters that will have a high frequency distribution (e.g. "AB")
            prop_low: A string of letters that will have a low frequency distribution (e.g. "CDE")
        """
        prop_high_adjusted = prop_high * approximate_high_low_objective_ratio
        while True:
            for resource in prop_low:
                yield resource
            for resource in prop_high_adjusted:
                yield resource


# Faux pretty printing functions
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


class Team:
    """A team is a collection of players that have decided to collaborate in order to achieve higher personal or societal value. 
    
    Attributes:
        name: The team's name
        players: A list of player objects that are part of the team
    
    Returns:
        A new team object
    """
    def __init__(self, player, name):
        """Creates a new team object
        
        Creates a new team consisting of exactly one player
        
        Args:
            name: The player's name
            player: A single player object
        
        Raises:
            No errors yet... 
        """
        self.name = name
        self.players = []
        self.players.append(player)
    
    def playerCount(self):
        """Count how many players there are."""
        return len(self.players)
    
    def totalValue(self):
        """Calculates a team's total score"""
        total = 0
        for player in self.players:
            total += player.currentTotal()
        return total
    
    def report(self):
        if self.players:
            players = ', '.join('%s' % player.name for player in self.players)
            print "We are %s; we have %s on our team; and our total social value is %s."%(self.name, players, self.totalValue())
        else:
            print "%s is empty." % (self.name)
    
    def addPlayer(self, player):
        self.players.append(player)
    
    def removePlayer(self, player):
        self.players.remove(player)

def pairs(lst):
    i = iter(lst)
    first = prev = i.next()
    for item in i:
        yield prev, item
        prev = item
    yield item, first        

#------------------------------------------------
#-------------
# Procedures
#-------------

# Create the resource and objective pools
resource_pool = ResourcePool(num_resources, num_players)
objective_pool = ObjectivePool(resource_pool)
objs_table = objective_pool.table

#---------------------------------
# Allocate pool items to players
#---------------------------------

class CollaborationModel():
    def __init__(self):
        self.build()
        self.createTeams()

    def run(self):
        team_indexes = range(num_players)
        
        # TODO: Stop this loop at Pareto efficiency
        for _ in xrange(3):  # Temporary loop... this will eventually go until there are no more changes in team structure
            print "----------------------------------------------------"
            print "Start again"
            print "----------------------------------------------------"
            random.shuffle(team_indexes)
            
            for pair in pairs(team_indexes):
                x = pair[0]
                y = pair[1]

                print self.teams[x].name, "and", self.teams[y].name, "meet"
            
                if len(self.teams[x].players) > 0 and len(self.teams[y].players) > 0:   # If both of the teams actualy have players...
                    for team1_player in self.teams[x].players:  # TODO: Build an actual algorithm
                        for team2_player in self.teams[y].players:  # Loop within a loop to compare every player in both teamas
                            # Simple temporary algorithm; this will be more complicated in the future with actual logic
                            # Right now, players go to the largest team. In the future they'll go wherever they gain the most value
                            # TODO: Drop objectives
                            if team1_player.resource == team2_player.resource:  
                                print "Merge!"
                                if self.teams[x].playerCount() > self.teams[y].playerCount():
                                    team2_player.joinTeam(self.teams[x])
                                else:
                                    team1_player.joinTeam(self.teams[y])

                # Temporary reporting stuff
                for team in pair:
                    print self.teams[team].name
                    for player in self.teams[team].players:
                        print "\t", player.name, player.resource, player.objectives
                print "\n"

    
    def createTeams(self):
        self.teams = []
        for i, player in enumerate(self.players.values()):
            startingTeam = Team(player, "Team %02d"%i)
            self.teams.append(startingTeam)
            self.players[i].setInitialTeam(startingTeam)
    
    def build(self):
        # Initialize empty players dictionary (only a dictionary so it can be indexed)
        players = {}

        # Build the players list and index of objectives
        players_list = range(num_players)
        objs_index = range(objective_pool.num_objs)

        # Shuffle the lists if shuffling is enabled
        if shuffle == True:
            random.shuffle(players_list)
            random.shuffle(objs_index)

        # `count` keeps track of the number of times a resource is allocated to a player. It will only ever go up to `num_players`
        count = 0

        # Initialize starting and stopping variables for slicing the objectives list
        start = 0
        stop = num_objs_per_player
        
        # Loop through the resource and objective pools and assign resources and objectives to each player. 
        # Player numbers are assigned using `count` as an index to `combined`
        for resource, quantity in sorted(resource_pool.pool.items()):
            for i in range(quantity):
                # Create a new player and add it to the players dictionary
                players[players_list[count]] = Player(name="Player %02d"%players_list[count], resource=resource, objectives=objs_index[start:stop:1], sim=self)

                # Increment everything
                count += 1
                start += num_objs_per_player
                stop += num_objs_per_player
        
        self.players = players

CollaborationModel().run()

# # Create a community of players
# community = Community(players=players)
# print "Total community social value: " + str(community.total()) + "\n"

# # Print out players
# listPlayers()