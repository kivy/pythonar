PythonAR
========

This project intend to provide a very simple way to restart applications
when you change source code or resources, thus providing a better workflow.

usage:

    reloader.py [-h] [-p PATH] [-a ACTION] [-f SECONDS] [-i IGNORELIST] [-s SECONDS] command

Allows to start a program, and to monitor changes in a folder, when changes
are detected in the folder, the command is restarted. This can be useful to
test a software you are developping and having immediate feedback. Or to
restart a daemon when configuration or data changes. Or any other use, the sky
is the limit :)

/!\ if still alive before a restart, the process will be killed, your
program has to be able to be killed without corrupting anything, which is
always a nice feature for a software anyway :).

positional arguments:
---------------------

    command

optional arguments:
-------------------

    -h, --help            show this help message and exit

    -p PATH, --path PATH  set the path to monitor for changes

    -a ACTION, --action ACTION
                        what action to perform when changes are detected

    -i FILES, --ignorelist FILES
                        list of filepatterns to ignore use * as glob,
                        used on complete filename

    -f SECONDS, --focus SECONDS
                        (linux only for now) Will prevent anything from
                        stealing focus for SECONDS seconds.

    -s SECONDS, --sleep SECONDS
                        ignore all events SECONDS seconds after the last
                        restart

dummy exemple:
--------------

    ./reloader.py -p testdir -i *.sw* -s 2 -a restart ls -l

will restart a ls process every time a file is created/changed/deleted
in testdir folder, ignoring all vim swapfiles, and won't listen to any
event less than 2 seconds after the last restart.
