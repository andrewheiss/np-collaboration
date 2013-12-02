# Load libraries
library(ggplot2)
library(scales)
library(reshape2)

generate.plot.data <- function(x) {
  df <- ddply(simulation, ~ variation + community_motivation, 
              function(d) data.frame(d[[x]]))
  
  # Create other table values
  dv <- gsub('_pct_fulfilled', '', x)
  
  df$variation <- factor(df$variation, levels=c(0, 1, 3, 5), labels=c('Baseline', 'Collaboration with cost', 'Costless collaboration', 'Market'))
  df$motivation <- factor(df$community_motivation, levels=c(0, 1), labels=c('Individual', 'Community'))
  
  #   community.type <- ifelse()
  
  res.freq.name <- paste(substr(x, 1, 2), '_high_freq', sep='')
  res.freq <- simulation[1, res.freq.name]
  resource.prevalence <- ifelse(res.freq == 1, 'High', 'Low')
  
  obj.count.name <- paste(substr(x, 1, 2), '_count', sep='')
  obj.count <- simulation[1, obj.count.name]
  objective.prevalence <- ifelse(obj.count == max.count, 'High', 'Low')
  
  objective.value <- ifelse(substr(x, 2, 2) == 1, 'High', 'Low')
  resource.name <- substr(x, 1, 1)
  
  #   pretty.label <- paste(dv, '\n', resource.prevalence, ' (res.)\n', objective.prevalence, ' (obj.)', sep='')
  pretty.label <- paste(dv, '\n', resource.prevalence, '\n', objective.prevalence, sep='')
  
  return(list('motivation'=df$motivation, 'variation'=df$variation, 'resource_prevalence'=resource.prevalence, 'objective_prevalence'=objective.prevalence, 'objective_value'=objective.value, 'dv'=dv, 'pretty.label'=pretty.label, 'resource'=resource.name, 'pct_fulfilled'=df$d..x..))
}

rows.list1 <- lapply(objective.list, FUN=generate.plot.data)
rows.table1 <- ldply(rows.list1, data.frame)

p <- ggplot(data=subset(rows.table1, variation!='Baseline' & motivation=='Individual'), aes(x=pretty.label, y=pct_fulfilled, fill=resource))
p <- ggplot(data=subset(rows.table1, variation!='Baseline' & motivation=='Community'), aes(x=pretty.label, y=pct_fulfilled, fill=resource))
p <- ggplot(data=rows.table1, aes(x=pretty.label, y=pct_fulfilled, fill=resource))

# Bar plot with error bars
p + stat_summary(aes(group=1), fun.y=mean, geom="bar") + 
  scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
  stat_summary(fun.data = mean_sdl, geom = "errorbar", mult = 1) + 
  facet_wrap(~motivation+variation, nrow=2) + guides(fill=FALSE) + theme_bw()

# Bar plot with jittered points
p + stat_summary(aes(group=1), fun.y=mean, geom="bar") + 
  geom_point(position="jitter", alpha=0.1) + 
  scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
  facet_wrap(~motivation+variation, nrow=2) + guides(fill=FALSE) + theme_bw()

# Violin plot
p + geom_violin(scale="width") + 
  stat_summary(aes(group=1), fun.y=mean, geom="point", size=5) + 
  scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
  facet_wrap(~motivation+variation, nrow=2) + guides(fill=FALSE) + theme_bw()
