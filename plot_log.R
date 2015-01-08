#!/usr/bin/Rscript
args = commandArgs(trailingOnly=TRUE)

if (length(args) < 2) {
  stop("USAGE: plot_log.R DATA.log PLOT.pdf ['PLOT TITLE'] [N_POINTS]")
}

logfile = args[1]
plotfile = args[2]
if (length(args) > 2) {
  plottitle = args[3]
} else {
  plottitle = ''
}
if (length(args) > 3) {
  npoints = as.numeric(args[4])
} else {
  npoints = 30
}

library(ResourceStats)

res = read.delim(logfile, as.is=TRUE)

res$Process = paste(res$Process, res$PID, sep=':')
res = res[, names(res) != 'PID']

res_downsampled = downsample_multiple_by_process(data=res, nbins=npoints)

plot_log(res_downsampled, plottitle, plotfile)
