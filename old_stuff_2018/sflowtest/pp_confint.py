import numpy as np
import scipy as sp
import scipy.stats

from sys import argv, stderr

# this script must be called with arguments:
### output file name
### space-separated list of data files (e.g. confint0-9)

def mean_std_confidence_interval(data, confidence=0.95):
  a = 1.0 * np.array(data)
  n = len(a)
  m, sd, se = np.mean(a), np.std(a), scipy.stats.sem(a)
  h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
  return m, m - h, m + h, sd

#outfname = argv[1]

infname_list = argv[1:]

data = {}
data_ewma = {}

for fname in infname_list:
  with open(fname) as f:
    for line in f:
      line = line.strip('\n').strip().strip(',')
      if line and not line.startswith('#') and not line.startswith('t'):
        splitted_line = line.split(',')
        if len(splitted_line) != 3:
          print('WARNING: line {} probably malformed.'.format(line))
          continue
        t = int(splitted_line[0])
        d = int(splitted_line[1])
        e = int(splitted_line[2])
        if t in data:
          data[t].append(d)
          data_ewma[t].append(e)
        else:
          data[t] = [d]
          data_ewma[t] = [e]

#print(data)

out_data = {}

print('t,data_mean,ewma_mean,ewma_mean_low,ewma_mean_high')

for t in data:
  mean_data = mean_std_confidence_interval(data[t])[0]
  mean, mean_low, mean_high, st_dev = mean_std_confidence_interval(data_ewma[t])
  out_data[t] = {
    'mean': mean,
    'mean_low': mean_low,
    'mean_high': mean_high,
    'st_dev': st_dev
  }
  try:
    print('{},{},{},{},{}'.format(t, int(mean_data), int(mean), int(mean_low), int(mean_high)))
  except:
    print(mean_data, mean, mean_low, mean_high, file=stderr)


