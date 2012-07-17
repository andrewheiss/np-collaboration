#!/usr/bin/env python
# 
# Nonprofit collaboration simulation
#-------------------------------------
# Copyright 2011-12
# Eva Witesman and Andrew Heiss
# Romney Institute of Public Management
# Brigham Young University
#

# Load libraries and functions
from collections import Counter, namedtuple
from itertools import islice
from string import ascii_uppercase
from random import shuffle, sample, seed
from copy import deepcopy

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
faux_pareto_rounds_without_merges = 500
variation = 0
community_motivation = False  # Set to True to have everyone work for community value instead of personal value
# seed(4567890)

# Turn on random allocation
shuffling = True


#---------------------------------------------------
#---------------------------------------------------
# Run the simulation. Do not edit below this line.
#---------------------------------------------------
#---------------------------------------------------

#----------
# Objects
#----------

class ResourcePool:
    """Creates a pool of resources with high and low distributions according to the frequency in `approximate_high_low_resource_ratio`
    
    For example, if there are 16 players, with 4 different types of resources, and an approximate ratio of 3:1, the pool will be a dictionary distributed like so:
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
        self.pool = dict(sorted(Counter(islice(r, players)).items()))

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
        DivdedResources = namedtuple('Resources', ['high', 'low'])
        letters = ascii_uppercase[:resources]
        high_count = resources // 2

        if shuffling == True:
            letters = ''.join(sample(letters, len(letters)))

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
        self.pool = dict(sorted(Counter(islice(o, self.num_objs)).items()))

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


class Community:
    """docstring for Community"""
    def __init__(self, players, teams):
        self.players = players
        self.teams = teams
    
    def total(self):
        """docstring for globalTotal"""
        total = 0
        for i, player in self.players.items():
            total += player.currentTotal()
        return total

    def activeTeams(self):
        return [ team.index for team in self.teams if team.playerCount() > 0 ]

    def last_team_index(self):
        return self.teams[-1].index


class Team:
    """A team is a collection of players that have decided to collaborate in order to achieve higher personal or societal value. 
    
    Attributes:
        name: The team's name
        players: A list of player objects that are part of the team
    
    Returns:
        A new team object
    """
    def __init__(self, index):
        """Creates a new team object
        
        Creates a new team ### consisting of exactly one player
        
        Args:
            name: The player's name
            player: A single player object
        
        Raises:
            No errors yet... 
        """
        self.name = "Team %02d"%index 
        self.index = index
        self.players = []
        # self.players.append(player)
    
    def playerCount(self):
        """Count how many players there are."""
        return len(self.players)
    
    def resources(self):
        """Find all the resources in the team and return a list of unique resource values"""
        resources = []
        for player in self.players:
            resources.append(player.resource)
        return uniquify(resources)
    
    def totalValue(self, newPlayer=None):
        """Calculates a team's total score"""
        if newPlayer is None:   # If no new hypothetical player is specified, use the regular team players
            players = self.players
        else:   # Otherwise, temporarily add the extra player to a copy of the team
            players = deepcopy(self.players)
            players.append(newPlayer)
        
        total = 0
        for player in players:
            total += player.currentTotal()
        return total
    
    def report(self):
        if self.players:
            players = ', '.join('%s' % player.name for player in self.players)
            print "We are %s; we have %s on our team; we have resources %s; and our total social value is %s."%(self.name, players, self.resources(), self.totalValue())
        else:
            print "%s is empty." % (self.name)
    
    def addPlayer(self, player):
        self.players.append(player)
    
    def removePlayer(self, player):
        self.players.remove(player)


