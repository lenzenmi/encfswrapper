#!/bin/python3
import tkinter
import subprocess
import os
import getpass
import argparse
import tempfile
import hashlib


class Tkinter_input(tkinter.Tk):

    def __init__(self):
        tkinter.Tk.__init__(self)
        self.title('encfs password')
        self.password = None

        tkinter.Label(self, text='Please enter encfs password').pack()
        self.entry = tkinter.Entry(self, show='*')
        self.entry.pack()
        self.entry.focus()

        def getpassword():
            self.password = self.entry.get()
            self.destroy()

        self.button = tkinter.Button(self, text='OK', command=getpassword)
        self.button.pack()

        self.bind('<Return>', lambda key: getpassword())
        self.focus_set()
        self.mainloop()


class Shell_input():

    def __init__(self):
        self.password = getpass.getpass('Enter encfs password: ')


def is_mounted(path):
    mtab = open('/etc/mtab', 'r')
    mounted = False
    for line in mtab.readlines():
        if ('encfs' in line) and (path in line):
            mounted = True
    mtab.close()
    return mounted


def get_path(path):
    path = os.path.abspath(os.path.realpath(os.path.expanduser(path)))
    if os.path.isdir(path):
        return path
    else:
        raise OSError('\"{}\" does not exist'.format(path))


def run(crypt_path, mount_path, wrapped_prog):

    crypt_path = get_path(crypt_path)
    mount_path = get_path(mount_path)

    md5 = hashlib.md5()
    md5.update(mount_path.encode('utf-8'))
    tmppath = (md5.hexdigest()[:10])

    tmp = tempfile.gettempdir()

    try:
        lockdir = os.path.join(
            tmp,
            'encfs-{}'.format(tmppath))
        if not os.path.isdir(lockdir):
            os.mkdir(lockdir)
        lockfile = tempfile.mkstemp('', 'encfs', lockdir)
        if not is_mounted(mount_path):
            try:
                password = Tkinter_input()
            except:
                password = Shell_input()
            subprocess.check_output(
                'echo "{}" | encfs --stdinpass {} {}'.format(
                    password.password,
                    crypt_path,
                    mount_path
                ),
                shell=True
            )

        if is_mounted(mount_path):
            subprocess.call(wrapped_prog)

    finally:
        os.close(lockfile[0])
        os.remove(lockfile[1])
        if is_mounted(mount_path) and len(os.listdir(lockdir)) == 0:
            subprocess.call(['fusermount', '-u', mount_path])
            os.rmdir(lockdir)


def main():
    parser = argparse.ArgumentParser(description='mount encfs while '
                                     'program runs')
    parser.add_argument('rootDir', nargs=1, help='encfs encrypted directory')
    parser.add_argument('mountPoint', nargs=1, help='encfs mount point')
    parser.add_argument('command',
                        metavar='command [options...]',
                        nargs=argparse.REMAINDER,
                        help='command to run')
    args = parser.parse_args()
    run(args.rootDir[0], args.mountPoint[0], args.command)


if __name__ == '__main__':
    main()
