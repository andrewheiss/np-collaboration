#--------------
# load_data.R
#--------------

# Install required packages
required.packages <- c('ggplot2', 'scales', 'reshape2', 'plyr', 'xtable')
new.packages <- required.packages[!(required.packages %in% installed.packages()[,"Package"])]
if(length(new.packages)) install.packages(new.packages)

# Load data
# setwd("~/Research/Nonprofit collaboration/R")
simulation <- read.csv('../Output/all_variations.csv', 
                       colClasses=c("variation"="factor", 
                                    "community_motivation"="factor"))

# Generate lists of objective statistics
num.resources <- simulation[1, 'num_resources']
objective.list <- paste(rep(letters[1:num.resources], each=2),
                        rep(c(1, 2), num.resources), '_pct_fulfilled', sep='')
count.list <- paste(rep(letters[1:num.resources], each=2),
                        rep(c(1, 2), num.resources), '_count', sep='')
max.count <- max(simulation[1, count.list])

# Baseline = variation 0
# Market = variation 5
# Costless collaboration = variation 3
# Collaboration with cost = variation 1

# Determine average social value met
# ddply(simulation, ~ variation + community_motivation, summarise, 
#       mean=mean(percent_social_value_met), sd=sd(percent_social_value_met))

