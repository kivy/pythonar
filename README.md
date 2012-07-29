PythonAR
========

This project intend to provide a very simple way to restart applications
when you change source code or resources, thus providing a better workflow.

usage: reloader.py [-h] [-p PATH] [-a ACTION] ...

Allows to start a program, and to monitor changes in a folder, when changes
are detected in the folder, the command is restarted. This can be useful to
test a software you are developping and having immediate feedback. Or to
restart a daemon when configuration or data changes. Or any other use, the sky
is the limit :)

positional arguments:

    command

optional arguments:

    -h, --help            show this help message and exit

    -p PATH, --path PATH  set the path to monitor for changes

    -a ACTION, --action ACTION
                        what action to perform when changes are detected
