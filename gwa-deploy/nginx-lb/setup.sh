#!/usr/bin/env bash
set -x
set -o pipefail
set -e

cd /gwa_deploy


json=$(linode-cli linodes create \
  --region us-east \
  --image linode/debian11 \
  --label linode-blue-green-lb \
  --type g6-standard-1 \
  --authorized_keys "$SSH_NGINX_LB_PUBLIC_KEY"  \
  --root_pass "$NGINX_LB_ROOT_PASSWORD" \
  --json)


vmId=$(echo "$json"    | jq -r '.[0].id')
vmNetIp=$(echo "$json" | jq -r '.[0].ipv4 | .[0]')

mkdir -p temp

echo "$SSH_NGINX_LB_PRIVATE_KEY_B64" | base64 -d > temp/ssh-devops-bg-priv-key
chmod 600 temp/ssh-devops-bg-priv-key

sshCmd="ssh -o StrictHostKeyChecking=no -oBatchMode=yes -i 'temp/ssh-devops-bg-priv-key' root@${vmNetIp} hostname"

# wait for ssh host ready
# wait upto 5 mins
timeout 300 \
  bash -c "until ${sshCmd}; do sleep 10; done"

ssh -i "temp/ssh-devops-bg-priv-key" \
  root@"$vmNetIp" "apt update && apt install -y nginx"

rm -rf temp/

