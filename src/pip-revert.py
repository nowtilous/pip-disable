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


def revert():
    args = parse_revert_args()
    snapshots = sorted(_snapshot_dir_location().iterdir(), key=os.path.getmtime)
    if len(snapshots) == 0:
        raise NoSnapshotsAvailable()

    if args.tag is not None:
        if not os.path.isfile(args.tag):
            raise FileNotFoundError()
        last_snapshot_path = _snapshot_dir_location() / args.tag
    elif args.n is not None:
        if args.n < 1 or args.n > len(snapshots):
            raise ValueError("Invalid revert count specified! Available range is 1 - {}".format(len(snapshots)))
        snapshots.reverse()
        last_snapshot_path = snapshots[args.n - 1]
    else:
        last_snapshot_path = max(snapshots)

    subprocess.run(['pip', 'install', '-r', last_snapshot_path])
    os.remove(last_snapshot_path)
    print("Successfully reverted to snapshot '{}'".format(last_snapshot_path))


def parse_snapshot_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', default=None, type=str)
    parser.add_argument('--tag', default=None, type=str)
    return parser.parse_args()


def parse_revert_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', default=None, type=int)
    parser.add_argument('--tag', default=None, type=str)
    return parser.parse_args()


def _snapshot_dir_location() -> Path:
    pip_config = subprocess.check_output(['pip', 'show', 'pip'], shell=True).decode()
    config_parser = ConfigParser()
    config_parser.read_string('[header_stub]' + pip_config)

    return Path(config_parser.get('header_stub', 'Location')) / SNAPSHOTS_DIR


class NoSnapshotsAvailable(Exception):
    pass


revert()
