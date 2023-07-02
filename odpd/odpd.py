#!/usr/bin/env python3
import configparser
import datetime
import json
import os
import subprocess
import sys

import requests
from dateutil.parser import parse

cache = None

def get_access_token(rclone_config_path=None, remote_name='onedrive'):
    global cache
    if cache is not None:
        return cache
    if rclone_config_path is None:
        rclone_config_path = os.path.expanduser('~/.config/rclone/rclone.conf')
    try:
        config = configparser.ConfigParser()
        config.read(rclone_config_path)
        token_info = json.loads(config[remote_name]['token'])
        if is_token_expired(token_info):
            raise Exception()
    except Exception as e:
        refresh_token_with_rclone(rclone_config_path, remote_name)
        return get_access_token(rclone_config_path, remote_name)
    cache = token_info['access_token']
    return cache

def is_rclone_installed():
    try:
        subprocess.run(['rclone', '--version'], check=True, stdout=subprocess.PIPE)
        return True
    except Exception as e:
        return False


def is_token_expired(token_info):
    expiry = parse(token_info['expiry'])
    now = datetime.datetime.now(datetime.timezone.utc)
    return expiry < now

def refresh_token_with_rclone(rclone_config_path, remote_name):
    if not is_rclone_installed():
        print('rclone is not installed. Please install it.', file=sys.stderr)
        sys.exit(1)
    try:
        subprocess.run(
            ['rclone', 'config', 'update', remote_name, 'token', rclone_config_path],
            check=True,
            stdout=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        subprocess.run(
            ['rclone', 'config', 'create', remote_name, 'onedrive', 'drive_type', 'personal', 'token', rclone_config_path],
            check=True,
            stdout=subprocess.PIPE
        )


def upload_file_to_onedrive(filepath, remotepath):
    if remotepath.startswith('/'):
        remotepath = remotepath[1:]
    if remotepath.endswith('/'):
        remotepath = remotepath[:-1]
    filename = os.path.basename(filepath)
    access_token = get_access_token()
    headers = {"Authorization": "Bearer " + access_token}
    endpoint = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remotepath}/" + filename + ":/content"

    with open(filepath, 'rb') as f:
        r = requests.put(endpoint, headers=headers, data=f)
        r.raise_for_status()

    return r.json().get('id')

def create_embed_link(file_id):
    access_token = get_access_token()
    headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"}
    endpoint = "https://graph.microsoft.com/v1.0/me/drive/items/" + file_id + "/createLink"

    payload = {
        "type": "embed"
    }

    r = requests.post(endpoint, headers=headers, json=payload)
    r.raise_for_status()

    return r.json().get('link').get('webUrl')

def main(filepath, remotepath):
    file_id = upload_file_to_onedrive(filepath, remotepath)
    embed_link = create_embed_link(file_id)
    print(embed_link)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("odpd: OneDrive Picture Direct Link Generator")
        print("  Usage: odpd.py <filepath> [remotepath]")
        sys.exit(1)
    main(sys.argv[1], "files/" if len(sys.argv) < 3 else sys.argv[2])
