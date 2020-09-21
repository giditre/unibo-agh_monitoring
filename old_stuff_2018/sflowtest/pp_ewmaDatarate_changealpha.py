from sys import argv, stderr, exit
from json import load

dirbasename = argv[1]
print(dirbasename)

jsonfbasename = argv[2]
print(jsonfbasename)

samp_ratio = argv[3]
print(samp_ratio)

alpha_list = list(argv[4].split())
print(alpha_list)

outfname = argv[5]

# load json
with open(dirbasename + samp_ratio.zfill(4) + '/' + jsonfbasename + '_alpha' + alpha_list[0] + '.json') as f:
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

sel = int(input('Select pair [0-{}] : '.format(len(pairs_list)-1)))

print('Selected port pair {}'.format(pairs_list[sel]))

datarate_dict = {}

for alpha in alpha_list:
  with open(dirbasename + samp_ratio.zfill(4) + '/' + jsonfbasename + '_alpha' + alpha + '.json') as f:
    j = load(f)
  
  datarate_dict[alpha] = []

  for e in j:
    if not e['flows']:
      datarate_dict[alpha].append('0')
      continue
    for f in e['flows']:
      if (f['inputPort'], f['outputPort']) == pairs_list[sel]:
        datarate_dict[alpha].append(f['ewmaDatarate'])

list_length = max([ len(datarate_dict[alpha_list[i]]) for i in range(len(alpha_list))])
print(list_length)

# for alpha in alpha_list:
#   print(alpha, len(datarate_dict[alpha]))
#   if len(datarate_dict[alpha]) != list_length:
#     exit('Error: mismatching list lengths')

with open(outfname, 'w') as f:
  t = 0
  for i in range(list_length):
    # insert timestamp
    print('{},'.format(t), end='', file=f)
    t += 1
    for alpha in alpha_list:
      if i < len(datarate_dict[alpha]):
        print(datarate_dict[alpha][i], end='', file=f)
      else:
        print('0', end='', file=f)
      if alpha_list.index(alpha) < list_length-1:
        print(',', end='', file=f)
    print('', file=f)


