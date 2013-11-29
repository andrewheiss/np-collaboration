#!/usr/bin/env python
# 
# Nonprofit collaboration simulation
#-------------------------------------
# Copyright 2011-13
# Eva Witesman and Andrew Heiss
# Romney Institute of Public Management
# Brigham Young University
#

# Load required libraries and functions
from collections import Counter, namedtuple
from itertools import islice
from string import ascii_uppercase
from random import shuffle, sample, seed, choice
from copy import deepcopy
import csv


#----------------------
# Classes and methods
#----------------------

class CollaborationModel():
    """A CollaborationModel object contains the core of the simulation and ties all other classes--resources, objectives, communities, teams, and players--together and allows players to interact in a way to maximize social or personal value.

    In the simulation, players are assigned one resource and an arbitrary number of objectives. A *resource* is unique to each player and essentially represents that player's competitive advantage, or supply in the market. Players have a set number of differently valued *objectives,* which correspond to market demand. Resources are represented with uppercase Latin letters (i.e. `A`, `B`, `C`) and objectives with lowercase Latin letters and numerals (i.e. `a1`, `a2`, `b1`, `c2`). Objectives with a subscripted 1 (i.e. `a1`) are classified as high-value, while objectives with a subscripted 2 are classified as low-value. Objective values can be arbitrarily set in the simulation, but by default high-value objectives are worth 20 points, while low-value objectives are worth 10.

    Objectives only benefit players when they match a player's assigned resource. For example, a player assigned resource `A` and objectives `a1`, `a2`, `b2`, `c1`, and `c2` would have 30 points, as `a1` (20 points) and `a2` (10 points) match the player's resource. The remaining three objectives (`b2`, `c1`, and `c2`) represent unmet demand and provide the incentive for that player to network with other players with different resources (specifically `B` and `C`). 

    Players are assigned resources and objectives at the outset of the simulation. The simulation builds a pool of resources distributed in frequency according to a given ratio. The table below demonstrates the resource pool in a simulation with 16 players, 4 different types of objectives, and an approximate ratio of 3:1. 

    Resource | Quantity  
    -------- | ------  
    `A`      | 6  
    `B`      | 6  
    `C`      | 2  
    `D`      | 2  


    After building a pool of resources, the simulation then creates a larger pool of objectives of varying value, again distributed in frequency according to a given ratio. The table below shows the objective pool for the sample 16-person, 4-resource example above, assuming there are 5 objectives per player distributed at an approximate ratio of 3:1.

    Objective | Quantity | Frequency | Value  
    --------- | -------- | --------- | ---  
    `a1`      | 15       | High      | High  
    `a2`      | 15       | High      | Low  
    `b1`      | 5        | Low       | High  
    `b2`      | 5        | Low       | Low  
    `c1`      | 5        | Low       | High  
    `c2`      | 5        | Low       | Low  
    `d1`      | 15       | High      | High  
    `d2`      | 15       | High      | Low  


    Each player is then randomly assigned one resource and a given number of objectives. In the ongoing example with 16 players, final resource and objective assignments are shown below. 

    Player    | Resource | Objectives                   | Value  
    --------- | -------- | ---------------------------- | ---  
    Player 00 | `C`      | `a2`, `d2`, `b2`, `c2`, `d2` | 10  
    Player 01 | `B`      | `d1`, `d2`, `d2`, `a1`, `a2` | 0  
    Player 02 | `D`      | `d2`, `d2`, `d2`, `d1`, `a1` | 50  
    Player 03 | `B`      | `d1`, `d1`, `a1`, `d1`, `c1` | 0  
    Player 04 | `A`      | `a1`, `d2`, `a1`, `d1`, `c2` | 40  
    Player 05 | `D`      | `a1`, `c1`, `a2`, `d1`, `b2` | 20  
    Player 06 | `C`      | `b1`, `d1`, `a2`, `d1`, `d2` | 0  
    Player 07 | `B`      | `c2`, `d1`, `c2`, `b1`, `d2` | 20  
    Player 08 | `B`      | `a2`, `a2`, `a2`, `a1`, `d1` | 0  
    Player 09 | `A`      | `a1`, `d2`, `a1`, `a2`, `a2` | 60  
    Player 10 | `B`      | `a2`, `d2`, `a1`, `a1`, `d1` | 0  
    Player 11 | `B`      | `b1`, `a1`, `d1`, `a1`, `b1` | 40  
    Player 12 | `A`      | `a2`, `d1`, `b2`, `a2`, `c1` | 20  
    Player 13 | `A`      | `c2`, `a2`, `a1`, `d2`, `a1` | 50  
    Player 14 | `A`      | `d1`, `c1`, `a2`, `b2`, `b1` | 10  
    Player 15 | `A`      | `a2`, `c1`, `b2`, `d2`, `d2` | 10  


    After creating a given number of players, separating them into teams, and assigning them a resource and a given number of objectives, player objects are shuffled and paired off (i.e. [(6, 7), (9, 10), (12, 13), (5, 6), (8, 9), (13, 14), (4, 5), (7, 8), (14, 15), (0, 1), (11, 12), (15, 0), (10, 11), (1, 2), (3, 4), (2, 3)]). Players are aware of the resources others have to offer, but not the objectives of others. Networking decisions are made according to a logical algorithm based on the number of points a player would gain by creating a network. 

    In each encounter, the first player (Player A) determines if collaborating with the second player (Player B) is beneficial. Player A looks at the change, or delta, in their current personal score (or the overall social score, if focused on maximizing societal benefit) in either (1) leaving their current team to join Player B, or (2) inviting Player B to leave their team and join Player A's team. Player B then accepts or refuses A's offer to leave (or request to join), depending on the delta B would gain through the collaborative relationship. 

    If there is no positive delta for Player A in moving to B's team or inviting B to join their team, Player A will do nothing and the interaction will end. If there is a positive delta for Player A in leaving to join B, but no positive delta for Player B, Player B will refuse and the interaction will end. If there is a positive delta for Player A in leaving to join B, and there is a positive delta for B if A joins, but an even higher delta for B if B leaves to join A (i.e. it's a better deal for B if they actually join A's team instead of having A join them), Player B will refuse, holding out for more points in a future interaction with another player.

    In the ongoing example, Player 05 has resource `D` and a total of 20 points, with only one objective `d1` matching their resource. When Player 05 meets Player 10, who has `B` and no objectives that match, Player 05 would gain 10 points by creating a network with Player 10--Player 10's `B` would fulfill the unmet `b2`. Player 10 would also benefit from a network--having access to Player 5's `D` would give Player 10's `d1` and `d2` and net 30 additional points. Because the network would be mutually beneficial, the two players create a network and pool their resources together. Future players can then enter that network and add their resources to the shared pool. 

    However, if Player 05 were to gain no benefit from collaboration with Player 10, but Player 10 could potentially gain points from leaving their current network and joining that of Player 05, Player 05 would refuse to network because there would be no benefit to them personally. Likewise, if Player 05 were to gain points from having Player 10 join their team, Player 10 would refuse if there were a lack of personal benefit. In instances where the requesting player would gain equal benefit from leaving their existing network or joining the responding player's network, the player chooses to stay or leave at random. 

    There are four variations in the networking algorithm:

        Variation 1: To network with another player, the requesting player (Player A) must drop one objective of their choice and leave it unfulfilled.
        Variation 2: To network with another player, the requesting player (Player A) must offer one objective of their choice as payment to the recipient (Player B).
        Variation 3: To network with another player, both players must agree to network.
        Variation 4: To network with another player, both players must agree to network. No team can contain more than two players.

    When players encounter each other, they use the algorithm that corresponds to the variation set at the top of this script in the variable `variation`.

    Each pair of players has a chance to interact with each other. If an exchange occurred, it is marked in CollaborationModel.run().merges_this_round. The players are then reshuffled and paired off again. If no exchange occurs in a round, it is marked in CollaborationModel.run().rounds_without_merges. Players continue to interact until there are an arbitrary number of rounds *in a row* where no exchanges occur (set in the 'faux_pareto_rounds_without_merges' variable at the top of the script). It is assumed that after that many rounds in a row with no changes, an approximation of Pareto efficiency will have been achieved--no players can improve anymore.

    
    Attributes:
        community: A Community object
        resource_pool: A ResourcePool object
        objective_pool: An ObjectivePool object
        objs_table: A list of dictionaries with each objective name and value, corresponding to ObjectivePool.table
        players: A dictionary of Player objects (uses a dictionary so that players can be indexed): e.g., {0: <__main__.Player instance at 0x106a895a8>, 1: <__main__.Player instance at 0x106a89e18>, ...}
        teams: A list of Team objects (uses a list because the teams don't need to be indexed): e.g., [<__main__.Team instance at 0x10be66d88>, <__main__.Team instance at 0x10be66dd0>, ...]
        dropped_objectives: A list of lists to track dropped objectives: e.g., [['d2', 10], ['b1', 20], ['a1', 20]]. Objectives are no longer indexed because uniqueness doesn't matter.
        traded_objectives: A list of lists to track dropped objectives. Objectives are no longer indexed because uniqueness doesn't matter and an objective can be traded multiple times.
    """
    def __init__(self, num_players, num_resources, num_objs_per_player, 
        approximate_high_low_resource_ratio, approximate_high_low_objective_ratio,
        value_high, value_low, variation, faux_pareto_rounds_without_merges, 
        community_motivation, csv_out, csv_header):
        #------------------------------------------------------------------
        # Create resource pool, objective pool, and dictionary of players
        #------------------------------------------------------------------
        self.resource_pool = ResourcePool(num_resources, num_players, approximate_high_low_resource_ratio)
        self.objective_pool = ObjectivePool(self.resource_pool, num_players, num_objs_per_player, approximate_high_low_objective_ratio, value_high, value_low)
        self.objs_table = self.objective_pool.table

        # Initialize simulation-wide variables passed to the class
        self.num_players = num_players
        self.value_high = value_high
        self.value_low = value_low
        self.variation = variation
        self.faux_pareto_rounds_without_merges = faux_pareto_rounds_without_merges
        self.community_motivation = community_motivation
        self.csv_out = csv_out
        self.csv_header = csv_header

        # Temporary sanity checking...
        # The algorithm chokes with high faux pareto values on variation 3, because it can be infinite
        if self.variation == 3:
          self.faux_pareto_rounds_without_merges = 5

        # Initialize empty players dictionary (only a dictionary so it can be indexed)
        players = {}

        # Build the players list and index of objectives
        players_list = range(num_players)
        objs_index = range(self.objective_pool.num_objs)

        shuffle(players_list)
        shuffle(objs_index)

        # `count` keeps track of the number of times a resource is allocated to a player. It will only ever go up to `num_players`
        count = 0

        # Initialize starting and stopping variables for slicing the objectives list
        start = 0
        stop = num_objs_per_player
        
        # Loop through the resource and objective pools and assign resources and objectives to each player. 
        # Player numbers are assigned using `count` as an index to `combined`
        for resource, quantity in sorted(self.resource_pool.pool.items()):
            for i in range(quantity):
                # Create a new player and add it to the players dictionary
                players[players_list[count]] = Player(name="Player %02d"%players_list[count], resource=resource, objective_indices=objs_index[start:stop:1], objectives_table=self.objs_table)

                # Increment everything
                count += 1
                start += num_objs_per_player
                stop += num_objs_per_player
        
        self.players = players

        #--------------------------
        # Assign players to teams
        #--------------------------
        self.teams = []
        for i, player in enumerate(self.players.values()):
            startingTeam = Team(i)
            startingTeam.addPlayer(player)
            self.teams.append(startingTeam)
            self.players[i].setInitialTeam(startingTeam)

        #------------------------------
        # Initialize community object
        #------------------------------
        self.community = Community(self.players, self.teams)

        #-----------------------------------------
        # Initialize other object-wide variables
        #-----------------------------------------
        # Map the global `variation` variable to the corresponding variation functions to be used in run()
        self.variations = {
            1: self.variation_1,
            2: self.variation_2,
            3: self.variation_3,
            4: self.variation_4,
            5: self.variation_5
        }

        self.dropped_objectives = []  # Keep track of dropped objectives
        self.traded_objectives = []  # Keep track of traded objectives

    def test_run(self):
        """Temporary function for running a single pair of players through one of the variations."""
        print "Running variation {0}, with a {1} focus".format(self.variation, "community" if self.community_motivation else "self-interested")
        # self.players[1].joinTeam(self.teams[0])
        # self.players[5].joinTeam(self.teams[2])
        # self.teams[2].report()
        # self.players[1].report()
        # for i in self.players:
        # #     self.players[i].report()
        # print self.community.total()
        self.variations[self.variation](self.players[0], self.players[2])

        # # for team in self.teams:
        # #     team.report()

        # # for i in self.players:
        # #     self.players[i].report()

        # print self.objs_table
        # print self.dropped_objectives

        # print self.community.total()


    def run(self, run_number):
        """Runs the actual simulation by pairing players off into random pairs and allowing each pair to collaborate, if beneficial. Players are paired off and interact until `faux_pareto_rounds_without_merges` rounds in a row pass with no trades or collaboration.

        Args:
            run_number: An integer that keeps track of how many times a simulation has been run; used as the row ID number in the exported CSV.
        """
        # Initialize count variables
        rounds_without_merges = 0
        merges_this_round = 0
        total_merges = 0
        total_encounters = 0

        # Capture pre-simulation data
        before_total = str(self.community.total())
        individual_statistics_before = self.community.individualStats()

        # print "Running self.variation {0} with a {1} focus".format(self.variation, "community" if self.community_motivation else "self-interested"), "\n"
        
        # # Temporary team reporting
        # print "-----------------------------------------------------------------------------------------------------------------------"
        # print "Initial player allocations:"
        # print "-----------------------------------------------------------------------------------------------------------------------"
        # for i in self.players:
        #     self.players[i].report()
        # print "-----------------------------------------------------------------------------------------------------------------------\n"


        #--------------------------
        # Main simulation routine
        #--------------------------
        if self.variation == 0:  # Variation 0 is used to export initial allocation data only
            total_encounters = 0.0001  # Not quite zero, since it is the denominator in some exported ratios
        else:  # If the variation is anything other than 0...
            while True:  # Loop this forever until told to break
                total_merges += merges_this_round  # Track how many team merges happen
                merges_this_round = 0  # Reset count, since this is a new round

                players_list = range(len(self.players))  # Build list of player indexes
                shuffle(players_list)

                pairs_of_players = list(pairs(players_list))  # Pair each player index up randomly
                shuffle(pairs_of_players)

                for pair in pairs_of_players:
                    a = self.players[pair[0]]
                    b = self.players[pair[1]]

                    if a.team != b.team:  # If the players aren't already on the same team
                        if self.variations[self.variation](a, b) == True:  # Run the specified variation algorithm
                            merges_this_round += 1
                        total_encounters += 1  # Update how many encounters occurred
                
                if merges_this_round == 0:  # If no merges happened this round, mark it
                    rounds_without_merges += 1
                else:  # Otherwise, reset the count of rounds without merges. The simulation stops after x tradeless rounds *in a row*
                    rounds_without_merges = 0
                
                if rounds_without_merges == self.faux_pareto_rounds_without_merges : break  # If x rounds without merges happen, stop looping


        #----------------
        # Export to CSV
        #----------------
        # Capture post-simulation data
        team_statistics = self.community.teamStats()
        individual_statistics_after = self.community.individualStats()
        subset = self.community.objectivesSubset()

        # Start the massive list of tuples to be exported to the CSV file; e.g., [("column_1", value_1), ("column_2", value_2)]
        csv_data = []

        # Basic simulation information
        csv_data.append(("id", run_number + 1))
        csv_data.append(("variation", self.variation))
        csv_data.append(("player_count", self.num_players))
        csv_data.append(("community_motivation", 1 if self.community_motivation else 0))
        csv_data.append(("encounters", total_encounters))
        csv_data.append(("switches", total_merges))
        csv_data.append(("switch_ratio", total_merges / float(total_encounters)))

        # Team information
        csv_data.append(("number_of_teams", team_statistics.number))
        csv_data.append(("team_size_min", team_statistics.min))
        csv_data.append(("team_size_max", team_statistics.max))
        csv_data.append(("team_size_mean", team_statistics.mean))
        csv_data.append(("team_size_median", team_statistics.median))

        # Individual statistics
        csv_data.append(("indiv_total_min_before", individual_statistics_before.min))
        csv_data.append(("indiv_total_max_before", individual_statistics_before.max))
        csv_data.append(("indiv_total_mean_before", individual_statistics_before.mean))
        csv_data.append(("indiv_total_median_before", individual_statistics_before.median))
        csv_data.append(("indiv_total_min_after", individual_statistics_after.min))
        csv_data.append(("indiv_total_max_after", individual_statistics_after.max))
        csv_data.append(("indiv_total_mean_after", individual_statistics_after.mean))
        csv_data.append(("indiv_total_median_after", individual_statistics_after.median))
        csv_data.append(("indiv_delta_mean", individual_statistics_after.mean - individual_statistics_before.mean))
        csv_data.append(("indiv_delta_median", individual_statistics_after.median - individual_statistics_before.median))

        # Social statistics
        csv_data.append(("social_value_before", before_total))
        csv_data.append(("social_value_after", self.community.total()))
        csv_data.append(("potential_social_value", self.community.potentialTotal(self.objs_table)))
        csv_data.append(("unmet_social_value", self.community.potentialTotal(self.objs_table) - self.community.total()))
        csv_data.append(("percent_social_value_met", self.community.total() / float(self.community.potentialTotal(self.objs_table))))

        # General objective statistics
        csv_data.append(("num_objectives", len(self.objective_pool.table)))
        csv_data.append(("objs_fulfilled", len(subset.fulfilled)))
        csv_data.append(("objs_held_unfulfilled", len(subset.unfulfilled)))
        csv_data.append(("objs_dropped", len(self.dropped_objectives)))
        csv_data.append(("objs_traded", len(self.traded_objectives)))
        csv_data.append(("objs_fulfilled_ratio", len(subset.fulfilled) / float(len(self.objective_pool.table))))
        csv_data.append(("objs_unfulfilled_ratio", (len(subset.unfulfilled) + len(self.dropped_objectives)) / float(len(self.objective_pool.table))))

        # Resource-specific objective statistics
        # This loop creates columns for each objective, organized by resource (i.e. a1, a2, b1, b2, etc.)
        for resource in self.resource_pool.resources_list:
            # Variable names (a1, b2, etc.)
            high_value_objective = resource[0].lower() + str(1)
            low_value_objective = resource[0].lower() + str(2)

            # Initialize count variables
            fulfilled_count_high = 0
            unfulfilled_count_high = 0
            dropped_count_high = 0
            traded_count_high = 0
            obj_count_high = 0
            fulfilled_count_low = 0
            unfulfilled_count_low = 0
            dropped_count_low = 0
            traded_count_low = 0
            obj_count_low = 0

            # Count stuff
            for obj in self.objective_pool.obj_list:
                if resource[0] == obj[0][0].upper():
                    if obj[1] == self.value_high: 
                        obj_count_high += 1 
                    else:
                        obj_count_low += 1

            for obj in subset.fulfilled:
                if resource[0] == obj[0][0].upper():
                    if obj[1] == self.value_high: 
                        fulfilled_count_high += 1 
                    else:
                        fulfilled_count_low += 1

            for obj in subset.unfulfilled: 
                if resource[0] == obj[0][0].upper():
                    if obj[1] == self.value_high: 
                        unfulfilled_count_high += 1 
                    else:
                        unfulfilled_count_low += 1

            for obj in self.dropped_objectives:
                if resource[0] == obj[0][0].upper():
                    if obj[1] == self.value_high: 
                        dropped_count_high += 1 
                    else:
                        dropped_count_low += 1

            for obj in self.traded_objectives: 
                if resource[0] == obj[0][0].upper():
                    if obj[1] == self.value_high: 
                        traded_count_high += 1 
                    else:
                        traded_count_low += 1

            # Add counts the csv_data list of tuples
            csv_data.append(("{0}_value".format(high_value_objective), self.value_high))
            csv_data.append(("{0}_count".format(high_value_objective), obj_count_high))
            csv_data.append(("{0}_high_freq".format(high_value_objective), 1 if resource[1] == "high_freq" else 0))
            csv_data.append(("{0}_trades".format(high_value_objective), traded_count_high))
            csv_data.append(("{0}_dropped".format(high_value_objective), dropped_count_high))
            csv_data.append(("{0}_fulfilled".format(high_value_objective), fulfilled_count_high))
            csv_data.append(("{0}_pct_fulfilled".format(high_value_objective), fulfilled_count_high/float(obj_count_high)))
            csv_data.append(("{0}_held_unfulfilled".format(high_value_objective), unfulfilled_count_high))

            csv_data.append(("{0}_value".format(low_value_objective), self.value_low))
            csv_data.append(("{0}_count".format(low_value_objective), obj_count_low))
            csv_data.append(("{0}_high_freq".format(low_value_objective), 1 if resource[1] == "high_freq" else 0))
            csv_data.append(("{0}_trades".format(low_value_objective), traded_count_low))
            csv_data.append(("{0}_dropped".format(low_value_objective), dropped_count_low))
            csv_data.append(("{0}_fulfilled".format(low_value_objective), fulfilled_count_low))
            csv_data.append(("{0}_pct_fulfilled".format(low_value_objective), fulfilled_count_low/float(obj_count_low)))
            csv_data.append(("{0}_held_unfulfilled".format(low_value_objective), unfulfilled_count_low))
 
        # Finally output the csv_data list to the CSV file
        if run_number == 0 and self.csv_header: self.csv_out.writerow([data[0] for data in csv_data])  # Output headers on the first run
        self.csv_out.writerow([data[1] for data in csv_data])  # Output the data

        # print "-----------------------------------------------------------------------------------------------------------------------"
        # print "Final team allocations:"
        # print "-----------------------------------------------------------------------------------------------------------------------"
        # for team in self.teams:
        #     team.report()
        # print "-----------------------------------------------------------------------------------------------------------------------"

        # # Temporary team reporting
        # print "\n-----------------------------------------------------------------------------------------------------------------------"
        # print "Final player allocations:"
        # print "-----------------------------------------------------------------------------------------------------------------------"
        # for i in self.players:
        #     self.players[i].report()
        # print "-----------------------------------------------------------------------------------------------------------------------"


    #-----------------------------------------------------------------------------------------------
    # Decision algorithms
    #
    # Each variation takes two arguments: `player_a` and `player_b`, which must be player objects.
    #-----------------------------------------------------------------------------------------------

    def largest_matching_team(self, player_a, player_b):
        """Simple example algorithm. Players join the team with the largest number of matching resources. As a result, players congregate to teams of their own resource."""
        team_a = player_a.team
        team_b = player_b.team

        if player_a.resource == player_b.resource:  
            if team_a.playerCount() > team_b.playerCount():
                player_b.joinTeam(team_a)
            else:
                player_a.joinTeam(team_b)
            return True
        else:
            return False


    def variation_5(self, player_a, player_b):
        """Simple trading with no networking. Player A meets Player B. They figure out the best one-shot trade. Player A selects the best possible objective to give away, as does Player B. If both mutually benefit, make the trade. Otherwise, walk away."""
        traded = False

        # Determine best objective to give away
        a_best_to_give = player_a.best_given_objective(player_a.resource, player_b.resource)
        b_best_to_give = player_b.best_given_objective(player_b.resource, player_a.resource)

        # Calculate hypothetical totals with those traded objectives
        a_total_if_no_trade = player_a.currentTotal()
        a_total_with_trade = player_a.currentTotal(objective_to_drop=a_best_to_give, given_objective=b_best_to_give, giver=player_b)

        b_total_if_no_trade = player_b.currentTotal()
        b_total_with_trade = player_b.currentTotal(objective_to_drop=b_best_to_give, given_objective=a_best_to_give, giver=player_a)

        a_delta_if_trade = a_total_with_trade - a_total_if_no_trade
        b_delta_if_trade = b_total_with_trade - b_total_if_no_trade 

        # Try to trade!
        if self.community_motivation is True: 
            # Determine community standing before and after trade
            community_before = self.community.total()
            community_total_with_trade = community_before + a_delta_if_trade + b_delta_if_trade            
            community_delta_if_trade = community_total_with_trade - community_before

            # If the community benefits, trade. Otherwise don't do anything
            if community_delta_if_trade > 0:
                player_a.giveObjective(a_best_to_give, player_b, traded_objectives_list=self.traded_objectives)
                player_b.giveObjective(b_best_to_give, player_a, traded_objectives_list=self.traded_objectives)
                traded = True

        else:  # If self.community_motivation is false...
            # If both players benefit, trade. Otherwise don't do anything
            if a_delta_if_trade > 0 and b_delta_if_trade > 0: 
                player_a.giveObjective(a_best_to_give, player_b, traded_objectives_list=self.traded_objectives)
                player_b.giveObjective(b_best_to_give, player_a, traded_objectives_list=self.traded_objectives)
                traded = True

        return traded


    def variation_1(self, player_a, player_b):
        """To network with another player, the requesting player (Player A) must drop one objective of their choice and leave it unfulfilled."""
        merged = False
        team_a = player_a.team
        team_b = player_b.team

        joint_resources_if_b_joins_a = uniquify(list(player_a.team.resources()) + list(player_b.resource))
        joint_resources_if_a_goes_to_b = uniquify(list(player_b.team.resources()) + list(player_a.resource))

        a_best_if_stay = player_a.best_given_objective(joint_resources_if_b_joins_a)
        a_best_if_move = player_a.best_given_objective(joint_resources_if_a_goes_to_b)

        a_total_if_move = player_a.currentTotal(player_b.team, objective_to_drop=a_best_if_move)
        a_total_if_stay = player_a.currentTotal(player_b, object_is_team=False, objective_to_drop=a_best_if_stay)
        b_total_if_move = player_b.currentTotal(player_a.team)
        b_total_if_stay = player_b.currentTotal(player_a, object_is_team=False)

        a_delta_if_move = a_total_if_move - player_a.currentTotal()  # A's hypothetical total on B's team after dropping an objective - A's current total
        a_delta_if_stay = a_total_if_stay - player_a.currentTotal()  # A's hypothetical total if B joins A, after dropping an objective - A's current total
        b_delta_if_move = b_total_if_move - player_b.currentTotal()  # B's hypothetical total on A's - B's current total
        b_delta_if_stay = b_total_if_stay - player_b.currentTotal()  # B's hypothetical total if A joined B - B's current total

        if self.community_motivation is True:  # MAYBE: This function is fine, but it's totally reusable. Make this more DRY-ish for the other variations.
            community_before = self.community.total()

            # Calculate deltas for all members of the team
            a_other_deltas = 0
            b_other_deltas = 0
            for player in [ p for p in team_a.players if p != player_a ]: # Iterate through all of the players on team A--exlcuding player A--to check their deltas
                player_delta = player.currentTotal(player_b, object_is_team=False) - player.currentTotal()
                a_other_deltas += player_delta

            for player in [ p for p in team_b.players if p != player_b ]: 
                player_delta = player.currentTotal(player_b, object_is_team=False) - player.currentTotal()
                b_other_deltas += player_delta

            community_total_a_to_b = community_before + a_delta_if_move + b_delta_if_stay + b_other_deltas
            community_total_b_to_a = community_before + a_delta_if_stay + b_delta_if_move + a_other_deltas

            community_delta_a_to_b = community_total_a_to_b - community_before
            community_delta_b_to_a = community_total_b_to_a - community_before

            if community_delta_a_to_b > 0 and community_delta_a_to_b > community_delta_b_to_a:
                # print "A should move to B"
                player_a.joinTeam(team_b)
                player_a.dropObjective(a_best_if_move, dropped_objectives_list=self.dropped_objectives)
                merged = True
            elif community_delta_b_to_a > 0 and community_delta_b_to_a > community_delta_a_to_b:
                # print "B should move to A"
                player_b.joinTeam(team_a)
                player_a.dropObjective(a_best_if_stay, dropped_objectives_list=self.dropped_objectives)
                merged = True
            elif community_delta_a_to_b > 0 and community_delta_a_to_b == community_delta_b_to_a:
                # print "Choose one..." 
                if choice(["move", "stay"]) == "stay":
                    player_b.joinTeam(team_a)
                    player_a.dropObjective(a_best_if_stay, dropped_objectives_list=self.dropped_objectives)
                else:
                    player_a.joinTeam(team_b)
                    player_a.dropObjective(a_best_if_move, dropped_objectives_list=self.dropped_objectives)
                merged = True
            else:
                # print "Don't do anything"
                merged = False

        else:  # If self.community_motivation is false...
            # # Player A's soliloquy
            # print "\nI'm {0} and I get to collaborate with {1}.".format(player_a.name, player_b.name)
            # print "On my current team, I have {0} points, objectives {1} and access to {2} ({3}).".format(player_a.currentTotal(), player_a.objectives, player_a.team.resources(), player_a.resource)
            # print "If I left to join {0} with {1}, I'd have {2} points because I'd have access to {3}. I would drop objective {4}, which is {5}.".format(
            #     player_b.team.name, 
            #     player_b.name, 
            #     a_total_if_move, 
            #     joint_resources_if_a_goes_to_b, 
            #     a_best_if_move, 
            #     player_a.objectives[a_best_if_move])
        
            # print "That would be a change of {0} points".format(a_delta_if_move)
            # print "But if {0} ({4}) came to join my team I would have {1} points because I'd have access to {2}. I would drop objective {3}.".format(
            #     player_b.name, 
            #     a_total_if_stay,
            #     joint_resources_if_b_joins_a,
            #     player_a.objectives[a_best_if_stay],
            #     player_b.resource)
            # print "And that would be a change of {0} points".format(a_delta_if_stay)
            
            # # # Player B's soliloquy
            # print "\nI'm {0} and {1} wants to collaborate with me".format(player_b.name, player_a.name)
            # print "On my current team, I have {0} points, objectives {1}, and access to {2}".format(player_b.currentTotal(), player_b.objectives, player_b.team.resources())
            # print "If I left to join {0} with {1}, I'd have {2} points because I'd have access to {3}".format(player_a.team.name, player_a.name, b_total_if_move, player_a.team.resources())
            # print "That would be a change of {0} points".format(b_delta_if_move)
            # print "But if {0} came to join my team I would have {1} points".format(player_a.name, b_total_if_stay)
            # print "And that would be a change of {0} points".format(b_delta_if_stay)

            # print "\n---------------------------\n"

            # print "Change for A if A moves to B:", a_delta_if_move
            # print "Change for A if B comes to A:", a_delta_if_stay
            # print "Change for B if B moves to A:", b_delta_if_move
            # print "Change for B if A comes to B:", b_delta_if_stay

            # print "\n---------------------------"

            # If both changes are negative, don't do anything
            if a_delta_if_stay <= 0 and a_delta_if_move <= 0:
                # print "All net changes are bad. Don't do anything."
                merged = False

            # If moving to B's team is better than staying, ask permission to move
            elif a_delta_if_move >= 0 and a_delta_if_move > a_delta_if_stay:
                merged = self.move(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_drop=a_best_if_move)

            # If staying is better than moving to B's team, invite B to join
            elif a_delta_if_stay >= 0 and a_delta_if_stay > a_delta_if_move:
                merged = self.invite(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_drop=a_best_if_stay)

            # If staying and moving give the same benefit, let B choose which one they want to do
            elif a_delta_if_stay == a_delta_if_move and a_delta_if_move > 0:
                # print "Either option is the same" 
                # Player A drops an objective because they are the initial requester
                if b_delta_if_move >= 0 and b_delta_if_move > b_delta_if_stay:
                    # print "B wants to move"
                    # merged = self.move(player_b, player_a, a_delta_if_move, a_delta_if_stay, objective_to_drop=a_best_if_stay)
                    merged = self.invite(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_drop=a_best_if_stay)
                elif b_delta_if_stay >= 0 and b_delta_if_stay > b_delta_if_move:
                    # print "B wants to stay"
                    # merged = self.invite(player_b, player_a, a_delta_if_move, a_delta_if_stay, a_best_if_move)
                    merged = self.move(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_drop=a_best_if_move)
                elif b_delta_if_stay == b_delta_if_move and b_delta_if_move > 0:
                    # print "Choose a random thing"
                    actions = [self.move, self.invite]
                    action = choice(actions)

                    if action == self.move:
                        merged = action(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_drop=a_best_if_move)
                    else:
                        merged = action(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_drop=a_best_if_stay)
                    
                else:
                    # print "Not a good deal for B. Don't do anything."
                    merged = False

        return merged


    def variation_2(self, player_a, player_b):
        """To network with another player, the requesting player (Player A) must offer one objective of their choice as payment to the recipient (Player B)."""
        merged = False
        team_a = player_a.team
        team_b = player_b.team

        joint_resources_if_b_joins_a = uniquify(list(player_a.team.resources()) + list(player_b.resource))
        joint_resources_if_a_goes_to_b = uniquify(list(player_b.team.resources()) + list(player_a.resource))

        a_best_if_stay = player_a.best_given_objective(joint_resources_if_b_joins_a)
        a_best_if_move = player_a.best_given_objective(joint_resources_if_a_goes_to_b)

        a_total_if_move = player_a.currentTotal(player_b.team, objective_to_drop=a_best_if_move)
        a_total_if_stay = player_a.currentTotal(player_b, object_is_team=False, objective_to_drop=a_best_if_stay)
        b_total_if_move = player_b.currentTotal(player_a.team, given_objective=a_best_if_stay, giver=player_a)  # Using these still results in 1200 points, but that's probably reality... maybe...
        b_total_if_stay = player_b.currentTotal(player_a, object_is_team=False, given_objective=a_best_if_move, giver=player_a)
        # b_total_if_move = player_b.currentTotal(player_a.team)
        # b_total_if_stay = player_b.currentTotal(player_a, object_is_team=False)

        a_delta_if_move = a_total_if_move - player_a.currentTotal()  # A's hypothetical total on B's team after dropping an objective - A's current total
        a_delta_if_stay = a_total_if_stay - player_a.currentTotal()  # A's hypothetical total if B joins A, after dropping an objective - A's current total
        b_delta_if_move = b_total_if_move - player_b.currentTotal()  # B's hypothetical total on A's - B's current total
        b_delta_if_stay = b_total_if_stay - player_b.currentTotal()  # B's hypothetical total if A joined B - B's current total

        # print "Combined resources if B comes to A", joint_resources_if_b_joins_a
        # print "Combined resources if A goes to B", joint_resources_if_a_goes_to_b, "\n"

        # print "Objective B gets if B comes to A", player_a.objectives[a_best_if_stay]
        # print "Objective B gets if A goes to B", player_a.objectives[a_best_if_move]

        if self.community_motivation is True:
            community_before = self.community.total()

            # Calculate deltas for all members of the team
            a_other_deltas = 0
            b_other_deltas = 0
            for player in [ p for p in team_a.players if p != player_a ]: # Iterate through all of the players on team A--exlcuding player A--to check their deltas
                player_delta = player.currentTotal(player_b, object_is_team=False) - player.currentTotal()
                a_other_deltas += player_delta

            for player in [ p for p in team_b.players if p != player_b ]: 
                player_delta = player.currentTotal(player_b, object_is_team=False) - player.currentTotal()
                b_other_deltas += player_delta

            community_total_a_to_b = community_before + a_delta_if_move + b_delta_if_stay + b_other_deltas
            community_total_b_to_a = community_before + a_delta_if_stay + b_delta_if_move + a_other_deltas

            community_delta_a_to_b = community_total_a_to_b - community_before
            community_delta_b_to_a = community_total_b_to_a - community_before

            if community_delta_a_to_b > 0 and community_delta_a_to_b > community_delta_b_to_a:
                # print "A should move to B"
                player_a.giveObjective(a_best_if_move, player_b, traded_objectives_list=self.traded_objectives)
                player_a.joinTeam(team_b)
                merged = True
            elif community_delta_b_to_a > 0 and community_delta_b_to_a > community_delta_a_to_b:
                # print "B should move to A"
                player_a.giveObjective(a_best_if_stay, player_b, traded_objectives_list=self.traded_objectives)
                player_b.joinTeam(team_a)
                merged = True
            elif community_delta_a_to_b > 0 and community_delta_a_to_b == community_delta_b_to_a:
                # print "Choose one..."
                if choice(["move", "stay"]) == "stay":
                    player_a.giveObjective(a_best_if_stay, player_b, traded_objectives_list=self.traded_objectives)
                    player_b.joinTeam(team_a)
                else:
                    player_a.giveObjective(a_best_if_move, player_b, traded_objectives_list=self.traded_objectives)
                    player_a.joinTeam(team_b)
                merged = True
            else:
                # print "Don't do anything"
                merged = False

        else:  # If self.community_motivation is false...
            # # Player A's soliloquy
            # print "\nI'm {0} and I get to collaborate with {1}.".format(player_a.name, player_b.name)
            # print "On my current team, I have {0} points, objectives {1} and access to {2} ({3}).".format(player_a.currentTotal(), player_a.objectives, player_a.team.resources(), player_a.resource)
            # print "If I left to join {0} with {1} ({6}), I'd have {2} points because I'd have access to {3} after giving away objective {4}, which is {5}.".format(
            #     player_b.team.name, 
            #     player_b.name, 
            #     a_total_if_move, 
            #     joint_resources_if_a_goes_to_b, 
            #     a_best_if_move, 
            #     player_a.objectives[a_best_if_move],
            #     player_b.resource)
            # print "That would be a change of {0} points".format(a_delta_if_move)

            # print "But if {0} came to join my team I would have {1} points because I'd have access to {2} after giving away objective {3}, which is {4}.".format(
            #     player_b.name, 
            #     a_total_if_stay,
            #     joint_resources_if_b_joins_a,
            #     a_best_if_stay,
            #     player_a.objectives[a_best_if_stay])
            # print "And that would be a change of {0} points".format(a_delta_if_stay)
            

            # # # Player B's soliloquy
            # print "\nI'm {0} and {1} wants to collaborate with me".format(player_b.name, player_a.name)
            # print "On my current team, I have {0} points, objectives {2} and access to {1}".format(player_b.currentTotal(), player_b.team.resources(), player_b.objectives)
            # print "If I left to join {0} with {1}, I'd have {2} points because I'd have access to {3}. I would gain objective {4}, which is {5}.".format(
            #     player_a.team.name, 
            #     player_a.name, 
            #     b_total_if_move, 
            #     joint_resources_if_b_joins_a,
            #     a_best_if_stay,
            #     player_a.objectives[a_best_if_stay])
            # print "That would be a change of {0} points".format(b_delta_if_move)
            # print "But if {0} came to join my team I would have {1} points, with access to {2} and objective {3}, which is {4}".format(
            #     player_a.name, 
            #     b_total_if_stay,
            #     joint_resources_if_a_goes_to_b,
            #     a_best_if_move,
            #     player_a.objectives[a_best_if_move])
            # print "And that would be a change of {0} points".format(b_delta_if_stay)

            # print "\n---------------------------\n"

            # print "Total for A as is:", player_a.currentTotal()
            # print "Total for B as is:", player_b.currentTotal(), "\n"

            # print "Total for A if A moves to B:", a_total_if_move
            # print "Total for A if B comes to A:", a_total_if_stay
            # print "Total for B if B moves to A:", b_total_if_move
            # print "Total for B if A comes to B:", b_total_if_stay, "\n"

            # print "Change for A if A moves to B:", a_delta_if_move
            # print "Change for A if B comes to A:", a_delta_if_stay
            # print "Change for B if B moves to A:", b_delta_if_move
            # print "Change for B if A comes to B:", b_delta_if_stay

            # print "\n---------------------------"

            # If both changes are negative, don't do anything
            if a_delta_if_stay <= 0 and a_delta_if_move <= 0:
                # print "All net changes are bad. Don't do anything."
                merged = False

            # If moving to B's team is better than staying, ask permission to move
            elif a_delta_if_move >= 0 and a_delta_if_move > a_delta_if_stay:
                merged = self.move(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_give=a_best_if_move)

            # If staying is better than moving to B's team, invite B to join
            elif a_delta_if_stay >= 0 and a_delta_if_stay > a_delta_if_move:
                merged = self.invite(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_give=a_best_if_stay)

            # If staying and moving give the same benefit, let B choose which one they want to do
            elif a_delta_if_stay == a_delta_if_move and a_delta_if_move > 0:
                # print "Either option is the same, so..." 
                # Player A drops an objective because they are the initial requester
                if b_delta_if_move >= 0 and b_delta_if_move > b_delta_if_stay:
                    # print "B wants to move"
                    # merged = self.move(player_b, player_a, a_delta_if_move, a_delta_if_stay, objective_to_give=a_best_if_stay)
                    merged = self.invite(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_give=a_best_if_stay)
                elif b_delta_if_stay >= 0 and b_delta_if_stay > b_delta_if_move:
                    # print "B wants to stay"
                    # merged = self.invite(player_b, player_a, a_delta_if_move, a_delta_if_stay, a_best_if_move)
                    merged = self.move(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_give=a_best_if_move)
                elif b_delta_if_stay == b_delta_if_move and b_delta_if_move > 0:
                    # print "Choose a random thing"
                    actions = [self.move, self.invite]
                    action = choice(actions)

                    if action == self.move:
                        merged = action(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_give=a_best_if_move)
                    else:
                        merged = action(player_a, player_b, b_delta_if_move, b_delta_if_stay, objective_to_give=a_best_if_stay)
                    
                else:
                    # print "Not a good deal for B. Don't do anything."
                    merged = False

        # print "\n***********************************\n"
        return merged


    def variation_3(self, player_a, player_b):
        """To network with another player, both players must agree to network."""
        merged = False
        team_a = player_a.team
        team_b = player_b.team

        a_total_if_move = player_a.currentTotal(player_b.team)
        a_total_if_stay = player_a.currentTotal(player_b, object_is_team=False)
        b_total_if_move = player_b.currentTotal(player_a.team)
        b_total_if_stay = player_b.currentTotal(player_a, object_is_team=False)

        a_delta_if_move = a_total_if_move - player_a.currentTotal()  # A's hypothetical total on B's team - A's current total
        a_delta_if_stay = a_total_if_stay - player_a.currentTotal()  # A's hypothetical total if B joins A - A's current total
        b_delta_if_move = b_total_if_move - player_b.currentTotal()  # B's hypothetical total on A's - B's current total
        b_delta_if_stay = b_total_if_stay - player_b.currentTotal()  # B's hypothetical total if A joined B - B's current total

        if self.community_motivation is True:
            community_before = self.community.total()

            # Calculate deltas for all members of the team
            a_other_deltas = 0
            b_other_deltas = 0
            for player in [ p for p in team_a.players if p != player_a ]: # Iterate through all of the players on team A--exlcuding player A--to check their deltas
                player_delta = player.currentTotal(player_b, object_is_team=False) - player.currentTotal()
                a_other_deltas += player_delta

            for player in [ p for p in team_b.players if p != player_b ]: 
                player_delta = player.currentTotal(player_b, object_is_team=False) - player.currentTotal()
                b_other_deltas += player_delta

            community_total_a_to_b = community_before + a_delta_if_move + b_delta_if_stay + b_other_deltas
            community_total_b_to_a = community_before + a_delta_if_stay + b_delta_if_move + a_other_deltas

            community_delta_a_to_b = community_total_a_to_b - community_before
            community_delta_b_to_a = community_total_b_to_a - community_before

            if community_delta_a_to_b > 0 and community_delta_a_to_b > community_delta_b_to_a:
                # print "A should move to B"
                player_a.joinTeam(team_b)
                merged = True
            elif community_delta_b_to_a > 0 and community_delta_b_to_a > community_delta_a_to_b:
                # print "B should move to A"
                player_b.joinTeam(team_a)
                merged = True
            elif community_delta_a_to_b > 0 and community_delta_a_to_b == community_delta_b_to_a:
                # print "Choose one..."
                if choice(["move", "stay"]) == "stay":
                    player_b.joinTeam(team_a)
                else:
                    player_a.joinTeam(team_b)
                merged = True
            else:
                # print "Don't do anything"
                merged = False

        else: # If self.community_motivation is false...
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

            # If both changes are negative, don't do anything
            if a_delta_if_stay <= 0 and a_delta_if_move <= 0:
                # print "All net changes are bad. Don't do anything."
                merged = False

            # If moving to B's team is better than staying, ask permission to move
            elif a_delta_if_move >= 0 and a_delta_if_move > a_delta_if_stay:
                merged = self.move(player_a, player_b, b_delta_if_move, b_delta_if_stay)

            # If staying is better than moving to B's team, invite B to join
            elif a_delta_if_stay >= 0 and a_delta_if_stay > a_delta_if_move:
                merged = self.invite(player_a, player_b, b_delta_if_move, b_delta_if_stay)

            # If staying and moving give the same benefit, let B choose which one they want to do
            elif a_delta_if_stay == a_delta_if_move and a_delta_if_move > 0:
                # print "Either option is the same" 

                if b_delta_if_move >= 0 and b_delta_if_move > b_delta_if_stay:
                    # print "Try to move to A"
                    merged = self.move(player_b, player_a, a_delta_if_move, a_delta_if_stay)
                elif b_delta_if_stay >= 0 and b_delta_if_stay > b_delta_if_move:
                    # print "Invite A to join B"
                    merged = self.invite(player_b, player_a, a_delta_if_move, a_delta_if_stay)
                elif b_delta_if_stay == b_delta_if_move and b_delta_if_move > 0:
                    # print "Choose a random thing"
                    actions = [self.move, self.invite]
                    merged = choice(actions)(player_b, player_a, a_delta_if_move, a_delta_if_stay)
                else:
                    # print "Not a good deal for B"
                    merged = False

        return merged


    def variation_4(self, player_a, player_b):
        """To network with another player, both players must agree to network. No team can contain more than two players."""
        merge_occurred = False
        team_a = player_a.team
        team_b = player_b.team

        a_current = player_a.currentTotal()
        b_current = player_b.currentTotal()
        a_new_team = player_a.currentTotal(player_b, object_is_team=False, new_team=True)
        b_new_team = player_b.currentTotal(player_a, object_is_team=False, new_team=True)
        a_delta_if_new_team = a_new_team - a_current
        b_delta_if_new_team = b_new_team - b_current

        if self.community_motivation is True:
            community_before = self.community.total()
            # print "Player A currently", a_current
            # print "Player B currently", b_current
            # print "Player A if they make a new team:", a_new_team
            # print "Player B if they make a new team:", b_new_team

            # Calculate deltas for team members left behind
            other_deltas = 0
            for player in [ p for p in (team_a.players + team_b.players) if (p != player_a and p != player_b) ]: # Iterate through all of the other players on the teams
                player_delta = player.currentTotal(alone=True) - player.currentTotal()
                other_deltas += player_delta

            # print "Other deltas", other_deltas

            community_total_new_team = community_before + a_delta_if_new_team + b_delta_if_new_team + other_deltas
            community_delta_new_team = community_total_new_team - community_before
            # print "Community total with new team:", community_total_new_team
            # print "Community delta with new team:", community_delta_new_team

            if community_delta_new_team > 0:
                # print "Create new team"
                # player_a.joinTeam(team_b)
                merge_occurred = True
            else:
                # print "Don't do anything"
                merge_occurred = False
        else:
            # print "\nPlayer A with A+B team:", player_a.currentTotal(player_b, object_is_team=False, new_team=True)
            # print "Player B with A+B team:", player_b.currentTotal(player_a, object_is_team=False, new_team=True)

            # print "\nChange for A if create A+B team:", a_delta_if_new_team
            # print "Change for B if create A+B team:", b_delta_if_new_team

            # A's turn to make changes first
            if a_delta_if_new_team > 0:
                # print "Try to make a new team with B."

                if b_delta_if_new_team > 0:
                    # print "B agrees. Make a new team."
                    merge_occurred = True
                else:
                    # print "B doesn't agree. No new team."
                    merge_occurred = False
            else:
                # print "Don't try to make a new team."
                merge_occurred = False

            # If nothing happened, let B try to make a change
            if merge_occurred is False:
                # print "B wants to try something too."

                if b_delta_if_new_team > 0:
                    if a_delta_if_new_team > 0:
                        # print "A agrees. Make a new team."
                        merge_occurred = True
                    else:
                        # print "A doesn't agree. No new team."
                        merge_occurred = False
                else:
                    # print "Just kidding. B doesn't want to do anything."
                    merge_occurred = False

        if merge_occurred:
            # print "Yay! Something good happened!"
            newTeam = Team(self.community.last_team_index() + 1)
            self.teams.append(newTeam)
            player_a.joinTeam(newTeam)
            player_b.joinTeam(newTeam)
            return True
        else:
            # print "Nope. Nothing good could happen. Carry on."
            return False


    # Globalish invitation and moving algorithms
    def invite(self, inviter, invitee, delta_if_move, delta_if_stay, objective_to_drop=None, objective_to_give=None):
        if (objective_to_drop and objective_to_give):
            raise Exception("Cannot pass `objective_to_drop` and `objective_to_give` at the same time.")

        # print "{0} inviting {1}".format(inviter.name, invitee.name)
        if delta_if_move >= 0 and delta_if_move > delta_if_stay:
            # print "This is the ideal situation. Permission granted."
            if objective_to_drop:
                inviter.dropObjective(objective_to_drop, dropped_objectives_list=self.dropped_objectives)
            if objective_to_give:
                inviter.giveObjective(objective_to_give, invitee, traded_objectives_list=self.traded_objectives)
            invitee.joinTeam(invitee.team)
            return True
        elif delta_if_stay >= 0 and delta_if_stay > delta_if_move:
            # print "It's better if the invitee stays... " 
            return False
        elif delta_if_move == delta_if_stay and delta_if_move > 0:
            # print "It doesn't matter to the invitee. Permission granted."
            if objective_to_drop:
                inviter.dropObjective(objective_to_drop, dropped_objectives_list=self.dropped_objectives)
            if objective_to_give:
                inviter.giveObjective(objective_to_give, invitee, traded_objectives_list=self.traded_objectives)
            invitee.joinTeam(invitee.team)
            return True
        else:
            # print "Permission denied"
            return False

    def move(self, asker, asked, delta_if_move, delta_if_stay, objective_to_drop=None, objective_to_give=None):
        if (objective_to_drop and objective_to_give):
            raise Exception("Cannot pass `objective_to_drop` and `objective_to_give` at the same time.")

        # print "{0} trying to join {1}".format(asker.name, asked.name)
        if delta_if_stay > 0 and delta_if_stay > delta_if_move:
            # print "This is the ideal situation. Permission granted."
            if objective_to_drop:
                asker.dropObjective(objective_to_drop, dropped_objectives_list=self.dropped_objectives)
            if objective_to_give:
                asker.giveObjective(objective_to_give, asked, traded_objectives_list=self.traded_objectives)
            asker.joinTeam(asked.team)
            return True
        elif delta_if_move > 0 and delta_if_move > delta_if_stay:
            # print "It's better if the asked moves... "
            return False
        elif delta_if_stay == delta_if_move and delta_if_stay > 0:
            # print "It doesn't matter to the asked. Permission granted."
            if objective_to_drop:
                asker.dropObjective(objective_to_drop, dropped_objectives_list=self.dropped_objectives)
            if objective_to_give:
                asker.giveObjective(objective_to_give, asked, traded_objectives_list=self.traded_objectives)
            asker.joinTeam(asked.team)
            return True
        else:
            # print "Permission denied"
            return False

