#!/usr/bin/Rscript
args = commandArgs(trailingOnly=TRUE)

if (length(args) < 1) {
  stop('USAGE: summarize_log.R DATA.log [SUMMARY.txt]')
}

logfile  = args[1]

if (length(args) > 1) {
  summfile = args[2]
} else {
  summfile = '' ## i.e. write to stdout
}

library(knitr)
source('resource_stats/R/summarize_log.R')

res = read.delim(logfile, as.is=TRUE)
log_summary = kable(summarize_log(res), output=FALSE)
write(log_summary, file=summfile)
