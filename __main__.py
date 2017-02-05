import sys
from omgchange.watcher import Watcher

# Todo: update arg options
# Todo: Make this file work right :D
verbose = False
cmd = []

def print_usage():
    print('Usage: python -m omgchange CMD FILES [options]\n'
          '\t-v|--verbose\tPrint verbose messages during operation'
          )
    exit(1)

# Handle CLI args
if len(sys.argv) > 1:
    if '-v' in sys.argv or '--verbose' in sys.argv:
        verbose = True
    else:
        print_usage()
else:
    print_usage()


w = Watcher(cmd, verbose=verbose)
w.monitor()
