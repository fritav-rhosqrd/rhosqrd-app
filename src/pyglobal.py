# RhoSqrd is a Python + Qt frontend to the FRITAV database
# Copyright (C) 2022  Eduard S. Lukasiewicz, Sascha Gaglia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import sys
import shutil
from AppKit import NSBundle

local_paths = \
    {
        "dir_paths": {
            "app_dir_path": (sys._MEIPASS
                             if getattr(sys, "Frozen", False)
                             else os.path.dirname(os.path.abspath(__file__)))
        },
        "file_paths": {
            "config_file_path": os.path.expanduser(r"~/Library/Application Support/rhosqrd/rhosqrd.conf"),
            "log_file_path": os.path.expanduser(r"~/Library/Application Support/rhosqrd/logs/rhosqrd.log"),
            "queryhistory_file_path": os.path.expanduser(r"~/Library/Application Support/rhosqrd/logs/queryhistory.json")
        }
    }

def running_in_a_bundle():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

def app_dir_setup():
    cfp = local_paths['file_paths']['config_file_path']
    lfp = local_paths['file_paths']['log_file_path']
    if not os.path.isfile(cfp):
        if not os.path.isdir(os.path.dirname(cfp)):
            os.mkdir(os.path.dirname(cfp))
        shutil.copy(NSBundle.mainBundle().pathForResource_ofType_("rhosqrd", "conf"), os.path.dirname(cfp))
    if not os.path.isfile(lfp):
        if not os.path.isdir(os.path.dirname(lfp)):
            os.mkdir(os.path.dirname(lfp))
        open(lfp, 'a').close()

def log_setup():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter('%(levelname)s: %(message)s')

    filelog = logging.FileHandler(local_paths['file_paths']['log_file_path'])
    filelog.setLevel(logging.INFO)
    filelog.setFormatter(formatter)
    root.addHandler(filelog)

    streamlog = logging.StreamHandler(sys.stdout)
    streamlog.setLevel(logging.INFO)
    streamlog.setFormatter(formatter)
    root.addHandler(streamlog)

