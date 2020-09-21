import json

from sys import argv, exit

f_name = argv[1]

metric = "network.incoming.bytes.rate"

with open(f_name) as f:
  measures_json = json.load(f)

measure_dict = {}

instances_list = list(measures_json.keys())
for instance in instances_list:
  measure_dict[instance] = []
  for meas in measures_json[instance][metric]:
    measure_dict[instance].append(meas['value'])

measures_list_length = len(measure_dict[instances_list[0]])
for instance in instances_list[1:]:
  if len(measure_dict[instance]) != measures_list_length:
    exit("ERROR: length mismatch.")

for instance in instances_list:
  print("{},".format(instance), end='')
print('')

for i in range(measures_list_length):
  for instance in instances_list:
    print('{},'.format(8*int(measure_dict[instance][i])), end='')
  print('')

