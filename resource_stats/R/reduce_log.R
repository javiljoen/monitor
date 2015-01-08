#' Downsample several columns by process
#'
#' Downsample a data frame with > 2 columns with the LTTB algorithm,
#' using the Split-Apply-Combine pattern to downsample the data for
#' each Process in \code{data} separately.
#'
#' @param data The data frame to downsample. The first column must be
#'   the "Time" column and there must be a column named "Process".
#' @param nbins The (maximum) number of rows of data to return for
#'   each process.
#'
#' @return A data frame with the same columns as \code{data} but at
#'   most \code{nbins} rows for each unique process in
#'   \code{data$Process}.
#'
#' @export
downsample_multiple_by_process = function(data, nbins) {

  downsample_multiple = function(dat, n) {

    downsample = function(vec, n) {
      matr = cbind(dat[, 1], vec)
      LTTB::LTTB(matr, n-2)[, 2]
    }

    plyr::colwise(downsample)(dat[, -ncol(dat)], n)
  }

  outdf = as.data.frame(matrix(NA, ncol=ncol(data), nrow=0))
  names(outdf) = names(data)

  for (p in unique(data$Process)) {
    data_subset = subset(data, Process==p)
    downsampled = downsample_multiple(data_subset, nbins)
    downsampled$Process = p
    outdf = rbind(outdf, downsampled)
  }

  return(outdf)
}
