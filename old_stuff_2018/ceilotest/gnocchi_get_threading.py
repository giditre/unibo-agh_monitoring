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

def gnocchi_get(endpoint, base_address='http://controller:8041/v1/', token_file='OS_token.json'):

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

  return json.dumps(r_json, indent=2)

class gnocchiGetThread(threading.Thread):
    def __init__(self, instance, metric, *args):
      threading.Thread.__init__(self)
      self.instance = instance
      self.metric = metric
      self.args = []
      for arg in args:
        self.args.append(arg)
      self.result = {
        self.instance: {
          self.metric: None
        }
      }
    def run(self):
      measures = json.loads(gnocchi_get(self.args[0], self.args[1], self.args[2]))
      #print_err(measures)
      last_measure = measures[-1] 
      self.result[self.instance][self.metric] = {
        'timestamp': last_measure[0],
        'granularity': last_measure[1],
        'value': last_measure[2],
      }
    def get_result(self):
      return self.result

if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  
  parser.add_argument("endpoint", help="Ceilometer endpoint")
  parser.add_argument("-b", "--base-address", help="Ceilometer base HTTP address")
  parser.add_argument("-t", "--token-file", help="OpenStack X-Auth token file name")
  parser.add_argument("-m", "--metrics-file", help="Metrics JSON file name")
  
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
        print_err(resource['instance_display_name'], metric['name'])
        endpoint = base_endpoint + metric['id'] + "/measures"
        thread = gnocchiGetThread(resource['instance_display_name'], metric['name'], endpoint, base_address, token_file)
        thread.start()
        gnocchiGetThread_list.append(thread)
        print_err('\n')

    for thread in gnocchiGetThread_list:
      thread.join()
      print(thread.get_result())

    #print(measures_json)
  
  else:
    print(gnocchi_get(endpoint, base_address, token_file))

