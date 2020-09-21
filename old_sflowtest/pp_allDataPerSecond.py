from sys import argv, stderr
from json import load

json_fname = argv[1]

# load json
with open(json_fname) as f:
  j = load(f)

#with open('alpha_ewma.dat') as f:
#  alpha_ewma = float(f.read().strip().strip('\n'))

alpha_ewma = float(argv[2])
print('EWMA: using alpha = {}'.format(alpha_ewma))

# create list of existing input-output pairs
pairs_list = []
for f in j:
  if 'inputPort' in f and 'outputPort' in f:
    pair = (f['inputPort'], f['outputPort'])
    if pair not in pairs_list:
      print('Found new in-out pair: {}'.format(pair), file=stderr)
      pairs_list.append(pair)

print('\nFound in-out pairs: {}\n'.format(pairs_list), file=stderr)

sel = int(input('Select pair [0-{}] : '.format(len(pairs_list)-1)))
print('Selected port pair {}'.format(pairs_list[sel]))

#print('# timestamp, perSecondDatarate of port pair {}'.format(pairs_list))

# curr_entryTime = 0

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

for f in j:
  if (f['inputPort'], f['outputPort']) == pairs_list[sel]:
    sel_flow = f
    break

sel_datarate_dict = {}

for t in sel_flow['allDataPerSecond']:
  sel_datarate_dict[int(t)] = int(sel_flow['allDataPerSecond'][t])

min_t = min(sel_datarate_dict.keys())
max_t = max(sel_datarate_dict.keys())

out_datarate_dict = {}

curr_ewma = None

for t in range(min_t, max_t+1):
  curr_t = t-min_t
  if t in sel_datarate_dict:
    out_datarate_dict[curr_t] = sel_datarate_dict[t]
  else:
    out_datarate_dict[curr_t] = 0
  curr_ewma = int(ewma(alpha_ewma, out_datarate_dict[curr_t], curr_ewma))
  print('{},{},{}'.format(curr_t, out_datarate_dict[curr_t], curr_ewma))



# for t in f['allDataPerSecond']:
  # print('{},{}'.format(t, f['allDataPerSecond'][t]))

  # # initialize new datarate dict
  # datarate_dict = {}
  # for pair in pairs_list:
  #   datarate_dict[pair] = 0

  # for f in e['flows']:
  #   datarate_dict[(f['inputPort'], f['outputPort'])] = f['perSecond']

  # # insert timestamp
  # print('{},'.format(t), end='')
  # t += 1
  # # insert data values
  # for pair in datarate_dict:
  #   print('{},'.format(datarate_dict[pair]), end='')
  # print()

