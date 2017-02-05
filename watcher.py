import datetime
import re
import os
from time import sleep
import sys
import subprocess


class Watcher:
    def __init__(self, cmd=None, verbose=False):
        self.files = []
        self.cmd = cmd or ["python3", "FrewsburgerPysite.py"]
        self.mtimes = {}
        self.verbose = verbose  # todo: set up logging instead?
        self.process = None

    def walk_dirs(self, dirnames):
        dir_files = []
        for dirname in dirnames:
            for path, dirs, files in os.walk(dirname):
                files = [ os.path.join(path, f) for f in files ]
                dir_files.extend(files)
                dir_files.extend(self.walk_dirs(dirs))
        return dir_files

    def add_files(self, files, regex=None):
        #: Files is a list of files
        #: Regex is a regular expression string that files should match
        if isinstance(files, str):
            files = [files]
        if not isinstance(files, list):
            raise ValueError("Expecting list, got {}".format(type(files)))

        regex = regex or [".*"]
        dirs = [ os.path.realpath(f) for f in files if os.path.isdir(f) ]
        files = [ os.path.realpath(f) for f in files if os.path.isfile(f) ]

        dir_files = self.walk_dirs(dirs)
        files.extend(dir_files)

        valid_files = []
        for f in files:
            if os.path.exists(f) and os.path.isfile(f):
                for r in regex:
                    if re.match(r, f):
                        valid_files.append(f)

        unique_files = [ f for f in valid_files if f not in self.files ]

        self.files += unique_files

        if self.verbose:
            print("Files to be watched:")
            for f in self.files:
                print(f)

        # Run monitor_once to get initial file times
        self.monitor_once()

    def monitor_once(self):
        if not self.files:
            raise ValueError("No files specified")
        for f in self.files:
            try:
                mtime = os.stat(f).st_mtime
            except OSError:
                # The file might be right in the middle of being written so sleep
                sleep(1)
                mtime = os.stat(f).st_mtime

            if f not in self.mtimes.keys():
                self.mtimes[f] = mtime
                continue

            if mtime > self.mtimes[f]:
                if self.verbose: print("File changed: %s" % os.path.realpath(f))
                self.mtimes[f] = mtime
                return 1
        return 0

    def monitor(self):
        rc = None

        # initially Start Server
        self.start_server()

        try:
            while rc is None:
                # Watch for changes
                if self.monitor_once():
                    # A file changed, restart the server
                    self.stop_server()
                    self.start_server()
                sleep(1)

        except KeyboardInterrupt:
            rc = 0
        finally:
            self.stop_server()
            exit(rc if rc else 1)

    def start_server(self):
        # Todo: Error handling
        if self.verbose: print("Starting Server")
        self.process = subprocess.Popen(self.cmd)

    def stop_server(self):
        # Todo: Error handling
        if self.verbose: print("Stopping Server")
        self.process.terminate()
