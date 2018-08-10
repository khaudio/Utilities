#!/usr/bin/env python

from getpass import getpass
from subprocess import Popen, PIPE, STDOUT
from sys import stdout


def stream(proc):
    for char in iter(lambda: proc.stdout.read(1), b''):
        stdout.buffer.write(char)


def main():
    username = input('github username: ').rstrip()
    repoName = input('New repository name: ').rstrip()
    privatePrompt = input('Create private repository (y/n)? ').rstrip().lower()
    if privatePrompt in ('Y', 'y'):
        private = 'true'
    elif privatePrompt in ('N', 'n', ''):
        private = 'false'
    # pw = getpass('Enter password...')
    create = Popen(
            ['curl', '-u', f"'{username}'", 'https://api.github.com/user/repos', '-d',
            ''.join(('{', f'"name":"{repoName}", "private":"{private}"', '}'))],
            stdin=PIPE, stdout=PIPE, stderr=STDOUT
        )
    # create.stdin.write(pw.encode('utf-8'))
    stream(create)


if __name__ == '__main__':
    main()
