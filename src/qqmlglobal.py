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

import sys
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine

# The class QGuiApplication contains the loop where all events coming from the window system are managed.
# It also handles the application's initialization / termination. There can only be ONE QGuiApplication
# for any Qt GUI application (the number of windows is irrelevant here). This class must precede any other
# GUI object. As QGuiApplication also handles command line arguments, we may pass 'sys.argv' to it.
app = QGuiApplication(sys.argv)

# The class QQmlApplicationEngine allows to load an application from a single QML file.
# Here we are just instantiating the class by defining the object 'engine'.
engine = QQmlApplicationEngine()

# Set root context of engine
ctx = engine.rootContext()
