"""
Functions that provision the linode instances and volumes
"""
from common import execute_cli
import logging
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)-9s %(funcName)-30s() %(message)s ",
    level=logging.DEBUG,
    datefmt="%Y-%m-%d at %H:%M:%S",
)

def show_linode_account():
    cmd = [
        "linode-cli",
        "account",
        "settings",
        "--json",
    ]
    json_object = execute_cli(cmd)
    return json_object

if __name__ == "__main__":
    print (str(show_linode_account()))


