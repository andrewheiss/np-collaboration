# Nonprofit Collaboration and the Resurrection of Market Failure

[Eva Witesman](http://fds.duke.edu/db/Sanford/rogerson) • Romney Institute of Public Management • Brigham Young University  
[Andrew Heiss](http://www.andrewheiss.com/) • Sanford School of Public Policy • Duke University

------

> Eva Witesman and Andrew Heiss, “Nonprofit Collaboration and the Resurrection of Market Failure: How a Resource-Sharing Environment Can Suppress Social Objectives,” *Voluntas: International Journal of Voluntary and Nonprofit Organizations*, 2016, 1–29, doi:[10.1007/s11266-016-9684-5](https://dx.doi.org/10.1007/s11266-016-9684-5).

## Abstract

Collaboration and its promotion by funders continue to accelerate. Although research has identified significant transaction costs associated with collaboration, little empirical work has examined the broader, societal-level economic outcomes of a resource-sharing environment. Does an environment that encourages collaboration shift our focus toward certain types of social objectives and away from others? This paper uses agent-based Monte Carlo simulation to demonstrate that collaboration is particularly useful when resources are rare but a social objective is commonly held. However, collaboration can lead to bad outcomes when the objective is not commonly shared; in such cases, markets outperform collaborative arrangements. These findings suggest that encouraging a resource-sharing environment can lead to inefficiencies even worse than market failure. We also demonstrate that failure to account for transaction costs when prescribing collaboration can result in quantifiably lower outcome levels than expected.


## Usage

You can generate the simulation data, plots, and tables used in the publisehd version with one simple command. After following the OS-specific prerequisites listed below, open a terminal window (or command prompt in Windows), navigate to this project, and type `make`. For example, if you saved this project in your Downloads folder, type:

	cd ~/Downloads/np-collaboration
	make

The resulting files will be in a new folder named "Output".

The simulation itself takes about 5 minutes to run on a quad-core computer (with 500 runs per variation and motivation). You can adjust the number of simulation runs in `simulation/run_simulation.py` with the variation `times_to_run_simulation`.


## Prerequisites

### OS X and Linux

Python 2.7 and make are installed by default. You only need to download and install [R **3.0**](http://www.r-project.org/).

### Windows

#### 1. Download and install software

* [Python **2.7**](http://www.python.org/download/) (not Python 3!)
* [R **3.0**](http://www.r-project.org/)
* [Make for Windows](http://gnuwin32.sourceforge.net/packages/make.htm)

#### 2. Add Python and R executables to the Windows path

To use the `makefile` and generate all the output files automatically, Windows' command prompt needs easy access to Python and R. After completing these steps, you'll be able to run those programs by just typing `python` at the command prompt instead of `C:\Python27\python.exe`.

1. Right click on "Computer" and select "Properties"
2. In the right-hand column, select "Advanced system settings"
3. Under the "Advanced" tab click the "Environment Variables..." button
4. Select the "path" variable from the user variables list and click "Edit..."
5. At the end of the really long string in "Variable value:", add the paths to your Python and R executable files, separated by semicolons. Don't edit the rest of the line. In the end, your path should look something like this (yours may vary depending on the versions and locations of Python and R): `C:\Windows;a_bunch_of_other_stuff;C:\Python27;C:\Program Files\R\R-3.0.2\bin`
6. Click "OK" to close all the dialogs
7. Restart your computer to apply the path changes (or perhaps just log out and log back in)

#### 3. Install R packages as administrator

When running scripts from the command line, Windows tries to make R install libraries system wide, which then causes permission errors. To fix this, install all requisite libraries as an administrator.

1. Right click on Command Prompt and select "Run as administrator"
2. Type `R` to open an R console.
3. Paste and run this command: `install.packages(c('ggplot2', 'scales', 'reshape2', 'plyr', 'xtable', 'rtf'), repos="http://cran.rstudio.com/")`
4. Type `q()`
5. Close the special administrator command prompt

#### 4. Run script

Navigate to the project (e.g. `cd C:\Users\yourname\Downloads\np-collaboration`) and type `make`.
