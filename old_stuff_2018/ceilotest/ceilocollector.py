from ceilo_get import ceilo_get, print_err
from nova_get import nova_get

import json

metrics_list = ['cpu_util', 'memory.usage', 'network.incoming.bytes.rate', 'network.outgoing.bytes.rate']

servers = nova_get("servers")
servers_json = json.loads(servers)

# build VM aka servers dictionary
servers_dict = {}
for s in servers_json['servers']:
  #print(s['id'], s['name'])
  servers_dict[s['id']] = {
    'name': s['name']
  }

resources = ceilo_get('resources')
resources_json = json.loads(resources)

for s_id in servers_dict:
  for res in resources_json:
    if s_id == res['resource_id']:
      for l in res['links']:
        if l['rel'] in metrics_list:
          servers_dict[s_id][l['rel']] = l['href']
    elif s_id + '-tap' in res['resource_id']:
      for l in res['links']:
        if l['rel'] in metrics_list:
          servers_dict[s_id][l['rel']] = l['href']

print(json.dumps(servers_dict, indent=2))

