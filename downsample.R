#!/usr/bin/Rscript

args = commandArgs(trailingOnly=TRUE)

if (length(args) == 0) {
  stop('USAGE: downsample.R DATA.log [N_out] [LESSDATA.log]')
}

datafile = args[1]

if (length(args) > 1) {
  n_out = as.integer(args[2])
  if (n_out < 3) {
    stop('Cannot return fewer than 3 rows per process')
  }
} else {
  n_out = 100
}

if (length(args) == 3) {
  outfile = args[3]
} else {
  outfile = ''
}

library(ResourceStats)
data = read.delim(datafile, as.is=TRUE)
downsampled = downsample_multiple_by_process(data, nbins=(n_out))
write.table(downsampled, outfile, sep='\t', row.names=FALSE, quote=FALSE)
