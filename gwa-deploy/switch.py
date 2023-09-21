from common import execute_linode_cli, execute_sh
from retry import retry
import logging
import json
import requests

"""
Issue linode-cli commands to create the controller switch
"""

PROJECT_ACRONYM = 'bgd'

def create_controller_switch(project):
    """ Create a controller nodebalancer to switch between blue and green envs """
    logging.info(f"here I am creating project_{project}")
    cmd = [
        "linode-cli",
        "nodebalancers",
        "create",
        "--label",
        f"{project}_Blue_Green_Switch",
        "--region",
        "us-east",
    ]
    json_object = execute_linode_cli(cmd)
    logging.debug(f"{json_object}")
    nodebalancer_id = json_object[0]["id"]
    return nodebalancer_id

# linode-cli nodebalancers update --tags project_bgd --tags env_common 360281
def add_tags(nb_id, PROJECT_ACRONYM, env):
    cmd = [
        "linode-cli",
        "nodebalancers",
        "update",
        "--tags",
        f"project_{PROJECT_ACRONYM}",         
        "--tags",
        f"env_{env}",
        str(nb_id)
    ]
    json_object = execute_linode_cli(cmd)
    return


def switch_delete():
    cmd = [
        "bash",
        "-c",
        "/gwa_deploy/nginx-lb/delete.sh"
    ]
    execute_sh(cmd)
    logging.info("Deleted linode with nginx load balancer")


def switch_create():
    cmd = [
        "bash",
        "-c",
        "/gwa_deploy/nginx-lb/setup.sh"
    ]
    execute_sh(cmd)

    logging.info(f"Created linode with nginx load balancer configured for project {PROJECT_ACRONYM}")

    switch_resource = switch_get()
    if switch_resource != []:
        if switch_smoke_test(switch_resource[0]['ipv4'][0]): 
            logging.info("[OK] Nginx switch smoke test passes")
            return switch_view()
        else:
            raise Exception(f"Smoke test failed {PROJECT_ACRONYM}")
    else:
        logging.info("No switch exists")

@retry(tries=20, delay=10)
def wait_for_http_get(ip):
    smoke_test_url = f"http://{ip}"
    logging.debug(f"Get of {smoke_test_url}")
    return requests.get(smoke_test_url)

def switch_view():
    response = switch_get()
    if response == []:
        msg = "No switch exists"
        ip = ''
    else:
        ip = response[0]['ipv4'][0]
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
