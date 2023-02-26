"""
Common functions related to running local and remote processes 
"""
import subprocess
import json
import logging


def execute_cli(cmd):
    """Run a command.   Assume the command is a linode-cli command and process error accordingly"""
    logging.debug(" ".join(cmd))
    completed_process = subprocess.run(cmd, cwd=".", check=False, shell=False, capture_output=True)

    if completed_process.returncode == 0:
        json_string = completed_process.stdout.decode()
        if json_string == "":  # Use case is no linode artifacts are returned
            return None
        else:
            json_object = json.loads(json_string)
            logging.debug(json.dumps(json_object, indent=2))
            return json_object
    else:
        logging.debug(completed_process.stdout.decode())
        logging.debug(completed_process.stderr.decode())
        raise Exception()


def execute_sh(cmd):
    """Execute local shell command within the docker container"""
    logging.debug(" ".join(cmd))
    p = subprocess.run(cmd, check=True, shell=False, capture_output=True)
    output = p.stdout.decode().rstrip()
    logging.debug(output)
    return output
