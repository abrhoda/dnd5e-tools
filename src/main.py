#!/usr/bin/env/ python

import argparse

from cli import parse
from utils import setup_logger
from setup import setup

if __name__ == '__main__':
    args = parse()
    setup_logger(args.log_level, args.log_file)

    print(vars(args))
    if args.command == 'setup':
        print('calling setup')
        setup(args.source, args.type)

    elif arg.command == 'run':
        print('run loop here')
        # TODO
