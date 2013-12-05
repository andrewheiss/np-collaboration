# Load data and libraries
source("load_data.R")
library(ggplot2)
library(scales)
library(reshape2)
library(plyr)

generate.plot.data <- function(x) {
  df <- ddply(simulation, ~ variation + community_motivation, 
              function(d) data.frame(d[[x]]))
  
  # Create other table values
  dv <- gsub('_pct_fulfilled', '', x)
  
  df$variation <- factor(df$variation, levels=c(0, 5, 3, 1), labels=c('Baseline', 'Market', 'Costless collaboration', 'Collaboration with cost'), ordered=TRUE)
  df$motivation <- factor(df$community_motivation, levels=c(1, 0), labels=c('Community', 'Individual'))
  
  res.freq.name <- paste(substr(x, 1, 2), '_high_freq', sep='')
  res.freq <- simulation[1, res.freq.name]
  resource.prevalence <- ifelse(res.freq == 1, 'High', 'Low')
  
  obj.count.name <- paste(substr(x, 1, 2), '_count', sep='')
  obj.count <- simulation[1, obj.count.name]
  objective.prevalence <- ifelse(obj.count == max.count, 'High', 'Low')
  
  objective.value <- ifelse(substr(x, 2, 2) == 1, 'High', 'Low')
  resource.name <- substr(x, 1, 1)
  
  pretty.label <- dv
  # pretty.label <- paste(dv, '\n', resource.prevalence, '\n', objective.prevalence, sep='')
  
  return(list('motivation'=df$motivation, 'variation'=df$variation, 'resource_prevalence'=resource.prevalence, 'objective_prevalence'=objective.prevalence, 'objective_value'=objective.value, 'dv'=dv, 'pretty.label'=pretty.label, 'resource'=resource.name, 'pct_fulfilled'=df$d..x..))
}

plot.data.list <- lapply(objective.list, FUN=generate.plot.data)
plot.data <- ldply(plot.data.list, data.frame)

# Add a tiny bit of noise for geom_violin
too.perfect <- which(plot.data$pct_fulfilled == 1)
noise <- rnorm(length(too.perfect))/100000
plot.data[too.perfect,'pct_fulfilled'] <- plot.data[too.perfect,'pct_fulfilled'] - noise

# Plot this stuff
p <- ggplot(data=plot.data, aes(x=pretty.label, y=pct_fulfilled, fill=resource))

# Violin plot
violin <- p + geom_violin(scale="width", size=0.25) + 
  stat_summary(aes(group=1), fun.y=mean, geom="point", size=2) + 
  scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
  facet_wrap(~motivation+variation, nrow=2) + guides(fill=FALSE) + 
  scale_fill_grey(start=0.2, end=0.95) + theme_bw() + 
  theme(axis.text=element_text(size=6), strip.text=element_text(size=6, face = 'bold'))

ggsave(plot=violin, filename="../Output/figure_1.pdf", width=7, height=5, units="in")

# Bar plot with error bars
# p + stat_summary(aes(group=1), fun.y=mean, geom="bar") + 
#   scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
#   stat_summary(fun.data = mean_sdl, geom = "errorbar", mult = 1) + 
#   facet_wrap(~motivation+variation, nrow=2) + guides(fill=FALSE) + theme_bw()

# Bar plot with jittered points
# p + stat_summary(aes(group=1), fun.y=mean, geom="bar") + 
#   geom_point(position="jitter", alpha=0.1) + 
#   scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
#   facet_wrap(~motivation+variation, nrow=2) + guides(fill=FALSE) + theme_bw()
