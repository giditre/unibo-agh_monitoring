import json
from datetime import datetime, timedelta
from sys import argv, stderr, exit

f_name = argv[1]

metrics_list = ["cpu_util", "network.incoming.bytes.rate"]

with open(f_name) as f:
  measures_json = json.load(f)

instances_list = list(measures_json.keys())
measures_dict = {}
for instance in instances_list:
  measures_dict[instance] = {}
  for metric in metrics_list:
    measures_dict[instance][metric] = {}
    for meas in measures_json[instance][metric]:
      measures_dict[instance][metric][meas['timestamp']] = int(meas['value'])

#print(json.dumps(measures_dict, sort_keys=True, indent=2))

measures_time_dict = {}

for instance in measures_dict:
  for metric in measures_dict[instance]:
    for t in measures_dict[instance][metric]:
      if t not in measures_time_dict:
        measures_time_dict[t] = {}
      if metric not in measures_time_dict[t]:
        measures_time_dict[t][metric] = {}
      if instance not in measures_time_dict[t][metric]:
        measures_time_dict[t][metric][instance] = {}
      measures_time_dict[t][metric][instance] = measures_dict[instance][metric][t]

#print(json.dumps(measures_time_dict, sort_keys=True, indent=2))

first_measure_time = None
for t in sorted(measures_time_dict.keys()):
  if not first_measure_time:
    first_measure_time = datetime.strptime(t, "%Y-%m-%dT%H:%M:%S+00:00")
  relative_time = int((datetime.strptime(t, "%Y-%m-%dT%H:%M:%S+00:00") - first_measure_time).total_seconds())
  print('{},'.format(relative_time), end='')
  for metric in metrics_list:
    if metric in measures_time_dict[t]:
      for instance in instances_list:
        try:
          if instance in measures_time_dict[t][metric]:
            print('{},'.format(measures_time_dict[t][metric][instance]), end='')
          else:
            print('0,', end='')
        except KeyError as e:
          print(measures_time_dict[t][metric], file=stderr)
          exit('ERROR: {}'.format(e)) 
    else:
      print('WARNING: metric {} not found at time {}'.format(metric, t), file=stderr)
      print('0,', end='')
  print('')


#print(json.dumps(measures_time_list, sort_keys=True, indent=2))

exit()

measures_list_length = len(measure_dict[instances_list[0]])
for instance in instances_list[1:]:
  if len(measure_dict[instance]) != measures_list_length:
    exit("ERROR: length mismatch.")

for instance in instances_list:
  print("{},".format(instance), end='')
print('')

for i in range(measures_list_length):
  for instance in instances_list:
    print('{},'.format(float(measure_dict[instance][i])), end='')
  print('')

