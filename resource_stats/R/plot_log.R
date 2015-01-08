#' Plot resource use
#'
#' Plot the resource use recorded in a log file with \code{monitor.py}
#'
#' @param data Data frame created by reading in
#'   \code{monitor.py} log file or downsampling such a data frame
#' @param title Title for the plot (optional)
#' @param file File to write the plot to (plot to screen if '')
#' @param w,h The width and height of the PDF image in inches
#' @param ... Other options to pass to \code{pdf()}
#' @return NULL
#' @export
#' @import ggplot2
#'
plot_log = function(data, title='', file='', w=12, h=6, ...) {
  molten = reshape2::melt(data, id.vars=c("Time", "Process"))

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
  q = q + labs(title=title, x="Time (s)", y="")
  q = q + theme(legend.position="top")

  if (file == '') {
    print(q)
  } else {
    pdf(file, w, h, ...)
    print(q)
    dev.off()
  }
}
