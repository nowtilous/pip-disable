import argparse
import os.path
import subprocess
import time

from pathlib import Path
from configparser import ConfigParser
import sys

SNAPSHOT_PREFIX = 'pip-snapshot'
SNAPSHOTS_DIR = 'Snapshots'

def main(*args):
    print(args)


def snapshot():
    args = parse_args()
    snapshot_file_name = SNAPSHOT_PREFIX + str(int(time.time()))
    if args.path is None:
        pip_snapshot_location = _find_pip_location() / SNAPSHOTS_DIR
        if not os.path.isdir(pip_snapshot_location):
            os.mkdir(pip_snapshot_location)
        snapshot_path = pip_snapshot_location / snapshot_file_name
    else:
        if not os.path.isdir(args.path):
            raise NotADirectoryError()
        snapshot_path = Path(args.path) / snapshot_file_name

    snapshot_file = open(snapshot_path, 'w+')
    subprocess.call(['pip', 'freeze', '>', snapshot_path], stdout=snapshot_file)

    print('Successfully saved snapshot to: {}'.format(snapshot_path))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default=None, type=str, help='Path to venv root')
    return parser.parse_args()


def _find_pip_location() -> Path:
    pip_config = subprocess.check_output(['pip', 'show', 'pip'], shell=True).decode()
    config_parser = ConfigParser()
    config_parser.read_string('[header_stub]' + pip_config)

    return Path(config_parser.get('header_stub', 'Location'))


snapshot()
