import get_OS_token

import requests
import json
import datetime
import argparse
from time import sleep

from sys import stderr, exit

base_address = 'http://controller:8777/v2/'
token_file = 'OS_token.json'

def print_err(*args, **kwargs):
  kwargs['file'] = stderr
  print(*args, **kwargs)

def is_expired(exp):
  utc_now = datetime.datetime.utcnow()
  exp_datetime = datetime.datetime.strptime(exp, "%Y-%m-%dT%H:%M:%S.%fZ")
  if (exp_datetime - utc_now).total_seconds() > 0:
    # not expired
    return False
  else:
    # expired
    return True

def ceilo_get(endpoint, base_address='http://controller:8777/v2/', token_file='OS_token.json'):

  with open(token_file) as f:
    token_json = json.load(f)
  
  token = token_json['token']
  expires_at_utc = token_json['expires_at_utc']
  if is_expired(expires_at_utc):
    print_err("Token expired, obtaining a new one...")
    get_OS_token.main()
    sleep(1)
    with open(token_file) as f:
      token_json = json.load(f)
    token = token_json['token']
  else:
    print_err("Token is still valid.\n")
  
  url = base_address + endpoint
  
  headers = { "X-Auth-Token": token }
  
  r = requests.get(url, headers=headers)
  
  r_json = json.loads(r.text)
  
  return json.dumps(r_json, indent=2)


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  
  parser.add_argument("endpoint", help="Ceilometer endpoint")
  parser.add_argument("-b", "--base-address", help="Ceilometer base HTTP address")
  parser.add_argument("-t", "--token-file", help="OpenStack X-Auth token file name")
  
  args = parser.parse_args()
  
  # store and print parsed arguments
  print_err('Information from arguments...')
  endpoint = args.endpoint
  print_err('...endpoint: {}'.format(endpoint))
  if args.base_address:
    base_address = args.base_address
  print_err('...Ceilometer base address: {}'.format(base_address))
  if args.token_file:
    token_file = args.token_file
  print_err('...Ceilometer token file: {}'.format(token_file))
  
  print_err('')
 
  print(ceilo_get(endpoint, base_address, token_file))

