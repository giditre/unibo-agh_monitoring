from sys import argv
import csv
import numpy as np

def numpy_ewma_vectorized_v2(data, window):

    alpha = 2 /(window + 1.0)
    alpha_rev = 1-alpha
    n = data.shape[0]

    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1/pows[:-1]
    offset = data[0]*pows[1:]
    pw0 = alpha*alpha_rev**(n-1)

    mult = data*pw0*scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums*scale_arr[::-1]
    return out

datafname = argv[1]

print(datafname)

data = []

n_cols = 0

with open(datafname) as dataf:
  # discover number of columns
  for line in dataf:
    if line.startswith('#'):
      continue
    n_cols = len([ x for x in line.strip('\n').split(',') if x ])
    break

  for i in range(n_cols):
    data.append([])

  for line in dataf:
    if line.startswith('#'):
      continue
    line = line.strip()
    splitted_line = line.split(',')
    for i in range(len(splitted_line)):
      el = splitted_line[i]
      if el:
        data[i].append(el)

n_rows = len(data[0])

data_ewma = []
data_ewma.append(data[0])
for l in data[1:]:
  data_ewma.append(list(numpy_ewma_vectorized_v2(np.array(l).astype("float"), 9)))

print(len(data_ewma))
print(n_rows, n_cols)

with open(datafname + '.ewma.txt', 'w') as f:
  for r in range(n_rows):
    for c in range(n_cols):
      print(r, c)
      f.write(str(int(data_ewma[c][r])))
      if c < n_cols-1:
        f.write(',')
    f.write('\n')
    
