#!/usr/bin/env python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import Popen, PIPE
from argparse import ArgumentParser, REMAINDER
from time import time, sleep
import re

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
parser.add_argument('-i', '--ignorelist', type=str, default='', nargs='*', help='files to ignore')
parser.add_argument('-f', '--focus', type=int, default=0, help='save focus and restore it for the next n seconds after restarting application, require xdotool (linux only)')
parser.add_argument('command', type=str, nargs=REMAINDER)


class RestartHandler(FileSystemEventHandler):
    def __init__(self, command, path, ignorelist, focus, **kwargs):
        super(RestartHandler, self).__init__(**kwargs)
        self.command = command
        self.ignorelist = ignorelist
        self.focus = focus
        self.start()

    def stop(self):
        self._process.terminate()
        print 'TERMINATED'

    def start(self):
        if self.focus:
            t = time()
            wid = int(Popen(['/usr/bin/env', 'xdotool', 'getwindowfocus'], stdout=PIPE).communicate()[0])

        self._process = Popen(self.command)
        print 'STARTED', self._process

        if self.focus:
            while time() < t + self.focus:
                Popen(['/usr/bin/env', 'xdotool', 'windowfocus', str(wid)])
                sleep(.01)

    def on_any_event(self, event):
        for i in self.ignorelist:
            if re.compile('^' + i.replace('*', '.*') + '$').match(event.src_path):
                return

        print 'terminating', self
        self.stop()
        self.start()


def monitor(command, path, action, focus, ignorelist=None):
        if action == 'restart':
            ev = RestartHandler(command, path=path, focus=focus, ignorelist=ignorelist)
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
    monitor(args.command, args.path, args.action, args.focus, args.ignorelist)
