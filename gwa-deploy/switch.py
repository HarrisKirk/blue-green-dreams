from common import execute_linode_cli, execute_sh
from retry import retry
import logging
import json
import requests
import os

"""
Issue linode-cli commands to manage the controller switch
"""

PROJECT_ACRONYM = "bgd"

def switch_delete():
    cmd = [
        "linode-cli",
        "linodes",
        "list",
        "--label",
        "linode-blue-green-lb",
        "--json"
    ]
    json_object = execute_linode_cli(cmd)
    if json_object == []:
        logging.warning(f"No switch found")
        return
    id = json_object[0]["id"]
    logging.debug(f"switch id: {id}")
    cmd = [
        "linode-cli",
        "linodes",
        "delete",
        f"{id}"
    ]
    execute_sh(cmd)
    logging.info(f"Deleted linode id {id} with nginx load balancer")


def switch_create():
    cmd = [
        "linode-cli",
        "linodes",
        "create",
        "--region",
        "us-east",
        "--image",
        "linode/debian11",
        "--label",
        "linode-blue-green-lb",
        "--type",
        "g6-standard-1",
        "--authorized_keys",
        os.environ.get("SSH_NGINX_LB_PUBLIC_KEY"),
        "--root_pass",
        os.environ.get("NGINX_LB_ROOT_PASSWORD"),
    ]
    json_object = execute_linode_cli(cmd)
    id = json_object[0]['id']
    ip = json_object[0]['ipv4'][0]
    logging.debug(f"Nginx switch create with id: {id} and IP: {ip}")

#
#    logging.info(f"Created linode with nginx load balancer configured for project {PROJECT_ACRONYM}")
#
#    switch_resource = switch_get()
#    if switch_resource != []:
#        if switch_smoke_test(switch_resource[0]["ipv4"][0]):
#            logging.info("[OK] Nginx switch smoke test passes")
#            return switch_view()
#        else:
#            raise Exception(f"Smoke test failed {PROJECT_ACRONYM}")
#    else:
#        logging.info("No switch exists")
#

@retry(tries=20, delay=10)
def wait_for_http_get(ip):
    smoke_test_url = f"http://{ip}"
    logging.debug(f"Get of {smoke_test_url}")
    return requests.get(smoke_test_url)


def switch_view():
    response = switch_get()
    if response == []:
        msg = "No switch exists"
        ip = ""
    else:
        ip = response[0]["ipv4"][0]
        msg = f"IP of switch is: {ip}"
    logging.info(msg)
    return ip


def switch_get():
    cmd = [
        "linode-cli",
        "linodes",
        "list",
        "--label",
        "linode-blue-green-lb",
    ]
    return execute_linode_cli(cmd)


def switch_smoke_test(switch_ip):
    response = wait_for_http_get(switch_ip)
    logging.debug(f"Response: {response.text}")
    if "Welcome to nginx" in response.text:
        return True
    else:
        return False
