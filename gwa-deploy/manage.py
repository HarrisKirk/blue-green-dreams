"""
Manage all aspects of the creation of infrastructure and app deployment
"""
from common import execute_linode_cli, execute_sh
import kubectl
import logging
import time
import base64
import json
import sys
import os
from retry import retry
import requests


logging.basicConfig(
    format="%(asctime)s %(levelname)-9s %(funcName)-30s() %(message)s ",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d at %H:%M:%S",
)

KUBERNETES_VERSION = "1.25"


@retry(tries=60, delay=30, logger=logging.getLogger())
def get_kubeconfig(cluster_id):
    cmd = [
        "linode-cli",
        "--json",
        "lke",
        "kubeconfig-view",
        cluster_id,
    ]
    json_object = execute_linode_cli(cmd)
    base_64_kubeconfig = json_object[0]["kubeconfig"]
    logging.debug(f"kubeconfig base64: {base_64_kubeconfig}")
    return base64.b64decode(base_64_kubeconfig).decode("ascii")


def create_cluster(k8s_env):
    """Create a K8S cluster"""
    cmd = [
        "linode-cli",
        "lke",
        "cluster-create",
        "--label",
        k8s_env,
        "--region",
        "us-east",
        "--node_pools.type",
        "g6-standard-1",
        "--k8s_version",
        KUBERNETES_VERSION,
        "--node_pools.count",
        kubectl.KUBERNETES_NODE_COUNT,
        "--json",
    ]
    json_object = execute_linode_cli(cmd)
    cluster_id = json_object[0]["id"]
    return str(cluster_id)


def delete_cluster(cluster_id):
    kubectl.delete_service()  # Must delete the NodeBalancer before and in addition to the cluster
    cmd = ["linode-cli", "lke", "cluster-delete", cluster_id]
    json_object = execute_linode_cli(cmd)
    logging.debug(f"cluster-delete returned {json_object}")
    logging.info(f"Cluster id '{cluster_id}' was deleted")
    return


def write_kubeconfig(kubeconfig):
    KUBECONFIG_DIR = os.environ["HOME"] + "/.kube"
    KUBECONFIG_FILE_PATH = KUBECONFIG_DIR + "/config"
    os.mkdir(KUBECONFIG_DIR)
    with open(KUBECONFIG_FILE_PATH, "w") as file:
        file.write(kubeconfig)
    return


def deployment_smoke_test(ingress_ip):
    response = wait_for_http_get(ingress_ip)
    logging.debug(f"Response: {response.text}")
    if "Richmond" not in response.text:
        return False
    logging.info("[OK] Site smoke test passes")
    return True


@retry(tries=20, delay=10, logger=logging.getLogger())
def wait_for_http_get(ingress_ip):
    smoke_test_url = f"http://{ingress_ip}:8000"
    logging.debug(f"Get of {smoke_test_url}")
    return requests.get(smoke_test_url)


def verify_deployment(k8s_env):
    cluster_id = create_cluster(k8s_env)
    logging.info(f"Cluster id '{cluster_id}' was created")
    kubeconfig = get_kubeconfig(cluster_id)
    logging.debug(f"kubeconfig as yaml: {kubeconfig}")
    write_kubeconfig(kubeconfig)
    kubectl.get_nodes()
    kubectl.create_secrets()
    kubectl.apply_deployment()
    kubectl.apply_service()
    ingress_ip = kubectl.get_ingress_ip()
    return cluster_id, ingress_ip


if __name__ == "__main__":
    k8s_env = sys.argv[1]
    logging.info(f"Creating k8s environment '{k8s_env}'")
    cluster_id, ingress_ip = verify_deployment(k8s_env)
    result = deployment_smoke_test(ingress_ip)
    delete_cluster(cluster_id)  # delete cluster to not incur charges
    if not result:
        raise Exception("'Richmond not found on the index page'")
