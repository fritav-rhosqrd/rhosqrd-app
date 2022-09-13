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

import csv
import os
import json
import sys
from datetime import datetime

import toml
import requests
import logging
from time import process_time
from collections import OrderedDict

# Qt packages
from PyQt6.QtCore import QObject, pyqtSlot

# Local modules
from pyglobal import local_paths, app_dir_setup
from qqmlglobal import ctx
import qbtable as QBT
import queryhistory as QH

# from PyQt6.QtGui import QPixmap
# from icons import icon_collection
# import base64

app_dir_setup()


class QueryBuilder(QObject):
    """Postgres Query Builder for QML
    This class facilitates communication between PostgreSQL and QML.
    In this specific case, the database is fixed (i.e., FRITAV)."""

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        try:
            self.config = toml.load(local_paths['file_paths']['config_file_path'])
        except IOError:
            logging.error("No configuration file could be found. Exiting.")
            sys.exit(1)
        self.api_url = self.config["fritavapi"]["url"]
        # QueryBuilder Parameters
        self.colnames = ()
        self.querytabs = ['aimer']  # Default search table ; Will be changed
        self.querystring = {}
        self.range_ = ()
        self.queryresult = []
        # QtQuick TableModel
        self.tablemodel = []
        # Setters (Admittedly not optimal, needs refactoring)
        self.setColumnNames()

    @pyqtSlot(str, result=bool)
    def isEmpty(self, option: str):
        if option == "QBSTR":
            return not self.querystring
        elif option == "QRES":
            return not self.queryresult
        else:
            logging.warning(f"QueryBuilder.isEmpty: Unrecognized option \'{option}\'. Ignoring.")

    @pyqtSlot(result=list)
    def getTableNames(self):
        data = requests.get(self.api_url + "tabmeta")
        data = json.loads(data.text)
        tabnames = list(set([data[i]['table_name'] for i in range(len(data))]))
        return tabnames

    @pyqtSlot(result=list)
    def getLanguages(self):
        data = requests.get(self.api_url + "tabmeta")
        data = json.loads(data.text)
        langs = list(set([data[i]['table_lang'] for i in range(len(data))]))
        return langs

    @pyqtSlot()
    def setColumnNames(self):
        logging.debug("Getting column names...")
        start = process_time()
        data = requests.get(self.api_url + "get_columns")
        end = process_time()
        logging.debug(f"Column names retrieved in {round(end - start, 4)}ms.")
        data = json.loads(data.text)
        data = [data[i]['column_name'] for i in range(len(data))]
        if self.config["ignore"]["queryignore"]:
            data = [i for i in data if i not in self.config["ignore"]["queryignore"]]
        self.colnames = tuple(data)

    @pyqtSlot(result=list)
    def getColumnNames(self):
        return self.colnames

    @pyqtSlot(str, result=list)
    def populateComboBox(self, s: str):  # This is the cause of reduced performance ; Will be substituted anyway
        logging.info(f"Populating combo box \'{s}\'...")
        start = process_time()
        data = requests.get(self.api_url + f"aimer?select={s}",
                            headers={"Range-Unit": "items", "Range": "0-99"})
        end = process_time()
        data = json.loads(data.text)
        logging.info(f"Combo box populated in {round(end - start, 4)}ms.")
        end = process_time()
        data = [i[s] for i in data]
        data = list(OrderedDict.fromkeys(data))  # Deduplicate
        data.insert(0, "")
        return data

    @pyqtSlot(str, str)
    def setQueryTabs(self, s: str, action: str):
        if action == "ADD":
            self.querytabs.append(s)
            print(self.querytabs)
        elif action == "REMOVE":
            self.querytabs.remove(s)
            print(self.querytabs)
        else:
            logging.warning(f"QueryBuilder.setQueryTabs: Unrecognized option \'{action}\'. Ignoring.")

    @pyqtSlot(str, str)
    def setQbStrEntry(self, k: str, v: str):
        if v != "":
            self.querystring[k] = v
        else:
            self.querystring.pop(k, None)
            logging.debug(
                f"The class attribute \'qbstr\' with type {type(self.querystring)} has changed: {str(self.querystring)}")

    @pyqtSlot(result=str)
    def getQbStr(self):
        return json.dumps(self.querystring, ensure_ascii=False)

    @pyqtSlot()
    def queryDB(self):
        self.queryresult = []
        ign = self.config["ignore"]["tableignore"]
        q = {k: "fts." + v for (k, v) in self.querystring.items()}
        if self.range_:
            q.update({"comp_dates_nr": fr"ov.[{self.range_[0]},{self.range_[1]}]"})
        for t in self.querytabs:
            start = process_time()
            data = requests.get(self.api_url + t, params=q)
            end = process_time()
            res = json.loads(data.text)
            res = [tuple({k: v for (k, v) in r.items() if k not in ign}.values()) for r in res]
            logging.info(f"Request {data.request.url} handled successfully (Status Code {data.status_code}). "
                         f"{len(res)} rows retrieved in {round(end - start, 4)}ms.")
            # getQbStr & getTimeRange are not needed here ; Just ref the class variables and change the QH code
            QH.QueryHistory().writeToQueryHistory(self.getQbStr(), self.getTimeRange(), len(res), round(end - start, 4))
            self.queryresult += res

    @pyqtSlot(result=str)
    def getResLength(self):
        return "Row Count: " + str(len(self.queryresult))

    @pyqtSlot()
    def setTableModel(self):  # Bad code ; Needs refactoring
        if self.queryresult:
            self.tablemodel = QBT.QBTable(self.queryresult)
        else:
            self.tablemodel = []
            logging.debug('Empty TableView as the query returned no results.')
        ctx.setContextProperty("PyQModel", self.tablemodel)

    @pyqtSlot(int, int)
    def setTimeRange(self, i: int, j: int):
        self.range_ = (i, j)

    @pyqtSlot(result=str)
    def getTimeRange(self):
        return json.dumps(self.range_)

    @pyqtSlot(str)
    def exportQueryResultAsCSV(self, s: str):  # Headers missing
        csv_exp_dir_path = os.path.normpath(os.path.expanduser(self.config['export']['csvdest']))
        # The code below builds the subtree
        # rhosqrd
        #    └── exports
        #           └── csv
        # if not existing.
        if not os.path.isdir(csv_exp_dir_path):
            if not os.path.isdir(os.path.dirname(csv_exp_dir_path)):
                logging.info(f"Directory \'{os.path.dirname(csv_exp_dir_path)}\' not found. Creating.")
                os.mkdir(os.path.dirname(csv_exp_dir_path))
            logging.info(f"Directory \'{csv_exp_dir_path}\' not found. Creating.")
            os.mkdir(csv_exp_dir_path)
        csv_exp_file_name = s + "." + "csv"
        csv_exp_file_path = os.path.join(csv_exp_dir_path, csv_exp_file_name)
        with open(csv_exp_file_path, "w+") as f:
            writer = csv.writer(f)
            writer.writerow(self.colnames)
            writer.writerows(self.queryresult)
            logging.info(f"Query result exported as \'{csv_exp_file_path}\'.")

    @pyqtSlot(str)
    def exportQueryResultAsXML(self, s: str):  # Incomplete ; The current body was adapted from exportQueryResultAsCSV
        xml_exp_dir_path = os.path.normpath(os.path.expanduser(self.config['export']['xmldest']))
        # The code below builds the subtree
        # rhosqrd
        #    └── exports
        #           └── xml
        # if not existing.
        if not os.path.isdir(xml_exp_dir_path):
            if not os.path.isdir(os.path.dirname(xml_exp_dir_path)):
                logging.info(f"Directory \'{os.path.dirname(xml_exp_dir_path)}\' not found. Creating.")
                os.mkdir(os.path.dirname(xml_exp_dir_path))
            logging.info(f"Directory \'{xml_exp_dir_path}\' not found. Creating.")
            os.mkdir(xml_exp_dir_path)
        xml_exp_file_name = s + "." + "xml"
        xml_exp_file_path = os.path.join(xml_exp_dir_path, xml_exp_file_name)

    @pyqtSlot(str, str, bool)
    def logFromQML(self, msg: str, logtype: str, timestamp: bool):
        logtypes = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        if logtype not in logtypes:
            logging.error(f"(QueryBuilder.logFromQML) Unrecognized option {logtype}, "
                          f"expected one of {logtypes}. Logging only this message.")
        else:
            if logtype == 'DEBUG':
                if timestamp:
                    logging.debug(msg + " ; " + f"TIMESTAMP : {str(datetime.now().replace(microsecond=0))}")
                else:
                    logging.debug(msg)
            elif logtype == 'INFO':
                if timestamp:
                    logging.info(msg + " ; " + f"TIMESTAMP : {str(datetime.now().replace(microsecond=0))}")
                else:
                    logging.info(msg)
            elif logtype == 'WARNING':
                if timestamp:
                    logging.warning(msg + " ; " + f"TIMESTAMP : {str(datetime.now().replace(microsecond=0))}")
                else:
                    logging.warning(msg)
            elif logtype == 'ERROR':
                if timestamp:
                    logging.error(msg + " ; " + f"TIMESTAMP : {str(datetime.now().replace(microsecond=0))}")
                else:
                    logging.error(msg)
