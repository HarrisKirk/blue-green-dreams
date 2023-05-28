import requests
import os
import json
import logging
import util

token = os.environ.get("LINODE_CLI_TOKEN")
headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

def get_k8s_nodes():
    url = f"https://api.linode.com/v4/linode/instances"
    parsed_json = _invoke_rest_call(url)
    all_linodes = parsed_json["data"]
    label_prefix_lke = "lke"
    k8s_nodes = [linode for linode in all_linodes if linode["label"].startswith(label_prefix_lke)]
    return k8s_nodes

def get_all_clusters():
    url = f"https://api.linode.com/v4/lke/clusters"
    parsed_json = _invoke_rest_call(url)
    data = parsed_json["data"]
    clusters = [{'id': cluster['id'], 'tags': cluster['tags']} for cluster in data ]
    return clusters

def get_cluster_id(env: str):
    url = f"https://api.linode.com/v4/lke/clusters"
    parsed_json = _invoke_rest_call(url)
    data = parsed_json["data"]
    clusters = []
    for cluster in data:
        tag_dict = util.tags_as_dict(cluster["tags"])
        logging.info(f"The tags associated with {cluster['id']} are: {tag_dict}")
        if env == util.tags_as_dict(cluster["tags"])["env"]:
            clusters.append(cluster)  
    if len(clusters) > 1:
        logging.exception(f"List of clusters with tag 'env_{env}' exceeds 1??")
    if clusters == []:
        return None
    cluster_id = clusters[0]["id"]
    return cluster_id

def _invoke_rest_call(url: str):
    logging.debug(f"REST call to {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    parsed_json = json.loads(response.text)
    pretty_json_string = json.dumps(parsed_json, indent=4, sort_keys=True)
    logging.debug(pretty_json_string)
    return parsed_json

