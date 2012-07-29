#!/usr/bin/env python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import Popen
from argparse import ArgumentParser, REMAINDER
from time import sleep

parser = ArgumentParser(description='''
Allows to start a program, and to monitor changes in a folder, when changes are
detected in the folder, the command is restarted.

This can be useful to test a software you are developping and having immediate
feedback.
Or to restart a daemon when configuration or data changes.
Or any other use, the sky is the limit :)
''')
parser.add_argument('-p', '--path', type=str, default='.', help='set the path to monitor for changes')
parser.add_argument('-a', '--action', type=str, default='restart', help='what action to perform when changes are detected')
#parser.add_argument('-i', '--ignore', type=str, default='',
parser.add_argument('command', type=str, nargs=REMAINDER)


class RestartHandler(FileSystemEventHandler):
    def __init__(self, command, path, ignorelist, **kwargs):
        super(RestartHandler, self).__init__(**kwargs)
        self.command = command
        self.start()

    def stop(self):
        self._process.terminate()
        print 'TERMINATED'

    def start(self):
        self._process = Popen(self.command)
        print 'STARTED', self._process

    def on_any_event(self, event):
        print 'terminating', self
        self.stop()
        self.start()


def monitor(command, path, action, ignorelist=None):
        if action == 'restart':
            ev = RestartHandler(command, path=path, ignorelist=ignorelist)
        else:
            raise NotImplementedError('action %s not implemented' % action)

        ob = Observer()
        ob.schedule(ev, path=path, recursive=True)
        ob.start()
        try:
            while True:
                sleep(1)
        except KeyboardInterrupt:
            ob.stop()
        ob.join()

if __name__ == '__main__':
    args = parser.parse_args()
    print args
    monitor(args.command, args.path, args.action)  # args.ignorelist)
