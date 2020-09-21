from sys import argv, stderr
from json import load

json_fname = argv[1]

# load json
with open(json_fname) as f:
  j = load(f)

# create list of existing input-output pairs
pairs_list = []
for e in j:
  for f in e['flows']:
    if 'inputPort' in f and 'outputPort' in f:
      pair = (f['inputPort'], f['outputPort'])
      if pair not in pairs_list:
        print('Found new in-out pair: {}'.format(pair), file=stderr)
        pairs_list.append(pair)

print('\nFound in-out pairs: {}\n'.format(pairs_list), file=stderr)

print('# timestamp, port pair, datarate [[, port pair, datarate] ...]')

i = 0
for e in j:
  # initialize new datarate dict
  datarate_dict = {}
  for pair in pairs_list:
    datarate_dict[pair] = 0
  # fill datarate_dict
  for f in e['flows']:
    datarate_dict[(f['inputPort'], f['outputPort'])] = f['avgDatarate'] if 'avgDatarate' in f else f['bandwidth']
  
  t = e['timestamp']
  #print('{},'.format(t), end='')
  print('{},'.format(i), end='')
  i += 1
  for pair in datarate_dict:
    print('{},'.format(datarate_dict[pair]), end='')
  print()


