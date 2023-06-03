import requests
import os
import json
import logging
import util

"""
Use the linode REST api to read information about account artifacts
"""

TOKEN = os.environ.get("LINODE_CLI_TOKEN")
HEADERS = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}
LINODE_API_ROOT = "https://api.linode.com/v4"

def get_k8s_nodes():
    parsed_json = _invoke_rest_call(f"/linode/instances")
    all_linodes = parsed_json["data"]
    label_prefix_lke = "lke"
    k8s_nodes = [linode for linode in all_linodes if linode["label"].startswith(label_prefix_lke)]
    return k8s_nodes


def get_all_clusters():
    parsed_json = _invoke_rest_call(f"/lke/clusters")
    data = parsed_json["data"]
    clusters = [{"id": cluster["id"], "tags": cluster["tags"]} for cluster in data]
    return clusters


def get_nodebalancer_id_by_ingress(ingress_ip):
    parsed_json = _invoke_rest_call(f"/nodebalancers")
    logging.debug(parsed_json)
    data = parsed_json["data"]
    ids = [{"id": nb["id"], "ipv4": nb["ipv4"]} for nb in data if nb["ipv4"] == ingress_ip]
    if len(ids) != 1:
        raise Exception(f"ERROR: ids of nodebalancer list {ids} != 1")
    return str(ids[0]["id"])


def get_nodebalancer_id(project: str, env: str):
    parsed_json = _invoke_rest_call(f"/nodebalancers")
    data = parsed_json["data"]
    nodebalancers = []
    for nb in data:
        tag_dict = util.tags_as_dict(nb["tags"])
        logging.debug(f"The tags associated with {nb['id']} are: {tag_dict}")
        if env == tag_dict.get("env") and project == tag_dict.get("project"):
            nodebalancers.append(nb)
    if len(nodebalancers) > 1:
        logging.exception(f"List of nodebalancers in project '{project}' and env '{env}' exceeds 1??")
    if nodebalancers == []:
        return None
    nodebalancers_id = nodebalancers[0]["id"]
    return str(nodebalancers_id)


def get_cluster_id(project: str, env: str):
    """Get the cluster ID of the k8s cluster in the project and environment"""
    parsed_json = _invoke_rest_call(f"/lke/clusters")
    data = parsed_json["data"]
    clusters = []
    for cluster in data:
        tag_dict = util.tags_as_dict(cluster["tags"])
        logging.debug(f"The tags associated with {cluster['id']} are: {tag_dict}")
        if env == tag_dict.get("env") and project == tag_dict.get("project"):
            clusters.append(cluster)
    if len(clusters) > 1:
        logging.exception(f"List of clusters in project '{project}' and env '{env}' exceeds 1??")
    if clusters == []:
        return None
    cluster_id = clusters[0]["id"]
    return str(cluster_id)


def _invoke_rest_call(url: str):
    logging.debug(f"REST call to {url}")
    response = requests.get(LINODE_API_ROOT + url, headers = HEADERS)
    if response.status_code != 200:
        return f"Error: {response.status_code} - {response.text}"
    parsed_json = json.loads(response.text)
    pretty_json_string = json.dumps(parsed_json, indent=4, sort_keys=True)
    logging.debug(pretty_json_string)
    return parsed_json
