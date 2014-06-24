#!/usr/bin/Rscript

arg = commandArgs(trailingOnly=TRUE)

if (length(arg) < 2) stop("\n\tUSAGE: summarize_log.r log_file summary_file")

logfile  = arg[1]
summfile = arg[2]
if (summfile == "-") summfile = "" ## i.e. write to stdout


res = read.delim(logfile, as.is=TRUE)
message(sprintf("Data read from %s", logfile))


## total resource usage (for each variable) at each time point
totals_by_time = aggregate(res[, 2:9], list(Time=res$Time), sum)
## max for each variable
peaks = round(apply(totals_by_time, 2, max))
## median for CPU, threads, & memory
medians = round(apply(totals_by_time[, 2:5], 2, median))


output_vals = c(round(peaks["Time"]/60),
                round(peaks["CPU."]/100), round(medians["CPU."]/100),
                peaks["Threads"], medians["Threads"],
                peaks["RSS"], medians["RSS"],
                peaks["VMS"], medians["VMS"],
                peaks[c("IO.reads", "IO.writes", "IO.read.MB", "IO.written.MB")])

output_vars = c("Time (min)",
                "Max CPUs", "Median CPUs",
                "Max threads", "Median threads",
                "Max RSS memory (MB)", "Median RSS memory (MB)",
                "Max VMS memory (MB)", "Median VMS memory (MB)",
                "Reads", "Writes", "Read (MB)", "Written (MB)")

output = paste(output_vars, output_vals, sep=":\t")


write(output, file=summfile)
if (summfile != "") message(sprintf("Summary written to %s", summfile))
