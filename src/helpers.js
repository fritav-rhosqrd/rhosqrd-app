// RhoSqrd is a Python + Qt frontend to the FRITAV database
// Copyright (C) 2022  Eduard S. Lukasiewicz, Sascha Gaglia
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

function fillCombosFromHistory (s, labelrep, cboxrep, replength) {
    let u = s.replace(/\s+/g,'').split('&');
    let v = [];
    for (let i = 0; i < u.length; i++) {
        v.push({
            key: u[i].split('=')[0],
            value: u[i].split('=')[1]
        })
    }
    for (let j = 0; j < v.length; j++) {
        for (let k = 0; k < replength; k++) {
            if (v[j].key === labelrep.itemAt(k).text) {
                cboxrep.itemAt(k).editText = v[j].value;
            }
        }
    }
}