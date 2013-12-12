**encfswrapper** mounts an `encfs filesystem`__ while another program executes. When all instances of programs started by encfswrapper using the same encfs mount point have terminated, the encfs filesystem is unmounted automatically.

__ encfs_
.. _encfs: http://www.arg0.net/encfs

========
Requires
========
* encfs_
* Python 3.x

============
Installation
============

.. code:: bash
    
    git clone git://github.com/lenzenmi/btrsnap.git
    python setup.py install
    
=====
Usage
=====


Usage is pretty simple. just call encfswrapper like you would encfs but append the command you want to run with all of its arguments

.. code:: bash

    encfswrapper rootDir mountPoint (command [options...])
    
Useful Examples
---------------

Zim
~~~

`Zim <http://zim-wiki.org/>`_ is a desktop wiki. It's lovely for making beautiful notes. It uses a simple markup language and stores everything in plain text files that can easily be read with any text editor.

Once you have a lot of useful notes, it may be nice to back them up on the cloud somewhere using a tool like `rsync <http://rsync.samba.org/>`_. The problem is that once you start sending your private notes out into the internet, you probably want it encrypted.

By default, zim stores your notes in your home folder in a directory called Notes. Lets move that.

.. code:: bash

    mv ~/Notes ~/Notes-old
    
Next we need to make a few directories for encfs.

.. code:: bash

    mkdir ~/.Notes # A hidden directory in your home folder for encrypted data.
    mkdir ~/Notes # Zim's default storage folder
    
Now go ahead and setup encfs

.. code:: bash

    encfs ~/.Notes ~/Notes

You'll be prompted for a password, and a bunch of other encfs settings. When it's done, Everything you copy into your ~/Notes folder will automatically be encrypted and stored in ~/.Notes. Let's do that.

.. code:: bash

    rsync -av ~/Notes-old ~/Notes
    
You can view all of your data in ~/Notes in plain text. If you start zim, it should work fine.

You can also look inside ~/.Notes to see all of your data in encrypted form.

Let's unmount our encfs folder.

.. code:: bash

    fusermount -u ~/Notes
    ls ~/Notes
    ls ~/.Notes
    
The ~/Notes folder should now be empty, but all of our encrypted data is still present inside ~/.Notes.

Now we can use encfswrapper to automate mounting this folder when we start zim.

.. code:: bash

    encfswrapper ~/.Notes ~/Notes zim --standalone

The standalone option is required to keep zim from demonizing which would cause encfswrapper to unmount your encfs mount point.

**Hurray:** zim should now be working normally and all of your stored notes will be encrypted! It's now safe to replicate your ~/.Notes folder anywhere on the internet.

A bit more advanced
^^^^^^^^^^^^^^^^^^^

Unfortunately the above command requires a lot more typing than before. Compare:

.. code:: bash
    :number-lines:
    
    zim
    encfswrapper ~/.Notes ~/Notes zim --standalone
    
We can improve this by writing a simple bash script and placing it in ``/usr/local/bin/zim`` and making it executable. If your PATH is setup correctly, as it should be by default, this file will run instead of the default /usr/bin/zim, thus overriding it.

``/usr/local/bin/zim``

.. code:: bash

    #!/bin/bash
    if [ "$ZIM_CRYPT" ] && [ "ZIM_MOUNT" ]; then
    	encfswrapper  "$ZIM_CRYPT" "$ZIM_MOUNT" /usr/bin/zim --standalone
    else
    	/usr/bin/zim
    fi

All we are doing here is checking to see if two environmental variables are set. If they are not, we run zim normally. If they are, we call encfswrapper to start zim. 

Now all we have to do is set those environmental variables. Add these lines to your ~/.bashrc file.

.. code:: bash

    export ZIM_CRYPT='~/.Notes'
    export ZIM_MOUNT='~/Notes'
    
That's it. Now you can start your encrypted zim the same way you always have.

.. code:: bash

    zim