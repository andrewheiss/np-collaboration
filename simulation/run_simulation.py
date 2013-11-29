#!/usr/bin/env python
from simulation import *
import random

#-----------------------------------------------------------
# Set up the simulation 
# (change these variables to create different simulations)
#-----------------------------------------------------------
random.seed(12345)
num_players = 16
num_resources = 4
num_objs_per_player = 5
value_high = 20
value_low = 10
approximate_high_low_resource_ratio = 3
approximate_high_low_objective_ratio = 3
faux_pareto_rounds_without_merges = 25
times_to_run_simulation = 500
variations = [0, 1, 3, 5]  # Must be 0, 1, 2, 3, 4, or 5. 0 exports initial allocation data; 1-5 actually run simulation algorithms.

#------------------------------
# Actual simulation procedure
#------------------------------
# Create CSV file
csv_file = open('all_variations.csv', 'wb')
csv_out = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)

# Run the simulation
for variation in variations:
  # Only include headers for variation 0
  if variation == 0:
    csv_header = True
  else:
    csv_header = False

  community_motivation = False  # Personal motivation
  for i in xrange(times_to_run_simulation):
    # simulation.test_run()
    simulation = CollaborationModel(num_players, num_resources, num_objs_per_player, 
      approximate_high_low_resource_ratio, approximate_high_low_objective_ratio,
      value_high, value_low, variation, faux_pareto_rounds_without_merges, 
      community_motivation, csv_out, csv_header)
    simulation.run(i)

  community_motivation = True  # Community motivation
  for i in xrange(times_to_run_simulation):
    simulation = CollaborationModel(num_players, num_resources, num_objs_per_player, 
      approximate_high_low_resource_ratio, approximate_high_low_objective_ratio,
      value_high, value_low, variation, faux_pareto_rounds_without_merges, 
      community_motivation, csv_out, csv_header)
    simulation.run(i + times_to_run_simulation)

csv_file.close()

# MAYBE: Export a text-based version of a single run
# MAYBE: Use RPy to build fancy ggplot graphs automatically