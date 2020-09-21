from datetime import datetime, timedelta
from json import dump, load

in_f_name = 'monitor_latency_test_10.txt'
in_f_basename, in_f_ext = in_f_name.rsplit('.', 1)

tz_offset = timedelta(hours=-2)

f = open(in_f_name)

mon_lat_dict = { 'data': {} }

first_syst_date = None

line = f.readline()
while line:
    if line.startswith('#'):
        line = f.readline().strip('\n')
        # print(line)
        syst_date = datetime.strptime(line, "%d %m %Y, %H.%M.%S, CEST") + tz_offset
        # print(syst_date)
        line = f.readline().strip('\n')
        # print(line)
        meas_date = datetime.strptime(line, "%Y-%m-%dT%H:%M:%S+00:00")
        # print(meas_date)
        if not first_syst_date:
            first_syst_date = syst_date
        elapsed_seconds = int((syst_date-first_syst_date).total_seconds())
        mon_lat_dict['data'][elapsed_seconds] = int((syst_date-meas_date).total_seconds())
        print(syst_date, mon_lat_dict['data'][elapsed_seconds])
    line = f.readline()

f.close()

mon_lat_dict['first_time'] = first_syst_date.__str__()

with open('pp_' + in_f_basename + '.json', 'w') as f:
    dump(mon_lat_dict, f, sort_keys=True)

with open('pp_' + in_f_basename + '.csv', 'w') as f:
    f.write('# {}\n'.format(mon_lat_dict['first_time']))
    for t in sorted(mon_lat_dict['data'].keys()):
        f.write('{},{}\n'.format(t, mon_lat_dict['data'][t]))
