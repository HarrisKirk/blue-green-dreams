"""
Functions that provision the linode instances and volumes
"""
from common import execute_cli, execute_sh
import logging
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)-9s %(funcName)-30s() %(message)s ",
    level=logging.INFO,
    datefmt="%Y-%m-%d at %H:%M:%S",
)

KUBERNETES_VERSION = "1.25"

def configure_cluster():
    # Verify kubectl is installed
    cmd = [
        "kubectl"
    ]
    print(execute_sh(cmd))
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
        "2",
        "--json",
    ]
    json_object = execute_cli(cmd)
    cluster_id = json_object[0]["id"]
    return cluster_id

def delete_cluster(cluster_id):
    """Delete a K8S cluster"""
    cmd = [
        "linode-cli",
        "lke",
        "cluster-delete",
        str(cluster_id)
    ]
    json_object = execute_cli(cmd)
    logging.debug(f"cluster-delete returned {json_object}")
    return

if __name__ == "__main__":
    cluster_id = create_cluster() 
    logging.info(f"Cluster id '{cluster_id}' was created")
    logging.info(f"Sleeping for the nodes to enter Running state (see GH-19)...")
    configure_cluster()
    time.sleep(180)
    delete_cluster(cluster_id)
    logging.info(f"Cluster id '{cluster_id}' was deleted")   

