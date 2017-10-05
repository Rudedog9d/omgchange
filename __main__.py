import sys
from omgchange.watcher import Watcher
import argparse

# Todo: Make this file work right :D
cmd = []

if __name__ == '__main__':
    # Handle CLI args
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', help='Print verbose messages during operation',
                        action='store_true')

    if len(sys.argv) < 1:
        parser.print_help()
        exit(1)

    w = Watcher(cmd, verbose=parser.verbose)
    w.monitor()
