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

import os
import re
import sys
import toml
import json
import logging
from datetime import datetime

# Qt packages
from PyQt6.QtCore import pyqtSlot, QObject

# Local modules
from pyglobal import local_paths, app_dir_setup

app_dir_setup()

class QueryHistory(QObject):
    try:
        __path = os.path.expanduser(toml.load(local_paths['file_paths']['config_file_path'])['queryhistory']['filepath'])
    except IOError:
        logging.error("The configuration file \'rhosqrd.conf\' couldn't be found (QueryHistory Error). Exiting.")
        sys.exit(1)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        # The code below builds the subtree
        # rhosqrd
        #    └── logs
        #         └── queryhistory.json
        # if not existing.
        if not os.path.isfile(self.__path):
            if not os.path.isdir(os.path.dirname(self.__path)):
                logging.info(f"File \'{os.path.isdir(os.path.dirname(self.__path))}\' not found. Creating.")
                os.mkdir(os.path.dirname(self.__path))
            with open(self.__path, "w") as f:
                logging.info(f"File \'{os.path.isfile(self.__path)}\' not found. Creating.")
                json.dump({"queryhistory": []}, f, indent=4)

    @pyqtSlot(str, str)
    def writeToQueryHistory(self, s: str, t: str, r: int, p: float):
        with open(self.__path, "r") as f:
            hist = json.load(f)
            hist['queryhistory'].append({'id': '{:04n}'.format(len(hist['queryhistory']) + 1),
                                         'timestamp': str(datetime.now().replace(microsecond=0)),
                                         'query': (lambda d: d.update({'comp_dates_nr': t}) or d
                                                   if json.loads(t) else d)(json.loads(s)),
                                         'rows': str(r),
                                         'perf': f'{p}ms'})
            logging.info(f"Query's metadata added to history file \'{self.__path}\'.")
        with open(self.__path, 'w') as f:
            json.dump(hist, f, indent=4, ensure_ascii=False)

    @pyqtSlot()
    def clearQueryHistory(self):
        with open(self.__path, 'w') as f:
            json.dump({"queryhistory": []}, f, indent=4)
            logging.info("Query history cleared.")

    @pyqtSlot(result=list)
    def getQueryHistory(self):
        with open(self.__path, "r") as f:
            hist = json.load(f)
            if hist['queryhistory']:
                l = [hist['queryhistory'][i]['query'] for i in range(len(hist['queryhistory']))]
                return [self.__format(i) for i in l[0:9]]
            else:
                return []

    def __format(self, j):
        s = json.dumps(j, separators=(" & ", " = "), ensure_ascii=False)
        s = re.sub("[{}\"]", "", s)
        return s