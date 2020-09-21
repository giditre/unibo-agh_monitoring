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

print('# timestamp, perSecondDatarate of port pair {}'.format(pairs_list))

curr_entryTime = 0

t = 0
for e in j:
  # initialize new datarate dict
  datarate_dict = {}
  for pair in pairs_list:
    datarate_dict[pair] = 0

  for f in e['flows']:
    datarate_dict[(f['inputPort'], f['outputPort'])] = f['ewmaDatarate']

  # insert timestamp
  print('{},'.format(t), end='')
  t += 1
  # insert data values
  for pair in datarate_dict:
    print('{},'.format(datarate_dict[pair]), end='')
  print()

