"""
=====
runwalker.py
=====

This module is contain the `ftpwalker` class which is responsible for
running a new walker.

============================

"""

import main_walker
from os import path, makedirs, listdir
import shutil
import checkplatform
import re


class ftpwalker:
    """
    ==============

    ``ftpwalker``
    ----------
    You can pass following arguments to class's caller at instantiation's time.
    server_name: The name of server
    url: The corresponding url
    root: The root path that you want to start the traversing from.
    daemon: Daemonization flag, which should be a boolean value (True, False)
    json_path: Corresponding path for saving the final json file.
    .. py:class:: ftpwalker()

    .. note::

    Example

    .. code-block:: python

    """
    def __init__(self, server_name, url, root='/', daemon=False):
        """
        .. py:attribute:: __init__()

           :param server_name: name of server
           :type server_name: str
           :param url: server's url
           :type url: str
           :param root: traversing start root
           :type root: str
           :param daemon: daemon flag
           :type daemon: boolean
           :rtype: None
        """
        self.name = re.sub(r'\W', '_', server_name)
        self.url = url
        platform_name = checkplatform.check()
        if daemon:
            print("Platform {}".format(platform_name))
            global daemon_obj
            if platform_name in {"Linux", "Mac"}:
                from daemons.unixdaemon import Daemon as daemon_obj
                daemon_obj = daemon_obj()
                try:
                    daemon_obj.stop()
                except:
                    pass
            else:
                from daemons.winservice import Service as daemon_obj
        self.daemon = daemon
        try:
            server_path = path.join(path.dirname(__file__), self.name)
        except Exception as exc:
            raise Exception("Please enter a valid name. {}".format(exc))
        else:
            self.server_path = server_path
        self.m_walker = main_walker.main_walker(server_name=self.name,
                                                url=self.url,
                                                server_path=self.server_path,
                                                root=root)

    def chek_state(self):
        """
        .. py:attribute:: chek_state()
        Check the current state. If a wanlker kas been run already
        it asks for continue or aborting, otherwise it starts the traversing.

           :rtype: None
        """
        if path.isdir(self.server_path):
            if len(listdir(self.server_path)) > 0:
                self.path_exit()
            else:
                self.path_not_exit(False)
        else:
            self.path_not_exit(True)
        daemon_obj.stop()

    def path_exit(self):
        """
        .. py:attribute:: path_exit()

        Runs if If a wanlker kas been run already.

           :rtype: None

        """
        while True:
            answer = input("""It seems that you've already
started traversing a server with this name.
Do you want to continue with current one(Y/N)?: """)
            if answer.strip().lower() in {'y', 'yes'}:
                print("Start resuming the {} server...".format(self.name))
                if self.daemon:
                    daemon_obj.start(self.m_walker.Process_dispatcher, True)
                else:
                    self.m_walker.Process_dispatcher(True)
                break
            elif answer.strip().lower() in {'n', 'no'}:
                # deleting the directory
                shutil.rmtree(self.server_path)
                if self.daemon:
                    daemon_obj.start(self.m_walker.Process_dispatcher, False)
                else:
                    self.m_walker.Process_dispatcher(False)
                break
            else:
                print("Answer with (Y/N).")

    def path_not_exit(self, create_dir):
        """
        .. py:attribute:: path_not_exit()
        Runs if there is no unsuccessful traversed server with this name.

           :param create_dir: A boolean value for creating a directory for this server
           in order to preserving the temp files.
           :type create_dir: boolean
           :rtype: None

        """
        # create the directory
        if create_dir:
            makedirs(self.server_path)
        if self.daemon:
            daemon_obj.start(self.m_walker.Process_dispatcher, False)
        else:
            self.m_walker.Process_dispatcher(False)