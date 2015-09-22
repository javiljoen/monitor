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
library(ResourceStats)

res = read.delim(logfile, as.is=TRUE)
log_summary = summarize_log(res)
names(log_summary)[2] = gsub('.log$', '', logfile)
log_summary = kable(log_summary, output=FALSE)
write(log_summary, file=summfile)
