#!/usr/bin/env python
import sys, os

# TODO: Fix this hack? to import things
# Add omgchange folder to syspath
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from omgchange.watcher import Watcher
