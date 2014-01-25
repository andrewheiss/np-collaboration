# Load data and libraries
source("load_data.R")
library(ggplot2)
library(grid)
library(scales)
library(reshape2)
library(plyr)

generate.plot.data <- function(x) {
  df <- ddply(simulation, ~ variation + community_motivation, 
              function(d) data.frame(d[[x]]))
  
  # Create other table values
  dv <- gsub('_pct_fulfilled', '', x)
  
  df$variation <- factor(df$variation, levels=c(0, 5, 3, 1), labels=c('Baseline', 'Market', 'Costless collaboration', 'Collaboration with cost'), ordered=TRUE)
  df$motivation <- factor(df$community_motivation, levels=c(1, 0), labels=c('Social', 'Individual'))
  
  res.freq.name <- paste(substr(x, 1, 2), '_high_freq', sep='')
  res.freq <- simulation[1, res.freq.name]
  resource.prevalence <- ifelse(res.freq == 1, 'High (left)', 'Low (right)')
  
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
# aes(alpha=...) is included as a dummy legend aesthetic so resource prevalence can be included. Transparency is removed below.
p <- ggplot(data=plot.data, aes(x=pretty.label, y=pct_fulfilled, fill=objective_prevalence, alpha=resource_prevalence))
violin <- p + geom_violin(scale="width", size=0.25, aes(linetype=objective_value)) +
  stat_summary(aes(group=1), fun.y=mean, geom="point", size=2) + 
  geom_vline(xintercept=4.5, colour="darkgrey", linetype=2) + 
  scale_y_continuous(labels=percent) + labs(x=NULL, y=NULL) + 
  facet_wrap(~ motivation + variation, nrow=2) + 
  scale_fill_grey(start=0.4, end=0.8, name="Objective prevalence") + 
  scale_alpha_discrete(range = c(1, 1), name="Resource prevalence") + # Remove transparency
  scale_linetype(name="Objective value") + 
  guides(fill=guide_legend(override.aes=list(size=0, linetype=0), order=2),
         alpha=guide_legend(override.aes=list(size=0, linetype=0), order=1, keywidth=unit(0, "line"))) + 
  theme_bw() + theme(legend.key = element_blank()) + 
  theme(axis.text=element_text(size=6), strip.text=element_text(size=6, face='bold'), 
        legend.text=element_text(size=6), legend.title=element_text(size=6),
        legend.key.size=unit(.7,"line"),
        legend.position="bottom", legend.box="horizontal")

ggsave(plot=violin, filename="../Output/figure_1.pdf", width=7, height=5, units="in")
