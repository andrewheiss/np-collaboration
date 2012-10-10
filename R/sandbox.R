library(ggplot2)

test <- read.table(pipe("pbpaste"), header=T)
variation_2.1 <- read.delim(pipe("pbpaste"), header=F, sep=",")
names(variation_2.1) <- c("trades", "before", "after")

individual.1 <- read.delim(pipe("pbpaste"), header=F, sep=",")
community.1 <- read.delim(pipe("pbpaste"), header=F, sep=",")
names(individual.1) <- c("trades", "before", "after")
names(community.1) <- c("trades", "before", "after")

t.test(individual.1$after, community.1$after)

individual <- data.frame(after = individual.1$after)
community <- data.frame(after = community.1$after)

individual.1$version <- "Self-interested focus"
community.1$version <- "Community focus"

versions <- rbind(individual.1, community.1)

p <- ggplot(versions, aes(after, fill = version))
p + geom_density(alpha = 0.2) +
  labs(x = "\nCommunity points (after)", y = "Density\n") +
  opts(title = "Variation 4 (team limit of 2)\n")



ggplot(variation_2.1, aes(after)) + geom_density(fill="blue")

variation_2 <- read.delim(pipe("pbpaste"), header=F, sep=",")
names(variation_2) <- c("trades", "before", "after")
ggplot(variation_2, aes(after)) + geom_density(fill="blue")

t.test(variation_2$after, variation_2.1$after)

variation.1 <- data.frame(after = variation_1$after)
variation.2 <- data.frame(after = variation_2$after)

variation.1$variation <- "Variation 1"
variation.2$variation <- "Variation 2"

variations <- rbind(variation.1, variation.2)

ggplot(variations, aes(after, fill = variation)) + geom_density(alpha = 0.2)


after.give <- data.frame(after = test$after.give)
after.hold <- data.frame(after = test$after.hold)

after.give$scenario <- 'Create team even if not ideal'
after.hold$scenario <- 'Hold out for better team'

things <- rbind(after.give, after.hold)

ggplot(things, aes(after, fill = scenario)) + geom_density(alpha = 0.2)

