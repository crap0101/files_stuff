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

from collections.abc import Iterable
from itertools import chain
import os
import sys

# external modules
from py_warnings import pywarn

# Manage warnings
class FilelistWarning(pywarn.CustomWarning):
    pass
# set warnings to nothing, to be customize in the modules where it's imported
pywarn.set_filter(pywarn.IGNORE_WARNINGS, FilelistWarning)


def dcount (depth, start=0, this=True):
    """Returns an iterator counting from *start* to *depth*,
    yielding *this* at each step. *depth* can be infinity."""
    if depth == float('+inf'):
        def inner_count():
            while True:
                yield this
    else:
        def inner_count():
            level = start
            while level < depth:
                level += 1
                yield this
    return inner_count

def find (path, depth=float('+inf')):
    """Yields pathnames starting from *path* descending *depth* levels.
    Level 0 is the level of *path*.
    Raise ValueError for invalid *depth* values.
    Use the py_warnings module to tune the behaviour in case of
    paths related errors."""
    if depth < 0:
        raise ValueError("find: invalid *depth* value, must be >= 0")
    levels = [[path]]
    for _ in dcount(depth)():
        new_level = []
        for base in levels[-1]:
            try:
                with os.scandir(base) as dir_iter:
                    for item in dir_iter:
                        if item.is_dir(follow_symlinks=False):
                            new_level.append(item.path)
            except PermissionError as e:
                pywarn.warn(FilelistWarning('while scanning {} => {}'.format(base, e)))
        if not new_level:
            break
        levels.append(new_level)
    for dirname in chain(*levels):
        try:
            with os.scandir(dirname) as dir_iter:
                for item in dir_iter:
                    if item.is_file():
                        yield item.path
        except PermissionError as e:
                pywarn.warn(FilelistWarning('while scanning {} => {}'.format(dirname, e)))


if __name__ == '__main__':
    try:
        for p in find(sys.argv[1], float(sys.argv[2])):
            print(p)
    except IndexError:
        print('USAGE: {} PATH DEPTH'.format(sys.argv[0]))
