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

# retrieve lowest firstTime
min_firstTime = -1
for e in j:
  for f in e['flows']:
    min_firstTime = f['firstTime']
    break
  if min_firstTime >= 0:
    break
print('Minimum firstTime: {}\n'.format(min_firstTime), file=stderr)

# retrieve highest lastTime
max_lastTime = -1
for e in j:
  for f in e['flows']:
    if f['lastTime'] > max_lastTime:
      max_lastTime = f['lastTime']
print('Maximum lastTime: {}\n'.format(max_lastTime), file=stderr)

print('# timestamp, perSecondDatarate of port pair {}'.format(pairs_list))

#f = j[len(j)-1]['flows']

for t in range(min_firstTime, max_lastTime+1):
  # initialize new datarate dict
  datarate_dict = {}
  for pair in pairs_list:
    datarate_dict[pair] = 0

  proceed = False
  for e in j:
    for f in e['flows']:
      if datarate_dict[(f['inputPort'], f['outputPort'])] > 0:
        # if value is already there, it means we can proceed with next t
        proceed = True
        break
      if str(t) in f['perSecond']:
        datarate_dict[(f['inputPort'], f['outputPort'])] = f['perSecond'][str(t)]
      #print(datarate_dict)
      #input()
    if proceed:
      break

  print('{},'.format(t), end='')
  t += 1
  for pair in datarate_dict:
    print('{},'.format(datarate_dict[pair]), end='')
  print()

