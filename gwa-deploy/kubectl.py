from common import execute_sh, execute_linode_cli
from retry import retry
import os
import logging
import json
import base64

"""
Issue kubectl commands on the running linode cluster
"""

WEATHER_API_TOKEN = os.environ.get("WEATHER_API_TOKEN")
KUBERNETES_NODE_COUNT = "2"


@retry(tries=60, delay=30)
def get_nodes():
    # Verify kubectl is communicating with cluster
    cmd = ["kubectl", "--output=json", "get", "nodes"]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    nodes = json_object["items"]
    if len(nodes) != int(KUBERNETES_NODE_COUNT):
        raise Exception(f"kubectl expected {KUBERNETES_NODE_COUNT} nodes but found {len(nodes)}")
    logging.info(f"kubectl OK: Retrieved node count: {len(nodes)}")
    return


@retry(tries=5, delay=10)
def apply_deployment():
    cmd = ["kubectl", "--output=json", "apply", "-f", "resources/deployment.yaml"]
    output = None
    try:
        output = execute_sh(cmd)
    except Exception as e:
        raise Exception(f"retrying {cmd}")
    json_object = json.loads(output)
    logging.debug(f"json ==> {json_object}")
    logging.info(f"kubectl deployment applied OK")
    return


def apply_service():
    cmd = ["kubectl", "--output=json", "apply", "-f", "resources/service.yaml"]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    logging.debug(f"json ==> {json_object}")
    logging.info(f"kubectl service applied OK")
    return


@retry(tries=5, delay=10)
def delete_service():
    cmd = ["kubectl", "delete", "svc", "gwa"]
    execute_sh(cmd)


def create_secrets():
    """Create k8s secret for the api key etc"""
    cmd = [
        "kubectl",
        "create",
        "secret",
        "generic",
        "gws-secret",
        f"--from-literal=WEATHER_API_TOKEN={WEATHER_API_TOKEN}",
    ]
    execute_sh(cmd)


@retry(tries=20, delay=10)
def get_ingress_ip():
    cmd = ["kubectl", "--output=json", "get", "svc", "gwa"]
    output = execute_sh(cmd)
    json_object = json.loads(output)
    logging.debug(f"json ==> {json_object}")
    ingress_ip = json_object["status"]["loadBalancer"]["ingress"][0]["ip"]
    if not ingress_ip:
        raise Exception(f"Ingress IP is empty in the returned json")
    logging.info(f"Load Balance Ingress is: {ingress_ip}")
    return ingress_ip


def apply_argocd():
    cmd = ["ls", "-al"]
    output = execute_sh(cmd)

    cmd = ["kubectl", "create", "namespace", "argocd"]
    output = execute_sh(cmd)

    # cmd = ["kubectl", "apply", "--namespace=argocd", "--dry-run=server", "-k", "."]
    # output = execute_sh(cmd, "./resources")
    return

@retry(tries=60, delay=60)
def get_kubeconfig(cluster_id):
    cmd = [
        "linode-cli",
        "lke",
        "kubeconfig-view",
        cluster_id,
    ]
    json_object = execute_linode_cli(cmd)
    base_64_kubeconfig = json_object[0]["kubeconfig"]
    logging.debug(f"kubeconfig base64: {base_64_kubeconfig}")
    logging.info(f"kubeconfig received OK from cluster {cluster_id}")
    return base64.b64decode(base_64_kubeconfig).decode("ascii")

def write_kubeconfig(kubeconfig):
    KUBECONFIG_DIR = os.environ["HOME"] + "/.kube"
    KUBECONFIG_FILE_PATH = KUBECONFIG_DIR + "/config"
    try:
        os.mkdir(KUBECONFIG_DIR)
    except FileExistsError:
        pass
    with open(KUBECONFIG_FILE_PATH, "w") as file:
        file.write(kubeconfig)
    logging.info(f"kubernetes config file written: {KUBECONFIG_FILE_PATH}")
    return
