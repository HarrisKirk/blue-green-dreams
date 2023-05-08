import requests
import os
import json
import logging


def get_k8s_nodes():
    token = os.environ.get("LINODE_CLI_TOKEN")
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
    url = f"https://api.linode.com/v4/linode/instances"
    logging.debug(f"REST call to {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    parsed_json = json.loads(response.text)
    pretty_json_string = json.dumps(parsed_json, indent=4, sort_keys=True)
    logging.debug(pretty_json_string)
    all_linodes = parsed_json["data"]
    label_prefix_lke = "lke"
    k8s_nodes = [linode for linode in all_linodes if linode["label"].startswith(label_prefix_lke)]
    return k8s_nodes
