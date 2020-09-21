from sys import stdin

value_list = []

for line in stdin.readlines():
  value_list.append(float(line))

if value_list:
  print('{:.2f}'.format(sum(value_list)/len(value_list)))
