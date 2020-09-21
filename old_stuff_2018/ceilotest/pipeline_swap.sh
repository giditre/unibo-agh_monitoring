#!/bin/bash

if ! [[ -f /etc/ceilometer/pipeline_all10.yaml ]] && ! [[ -f /etc/ceilometer/pipeline_slow.yaml ]]; then
  echo "ERROR: no customized file found!"
  exit 1
fi

if [[ -f /etc/ceilometer/pipeline_all10.yaml ]]; then
  # it means pipeline_slow is currently enforced
  echo "Now enforcing pipeline_slow. Modify it?"
  read resp
  if [[ $resp != y ]]; then
    exit 0
  fi
  mv /etc/ceilometer/pipeline.yaml /etc/ceilometer/pipeline_slow.yaml
  mv /etc/ceilometer/pipeline_all10.yaml /etc/ceilometer/pipeline.yaml
  ls /etc/ceilometer/pipeline*.yaml
  echo "Now enforcing pipeline_all10"
elif [[ -f /etc/ceilometer/pipeline_slow.yaml ]]; then
  # it means pipeline_all10 is currently enforced
  echo "Now enforcing pipeline_all10. Modify it?"
  read resp
  if [[ $resp != y ]]; then
    exit 0
  fi
  mv /etc/ceilometer/pipeline.yaml /etc/ceilometer/pipeline_all10.yaml
  mv /etc/ceilometer/pipeline_slow.yaml /etc/ceilometer/pipeline.yaml
  ls /etc/ceilometer/pipeline*.yaml
  echo "Now enforcing pipeline_slow"
fi

chown root:ceilometer /etc/ceilometer/pipeline*

echo "Now restarting openstack-ceilometer-*"
systemctl restart openstack-ceilometer-*

#echo "Now restarting openstack-gnocchi-*"
#systemctl restart openstack-gnocchi-*

echo "Done."

