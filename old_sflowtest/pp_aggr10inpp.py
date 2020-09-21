from sys import argv

in_fname = argv[1]

f = open(in_fname)

line = f.readline()

# print header
print(line, end='')

n_columns = len([ c for c in line.strip('\n').strip(',').split(',') if c ])

# print first line of data consisting of all zeros
for i in range(n_columns):
  print('0,', end='')
print()

columns = [10] + [ 0 for i in range(n_columns-1) ]

i = 1
i_aggr10 = 10

while not line.startswith('5'):
  line = f.readline()

while line:
  splitted_line = line.strip('\n').strip(',').split(',')
  for c in range(1,n_columns):
    columns[c] += int(splitted_line[c])
  i += 1
  if i == i_aggr10:
    i_aggr10 += 10
    print('{},'.format(columns[0]), end='')
    for c in range(1,n_columns):
      print('{},'.format(int(columns[c]/10)), end='')
    print()
    columns = [i_aggr10] + [ 0 for i in range(n_columns-1) ]
  line = f.readline()

print('{},'.format(columns[0]), end='')
for c in range(1,n_columns):
  print('{},'.format(0), end='')
print()

