install.packages("devtools")
library(devtools)
install_github("klutometis/roxygen")
library(roxygen2)

setwd('~/tools/code/monitor/')
create('resource_stats')

setwd('resource_stats/')
document()
use_data(timeseries)

setwd('..')
install('resource_stats')
