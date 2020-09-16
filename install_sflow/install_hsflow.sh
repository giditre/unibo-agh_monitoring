wget https://github.com/sflow/host-sflow/releases/download/v2.0.25-3/hsflowd-centos7-2.0.25-3.x86_64.rpm
sudo yum install hsflowd-centos7-2.0.25-3.x86_64.rpm
systemctl enable hsflowd
sudo vim /etc/hsflowd.conf
service hsflowd start
