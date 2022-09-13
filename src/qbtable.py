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

from PyQt6.QtCore import pyqtSlot, Qt, QVariant, QAbstractTableModel

class QBTable(QAbstractTableModel):
    def __init__(self, data):
        super(QBTable, self).__init__()
        self._data = data

    @pyqtSlot(result=QVariant)
    def getTableModel(self):
        return []

    def headerData(self, section, orientation, role, result=str):
        if role == Qt.ItemDataRole.DisplayRole:
            return f"Test {section}"

    def data(self, index, role, result=QVariant):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index, result=int):
        return len(self._data)

    def columnCount(self, index, result=int):
        return len(self._data[0])

