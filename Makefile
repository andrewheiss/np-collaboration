all: simulation output
simulation: simulation/all_variations.csv
output: Output/table_4.html Output/figure_1.pdf

Output/all_variations.csv: simulation/run_simulation.py
	-mkdir Output 2>/dev/null
	cd simulation; python run_simulation.py

Output/table_4.html: R/table_4.R R/load_data.R Output/all_variations.csv
	-mkdir Output 2>/dev/null
	cd R; Rscript table_4.R

Output/figure_1.pdf: R/figures.R R/load_data.R Output/all_variations.csv
	-mkdir Output 2>/dev/null
	cd R; Rscript figures.R; rm Rplots.pdf  # TODO: Make R not output this extra pdf