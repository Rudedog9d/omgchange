
import datetime
import re
import os
import time

class Watcher:
    def __init__(self, cmd, verbose=False):
        self.files = []
        self.cmd = []
        self.mtimes = {}
        self.verbose = verbose

