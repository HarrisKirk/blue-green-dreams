from common import execute_linode_cli, execute_sh
from retry import retry
import logging
import json
import requests
import os
import base64

"""
Issue linode-cli commands to manage the controller switch
"""

PROJECT_ACRONYM = "bgd"


def switch_delete(env):
    json_object = switch_get(env)
    if json_object == []:
        logging.warning(f"No switch found in environment '{env}'")
        return
    id = json_object[0]["id"]
    logging.debug(f"switch id: {id}")
    cmd = ["linode-cli", "linodes", "delete", f"{id}"]
    execute_sh(cmd)
    logging.info(f"Deleted linode id {id} with nginx load balancer")

def writeSshPrivateKeyToTmp():
    decoded_private_key = base64.b64decode(os.environ.get("SSH_NGINX_LB_PRIVATE_KEY_B64"))
    private_key_file = "/tmp/bgd_decoded.txt"
    with open(private_key_file, mode="w") as file:
        file.write(decoded_private_key.decode())
    execute_sh(["chmod", "600", private_key_file])


def switch_create(env):
    """
    Create a linode instance with nginx as a switch to route traffic to k8s cluster
    """
    cmd = [
        "linode-cli",
        "linodes",
        "create",
        "--region",
        "us-east",
        "--image",
        "linode/debian11",
        "--label",
        f"{PROJECT_ACRONYM}-{env}-switch",
        "--type",
        "g6-standard-1",
        "--authorized_keys",
        os.environ.get("SSH_NGINX_LB_PUBLIC_KEY"),
        "--root_pass",
        os.environ.get("NGINX_LB_ROOT_PASSWORD"),
        "--tags",
        f"project_{PROJECT_ACRONYM}",
        "--tags",
        f"env_{env}",
    ]
    json_object = execute_linode_cli(cmd)
    id = json_object[0]["id"]
    ip = json_object[0]["ipv4"][0]
    logging.info(f"Linode instance with id: {id} and IP: {ip} is provisioning")

    writeSshPrivateKeyToTmp()
    private_key_file = "/tmp/bgd_decoded.txt"
    cmd = [
        "ssh",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        "BatchMode=yes",
        "-i",
        private_key_file,
        f"root@{ip}",
        "hostname",
    ]
    wait_for_cmd(cmd)
    logging.debug(f"switch at ip '{ip}' is in the 'Running' state")
    cmd = ["ssh", "-i", private_key_file, f"root@{ip}", "apt update && apt install -y nginx"]
    wait_for_cmd(cmd)
    os.remove(private_key_file)
    logging.debug("nginx was installed with 'apt update'")
    logging.info(f"Created linode with nginx load balancer configured for project {PROJECT_ACRONYM}")
    if switch_smoke_test(ip):
        logging.info(f"[OK] Nginx switch smoke test passes")
    else:
        raise Exception(f"Smoke test of ip {ip} failed")


@retry(tries=30, delay=10, logger=logging.getLogger())
def wait_for_cmd(cmd):
    execute_sh(cmd)


@retry(tries=20, delay=10)
def wait_for_http_get(ip):
    smoke_test_url = f"http://{ip}"
    logging.debug(f"Get of {smoke_test_url}")
    return requests.get(smoke_test_url)


def switch_view(env):
    response = switch_get(env)
    if response == []:
        msg = f"No switch exists in environment '{env}'"
        ip = ""
    else:
        ip = response[0]["ipv4"][0]
        msg = f"IP of switch is: {ip}"
    logging.info(msg)
    return ip


def switch_get(env):
    cmd = [
        "linode-cli",
        "linodes",
        "list",
        "--tags",
        f"project_{PROJECT_ACRONYM}",
        "--tags",
        f"env_{env}",
    ]
    return execute_linode_cli(cmd)


def switch_smoke_test(switch_ip):
    response = wait_for_http_get(switch_ip)
    logging.debug(f"Response: {response.text}")
    if "Welcome to nginx" in response.text:
        return True
    else:
        return False
