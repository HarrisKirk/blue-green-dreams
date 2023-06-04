from common import execute_linode_cli, execute_sh
from retry import retry
import logging
import json

"""
Issue linode-cli commands to create the controller switch
"""

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

def switch_delete(nb_id):
    cmd = [
        "linode-cli",
        "nodebalancers",
        "rm",
        str(nb_id)
    ]
    json_object = execute_linode_cli(cmd)        
    return    