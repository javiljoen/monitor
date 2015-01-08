#' Summarize resource use
#'
#' Summarize the resource use recorded in a log file with \code{monitor.py}
#'
#' @param res Data frame created by reading in \code{monitor.py} log file
#' @return Data frame summarizing the maximum and median values of the
#'   CPU, RAM, and Disk I/O usage
#' @aliases summarise_log
#' @export
summarize_log = function(res) {
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

  return(data.frame(Metric=output_vars, Value=output_vals))
}
