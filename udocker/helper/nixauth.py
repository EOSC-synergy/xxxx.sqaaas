# -*- coding: utf-8 -*-
"""Linux utilities, authentication"""

import re
import pwd
import grp


class NixAuthentication(object):
    """Provides abstraction and useful methods to manage
    passwd and group based authentication, both for the
    host system and for the container.
    If passwd_file and group_file are None then the host
    system authentication databases are used.
    """

    def __init__(self, conf, passwd_file=None, group_file=None):
        self.conf = conf
        self.passwd_file = passwd_file
        self.group_file = group_file

    def _get_user_from_host(self, wanted_user):
        """get user information from the host /etc/passwd"""
        wanted_uid = ""
        if (isinstance(wanted_user, int) or
                re.match("^\\d+$", wanted_user)):
            wanted_uid = str(wanted_user)
            wanted_user = ""
        if wanted_uid:
            try:
                usr = pwd.getpwuid(int(wanted_uid))
            except (IOError, OSError, KeyError):
                return("", "", "", "", "", "")
            return(str(usr.pw_name), str(usr.pw_uid), str(usr.pw_gid),
                   str(usr.pw_gecos), usr.pw_dir, usr.pw_shell)
        else:
            try:
                usr = pwd.getpwnam(wanted_user)
            except (IOError, OSError, KeyError):
                return("", "", "", "", "", "")
            return(str(usr.pw_name), str(usr.pw_uid), str(usr.pw_gid),
                   str(usr.pw_gecos), usr.pw_dir, usr.pw_shell)

    def _get_group_from_host(self, wanted_group):
        """get group information from the host /etc/group"""
        wanted_gid = ""
        if (isinstance(wanted_group, int) or
                re.match("^\\d+$", wanted_group)):
            wanted_gid = str(wanted_group)
            wanted_group = ""
        if wanted_gid:
            try:
                hgr = grp.getgrgid(int(wanted_gid))
            except (IOError, OSError, KeyError):
                return("", "", "")
            return(str(hgr.gr_name), str(hgr.gr_gid), str(hgr.gr_mem))
        else:
            try:
                hgr = grp.getgrnam(wanted_group)
            except (IOError, OSError, KeyError):
                return("", "", "")
            return(str(hgr.gr_name), str(hgr.gr_gid), str(hgr.gr_mem))

    def _get_user_from_file(self, wanted_user):
        """Get user from a passwd file"""
        wanted_uid = ""
        if (isinstance(wanted_user, int) or
                re.match("^\\d+$", wanted_user)):
            wanted_uid = str(wanted_user)
            wanted_user = ""
        try:
            inpasswd = open(self.passwd_file)
        except (IOError, OSError):
            return("", "", "", "", "", "")
        else:
            for line in inpasswd:
                (user, dummy, uid, gid, gecos, home,
                 shell) = line.strip().split(":")
                if wanted_user and user == wanted_user:
                    return(user, uid, gid, gecos, home, shell)
                if wanted_uid and uid == wanted_uid:
                    return(user, uid, gid, gecos, home, shell)
            inpasswd.close()
            return("", "", "", "", "", "")

    def _get_group_from_file(self, wanted_group):
        """Get group from a group file"""
        wanted_gid = ""
        if (isinstance(wanted_group, int) or
                re.match("^\\d+$", wanted_group)):
            wanted_gid = str(wanted_group)
            wanted_group = ""
        try:
            ingroup = open(self.group_file)
        except (IOError, OSError):
            return("", "", "")
        else:
            for line in ingroup:
                (group, dummy, gid, users) = line.strip().split(":")
                if wanted_group and group == wanted_group:
                    return(group, gid, users)
                if wanted_gid and gid == wanted_gid:
                    return(group, gid, users)
            ingroup.close()
            return("", "", "")

    def add_user(self, user, passw, uid, gid, gecos,
                 home, shell):
        """Add a *nix user to a /etc/passwd file"""
        try:
            with open(self.passwd_file, "a") as opass:
                opass.write("%s:%s:%s:%s:%s:%s:%s\n" %
                            (user, passw, uid, gid, gecos, home, shell))
            return True
        except (IOError, OSError):
            return False

    def add_group(self, group, gid):
        """Add a group to a /etc/passwd file"""
        try:
            with open(self.group_file, "a") as ogroup:
                ogroup.write("%s:x:%s:\n" % (group, gid))
                return True
        except (IOError, OSError):
            return False

    def get_user(self, wanted_user):
        """Get host or container user"""
        if self.passwd_file:
            return self._get_user_from_file(wanted_user)
        return self._get_user_from_host(wanted_user)

    def get_group(self, wanted_group):
        """Get host or container group"""
        if self.group_file:
            return self._get_group_from_file(wanted_group)
        return self._get_group_from_host(wanted_group)

    def get_home(self):
        """Get host or container home directory"""
        (r_user, dum, dum, dum, r_home, dum) = self.get_user(self.conf['uid'])
        if r_user:
            return r_home
        return ""
