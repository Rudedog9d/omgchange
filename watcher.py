import re
import os
from time import sleep
import subprocess
from omgchange.output_watcher import OutputWatcher


class Watcher:
    def __init__(self, cmd=None, verbose=False, exit_on_failure=False, sleep_time=1):
        self._output_watcher = None
        self._mtimes = {}
        self.files = []
        self.process = None
        self.sleep_time = sleep_time
        self.verbose = verbose  # todo: set up logging instead?
        self.cmd = cmd or []  # in format of subprocess.Popen(cmd=[])

        # When the child server fails, exit watcher or restart server
        self.exit_on_failure = exit_on_failure

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

        # If verbose, print out the files being watched
        if self.verbose:
            print("Files to be watched:")
            for f in self.files:
                print(f)

        # Run monitor_once to get initial file times
        self.monitor_once()

    def monitor_once(self):
        #: Check for modifications in file times
        if not self.files:
            raise ValueError("No files specified")
        for f in self.files:
            try:
                mtime = os.stat(f).st_mtime
            except OSError:
                # The file might be right in the middle of being written so sleep
                sleep(1)
                mtime = os.stat(f).st_mtime

            if f not in self._mtimes.keys():
                self._mtimes[f] = mtime
                continue

            if mtime > self._mtimes[f]:
                if self.verbose: print("File changed: %s" % os.path.realpath(f))
                self._mtimes[f] = mtime
                return 1
        return 0

    def monitor(self):
        if not self.cmd:
            raise ValueError("No server command defined")
        rc = None

        # initially Start Server
        self.start_server()

        if self.verbose:
            print("Starting monitor loop")

        try:
            while rc is None:
                # Sleep for the cycle - do it first, so process
                # has time to start initially
                sleep(self.sleep_time)

                # Set process.returncode
                self.process.poll()
                # Get process.returncode
                rc = self.process.returncode

                if rc is not None:
                    # else rc is not None:
                    if self.exit_on_failure:
                        # Handle the child process exiting
                        raise ChildProcessError("\nServer Failed with return code {}".format(rc))
                    else:
                        # Wait for input, then restart server
                        # TODO: Audio alert? That'd be cool
                        print("\nServer Failed with return code {}".format(rc))
                        input("Press Enter to Restart...")
                        # Ensure server is dead, start server, and reset rc
                        self._stop_server_safe()
                        self.start_server()
                        rc = None

                # Watch for changes
                if self.monitor_once():
                    # A file changed, restart the server
                    self.stop_server()
                    self.start_server()

        except KeyboardInterrupt:
            rc = 0
        except ChildProcessError as e:
            print(e)
        self.exit(rc)

    def start_server(self):
        # Todo: Error handling
        if self.verbose: print("Starting Server")
        self.process = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)  # redirect stderr to STDOUT because flask -_-
        if self._output_watcher:
            # Watcher thread already exists, just change the process
            self._output_watcher.change_process(self.process)
        else:
            # Create a new thread that will watch the output of the process
            self._output_watcher = OutputWatcher(process=self.process)
            self._output_watcher.start()

    def stop_server(self):
        # Todo: Error handling
        if self.verbose: print("Stopping Server")
        self.process.terminate()

    def _stop_server_safe(self):
        # Stop server, but catch exception if process doesn't exist
        # stop_server() is the exposed version to give user more control/information
        try:
            self.stop_server()
        except ProcessLookupError:
            # If process does not exist, job is done
            pass

    def exit(self, rc=0):
        # Stop the server, then exit and join the watcher thread
        self._stop_server_safe()
        self._output_watcher.exit()
        self._output_watcher.join()
        exit(rc)
