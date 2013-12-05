.PHONY: all simulation output finished

#--------------------
# Color definitions
#--------------------
ifeq ($(OS),Windows_NT)
NO_COLOR    = 
BOLD_COLOR	= 
OK_COLOR    = 
WARN_COLOR  = 
ERROR_COLOR = 
else
NO_COLOR    = \x1b[0m
BOLD_COLOR	= \x1b[37;01m
OK_COLOR    = \x1b[32;01m
WARN_COLOR  = \x1b[33;01m
ERROR_COLOR = \x1b[31;01m
endif

#--------------
# Compilation
#--------------
all: simulation output
simulation: Output/all_variations.csv
output: Output/table_4.html Output/figure_1.pdf finished

#-------------------
# Individual parts
#-------------------
Output/all_variations.csv: simulation/run_simulation.py
	@echo "Running simulation $(WARN_COLOR)(this can take a while)...$(NO_COLOR)"
	@-mkdir Output 2>/dev/null || true
	@cd simulation; python run_simulation.py

Output/table_4.html: R/table_4.R R/load_data.R Output/all_variations.csv
	@echo "Creating tables..."
	@-mkdir Output 2>/dev/null || true
	@cd R; Rscript table_4.R

Output/figure_1.pdf: R/figures.R R/load_data.R Output/all_variations.csv
	@echo "Creating figures..."
	@-mkdir Output 2>/dev/null || true
	@cd R; Rscript figures.R

finished:
	@echo "$(OK_COLOR)All done!$(NO_COLOR)"
	@echo "$(BOLD_COLOR)Check the Output folder for the completed files.$(NO_COLOR)"
