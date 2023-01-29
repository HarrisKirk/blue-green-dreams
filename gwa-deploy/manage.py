"""
Manage all aspects of the creation of infrastructure and app deployment
"""
from common import execute_cli, execute_sh
import logging
import time
import base64
import json
from retry import retry

logging.basicConfig(
    format="%(asctime)s %(levelname)-9s %(funcName)-30s() %(message)s ",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d at %H:%M:%S",
)

KUBERNETES_VERSION = "1.25"
KUBECONFIG_FILE = "/tmp/kubeconfig.yaml"
KUBERNETES_NODE_COUNT = "2"


@retry(tries=12, delay=30, logger=logging.getLogger())
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
    return base64.b64decode(base_64_kubeconfig).decode('ascii')

@retry(tries=12, delay=30, logger=logging.getLogger())
def verify_cluster_communication():
    # Verify kubectl is communicating with cluster
    cmd = [
        "kubectl",
        f"--kubeconfig={KUBECONFIG_FILE}",
        "--output=json",
        "get",
        "nodes"
    ]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    nodes = json_object["items"]
    if len(nodes) != int(KUBERNETES_NODE_COUNT):
        raise Exception(f"kubectl expected {int(KUBERNETES_NODE_COUNT)} nodes but found {len(nodes)}")
    logging.info(f"kubectl OK: Retrieved node count: {len(nodes)}")
    return

def create_cluster():
    """Create a K8S cluster"""
    cmd = [
        "linode-cli",
        "lke",
        "cluster-create",
        "--label",
        "gwa",
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
    """Delete a K8S cluster"""
    cmd = [
        "linode-cli",
        "lke",
        "cluster-delete",
        cluster_id
    ]
    json_object = execute_cli(cmd)
    logging.debug(f"cluster-delete returned {json_object}")
    return

def write_kubeconfig(kubeconfig):
    with  open(KUBECONFIG_FILE, "w") as file:
        file.write(kubeconfig)
    return

def verify_deployment():
    cluster_id = create_cluster() 
    logging.info(f"Cluster id '{cluster_id}' was created")
    kubeconfig = get_kubeconfig(cluster_id)
    logging.debug(f"kubeconfig as yaml: {kubeconfig}")
    write_kubeconfig(kubeconfig)
    verify_cluster_communication()
    delete_cluster(cluster_id)
    logging.info(f"Cluster id '{cluster_id}' was deleted")   


if __name__ == "__main__":
    verify_deployment()

