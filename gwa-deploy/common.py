"""
Common shell commands.
"""
import subprocess
import json
import logging


def execute_linode_cli(cmd):
    # Check if all elements in cmd are strings
    if not all(isinstance(item, str) for item in cmd):
        logging.warning(f"execute_linode_cli: cmd contains a non-string element: {cmd}")

    """Run a command.   Assume the command is a linode-cli command and specify --json as return type."""
    if "--json" not in cmd:
        cmd.append("--json")
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


def execute_sh(cmd, wd="."):
    """Execute local shell command within the docker container"""
    logging.debug(" ".join(cmd))
    completed_process = subprocess.run(cmd, cwd=wd, check=False, shell=False, capture_output=True)
    stdout = completed_process.stdout.decode().rstrip()
    logging.debug(stdout)
    if completed_process.returncode != 0:
        logging.debug(stdout)
        logging.debug(completed_process.stderr.decode())
        raise Exception()
    return stdout
