from sys import argv, stderr
from json import load

def ewma(alpha, sample, current_mean):
  if current_mean == None:
    return sample
  else:
    return sample*alpha + (1.0-alpha)*current_mean

def ewma_vector(alpha, vector):
  # initialize current_mean to first sample, and remove sample from list (pop)
  if vector:
    current_mean = vector.pop(0)
  else:
    return None
  # compute mean for every sample
  for sample in vector:
    current_mean = sample*alpha + (1.0-alpha)*current_mean
  # return current mean
  return current_mean


json_fname = argv[1]
alpha_ewma_list_str = argv[2]

# load json
with open(json_fname) as f:
  j = load(f)

#with open('alpha_ewma.dat') as f:
#  alpha_ewma = float(f.read().strip().strip('\n'))

alpha_ewma_list = [ float(a) for a in alpha_ewma_list_str.split() ]
print('EWMA: using alpha list {}'.format(alpha_ewma_list), file=stderr)

# create list of existing input-output pairs
pairs_list = []
for f in j:
  if 'inputPort' in f and 'outputPort' in f:
    pair = (f['inputPort'], f['outputPort'])
    if pair not in pairs_list:
      print('Found new in-out pair: {}'.format(pair), file=stderr)
      pairs_list.append(pair)

print('\nFound in-out pairs: {}\n'.format(pairs_list), file=stderr)

print('Select pair [0-{}] : '.format(len(pairs_list)-1), file=stderr)

sel = input()

if ',' not in sel:
  sel = int(sel)
  print('Selected port pair {}'.format(pairs_list[sel]), file=stderr)
  
  for f in j:
    if (f['inputPort'], f['outputPort']) == pairs_list[sel]:
      sel_flow = f
      break
  
  sel_datarate_dict = {}
  
  for t in sel_flow['allDataPerSecond']:
    sel_datarate_dict[int(t)] = int(sel_flow['allDataPerSecond'][t])
  
  min_t = min(sel_datarate_dict.keys())
  max_t = max(sel_datarate_dict.keys())
  
  # add empty intervals before and after, for plotting reasons
  min_t -= 10
  max_t += 10
  
  out_datarate_dict = {}
  
  curr_ewma = {}
  for alpha_ewma in alpha_ewma_list:
    curr_ewma[alpha_ewma] = None
  
  #print(sel_datarate_dict)

  # csv header
  print('t,data,', end = '')
  for alpha_ewma in alpha_ewma_list:
    print('a{},'.format(alpha_ewma), end = '')
  print('')

  for t in range(min_t, max_t+1, 10):
    curr_t = t-min_t
    if t in sel_datarate_dict:
      out_datarate_dict[curr_t] = sel_datarate_dict[t]
    else:
      #out_datarate_dict[curr_t] = 0
      continue
    print('{},{},'.format(curr_t, out_datarate_dict[curr_t]), end = '')
    for alpha_ewma in alpha_ewma_list:
      curr_ewma[alpha_ewma] = int(ewma(alpha_ewma, out_datarate_dict[curr_t], curr_ewma[alpha_ewma]))
      print('{},'.format(curr_ewma[alpha_ewma]), end = '')
    print('')