class ResourcePool:
    """Creates a pool of resources with high and low distributions according to the frequency in `approximate_high_low_resource_ratio`
    
    For example, if there are 16 players, with 4 different types of resources, and an approximate ratio of 3:1, the pool will be a dictionary distributed like so:
    {'A': 6, 'B': 6, 'C': 2, 'D': 2}
    with A and B as high frequency resources and C and D as low frequency
    
    Attributes:
        high: A string of the high frequency resources (e.g. "AB")
        low: A string of the low frequency resources (e.g. "CD")
        resources_list: A list of tuples (e.g. [('A', 'high_freq'), ('B', 'high_freq'), ('C', 'low_freq'), ('D', 'low_freq')])
        pool: A dictionary structured like {'resource name': quantity, ...}
    
    Returns: 
        A resource pool object
    """
    def __init__(self, resources, players, approximate_high_low_resource_ratio):
        """Create the resource pool object
        
        Args:
            resources: The number of resource types
            players: The number of players in the simulation
        """
        divided = self.divide_high_low(resources)
        self.high = divided.high
        self.low = divided.low

        resources_list = []
        for resource in list(divided.high):
            resources_list.append((resource, "high_freq"))

        for resource in list(divided.low):
            resources_list.append((resource, "low_freq"))

        self.resources_list = sorted(resources_list)

        r = self.create_distribution_ratios(divided.low, divided.high, approximate_high_low_resource_ratio)
        self.pool = dict(sorted(Counter(islice(r, players)).items()))

    def create_distribution_ratios(self, prop_low, prop_high, approximate_high_low_resource_ratio):
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
        pool: A dictionary of objective distributions (e.g. {'a1': 15, 'a2': 15, 'b1': 5, 'b2': 5, 'c2': 15, 'c1': 15, 'd2': 5, 'd1': 5}) (a dictionary so that the objectives can be indexed)
        table: A list of dictionaries with each objective name and value (e.g. [{'name': 'a1', 'value': 20},... {'name': 'c2', 'value': 10},...])
    
    Returns: 
        An objective pool object
    """
    def __init__(self, resource_pool, num_players, num_objs_per_player, approximate_high_low_objective_ratio, value_high, value_low):
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
        o = self.create_distribution_ratios(objectives_low, objectives_high, approximate_high_low_objective_ratio)
        self.pool = dict(sorted(Counter(islice(o, self.num_objs)).items()))

        # Create a list of named dictionary pairs for each objective in the pool
        objs_table = []
        objs_list = []
        for i in self.pool.items():
            for j in range(i[1]):
                if int(i[0][1]) == 1: # if the objective's subscript is 1 (e.g. "a1")
                    value = value_high
                else:
                    value = value_low
                objs_table.append({'name':i[0], 'value':value})
                objs_list.append([i[0], value])
        self.table = objs_table
        self.obj_list = objs_list

    def create_distribution_ratios(self, prop_low, prop_high, approximate_high_low_objective_ratio):
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
    """A community contains all the players and teams involved in a simulation. 

    The object also provides functions for retrieving statistics about the community.

    Attributes:
        players: A dictionary of the player objects provided at initialization
        teams: A list of the team objects provided at initialization
    
    Returns: 
        A new community object
    """
    def __init__(self, players, teams):
        """
        Initialize community object with given players and teams.

        Args:
            players: A dictionary of player objects to be added to the community (generated in CollaborationModel::build())
            teams: A list of team objects to be added to the community (also generated in CollaborationModel::build())
        """
        self.players = players
        self.teams = teams
    
    def total(self):
        """Returns the combined values of all teams in the community, or the current social value of the community."""
        total = 0
        for i, player in self.players.items():
            total += player.currentTotal()
        return total

    def activeTeams(self):
        """Returns a list of all teams in the community that have at least one player."""
        return [ team for team in self.teams if team.playerCount() > 0 ]

    def last_team_index(self):
        """Returns the index of the last team in the community.

        Used in variation 4 of the simulation, where new teams of two players are added to the community. 
        Those teams use the next sequential team index when created.
        """
        return self.teams[-1].index

    def teamStats(self):
        """Calculate basic summary statistics for the teams in the community.

        Returns a named tuple of class 'TeamStatistics' with attributes number, min, max, mean, and median.
        """
        team_sizes = [ team.playerCount() for team in self.activeTeams() ]
        TeamStatistics = namedtuple('TeamStatistics', 'number, min, max, mean, median')
        return TeamStatistics(len(team_sizes), min(team_sizes), max(team_sizes), mean(team_sizes), median(team_sizes))

    def individualStats(self):
        """Calculate basic summary statistics for the players in the community.

        Returns a named tuple of class 'IndividualStatistics' with attributes number, min, max, mean, and median.
        """
        player_scores = [player.currentTotal() for i, player in self.players.items() ]
        IndividualStatistics = namedtuple('IndividualStatistics', 'min, max, mean, median')
        return IndividualStatistics(min(player_scores), max(player_scores), mean(player_scores), median(player_scores))

    def potentialTotal(self, objectives_table):
        """Returns the potential total community social value given the objectives available in the simulation.

        Args: 
            objectives_table: List of dictionaries of objectives in an ObjectivePool() object (e.g. [{'name': 'a1', 'value': 20},... {'name': 'c2', 'value': 10},...])
        """
        return sum(objective['value'] for objective in objectives_table)

    def objectivesSubset(self):
        """Determines which of the objectives in the community have been fulfilled (i.e. the player holding the objective has access to a matching resource in their team).

        Player.objectivesSubset() returns a named tuple of a player's fulfilled and unfulfilled objectives. This method loops through all the players on the team and makes comprehensive lists of all players' fulfilled and unfulfilled objectives. 

        Returns a named tuple of class 'ObjectivesSubset' with attributes fulfilled and unfulfilled.
        """
        ObjectivesSubset = namedtuple('ObjectivesSubset', 'fulfilled, unfulfilled')
        fulfilled = []
        unfulfilled = []

        # Loop through all the players and separate their objectives into fulfilled and unfulfilled lists
        for player in self.players:
            player_subset = self.players[player].objectivesSubset()
            fulfilled += player_subset.fulfilled
            unfulfilled += player_subset.unfulfilled

        return ObjectivesSubset(fulfilled, unfulfilled)


class Team:
    """A team is a collection of players that have decided to collaborate in order to achieve higher personal or societal value. 
    
    Attributes:
        name: The team's name
        index: The index of the team (zero-based)
        players: A list of player objects that are part of the team
    
    Returns:
        A new team object
    """
    def __init__(self, index):
        """Creates a new team object consisting of exactly one player.
        
        Args:
            name: The player's name
            player: A single player object
        """
        self.name = "Team %02d"%index 
        self.index = index
        self.players = []
    
    def playerCount(self):
        """Returns a count how many players there are on the team."""
        return len(self.players)
    
    def resources(self):
        """Returns a list of all unique resources available on the team."""
        resources = []
        for player in self.players:
            resources.append(player.resource)
        return uniquify(resources)
    
    def totalValue(self, newPlayer=None):
        """Returns a team's current value.

        Args:
            newPlayer: Optionally pass a player object to calculate the team's value with that player on the team
        """
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
        """Pretty prints a sentence explaining the team's current standing.

        For example, "We are Team 02; we have Player 02, Player 05 on our team; we have resources ['D', 'C']; and our total social value is 60."
        """
        if self.players:
            players = ', '.join('%s' % player.name for player in self.players)  # Build a comma separated list of players
            print "We are %s; we have %s on our team; we have resources %s; and our total social value is %s."%(self.name, players, self.resources(), self.totalValue())
        else:
            print "%s is empty." % (self.name)
    
    def addPlayer(self, player):
        """Adds a given player object to the team."""
        self.players.append(player)
    
    def removePlayer(self, player):
        """Removes a given player object from the team."""
        self.players.remove(player)


class Player:
    """A player is the primary element of the simulation and is responsible for maximizing its personal or societal value by trading objectives with other players.
    
    Attributes:
        name: The player's name
        resource: The name of a resource (i.e. "A")
        objectives: A dictionary of lists, corresponding to the objective index, objective name, and objective value. (i.e. {0: ['a1', 20], 1: ['d1', 20], 2: ['a2', 10], 3: ['b2', 10], 4: ['c1', 20]})
    
    Returns:
        A new player object
    """

    def __init__(self, name, resource, objective_indices, objectives_table):
        """Creates a new player object based on resource and objective pools created beforehand.
        
        Args:
            name: The player's name
            resource: The name of a resource (i.e. "A")
            objective_indices: A list of objective indices (i.e. [1, 2, 3, 4, 5])
            objectives_table: List of dictionaries of objectives in an ObjectivePool() object (e.g. [{'name': 'a1', 'value': 20},... {'name': 'c2', 'value': 10},...])
        """
        self.name = name
        self.resource = resource
        
        # Build the dictionary of lists: {`index`: [`objective name`, `objective value`]}
        self.objectives = {}
        for i in objective_indices:
            self.objectives[i] = [objectives_table[i]['name'], objectives_table[i]['value']]

    def currentTotal(self, test_object=None, object_is_team=True, new_team=False, alone=False, objective_to_drop=None, given_objective=None, giver=None):
        """Returns a player's current total, summing the values of all objectives that match a player's assigned resource. Additional arguments return the player's hypothetical total.
        
        Args:
            test_object: A team or player object that will be used to calculate a player's hypothetical total.
            object_is_team: Boolean that defaults to true. By default, this will test a hypothetical team; if false, it will test a hypothetical player.
            new_team: Boolean that defaults to false. If true, the current player's resource will be combined with the resource of the test_object (which must be a player); if false, the current player's resource will be combined with the resources of the test_object's team.
            alone: Boolean that defaults to false. If true, the player's total will be calculated using only their given resource; if false, the player's team's resources will be used.
            objective_to_drop: The integer index indicating which objective to disregard when calculating the current total (used for variations 1 and 1).
            given_objective: The integer index indicating which objective to add when calculating the current total (used for variation 2).
            giver: The player object hypothetically giving up their objective.

        Raises:
            A general exception if the method is called with new_team and a team object, since new_team implies that the player will leave their current team to make a new one in variation 4.
            A general exception if the method is called with new_team and object_is_team both set to true, since new_team requires that test_object is a player, not a team.
            A general exception if the method is called with giver and not with given_objective, since given_objective requires that someone gives that objective.
        """

        # Check to make sure the method is called properly
        if (object_is_team is True or test_object is None) and new_team is True:
            raise Exception("Can't use `new_team` on a team object or without a `test_object`")
        if new_team is True and object_is_team is True:
            raise Exception("`new_team` and `object_is_team` cannot both be true.")
        if giver is None and not given_objective is None:
            raise Exception("Can't have a `giver` without a `given_objective`") 

        # Determine which objectives to use in the total calculation
        if given_objective and objective_to_drop:  # If an objective is dropped and given away, like in variation 5...
            objectives = deepcopy(self.objectives)  # Make a copy of the dictionary
            del objectives[objective_to_drop]  # Remove the objective
            objectives[given_objective] = giver.objectives[given_objective]
        else:  # All other variations
            if not objective_to_drop is None:
                objectives = deepcopy(self.objectives)  # Make a copy of the dictionary
                del objectives[objective_to_drop]  # Remove the objective
            elif not given_objective is None:
                objectives = deepcopy(self.objectives)  # Make a copy of the dictionary
                objectives[given_objective] = giver.objectives[given_objective]
            else:
                objectives = self.objectives  # Use the full dictionary of objectives

        # Determine which pool of resources to use in the total calculation
        if alone:  # If alone, just use the player's single given resource; nobody else's
            resources = self.resource
        elif test_object is None and not alone:  # If no object is specified, use the actual team
            resources = self.team.resources()
        else:  # Create a hypothetical pool of team resources
            if object_is_team == True:  # Combine the hypothetical team's resources and the actual player's single resource
                    resources = uniquify(test_object.resources() + list(self.resource))
            else:
                if new_team == True:  # Combine the single resource of the actual player and the single resource of the hypothetical player
                    resources = uniquify(list(self.resource) + list(test_object.resource))
                else:  # Combine the hypothetical player's single resource and the actual player's team resources
                    resources = uniquify(self.team.resources() + list(test_object.resource))  
        
        # Calculate the total of each fulfilled objective, given the player's hypothetical or actual objectives and hypothetical or actual resource pool
        total = 0
        for index, details in objectives.items():  # objectives.items() is a dictionary with a list, i.e. {41: ['c2', 10], 5: ['a1', 20], 13: ['a1', 20], 30: ['b1', 20], 71: ['d2', 10]}
            for resource in resources:
                if resource == details[0][0].upper():  # details[0] is the first element in the list, i.e. 'c2'. details[0][0] is the first letter, i.e. 'c'
                    total += details[1]  # details[1] is the second element in the list, i.e. 10

        return total

    def objectivesSubset(self):
        """Determines which of the player's objectives have been fulfilled (i.e. the player holding the objectives has access to a matching resource in their team).

        Returns a named tuple of class 'ObjectivesSubset' with attributes fulfilled and unfulfilled.
        """
        # Retrieve the player's resources and objectives
        resources = self.team.resources()
        objectives = self.objectives

        ObjectivesSubset = namedtuple('ObjectivesSubset', 'fulfilled, unfulfilled')

        met = {}  # Initialize the met dictionary, which mirrors the structure of the community's objective pool (i.e. {5: ['a1', 20], 30: ['b1', 20]})
        for index, details in objectives.items():  # See comments at the end of Player::currentTotal() for an explanation of objective.items() and details[]
            for resource in resources:
                if resource == details[0][0].upper():
                    met[index] = details

        unfulfilled_indexes = [objective for objective in objectives if objective not in met]  # See which objectives weren't met
        unmet = {i : objectives[i] for i in unfulfilled_indexes}  # Dictionary comprehension to create unmet dictionary, mirroring the structure of met (i.e. {0: ['a1', 20], 26: ['b2', 10], 27: ['b2', 10]})

        return ObjectivesSubset(met.values(), unmet.values())  # Return just the values from the met and unmet dictionaries
    
    def dropObjective(self, objective_to_drop, dropped_objectives_list):
        """Drops an objective.

        Args:
            objective_to_drop: Objective index to drop
            dropped_objective_list: Community object attribute keeping track of dropped objectives
        """
        dropped = self.objectives.pop(objective_to_drop)  # Remove the objective from the current player
        dropped_objectives_list.append(dropped)  # Mark it

    def giveObjective(self, objective_to_give, receiver, traded_objectives_list):
        """Gives an objective to a specified player.

        Args:
            objective_to_give: Objective index to give away
            receiver: Player object to receive the given objective
            traded_objectives_list: Community object attribute keeping track of traded objectives
        """
        give_away = self.objectives.pop(objective_to_give)  # Remove the objective from the current player
        traded_objectives_list.append(give_away)  # Mark it
        receiver.objectives[objective_to_give] = give_away  # Give the objective to the receiver
    
    def joinTeam(self, team):
        """Adds a player to a different team.

        Args: 
            team: Team object to join
        """
        self.team.removePlayer(self)  # Leave current team
        team.addPlayer(self)  # Join new team
        self.team = team  # Reassign new team to player attributes
    
    def setInitialTeam(self, team):
        """Sets a player's initial team to the team object provided."""
        self.team = team
    
    def report(self):
        """Pretty prints a sentence explaining the player's current position.

        For example, "I am Player 01; I have resource C; I have objectives a1, d1, a1, c1, d1; I'm on team Team 00; and my total value is 60."
        """
        objectives = ', '.join('%s' % obj[0] for obj in self.objectives.values())  # Build a comma separated list of objectives
        print "I am %s; I have resource %s; I have objectives %s; I'm on team %s; and my total value is %s."%(self.name, self.resource, objectives, self.team.name, self.currentTotal())

    def best_given_objective(self, resource_pool, other_resource=None):
        """
        Determines the best objective to drop or give away.

        Args:
            resource_pool: A list of resources to consider when determining which objective to get rid of (i.e. ['B', 'D', 'C'])
            other_resource (optional): The resource of the other player when running variation 5

        Returns the index of the objective to be dropped or given away.
        """
        # Initialize dictionaries to organize objectives with.
        good = {}  # good_high and good_low contain the player's fulfilled high-value and low-value objectives 
        good_high = {}
        good_low = {}

        worthless = {}  # worthless_high and worthless_low contain the player's unfulfilled high-value and low-value objectives
        worthless_high = {}
        worthless_low = {}

        best_objective = None

        # Build general good and worthless dictionaries
        for index, details in self.objectives.items():
            for resource in resource_pool:
                if resource == details[0][0].upper():
                    good[index] = details

            if index not in good:
                worthless[index] = details

        # Separate good and worthless into high and low
        if len(good) > 0:
            for index, details in good.items():
                if int(details[0][1]) == 1:
                    good_high[index] = details
                else:
                    good_low[index] = details

        if len(worthless) > 0:
            for index, details in worthless.items():
                if int(details[0][1]) == 1:
                    worthless_high[index] = details
                else:
                    worthless_low[index] = details

        if other_resource:
            # Try to match an objective to the other player's resource
            # Order of selection = worthless_low -> worthless_high -> good_low. Don't potentially give up any good_high.
            for index, details in worthless_low.items():
                if details[0][0].upper() == other_resource:
                    best_objective = index
                    break
            if not best_objective:  # If nothing was found in worthless_low, make an offer from worthless_high
                for index, details in worthless_high.items():
                    if details[0][0].upper() == other_resource:
                        best_objective = index
                        break
            if not best_objective:  # If nothing was found in worthless_high, make an offer from good_low
                for index, details in good_low.items():
                    if details[0][0].upper() == other_resource:
                        best_objective = index
                        break
            # If no good match was found, use the regular selection algorithm below to give away an objective that doesn't match
            
        if not best_objective:
            # Choose an objective to get rid of, starting with the worthless_low dictionary
            # Order of selection = worthless_low -> worthless_high -> good_low -> good_high
            if len(worthless_low.keys()) > 0:
                best_objective = worthless_low.keys()[0]
            elif len(worthless_high.keys()) > 0:
                best_objective = worthless_high.keys()[0]
            elif len(good_low.keys()) > 0:
                best_objective = good_low.keys()[0]
            elif len(good_high.keys()) > 0:
                best_objective = good_high.keys()[0]

        return best_objective  # Return the key or index of the objective


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

def mean(n):
    if len(n):
        return sum(n) / float(len(n))
    else:
        return 0.0

def median(n):
    l = len(n)
    if not l%2:
        return (n[(l/2)-1]+n[l/2])/2.0
    return n[l/2]


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
