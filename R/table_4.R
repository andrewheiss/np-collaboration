# Load data and libraries
source("load_data.R")
library(plyr)
library(xtable)

# Format table output: mean (sd)
# Accepts a 1 row dataframe, like so:
#    mean    sd
#    2.3234  0.6583
cleaned <- function(x) {
  average <- round(x[,1], 3)
  stdev <- round(x[,2], 3)
  paste(average, ' (', stdev, ')', sep='')
}

# Function for lapply, which loops through each objective and outputs a summary row
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
  
  # Return list of everything
  return(list('resource_prevalence'=resource.prevalence, 'objective_prevalence'=objective.prevalence, 
              'objective_value'=objective.value, 'dv'=dv, 
              'baseline_social'=cleaned(df[2,3:4]), 'market_social'=cleaned(df[8,3:4]), 
              'costless_social'=cleaned(df[6,3:4]), 'with_cost_social'=cleaned(df[4,3:4]), 
              'baseline_individual'=cleaned(df[1,3:4]), 'market_individual'=cleaned(df[7,3:4]), 
              'costless_individual'=cleaned(df[5,3:4]), 'with_cost_individual'=cleaned(df[3,3:4])))
}

# Create a list of all the data
rows.list <- lapply(objective.list, FUN=generate.row)

# Convert that list to a data frame
rows.table <- ldply(rows.list, data.frame)

# Export the table
print(xtable(rows.table, digits=3), type="html", file="../Output/table_4.html", include.rownames=FALSE)
