#!/usr/bin/Rscript

arg = commandArgs(trailingOnly=TRUE)

if (length(arg) < 2) {
  stop("\n\tUSAGE: plot_log.r DATA.log PLOT.pdf ['PLOT TITLE']")
}

logfile = arg[1]
plotfile = arg[2]
if (length(arg) == 3) {
  plottitle = arg[3]
} else {
  plottitle = ""
}
  
library(ggplot2, quietly=TRUE)
library(reshape2, quietly=TRUE)
source('reduce_log.R')

res = read.delim(logfile, as.is=TRUE)
message(sprintf("Data read from %s", logfile))

res$Process = paste(res$Process, res$PID, sep=":")
res = res[,names(res)!="PID"]

res_downsampled = downsample_multiple_by_process(data=res, nbins=30)

molten = melt(res_downsampled, id.vars=c("Time", "Process"))

molten$variable = factor(molten$variable,
                         levels=c("CPU.", "Threads",
                                  "RSS", "VMS",
                                  "IO.reads", "IO.writes",
                                  "IO.read.MB", "IO.written.MB"),
                         labels=c("CPU (%)", "# threads",
                                  "RSS (MB)", "VMS (MB)",
                                  "# reads", "# writes",
                                  "Read (MB)", "Written (MB)"))

q = ggplot(data=molten, aes(x=Time, y=value, colour=Process))
q = q + geom_line()
q = q + facet_wrap(~ variable, ncol=4, scales="free_y")
q = q + labs(title=plottitle, x="Time (s)", y="")
q = q + theme(legend.position="top")

pdf(plotfile, 12, 6)
print(q)
dev.off()
message(sprintf("Plot written to %s", plotfile))
