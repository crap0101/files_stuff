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

from collections import defaultdict
from collections.abc import Callable, Sequence, Iterator
from functools import partial
import hashlib
from fnmatch import fnmatch
from numbers import Number
import os
import re
import sys

# external modules
from py_warnings import pywarn

# Manage warnings
class PathWarning(pywarn.CustomWarning):
    pass
# set warnings to nothing, to be customize in the modules where it's imported
pywarn.set_filter(pywarn.IGNORE_WARNINGS, PathWarning)


#
# Manage the 'strict' parameter of os.path.realpath (added since python 3.10)
#
vinfo = sys.version_info
if vinfo.major == 3 and vinfo.minor < 10:
    realpath = os.path.realpath
else:
    realpath = partial(os.path.realpath, strict=True)


def check_pattern (path: str,
                   patterns: Sequence[str]) -> bool:
    """
    Checks if $path matches any elements of $patterns (use fnmatch).
    """
    return any(fnmatch(path, p) for p in patterns)


def check_regex (path: str, cregex: Sequence[re.Pattern], match_method: str = 'search') -> bool:
    """
    Checks if $path matches any elements of $cregex,
    using re.Patter.$match_method for testing $path (default to 'search').
    """
    return any(getattr(r, match_method)(path) for r in cregex)


def check_regular (path: str) -> bool:
    """
    Returns True if $path is a regular file and not a broken symlink nor
    a file for wich the user doesn't have enough permissions.
    """
    return os.path.exists(path) and os.path.isfile(path)


def check_stat_attr (path: str,
                        op: Callable,
                        stat_attr: str,
                        value: Number) -> bool:
    """
    Checks if $path has the $stat_attr attribute set
    to $value using $op as comparison function.
    """
    return op(getattr(os.stat(path), stat_attr), value)


def exclude_pattern (path: str, patterns: Sequence[str]) -> bool:
    """
    Returns True if $path *don't* match any of $patterns (use fnmatch).
    """
    return not check_pattern(path, pattern)


def exclude_regex (path: str, cregex: Sequence[re.Pattern], match_method: str = 'search') -> bool:
    """
    Returns True if $path *not* match any of the $regex pattern,
    using re.Patter.$match_method for testing $path (default to 'search').
    """
    return not check_regex(path, cregex, match_method)


def expand_path (path: str) -> str:
    """Expands $path to the canonical form."""
    return os.path.abspath(os.path.expanduser(os.path.expandvars(path)))


def get_hash (path: str, hash_type_name: str, size: int) -> str:
    """
    Returns the hash of $path using hashlib.new($hash_type_name).
    Reads blocks of $size bytes of the file at a time.
    """
    with open(path, 'rb') as f:
        hashed = hashlib.new(hash_type_name)
        while True:
            buf = f.read(size)
            if not buf:
                break
            hashed.update(buf)
    return hashed.hexdigest()


def get_real (path: str) -> tuple[bool, str|None, None|Exception]:
    """
    Return the canonical path of *path*, checking if realpath($path) == $path
    Returns (bool, realpath, None) or, if something's wrong, (False, None, raised exception).
    See: https://docs.python.org/3.8/library/os.path.html#os.path.realpath
    """
    try:
        real_path = realpath(path)
        is_real = (real_path == path)
        return is_real, real_path, None
    except OSError as err:
        pywarn.warn(PathWarning(f'{path} => {err}'))
        return False, None, err


def prune_regular (path: str) -> tuple[bool, str]:
    """
    Return the real path of $path if it's a regular file, or False.
    """
    is_real, real_path, err = get_real(path)
    if real_path:
        return check_regular(real_path) and real_path
    return False
"""
def prune_regular_m (path: str) -> str:
    '''
    Return the real path of $path if $path is a regular file,
    otherwise returns the empty string.
   '''
    ok, real_path = prune_regular(path)
    return real_path if ok else ""
"""

def prune_regular_s (paths: Sequence[str]) -> Iterator[str]:
    """Yields only regular $paths"""
    for path in paths:
        if real_path := prune_regular(path):
            yield real_path



def _find_irregular (paths: Sequence[str]):
    raise NotImplementedError('to be written')
    #XXX+TODO: write a filter to find broken links or not stat-able files only
