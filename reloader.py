#!/usr/bin/env python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent
from subprocess import Popen, PIPE
from argparse import ArgumentParser, REMAINDER
from time import time, sleep
import re
import six

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    colored = None

parser = ArgumentParser(description='''
Allows to start a program, and to monitor changes in a folder, when changes are
detected in the folder, the command is restarted.

This can be useful to test a software you are developping and having immediate
feedback.
Or to restart a daemon when configuration or data changes.
Or any other use, the sky is the limit :)
''')
parser.add_argument('-p', '--path', type=str, default='.',
                    help='set the path to monitor for changes')
parser.add_argument('-a', '--action', type=str, default='restart',
                    help='what action to perform when changes are detected')
parser.add_argument('-i', '--ignorelist', type=str, default='', nargs='*',
                    help='files to ignore')
parser.add_argument('-f', '--focus', type=int, default=0,
                    help='save focus and restore it for the next n'
                    'seconds after restarting application, require'
                    'xdotool (linux only)')
parser.add_argument('-s', '--sleep', type=int, default=0,
                    help='ignore events for n seconds after the last restart')
parser.add_argument('command', type=str, nargs=REMAINDER)


def log(color, string):
    if colored:
        six.print_(colored(string, color))
    else:
        six.print_(string)


class RestartHandler(FileSystemEventHandler):
    def __init__(self, command, path, ignorelist, focus, sleeptime, **kwargs):
        super(RestartHandler, self).__init__(**kwargs)
        self.command = command
        self.ignorelist = ignorelist
        self.focus = focus
        self.sleep = sleeptime
        self.start()

    def stop(self):
        self._process.terminate()
        log('red', 'TERMINATED')

    def start(self, geometry=None):
        self._last_restart = time()
        if self.focus:
            t = time()
            wid = int(Popen(['/usr/bin/env', 'xdotool', 'getwindowfocus'],
                            stdout=PIPE).communicate()[0])

        self._process = Popen(self.command)
        log('green', 'STARTED %s' % self._process)

        if geometry:
            self.swid = int(Popen(['/usr/bin/env', 'xdotool', 'getwindowfocus'],
                                  stdout=PIPE).communicate()[0])
        else:
            self.swid = None

        if self.focus:
            while time() < t + self.focus:
                # try to detect a window appeared by tracking focus
                # change, NOT 100% safe!
                swid = int(Popen(['/usr/bin/env', 'xdotool', 'getwindowfocus'],
                                 stdout=PIPE).communicate()[0])
                if swid != wid:
                    six.print_("got swid", swid)
                    self.swid = swid
                    if geometry:
                        self.replace(geometry)

                Popen(['/usr/bin/env', 'xdotool', 'windowfocus', str(wid)])
                sleep(.01)

        if geometry:
            self.replace(geometry)

    def replace(self, geometry):
        six.print_(geometry)
        x, y = geometry.split('\n')[1].strip().split(' ')[1].split(',')
        w, h = geometry.split('\n')[2].strip().split(' ')[1].split('x')
        Popen(['/usr/bin/env', 'xdotool', 'windowsize', str(self.swid), w, h])
        Popen(['/usr/bin/env', 'xdotool', 'windowmove', str(self.swid), x, y])

    def on_any_event(self, event):
        if self.sleep and time() < self._last_restart + self.sleep:
            return

        for i in self.ignorelist:
            r = re.compile('^' + i.replace('*', '.*') + '$')
            if r.match(event.src_path):
                return
            if isinstance(event, FileMovedEvent) and r.match(event.dest_path):
                return

        log('blue', '%s RESTARTING' % event)

        geometry = None
        if self.swid:
            geometry = Popen(['/usr/bin/env', 'xdotool', 'getwindowgeometry',
                              str(self.swid)],
                             stdout=PIPE).communicate()[0]
        self.stop()
        self.start(geometry)


def monitor(command, path, action, focus, sleeptime, ignorelist=None):
        if action == 'restart':
            ev = RestartHandler(command, path=path, focus=focus,
                                sleeptime=sleeptime,
                                ignorelist=ignorelist)
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
    log('blue', str(args))
    monitor(args.command, args.path, args.action, args.focus, args.sleep,
            args.ignorelist)
