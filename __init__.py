#!/usr/bin/env python
import sys
from omgchange.watcher import Watcher

if __name__ == '__main__':
    # Todo: update arg options
    verbose = False
    cmd = []

    # Handle CLI args
    if len(sys.argv) > 1:
        if '-v' in sys.argv or '--verbose' in sys.argv:
            verbose = True
        else:
            print('Usage: ./{} [options]\n'
                  'Options: -v|--verbose\tPrint verbose messages during operation'
                  )
            exit(1)

    w = Watcher(cmd, verbose=verbose)
    w.monitor()