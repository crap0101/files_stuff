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

def dcount (depth):
    if depth == float('+inf'):
        def inner_count():
            while True:
                yield True
    else:
        def inner_count():
            #depth = depth
            level = 0
            while level < depth:
                level += 1
                yield True
    return inner_count

def find (path, depth=float('+inf')):
    """Yields pathnames starting from *path* descending *depth* levels.
    Level 0 is the level of *path*."""
    if depth < 0:
        raise ValueError("find: invalid *depth* value, must be >= 0")
    levels = [[path]]
    for _ in dcount(depth)():
        new_level = []
        for base in levels[-1]:
            with os.scandir(base) as dir_iter:
                for item in dir_iter:
                    if item.is_dir(follow_symlinks=False):
                        new_level.append(item.path)
        if not new_level:
            break
        levels.append(new_level)
    for dirname in chain(*levels):
        with os.scandir(dirname) as dir_iter:
            for item in dir_iter:
                if item.is_file():
                    yield item.path


if __name__ == '__main__':
    for p in find(sys.argv[1], float(sys.argv[2])):
        print(p)
