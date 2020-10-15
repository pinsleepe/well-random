library(plumber)

# setwd("~/well-random/R")

p = plumb(dir = "api")
p$run(port = 8000)