class Player:
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

    def currentTotal(self, test_object=None, object_is_team=True, new_team=False):
        """Sum the values of all objectives that match a player's assigned resource
        
        Args:
            test_object: Either a team or a player object that will be used hypothetically
            object_is_team: Boolean that defaults to true. By default, this will test a hypothetical team. If false, it will test a hypothetical player.
        """

        # Check to make sure the method is called properly
        if (object_is_team is True or test_object is None) and new_team is True:
            raise Exception("Can't use `new_team` on a team object or without a `test_object`")

        resources = []

        # If no object is specified, use the actual team
        if test_object is None:
                resources = self.team.resources()
        else:
            # Otherwise, create a hypothetical pool of team resources using by either 
            # (1) Combining the hypothetical team's resources and the actual player's single resource
            # or
            # (2) Combining the hypothetical player's single resource and the actual player's team resources

            if object_is_team == True:
                    resources = uniquify(test_object.resources() + list(self.resource))
            else:
                if new_team == True:
                    resources = uniquify(list(self.resource) + list(test_object.resource))
                else:
                    resources = uniquify(self.team.resources() + list(test_object.resource))
        
        # Calculate the player's total personal score based on the pool of resources available
        total = 0
        for index, details in self.objectives.items():
            for resource in resources:
                if resource == details[0][0].upper():
                    total += details[1]
        return total
    
    def dropObjective(self):
        """docstring for dropObjective"""
        # TODO: Drop objectives
        pass
    
    def joinTeam(self, team):
        """Add a player to a team... eventually only after checking to see if the alliance is beneficial and after dropping an objective"""
        # Drop an objective someday
        self.team.removePlayer(self)    # Leave current team
        team.addPlayer(self)            # Join new team
        self.team = team                # Reassign new team to player attributes
    
    def setInitialTeam(self, team):
        self.team = team
    
    def report(self):
        # Build a comma separated list of objectives
        objectives = ', '.join('%s' % obj[0] for obj in self.objectives.values())
        
        print "I am %s; I have resource %s; I have objectives %s; I'm on team %s; and my total value is %s."%(self.name, self.resource, objectives, self.team.name, self.currentTotal()) 


