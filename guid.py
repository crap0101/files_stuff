#!/usr/bin/env python
# -*- coding: utf-8 -*-
# managing GIDs and UIDs

# Copyright (C) 2025 Marco Chieppa

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not see <http://www.gnu.org/licenses/>

import grp
import pwd

def _groups_of (username):
    """Return the groups to which *username* belongs."""
    return list(x.gr_name for x in grp.getgrall() if username in x.gr_mem)

def _users_of (groupname):
    """Return usernames which belongs to *groupname*."""
    return grp.getgrnam(groupname).gr_mem
    
def _attr_from_username (username, attr):
    """Return the attribute *attr* of the given *username*"""
    return getattr(pwd.getpwnam(username), attr)

def _attr_from_groupname (groupname, attr):
    """Return the attribute *attr* of the given *groupname*"""
    return getattr(grp.getgrnam(groupname), attr)

def attr_from_uid (uid, attr):
    """Return the attribute *attr* of the given *uid*"""
    return getattr(pwd.getpwuid(uid), attr)
def attr_from_gid (gid, attr):
    """Return the attribute *attr* of the given *gid*"""
    return getattr(grp.getgrgid(gid), attr)

def name_from_uid (uid):
    return attr_from_uid(uid, 'pw_name')
def uid_from_name (name):
    return _attr_from_username(name, 'pw_uid')

def name_from_gid (gid):
    return attr_from_gid(gid, 'gr_name')
def gid_from_name (name):
    return _attr_from_groupname(name, 'gr_gid')

def groups_of_uid (uid):
    return _groups_of(name_from_uid(uid))
def groups_of_name (name):
    return _groups_of(name)

def users_of_gid (gid):
    """Return a list of usernames which belongs to the given *gid*"""
    return _users_of(name_from_gid(gid))
def users_of_name (groupname):
    """Return a list of usernames which belongs to *groupname*"""
    return _users_of(groupname)

if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--from-uid',
                        dest='uids', default=[], nargs='+', type=int,
                        action='extend', metavar='UID',
                        help='get names from the given %(metavar)ss.')
    parser.add_argument('-g', '--from-gid',
                        dest='gids', default=[], nargs='+', type=int,
                        action='extend', metavar='GID',
                        help='get names from the given %(metavar)ss.')
    parser.add_argument('-U', '--get-uid',
                        dest='usernames', default=[], nargs='+',
                        action='extend', metavar='USERNAME',
                        help='get users id from the given %(metavar)ss.')
    parser.add_argument('-G', '--get-gid',
                        dest='groupnames', default=[], nargs='+',
                        action='extend', metavar='GROUPNAME',
                        help='get group id from the given %(metavar)ss.')
    parser.add_argument('-l', '--groups-of',
                        dest='group_of', default=[], nargs='+',
                        action='extend', metavar='USERNAME',
                        help='get the groups to which each %(metavar)s belongs.')
    parser.add_argument('-L', '--users-of',
                        dest='users_of', default=[], nargs='+',
                        action='extend', metavar='GROUPNAME',
                        help='get the usernames which belongs to %(metavar)s.')

    args = parser.parse_args()
    for e in args.uids:
        try:print(e, name_from_uid(e))
        except KeyError as err: print(e, 'FAIL: {}'.format(err), file=sys.stderr)
    for e in args.gids:
        try:print(e, name_from_gid(e))
        except KeyError as err: print(e, 'FAIL: {}'.format(err), file=sys.stderr)
    for e in args.usernames:
        try:print(e, uid_from_name(e))
        except KeyError as err: print(e, 'FAIL: {}'.format(err), file=sys.stderr)
    for e in args.groupnames:
        try:print(e, gid_from_name(e))
        except KeyError as err: print(e, 'FAIL: {}'.format(err), file=sys.stderr)
    for e in args.group_of:
        try:print(e, groups_of_name(e))
        except KeyError as err: print(e, 'FAIL: {}'.format(err), file=sys.stderr)
    for e in args.users_of:
        try:print(e, users_of_name(e))
        except KeyError as err: print(e, 'FAIL: {}'.format(err), file=sys.stderr)
