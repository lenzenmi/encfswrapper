#!/bin/python3
'''
A command line program to mount an encrypted encfs filesystem while another
program executes.
'''
import argparse
import getpass
import hashlib
import os
import subprocess
import tempfile
import tkinter


class Tkinter_input(tkinter.Tk):
    '''
    class to get password from the user using tkinter

    Attributes:
        * password (str): the password entered by the user.
    '''

    def __init__(self):
        tkinter.Tk.__init__(self)
        self.title('encfswrapper')
        self.password = ''

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
    '''
    class to get password from the user using shell

    Attributes:
        * password (str): the password entered by the user.
    '''

    def __init__(self):
        self.password = getpass.getpass('Enter encfs password: ')


def is_mounted(path):
    '''
    Test if the encfs mount path is in /etc/mtab.

    Args:
        * path (str): absolute path to the encfs mount

    Returns:
        * (bool): True = mounted, False = not-mounted
    '''
    mtab = open('/etc/mtab', 'r')
    mounted = False
    for line in mtab.readlines():
        if ('encfs' in line) and (path in line):
            mounted = True
    mtab.close()
    return mounted


def get_path(path):
    '''
    Converts user entered path to absolute path.

    Args:
        path (str): user entered path such as '~/encfs/'

    Returns:
        absolute_path (str): /home/user/endfs

    Raises:
        OSError: if path does not exist.
    '''
    path = os.path.abspath(os.path.realpath(os.path.expanduser(path)))
    if os.path.isdir(path):
        return path
    else:
        raise OSError('\"{}\" does not exist'.format(path))


def run(crypt_path, mount_path, wrapped_prog):
    '''
    mounts encfs and starts another program. Waits until that program has
    terminated then unmounts the encfs mount point. Can be executed multiple
    times. In that case, the encfs filesystem will not unmount until all
    programs started by encfswrapper have terminated.

    Args:
        * crypt_path (str): user entered path to the encrypted encfs data.
        * mount_path (str): user entered path to the encfs mountpoint
        * wrapped_progs (list): list of subprocess.Popen arguments to execute
          the external program.

    Example:
        run('~/.encfs', '~/encfs/', ['zim', '--standalone'])
    '''
    crypt_path = get_path(crypt_path)
    mount_path = get_path(mount_path)

    md5 = hashlib.md5()
    md5.update(mount_path.encode('utf-8'))
    tmppath = (md5.hexdigest())

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
            encfs = subprocess.Popen(
                ['/usr/bin/encfs', '--stdinpass', crypt_path, mount_path],
                stdin=subprocess.PIPE,
            )
            encfs.communicate(input=password.password.encode('utf-8'))

        if is_mounted(mount_path):
            subprocess.call(wrapped_prog)

    finally:
        os.close(lockfile[0])
        os.remove(lockfile[1])
        if is_mounted(mount_path) and len(os.listdir(lockdir)) == 0:
            subprocess.call(['fusermount', '-u', mount_path])
            os.rmdir(lockdir)


def main():
    '''
    cli interface.
    '''
    parser = argparse.ArgumentParser(
        description='mount encfs while COMMAND runs. Automatically unmount '
        'encfs after COMMAND terminates ')
    parser.add_argument('rootDir', nargs=1, help='encfs encrypted directory')
    parser.add_argument('mountPoint', nargs=1, help='encfs mount point')
    parser.add_argument('command',
                        metavar='COMMAND [options...]',
                        nargs=argparse.REMAINDER,
                        help='command to run including its arguments '
                             'and options.'
                        )
    args = parser.parse_args()
    run(args.rootDir[0], args.mountPoint[0], args.command)


if __name__ == '__main__':
    main()
