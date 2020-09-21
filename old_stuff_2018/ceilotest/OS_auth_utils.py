import requests
import json
import datetime
from sys import stderr

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

def get_token():

  url = "http://controller:35357/v3/auth/tokens?nocatalog"
  headers = {'Content-Type': 'application/json'}
  payload = json.loads('{"auth":{"identity":{"methods":["password"],"password":{"user":{"domain":{"name":"Default"},"name":"admin","password":"welcomeadmin"}}},"scope":{"project":{"domain":{"name":"Default"},"name":"sflow-test"}}}}')
  
  r = requests.post(url, headers=headers, json=payload)
  
  token = r.headers['X-Subject-Token']
  print_err('Token is: {}'.format(token))
  
  r_json = json.loads(r.text)
  expires_str = r_json['token']['expires_at']
  #expires_datetime = datetime.datetime.strptime(expires_str, "%Y-%m-%dT%H:%M:%S.%fZ")
  #expires_timedelta = expires_datetime - datetime.datetime.utcnow()
  #print("Token will expire in {} minutes ({})".format(int(expires_timedelta.total_seconds()/60), expires_str))
  
  token_json = {
    'token': token,
    'expires_at_utc': expires_str
  }
  
  with open('OS_token.json', 'w') as f:
    json.dump(token_json, f)

def get_token_if_expired():
  with open('OS_token.json', 'r') as f:
    token_json = json.load(f)
  if is_expired(token_json['expires_at_utc']):
    get_token()

if __name__ == "__main__":
  get_token_if_expired()

  with open('OS_token.json', 'r') as f:
    token_json = json.load(f)

  print(token_json)

