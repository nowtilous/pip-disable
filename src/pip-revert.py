import argparse
import os.path
import subprocess
import time

from pathlib import Path
from configparser import ConfigParser

import sys

SNAPSHOTS_DIR = 'Snapshots'


def snapshot():
    args = parse_snapshot_args()
    snapshot_file_name = str(int(time.time())) if args.tag is None else args.tag
    if args.path is None:
        pip_snapshot_location = _snapshot_dir_location()
        if not os.path.isdir(pip_snapshot_location):
            os.mkdir(pip_snapshot_location)
        snapshot_path = pip_snapshot_location / snapshot_file_name
    else:
        if not os.path.isdir(args.path):
            raise NotADirectoryError()
        snapshot_path = Path(args.path) / snapshot_file_name

    snapshot_file = open(snapshot_path, 'w')
    subprocess.call(['pip', 'freeze'], stdout=snapshot_file)

    print('Successfully saved snapshot to: {}'.format(snapshot_path))
    return snapshot_path


def revert():

    last_snapshot_path = max(list(_snapshot_dir_location().glob('*')), key=os.path.getmtime)
    current_snapshot = snapshot()

    try:
        subprocess.run(['pip', 'install', '-r', last_snapshot_path])
        os.remove(last_snapshot_path)
    except ...:
        subprocess.run(['pip', 'install', '-r', current_snapshot])


def parse_snapshot_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default=None, type=str)
    parser.add_argument('--tag', default=None, type=str)
    return parser.parse_args()


def parse_revert_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', default=None, type=str)
    parser.add_argument('--tag', default=None, type=str)
    return parser.parse_args()


def _snapshot_dir_location() -> Path:
    pip_config = subprocess.check_output(['pip', 'show', 'pip'], shell=True).decode()
    config_parser = ConfigParser()
    config_parser.read_string('[header_stub]' + pip_config)

    return Path(config_parser.get('header_stub', 'Location')) / SNAPSHOTS_DIR


revert()
