#!/usr/bin/env bash
set -x
set -o pipefail
set -e

linodeId=$(linode-cli linodes list --label linode-blue-green-lb --json | jq -r '.[0].id')

linode-cli linodes delete "$linodeId"


