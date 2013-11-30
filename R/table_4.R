# Load libraries
library(plyr)
library(xtable)

# Load data
setwd("~/Research/Nonprofit collaboration/R")
simulation <- read.csv('../simulation/all_variations.csv', 
                       colClasses=c("variation"="factor", 
                                    "community_motivation"="factor"))

# Baseline = variation 0
# Market = variation 5
# Costless collaboration = variation 3
# Collaboration with cost = variation 1

# Determine average social value met
# ddply(simulation, ~ variation + community_motivation, summarise, 
#       mean=mean(percent_social_value_met), sd=sd(percent_social_value_met))

# Generate lists of objective statistics
num.resources <- simulation[1, 'num_resources']
objective.list <- paste(rep(letters[1:num.resources], each=2),
                        rep(c(1, 2), num.resources), '_pct_fulfilled', sep='')
count.list <- paste(rep(letters[1:num.resources], each=2),
                        rep(c(1, 2), num.resources), '_count', sep='')
max.count <- max(simulation[1, count.list])


cleaned <- function(x) {
  top <- round(x[,1], 3)
  bottom <- round(x[,2], 3)
  paste(top, ' (', bottom, ')', sep='')
}

generate.row <- function(x) {
  # Get mean and standard deviation for chunk
  # See http://stackoverflow.com/questions/10178203/sending-in-column-name-to-ddply-from-function
  # for why the custom function is needed for ddply instead of just using ddply's summarise() function.
  # Single run:
  # ddply(simulation, ~ variation + community_motivation, summarise, mean=mean(a1_pct_fulfilled), sd=sd(a1_pct_fulfilled))
  df <- ddply(simulation, ~ variation + community_motivation, 
              function(d) data.frame(mean=mean(d[[x]]), sd=sd(d[[x]])))
  
  # Create other table values
  dv <- gsub('_pct_fulfilled', '', x)
  
  res.freq.name <- paste(substr(x, 1, 2), '_high_freq', sep='')
  res.freq <- simulation[1, res.freq.name]
  resource.prevalence <- ifelse(res.freq == 1, 'High', 'Low')
  
  obj.count.name <- paste(substr(x, 1, 2), '_count', sep='')
  obj.count <- simulation[1, obj.count.name]
  objective.prevalence <- ifelse(obj.count == max.count, 'High', 'Low')
  
  objective.value <- ifelse(substr(x, 2, 2) == 1, 'High', 'Low')

#   return(list('resource_prevalence'=resource.prevalence, 'objective_prevalence'=objective.prevalence, 
#               'objective_value'=objective.value, 'dv'=dv, 
#               'market_individual'=df[7,3:4], 'market_social'=df[8,3:4], 
#               'costless_individual'=df[5,3:4], 'costless_social'=df[6,3:4],
#               'with_cost_individual'= df[3,3:4], 'with_cost_social'= df[4,3:4]))
  
  return(list('resource_prevalence'=resource.prevalence, 'objective_prevalence'=objective.prevalence, 
              'objective_value'=objective.value, 'dv'=dv, 
              'market_social'=cleaned(df[8,3:4]), 'costless_social'=cleaned(df[6,3:4]),
              'with_cost_social'=cleaned(df[4,3:4]), 'market_individual'=cleaned(df[7,3:4]), 
              'costless_individual'=cleaned(df[5,3:4]), 'with_cost_individual'=cleaned(df[3,3:4])))
}

rows.list <- lapply(objective.list, FUN=generate.row)
rows.table <- ldply(rows.list, data.frame)
rows.table

print(xtable(rows.table, digits=3), type="html", file="table4.html", include.rownames=FALSE)

# system("/Users/andrew/.cabal/bin/pandoc -s table1.html -o table1.rtf && rm table1.html")
# rtf <- RTF('blah.rtf')
# addTable(rtf, rows.table, row.names=FALSE)
# done(rtf)
