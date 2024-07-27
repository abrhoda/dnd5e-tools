import logging
import argparse

from version import __version__

logger = logging.getLogger(__name__)
VERSION = '0.1.0'

def parse() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='', epilog='')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}', help='Version of the tool.')
    parser.add_argument('--log-level', default='WARNING', type=str.upper, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set log level for fine tuned logging output.')
    parser.add_argument('--log-file', action='store', type=str, help='logging output into a log file to help visibility.')
    
    subparsers = parser.add_subparsers(required=True, dest='command', help='** HELP MSG ABOUT SUBPARSERS **')

    setup_parser = subparsers.add_parser('setup', help='Setup functionality and utilities.')
    setup_parser.add_argument('-t', '--type', default='ALL', type=str.upper, choices=['ALL', 'BESTIARY'],
                              help='Fine tune control of which modules to set up. BESTIARY will set up data for all monsters/encounters and matching stat blocks along with information and images. ALL sets up data for all modules.')
    setup_parser.add_argument('-s', '--source', action='store', type=str, required=True, 
                              help='Location of 5e tools repo. Must point to the root of this project. (use: `git pull https://github.com/5etools-mirror-2/5etools-mirror-2.github.io.git` to get the repo)')
    
    encounter_parser = subparsers.add_parser('encounter', help='Builds an encounter')
    encounter_parser.add_argument('-e', '--environment', type=str.upper, default='ANY', choices=['ANY', 'ARCTIC', 'COASTAL', 'DESERT', 'FOREST', 'GRASSLAND', 'HILL', 'MOUNTAIN', 'NONE', 'SWAMP', 'UNDERDARK', 'UNDERWATER', 'URBAN'], help='Filter monsters for the encounter by environment.')
    encounter_parser.add_argument('--challenge-rating', type=float, required=True)
    #encounter_parser.add_argument()

    return parser.parse_args()
