from sys import stdin, stderr, argv, exit
import numpy as np
import scipy as sp
import scipy.stats

from json import dumps

def mean_std_confidence_interval(data, confidence=0.95):
  a = 1.0 * np.array(data)
  n = len(a)
  m, sd, se = np.mean(a), np.std(a), scipy.stats.sem(a)
  h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
  return m, m - h, m + h, sd

in_fname_list = argv[1:]

instance_list = ['vm-1', 'vm-2']
metrics_list = ['cpu', 'net']

data_dict = {}

for instance in instance_list:
  data_dict[instance] = {}
  for metric in metrics_list:
    data_dict[instance][metric] = {}

for fname in in_fname_list:
  with open(fname) as f:
    for line in f:
      if line:
        line = line.strip('\n').strip(',')
        #print(line)
        t, vm1_cpu, vm1_net, vm2_cpu, vm2_net = line.split(',')

        if not t in data_dict['vm-1']['cpu']:
          data_dict['vm-1']['cpu'][t] = [vm1_cpu]
        else:
          data_dict['vm-1']['cpu'][t].append(vm1_cpu)

        if not t in data_dict['vm-2']['cpu']:
          data_dict['vm-2']['cpu'][t] = [vm2_cpu]
        else:
          data_dict['vm-2']['cpu'][t].append(vm2_cpu)

        if not t in data_dict['vm-1']['net']:
          data_dict['vm-1']['net'][t] = [vm1_net]
        else:
          data_dict['vm-1']['net'][t].append(vm1_net)

        if not t in data_dict['vm-2']['net']:
          data_dict['vm-2']['net'][t] = [vm2_net]
        else:
          data_dict['vm-2']['net'][t].append(vm2_net)

#print(data_dict)

stats_dict = {}

max_t = 0

for instance in instance_list:
  stats_dict[instance] = {}
  for metric in metrics_list:
    stats_dict[instance][metric] = {}
    for t in data_dict[instance][metric]:
      for i in range(len(data_dict[instance][metric][t])):
        data_dict[instance][metric][t][i] = int(data_dict[instance][metric][t][i])
      if int(t) > max_t:
        max_t = int(t)
        
      mean, mean_low, mean_high, st_dev = mean_std_confidence_interval(data_dict[instance][metric][t])

      #if mean_low == 

      #print('{},{},{},{}'.format(t, int(mean), int(mean_low), int(mean_high)))

      stats_dict[instance][metric][t] = {
        'mean': mean,
        'mean_low': mean_low,
        'mean_high': mean_high
      }

print(dumps(stats_dict, indent=2), file=stderr)

print('t,vm1_cpu_m,vm1_cpu_ml,vm1_cpu_mh,vm2_cpu_m,vm2_cpu_ml,vm2_cpu_mh,vm1_net_m,vm1_net_ml,vm1_net_mh,vm2_net_m,vm2_net_ml,vm2_net_mh,')

for t in range(0, max_t+1, 10):
  t = str(t)
  print('{},'.format(t), end='')
  for instance in instance_list:
    for metric in metrics_list:
      print('{},{},{},'.format(round(stats_dict[instance][metric][t]['mean'], 2),
                              round(stats_dict[instance][metric][t]['mean_low'], 2),
                              round(stats_dict[instance][metric][t]['mean_high'], 2)), end='')
  print('')


