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
import sys
import logging

# Qt packages
from PyQt6.QtCore import QUrl
from PyQt6.QtQml import qmlRegisterType

# macOS-specific packages
from AppKit import NSBundle

# Local modules
from pyglobal import local_paths, running_in_a_bundle, app_dir_setup, log_setup
from qqmlglobal import app, engine, ctx
import querybuilder as QB
import queryhistory as QH

if __name__ == "__main__":
    # Checking if app dir exists one last time
    app_dir_setup()
    # Start logging system
    log_setup()

    if running_in_a_bundle():
        logging.info('(Running in a bundle) Initializing ... ')
    else:
        logging.info('(Running as a Python process) Initializing ... ')

    # Register QB and QH as types
    qmlRegisterType(QB.QueryBuilder, "QueryBuilder", 1, 0, "QueryBuilder")
    qmlRegisterType(QH.QueryHistory, "QueryHistory", 1, 0, "QueryHistory")

    # Instantiate object of class QueryBuilder
    qb = QB.QueryBuilder()
    qh = QH.QueryHistory()

    # Set property of root context
    ctx.setContextProperty("QueryBuilder", qb)
    ctx.setContextProperty("QueryHistory", qh)

    # The QQmlApplicationEngine object 'engine' is now responsible for loading the QML file
    qml_file_path = os.path.join(local_paths['dir_paths']['app_dir_path'], "QueryBuilder.qml")
    if running_in_a_bundle():
        engine.load(NSBundle.mainBundle().pathForResource_ofType_("QueryBuilder", "qml"))
    else:
        engine.load(QUrl.fromLocalFile(qml_file_path))

    # This ensures the correct termination of all Qt windows.
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
