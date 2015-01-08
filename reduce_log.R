source('lttb.R')
library(plyr)

downsample_multiple = function(dat, n) {
  downsample = function(vec, n) {
    matr = cbind(dat[, 1], vec)
    LTTB(matr, n-2)[, 2]
  }
  
  colwise(downsample)(dat[, -ncol(dat)], n)
}

downsample_multiple_by_process = function(data, nbins) {
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
