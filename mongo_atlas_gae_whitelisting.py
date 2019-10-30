'''
    Simple Script to whitelist all the GAE IPs into a MongoDB Atlas Cluster
    @luisfernando
    https://github.com/luisfernando/MongoAtlasScripts
'''
import requests
from requests.auth import HTTPDigestAuth
import os
import json

GROUP_ID = ""  # this can be found at https://cloud.mongodb.com/v2/{GROUP_ID} when you log into your atlas account

# Generate your API Keys on Project -> Access Management -> API Keys
PUB_KEY = ""  # API Public keys UPPERCASE
PRIVATE_KEY = ""  # Generated Private Key

COMMENT = "GAE Cloud IP Block"
BASE_BLOCK = "_cloud-netblocks{i}.googleusercontent.com"
CURRENT_BLOCK = 1
MAX_BLOCK = 7

ip_address_groups = list()


def process_ips(content):
    content = content.replace("v=spf1", "")
    content = content.replace("?all", "")
    content = content.replace('"', "")
    content = content.replace("ip4:", "")
    content = content.strip().split("\n")

    for ip in content:
        if "include" not in ip and "ip6:" not in ip:
            new_address = dict()
            new_address["cidrBlock"] = ip
            new_address["comment"] = COMMENT
            ip_address_groups.append(new_address)

    # print(content)


def mongo_atlas_white_list(range):
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    params = (
        ('pretty', 'true'),
    )

    data = json.dumps(range)
    # print(data)
    response = requests.post('https://cloud.mongodb.com/api/atlas/v1.0/groups/' + GROUP_ID + '/whitelist?pretty=true',
                             headers=headers, data=data, auth=HTTPDigestAuth(PUB_KEY, PRIVATE_KEY))

    print(response.content)


# Here we do a simple thing, we use dig command (linux/osx) and get all the IP Addresses from the GCP Blocks

while CURRENT_BLOCK <= MAX_BLOCK:
    uri = BASE_BLOCK.replace("{i}", str(CURRENT_BLOCK))
    cmd_get_ips = 'dig txt ' + uri + ' +short | tr " " "\n"'
    get_ips = os.popen(cmd_get_ips).read()
    process_ips(get_ips)
    CURRENT_BLOCK = CURRENT_BLOCK + 1

# Once the list is created we create an API Request to add each block
mongo_atlas_white_list(ip_address_groups)

# FIXME: Make this a console based script to pass the private/public keys and group as arguments
