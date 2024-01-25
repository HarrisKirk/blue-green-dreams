import os
import base64
from common import execute_linode_cli
from retry import retry
import logging

"""
Functions to get and set a cluster's kubeconfig file
"""


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
