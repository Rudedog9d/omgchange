#!/usr/bin/env python3
import threading


class OutputWatcher(threading.Thread):
    def __init__(self, process=None, prefix=None):
        super(OutputWatcher, self).__init__()
        self._run = True
        self._process_changed = False
        self.process = process
        self.prefix = prefix or "Server: "

    def run(self):
        while self._run:
            if self.process is None:
                return 1
            for line in self.process.stdout:
                print("{}{}".format(self.prefix, line.decode()), end='')
        if self._process_changed:
            # if process changed, do run() again
            # Recursion bad here?
            self._process_changed = False
            self.run()
        return

    def exit(self):
        #: Set exit flag to True and exit process
        self._run = False
        self._process_changed = False  # should be false, but make sure

    def change_process(self, process):
        from subprocess import Popen
        if not isinstance(process, Popen):
            raise ValueError("Not a valid Popen process")
        self.process = process
        self._process_changed = True
