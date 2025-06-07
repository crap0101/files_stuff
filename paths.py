#!/usr/bin/env python
# -*- coding: utf-8 -*-
# managing paths module

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

import os
import warnings

#########################
# GENERIC UTILITY FUNCS #
#########################

def showwarning (message, cat, fn, lno, *a, **k):
    print(message)
warnings.showwarning = showwarning


#
# Manage the 'strict' parameter of os.path.realpath (added since python 3.10)
#
vinfo = sys.version_info
if vinfo.major == 3 and vinfo.minor < 10:
    realpath = os.path.realpath
else:
    realpath = partial(os.path.realpath, strict=True)



def check_real (path: str) -> tuple[bool, str|None, None|Exception]:
    """
    Checks if realpath($path) == $path
    Returns (bool, realpath, None) or (False, None, raised exception).
    See: https://docs.python.org/3.8/library/os.path.html#os.path.realpath
    """
    try:
        real_path = realpath(path)
        is_real = (real_path == path)
        return is_real, real_path, None
    except OSError as err:
        warnings.warn(f'{path} => {err}')        
        return False, None, err


def check_regular (path: str) -> bool:
    """
    Returns True if $path is a regular file and not a broken symlink nor
    a file for wich the user doesn't have enough permissions.
    """
    return os.path.exists(path) and os.path.isfile(path)


def _find_irregular (paths: Sequence[str]):
    raise NotImplementedError('to be written')
    #XXX+TODO: write a filter to find broken links or not stat-able files only
