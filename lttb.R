# Largest-Triangle-Three-Buckets
# https://github.com/sveinn-steinarsson/flot-downsample

## Area of a triangle given duples of vertex coordinates
A_tri = function(A, B, C) {
  0.5 * abs((A[1] - C[1]) * (B[2] - A[2]) - (A[1] - B[1]) * (C[2] - A[2]))
}

## set up test data
logfile = 'test/monitor.log'
res = read.delim(logfile, as.is=TRUE)
res = res[res$Process == 'samtools', 1:2]
res = res[1:100,]
res = as.matrix(res)

## params
N = nrow(res)
n_bins = 9
bin_width = (N - 2) / n_bins

## set up output
out = matrix(NA, nrow=(n_bins + 2), ncol=ncol(res))
out[1, ] = res[1, ]
out[nrow(out), ] = res[nrow(res), ]

## LTTB algorithm
for (i in 1 + 1:n_bins) {
  A.i = out[i - 1, ]
  if (i < n_bins) {
    C.i = apply(res[floor(i * bin_width + 1:bin_width), ], 2, mean)
    B = res[floor(((i - 1) * bin_width + 1):(i * bin_width)), , drop=F]
  } else {
    B = res[floor(((i - 1) * bin_width + 1):(N - 1)), , drop=F]
    C.i = out[nrow(out), ]
  }
  B.i = B[which.max(apply(B, 1, A_tri, A=A.i, C=C.i)), ]
  out[i, ] = B.i
}

out

# plot(res[,1], res[,2], type='l')
# lines(out[,1], out[,2], col='red')
