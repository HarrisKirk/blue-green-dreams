from common import execute_sh
from retry import retry
import os
import logging
import json

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
    output = execute_sh(cmd)
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
