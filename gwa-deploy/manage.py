"""
Manage all aspects of the creation of infrastructure and app deployment
"""
from common import execute_cli, execute_sh
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
KUBERNETES_NODE_COUNT = "2"


@retry(tries=60, delay=30, logger=logging.getLogger())
def get_kubeconfig(cluster_id):
    cmd = [
        "linode-cli",
        "--json",
        "lke",
        "kubeconfig-view",
        cluster_id,
    ]
    json_object = execute_cli(cmd)
    base_64_kubeconfig = json_object[0]["kubeconfig"]
    logging.debug(f"kubeconfig base64: {base_64_kubeconfig}")
    return base64.b64decode(base_64_kubeconfig).decode("ascii")


@retry(tries=60, delay=30, logger=logging.getLogger())
def verify_cluster_communication():
    # Verify kubectl is communicating with cluster
    cmd = ["kubectl", "--output=json", "get", "nodes"]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    nodes = json_object["items"]
    if len(nodes) != int(KUBERNETES_NODE_COUNT):
        raise Exception(f"kubectl expected {int(KUBERNETES_NODE_COUNT)} nodes but found {len(nodes)}")
    logging.info(f"kubectl OK: Retrieved node count: {len(nodes)}")
    return

def apply_deployment():
    cmd = ["kubectl", "--output=json", "apply", "-f", "resources/deployment.yaml"]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    logging.debug(f"json ==> {json_object}")
    logging.info(f"kubectl deployment OK")
    return

def apply_service():
    cmd = ["kubectl", "--output=json", "apply", "-f", "resources/service.yaml"]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    logging.debug(f"json ==> {json_object}")
    logging.info(f"kubectl service OK")
    return

@retry(tries=5, delay=10, logger=logging.getLogger())
def get_ingress_ip():
    cmd = ["kubectl", "--output=json", "get", "svc", "gwa"]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    logging.debug(f"json ==> {json_object}")
    ingress_ip = json_object["status"]["loadBalancer"]["ingress"][0]["ip"]
    logging.info(f"Load Balance Ingress is: {ingress_ip}")
    return ingress_ip


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
        KUBERNETES_NODE_COUNT,
        "--json",
    ]
    json_object = execute_cli(cmd)
    cluster_id = json_object[0]["id"]
    return str(cluster_id)


def delete_cluster(cluster_id):
    """Delete a K8S cluster, starting with service"""
    cmd = ["kubectl", "delete", "svc", "gwa"]
    execute_sh(cmd)

    cmd = ["linode-cli", "lke", "cluster-delete", cluster_id]
    json_object = execute_cli(cmd)
    logging.debug(f"cluster-delete returned {json_object}")
    return


def write_kubeconfig(kubeconfig):
    KUBECONFIG_DIR = os.environ['HOME'] + "/.kube"
    KUBECONFIG_FILE_PATH = KUBECONFIG_DIR + "/config"
    os.mkdir(KUBECONFIG_DIR)
    with open(KUBECONFIG_FILE_PATH, "w") as file:
        file.write(kubeconfig)
    return

def deployment_smoke_test(ingress_ip):
    smoke_test_url = f"http://{ingress_ip}:8000"
    logging.debug(f"Get of {smoke_test_url}")
    response = requests.get(smoke_test_url)
    logging.debug(f"Response: {response.text}")
    if 'Richmond' not in response.text:
        raise Exception("'Richmond not found on the index page'")
    logging.info( "[OK] Site smoke test passes")
    return

def verify_deployment(k8s_env):
    cluster_id = create_cluster(k8s_env)
    logging.info(f"Cluster id '{cluster_id}' was created")
    kubeconfig = get_kubeconfig(cluster_id)
    logging.debug(f"kubeconfig as yaml: {kubeconfig}")
    write_kubeconfig(kubeconfig)
    verify_cluster_communication()
    apply_deployment()
    apply_service()
    time.sleep(10)
    ingress_ip = get_ingress_ip()
    time.sleep(30)
    deployment_smoke_test(ingress_ip)
    delete_cluster(cluster_id)
    logging.info(f"Cluster id '{cluster_id}' was deleted")


if __name__ == "__main__":
    k8s_env = sys.argv[1]
    logging.info(f"Creating k8s environment '{k8s_env}'")
    verify_deployment(k8s_env)    