class CollaborationModel:
    def __init__(self):
        self.build()
        self.createTeams()

    def variation_1(self, team_a, team_b, player_a, player_b):
        pass

    def variation_2(self, team_a, team_b, player_a, player_b):
        pass

    def test_variation_3(self):
        self.players[1].joinTeam(self.teams[0])
        self.variation_3(self.teams[0], self.teams[2], self.players[0], self.players[2])

    def variation_3(self, player_a, player_b):
        team_a = player_a.team
        team_b = player_b.team
        # a_delta_if_move = 20
        # a_delta_if_stay = 50
        # b_delta_if_move = 10
        # b_delta_if_stay = 40
        # TODO: Make these conditional on community vs. individual welfare. Keep variable names the same.
        if community_motivation is True:
        else:
            a_delta_if_move = player_a.currentTotal(player_b.team) - player_a.currentTotal()  # A's hypothetical total on B's team - A's current total
            a_delta_if_stay = player_a.currentTotal(player_b, object_is_team=False) - player_a.currentTotal()  # A's hypothetical total if B joins A - A's current total
            
            b_delta_if_move = player_b.currentTotal(player_a.team) - player_b.currentTotal()  # B's hypothetical total on A's - B's current total
            b_delta_if_stay = player_b.currentTotal(player_a, object_is_team=False) - player_b.currentTotal()  # B's hypothetical total if A joined B - B's current total

        # # Player A's soliloquy
        # print "\nI'm {0} and I get to collaborate with {1}.".format(player_a.name, player_b.name)
        # print "On my current team, I have {0} points and access to {1}".format(player_a.currentTotal(), player_a.team.resources())
        # print "If I left to join {0} with {1}, I'd have {2} points because I'd have access to {3}".format(player_b.team.name, player_b.name, player_a.currentTotal(player_b.team), player_b.team.resources())
    
        # print "That would be a change of {0} points".format(a_delta_if_move)
        # print "But if {0} came to join my team I would have {1} points".format(player_b.name, player_a.currentTotal(player_b, object_is_team=False))
        # print "And that would be a change of {0} points".format(a_delta_if_stay)
        
        # # Player B's soliloquy
        # print "\nI'm {0} and {1} wants to collaborate with me".format(player_b.name, player_a.name)
        # print "On my current team, I have {0} points and access to {1}".format(player_b.currentTotal(), player_b.team.resources())
        # print "If I left to join {0} with {1}, I'd have {2} points because I'd have access to {3}".format(player_a.team.name, player_a.name, player_b.currentTotal(player_a.team), player_a.team.resources())
        # print "That would be a change of {0} points".format(b_delta_if_move)
        # print "But if {0} came to join my team I would have {1} points".format(player_a.name, player_b.currentTotal(player_a, object_is_team=False))
        # print "And that would be a change of {0} points".format(b_delta_if_stay)

        # print "\n---------------------------\n"

        # print "Change for A if A moves to B:", a_delta_if_move
        # print "Change for A if B comes to A:", a_delta_if_stay
        # print "Change for B if B moves to A:", b_delta_if_move
        # print "Change for B if A comes to B:", b_delta_if_stay

        # print "\n---------------------------"

        #---------------------
        # Decision algorithm
        #---------------------

        def a_ask_b_to_join():
            # print "Inviting B"
            if b_delta_if_move >= 0 and b_delta_if_move > b_delta_if_stay:
                # print "This is the ideal situation; {0} will gain {1} points and {2} will gain {3}. Permission granted.".format(player_a.name, a_delta_if_stay, player_b.name, b_delta_if_move)
                player_b.joinTeam(team_a)
                return True
            elif b_delta_if_stay >= 0 and b_delta_if_stay > b_delta_if_move:
                # print "It's better if B stays... but why not"  # TODO: Don't have the player join
                player_b.joinTeam(team_a)
                return True
            elif b_delta_if_move == b_delta_if_stay and b_delta_if_move > 0:
                # print "It doesn't matter to B. Permission granted."
                player_b.joinTeam(team_a)
                return True
            else:
                # print "Permission denied"
                return False

        def a_try_move_to_b():
            # print "Trying to move"
            if b_delta_if_stay > 0 and b_delta_if_stay > b_delta_if_move:
                # print "aa This is the ideal situation; {0} will gain {1} points and {2} will gain {3}. Permission granted.".format(player_a.name, a_delta_if_move, player_b.name, b_delta_if_stay)
                player_a.joinTeam(team_b)
                return True
            elif b_delta_if_move > 0 and b_delta_if_move > b_delta_if_stay:
                # print "aa It's better if B moves... but why not"  # TODO: Don't have the player join
                player_a.joinTeam(team_b)
                return True
            elif b_delta_if_stay == b_delta_if_move and b_delta_if_stay > 0:
                # print "aa It doesn't matter to B. Permission granted."
                player_a.joinTeam(team_b)
                return True
            else:
                # print "aa Permission denied"
                return False
            # TODO: Let B try to make an offer if none was made
            # TODO: Use a boolean and return that at the end instead of tons of returns in the middle

        # If both changes are negative, don't do anything
        if a_delta_if_stay <= 0 and a_delta_if_move <= 0:
            # print "All net changes are bad. Don't do anything."
            return False

        # If moving to B's team is better than staying, ask permission to move
        elif a_delta_if_move >= 0 and a_delta_if_move > a_delta_if_stay:
            return a_try_move_to_b()

        # If staying is better than moving to B's team, invite B to join
        elif a_delta_if_stay >= 0 and a_delta_if_stay > a_delta_if_move:
            return a_ask_b_to_join()

        # If staying and moving give the same benefit, choose one randomly
        elif a_delta_if_stay == a_delta_if_move and a_delta_if_move > 0:
            # print "Either option is the same" 
            actions = [a_try_move_to_b, a_ask_b_to_join]  # Create a list of the two functions
            shuffle(actions)  # Shuffle the list
            if actions[0]():  # Try either inviting or moving. If that fails, try the other one.
                return True
            else:
                return actions[1]()

    def test_variation_4(self):
        self.players[1].joinTeam(self.teams[0])
        self.players[5].joinTeam(self.teams[2])
        self.variation_4(self.teams[0], self.teams[2], self.players[0], self.players[2])

    def variation_4(self, team_a, team_b, player_a, player_b):
        player_a.report()
        team_a.report()
        print "Player A on their current team:", player_a.currentTotal()
        print "Player A alone:", player_a.currentTotal(alone=True)
        print ""

        player_b.report()
        team_b.report()
        print "Player B on their current team:", player_b.currentTotal()
        print "Player B alone:", player_b.currentTotal(alone=True)
        print ""

        print "Player A with A and B only:", player_a.currentTotal(player_b, object_is_team=False, alone=True)
        print "Player B with A and B only:", player_b.currentTotal(player_a, object_is_team=False, alone=True)

        # if team_b.playerCount() > 1:  # B's team already has two people
        #     a_delta_if_move = 0
        # else:                         # B's team only has one person
        #     a_delta_if_move = player_a.currentTotal(player_b.team) - player_a.currentTotal()

        # a_delta_if_move = player_a.currentTotal(player_b.team) - player_a.currentTotal()  # A's hypothetical total on B's team - A's current total
        # a_delta_if_stay = player_a.currentTotal(player_b, object_is_team=False) - player_a.currentTotal()  # A's hypothetical total if B joins A - A's current total

    def test(self):
        community = Community(self.players, self.teams)

        self.players[1].joinTeam(self.teams[0])
        new_team = Team(community.last_team_index() + 1)
        self.teams.append(new_team)

        self.players[4].joinTeam(self.teams[16])

        print community.activeTeams()
        print community.last_team_index()
        players_list = range(len(self.players))
        shuffle(players_list)

        for pair in pairs(players_list):
            a = self.players[pair[0]]
            b = self.players[pair[1]]
            print a.name, b.name
            # if self.variation_3(a, b) == True:
            #     merges += 1

    def run(self):
        community = Community(self.players, self.teams)
        rounds_without_merges = 0
        total_merges = 0
        merges_this_round = 0
        
        # Temporary team reporting
        # for i in self.players:
            # self.players[i].report()
        # print ""
        
        print "Total community social value before playing: " + str(community.total()) + "\n"

        while True:
            # Track how many team merges happen
            total_merges += merges_this_round
            merges_this_round = 0

            players_list = range(len(self.players))  # Build list of player indexes
            shuffle(players_list)  # ...and shuffle it

            # Pair each index up at random... those two players then meet and run the appropriate algorithm
            for pair in pairs(players_list):
                a = self.players[pair[0]]
                b = self.players[pair[1]]

                if self.variation_3(a, b) == True:
                    merges_this_round += 1
                if a.team != b.team:  # If the players aren't already on the same team
                    if self.variation_3(a, b) == True:
                        merges_this_round += 1
            
            # If no merges happened this round, mark it
            if merges_this_round == 0:
                rounds_without_merges += 1
            
            # If x rounds without merges happen, stop looping
            if rounds_without_merges >= faux_pareto_rounds_without_merges : break
        
        print "Total number of team switches: {0}\n".format(total_merges)

        print "Final teams:"
        for team in self.teams:
            team.report()

        print "Total community social value after playing: " + str(community.total()) + "\n"

        # Temporary team reporting
        # for i in self.players:
            # self.players[i].report()  
            
    
    def largest_matching_team(self, team1, team2, team1_player, team2_player):
        """Simple temporary algorithm for development. Players join the team with the largest number of matching resources. As a result, players congregrate to teams/networks of their own resorce."""
        if team1_player.resource == team2_player.resource:  
            if team1.playerCount() > team2.playerCount():
                team2_player.joinTeam(team1)
            else:
                team1_player.joinTeam(team2)
            return True
    
    def createTeams(self):
        self.teams = []
        for i, player in enumerate(self.players.values()):
            startingTeam = Team(i)
            startingTeam.addPlayer(player)
            self.teams.append(startingTeam)
            self.players[i].setInitialTeam(startingTeam)
    
    def build(self):
        # Initialize empty players dictionary (only a dictionary so it can be indexed)
        players = {}

        # Build the players list and index of objectives
        players_list = range(num_players)
        objs_index = range(objective_pool.num_objs)
        # print(resource_pool.pool)
        # print(objective_pool.pool)

        # Shuffle the lists if shuffling is enabled
        if shuffling == True:
            shuffle(players_list)
            shuffle(objs_index)

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


# Important mini functions
def pairs(lst):
    i = iter(lst)
    first = prev = i.next()
    for item in i:
        yield prev, item
        prev = item
    yield item, first

def uniquify(seq):
    """Take a list and return only the unique values in that list. Does not preserve list order."""
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]


# Temporary faux pretty printing functions
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


#------------------------------------------------------------------------------
#------------------------------
# Actual simulation procedure
#------------------------------
# Create the global resource and objective pools 
resource_pool = ResourcePool(num_resources, num_players)
objective_pool = ObjectivePool(resource_pool)
objs_table = objective_pool.table

# Run the simulation
CollaborationModel().run()

# Extra sandboxy stuff
# for _ in xrange(5):
# for _ in itertools.repeat(None, N):
# CollaborationModel().test()
# # Print out players
# listPlayers()