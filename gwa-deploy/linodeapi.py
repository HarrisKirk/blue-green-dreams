import requests
import os
import json
import logging

def get_account_info(tag):
    token = os.environ.get("LINODE_CLI_TOKEN")  
    headers =  {"Content-Type":"application/json", "Authorization": f"Bearer {token}"}
    response = requests.get(f"https://api.linode.com/v4/tags/{tag}", headers=headers)
    if response.status_code == 200:
        parsed_json = json.loads(response.text)
        pretty_json_string = json.dumps(parsed_json, indent=4, sort_keys=True)
        logging.debug(pretty_json_string)
        object_count = len(parsed_json["data"])
        return(object_count)
    else:
        return(f"Error: {response.status_code} - {response.text}")
