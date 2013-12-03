#!/usr/bin/env python
from simulation import *
from multiprocessing import Pool
import random
import fileinput
import os

#-----------------------------------------------------------
# Set up the simulation 
# (change these variables to create different simulations)
#-----------------------------------------------------------
seed = 12345
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
def run_variation(variation):
  # Seed has to be set here because of multiprocessing
  random.seed(seed)
  # On variation 0, include headers and make sure the file is opened with 'wb' to create a new file. 
  # Use 'awb' after that to append to the new file
  if variation == 0:
    csv_header = True
  else:
    csv_header = False

  # Initialize
  csv_file = open('variation_{0}.csv'.format(variation), 'wb')
  csv_out = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_ALL)

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

# Single core version
# map(run_variation, variations)

# Multiple core version! (65% performance boost!)
# This line needed for Windows (see http://docs.python.org/2/library/multiprocessing.html#windows)
if __name__ == '__main__':
  pool = Pool() 
  pool.map(run_variation, variations)
  pool.close()
  pool.join()

# Loop through the temporary csv files, combine them, and delete them
filenames = ['variation_{0}.csv'.format(variation) for variation in variations]
with open('../Output/all_variations.csv', 'w') as fout:
    for line in fileinput.input(filenames):
        fout.write(line)
[os.remove(fn) for fn in filenames]
