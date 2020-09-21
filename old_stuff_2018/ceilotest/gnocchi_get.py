import OS_auth_utils
from OS_auth_utils import print_err, is_expired

import requests
import json
import datetime
import argparse
import threading
from time import sleep

from sys import stderr, exit

base_address = 'http://controller:8041/v1/'
token_file = 'OS_token.json'
metrics_file = ''
limit = 0

def gnocchi_get(endpoint, base_address='http://controller:8041/v1/', token_file='OS_token.json', limit=0):

  with open(token_file) as f:
    token_json = json.load(f)

  token = token_json['token']
 
  url = base_address + endpoint
  headers = { "X-Auth-Token": token }
  r = requests.get(url, headers=headers)

  try:
    r_json = json.loads(r.text)
  except json.decoder.JSONDecodeError:
    print_err('JSONDecodeError while decoding the JSON')
    print_err("---\n" + r.text + "\n---\n")
    return 'JSONDecodeError'

  if limit == 0:
    return json.dumps(r_json)
  else:
    return json.dumps(r_json[-limit])

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  
  parser.add_argument("endpoint", help="Ceilometer endpoint")
  parser.add_argument("-b", "--base-address", help="Ceilometer base HTTP address")
  parser.add_argument("-t", "--token-file", help="OpenStack X-Auth token file name")
  parser.add_argument("-m", "--metrics-file", help="Metrics JSON file name")
  parser.add_argument("-l", "--limit", help="Limit results to the most recent ones")
  
  args = parser.parse_args()
  
  # store and print parsed arguments
  print_err('Information from arguments...')
  endpoint = args.endpoint
  print_err('...endpoint: {}'.format(endpoint))
  if args.base_address:
    base_address = args.base_address
  print_err('...gnocchi base address: {}'.format(base_address))
  if args.token_file:
    token_file = args.token_file
  print_err('...OpenStack Keystone token file: {}'.format(token_file))
  if args.metrics_file:
    metrics_file = args.metrics_file
    print_err('...metrics file: {}'.format(metrics_file))
  if args.limit:
    limit = int(args.limit)
    print_err('...limit: {}'.format(limit))
  
  print_err('')
 
  OS_auth_utils.get_token_if_expired()

  if metrics_file:
    with open(metrics_file) as f:
      metrics_json = json.load(f)

    base_endpoint = endpoint + "/"

    measures_json = {}

    for resource in metrics_json:
      measures_json[resource['instance_display_name']] = {}

    gnocchiGetThread_list = []

    for resource in metrics_json:
      for metric in resource['metrics']:
        # print_err(resource['instance_display_name'], metric['name'])
        endpoint = base_endpoint + metric['id'] + "/measures"
        last_measures = json.loads(gnocchi_get(endpoint, base_address, token_file, limit))
        if limit == 1:
          measures_json[resource['instance_display_name']][metric['name']] = {
            'timestamp': last_measures[0],
            'granularity': last_measures[1],
            'value': last_measures[2],
          }
        else:
          measures_json[resource['instance_display_name']][metric['name']] = []
          for m in last_measures:
            measures_json[resource['instance_display_name']][metric['name']].append({
              'timestamp': m[0],
              'granularity': m[1],
              'value': m[2],
            })

    print(json.dumps(measures_json, indent=2))
  
  else:
    print(gnocchi_get(endpoint, base_address, token_file, limit))

