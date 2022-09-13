// RhoSqrd is a Python + Qt frontend to the FRITAV database
// Copyright (C) 2022  Eduard S. Lukasiewicz, Sascha Gaglia

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import QtQuick
import QtQuick.Window
import QtQuick.Controls
import QtQuick.Layouts
import QueryBuilder 1.0
import QueryHistory 1.0
import "helpers.js" as Helpers


ApplicationWindow {
    id: qbpage
    width: 1280
    height: 800
    visible: true
    QueryBuilder {
        id: qb
    }
    QueryHistory {
        id: qh
    }
    Component.onCompleted: qb.logFromQML('START OF SESSION', 'INFO', true)
    MenuBar {
        id: menubarqb
        width: parent.width
        Menu {
            id: fileqb
            title: qsTr("File")
            MenuItem {
                text: qsTr("Export Query Result as CSV")
                onClicked: {
                    csvexportdialog.open()
                }
                Dialog {
                    id: csvexportdialog
                    title: qsTr("Export to CSV")
                    parent: Overlay.overlay
                    anchors.centerIn: Overlay.overlay
                    width: 280
                    height: 120
                    modal: true
                    closePolicy: Popup.CloseOnPressOutside
                    ColumnLayout {
                        id: csvexportdialogcl
                        anchors.fill: parent
                        TextField {
                            id: csvexportfilename
                            Layout.alignment: Qt.AlignHCenter
                            implicitWidth: csvexportdialog.width*0.95
                            selectByMouse: true
                            placeholderText: "filename"
                        }
                        Text {
                            id: emptyfilenamewarning
                            Layout.alignment: Qt.AlignHCenter
                            text: qsTr("ERROR: You must specify a filename.")
                            color: "#FF3030"
                            visible: false
                        }
                        Text {
                            id: csvexportsuccess
                            Layout.alignment: Qt.AlignHCenter
                            text: qsTr("Your CSV export was successful.")
                            color: "#3ECD3E"
                            visible: false
                        }
                        RowLayout {
                            Layout.alignment: Qt.AlignBottom | Qt.AlignHCenter
                            Button {
                                text: qsTr("Cancel")
                                onClicked: {
                                    csvexportdialog.close()
                                }
                            }
                            Button {
                                text: qsTr("Export")
                                onClicked: {
                                    if (csvexportfilename.text === ""){
                                        emptyfilenamewarning.visible = true
                                    }
                                    else {
                                        emptyfilenamewarning.visible = false
                                        qb.exportQueryResultAsCSV(csvexportfilename.text)
                                        csvexportsuccess.visible = true
                                    }
                                }
                            }
                        }
                    }
                }
            }
            MenuSeparator {}
            MenuItem {
                text: qsTr("Exit")
                onClicked: {
                    qbpage.close()
                }
            }
        }
        Menu {
            id: historyqb
            title: qsTr("Query History")
            MenuItem {
                id: showallhistory
                text: qsTr("Show All Query History")
            }
            MenuSeparator {
                visible: (rephistory.count === 0) ? false : true
            }
            Repeater {
                id: rephistory
                model: qh.getQueryHistory()
                MenuItem {
                    text: modelData
                    onClicked: {
                        Helpers.fillCombosFromHistory(modelData, replabel, repcbox, qb.getColumnNames().length)
                    }
                }
            }
            MenuSeparator {}
            MenuItem {
                id: clearhistory
                text: qsTr("Clear Query History")
                onClicked: {
                    clearhistorydialog.open()
                }
                Dialog {
                    id: clearhistorydialog
                    parent: Overlay.overlay
                    anchors.centerIn: Overlay.overlay
                    width: 260
                    height: 60
                    modal: true
                    ColumnLayout {
                        anchors.fill: parent
                        Text {
                            Layout.alignment: Qt.AlignHCenter
                            Layout.columnSpan: 2
                            text: qsTr("Are you sure?")
                        }
                        RowLayout {
                            Layout.alignment: Qt.AlignHCenter
                            spacing: 1
                            Button {
                                id: clearhistorycancelbutton
                                text: qsTr("Cancel")
                                onClicked: {
                                    clearhistorydialog.close()
                                }
                            }
                            Button {
                                id: clearhistorybutton
                                text: qsTr("Clear Query History")
                                onClicked: {
                                    qh.clearQueryHistory()
                                    rephistory.model = qh.getQueryHistory()
                                    clearhistorydialog.close()
                                }
                            }
                        }
                    }
                }
            }
        }

        Menu {
            id: help
            title: qsTr("Help")
            MenuItem {
                text: qsTr("Syntax Cheatsheet")
            }
            MenuItem {
                text: qsTr("Documentation")
            }
        }
    }
    /* This is the top abstract level of the QB interface.
    A RowLayout is used in order to put the query string
    builder next to the table visualization tool. */
    ColumnLayout {
        id: toplayout
        anchors.fill: parent
        anchors.margins: 20
        RowLayout {
            id: splitlayout
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 20
            // This is the top abstract level of the query string builder
            ColumnLayout {
                id: splitleft
                spacing: 20
                // This contains all search fields.
                Flickable {
                    id: flickqbgl
                    Layout.alignment: Qt.AlignHCenter
                    flickableDirection: Flickable.VerticalFlick
                    contentHeight: qbgl.height
                    contentWidth: qbgl.width
                    height: 440
                    width: 320
                    clip: true
                    GridLayout {
                        id: qbgl
                        width: parent.width
                        columns: 2
                        rowSpacing: 5
                        columnSpacing: 5
                        Text{
                            id: timesliderlabel
                            text: "range"
                        }
                        RangeSlider {
                            id: timeslider
                            Layout.alignment: Qt.AlignHCenter
                            from: 1200
                            to: 1400
                            stepSize: 1.0
                            first.value: 1200
                            second.value: 1400
                            first.handle: Rectangle {
                                x: timeslider.leftPadding + timeslider.first.visualPosition * (timeslider.availableWidth - width)
                                y: timeslider.topPadding + timeslider.availableHeight / 2 - height / 2
                                implicitWidth: 16
                                implicitHeight: 16
                                radius: 8
                                color: timeslider.first.pressed ? "#f0f0f0" : "#f6f6f6"
                                border.color: "#bdbebf"
                                ToolTip {
                                    parent: timeslider.first.handle
                                    visible: timeslider.first.pressed
                                    text: timeslider.first.value.toFixed(0)
                                }
                                //Text {
                                //    id: firsthandletext
                                //    text: parseInt(timeslider.first.value)
                                //    anchors.top: parent.bottom
                                //}
                            }
                            second.handle: Rectangle {
                                x: timeslider.leftPadding + timeslider.second.visualPosition * (timeslider.availableWidth - width)
                                y: timeslider.topPadding + timeslider.availableHeight / 2 - height / 2
                                implicitWidth: 16
                                implicitHeight: 16
                                radius: 8
                                color: timeslider.second.pressed ? "#f0f0f0" : "#f6f6f6"
                                border.color: "#bdbebf"
                                ToolTip {
                                    parent: timeslider.second.handle
                                    visible: timeslider.second.pressed
                                    text: timeslider.second.value.toFixed(0)
                                }
                                //Text {
                                //    id: secondhandletext
                                //    text: parseInt(timeslider.second.value)
                                //    anchors.top: parent.bottom
                                //}
                            }
                            first.onMoved: qb.setTimeRange(parseInt(first.value), parseInt(second.value))
                            second.onMoved: qb.setTimeRange(parseInt(first.value), parseInt(second.value))
                        }
                        Rectangle {
                            Layout.columnSpan: 2
                            Layout.fillWidth: true
                            height: 1
                            color: "lightgrey"
                        }
                        Text{
                            id: langlabel
                            text: "lang"
                        }
                        // Checkable Language CBox
                        ComboBox {
                            id: langcbox
                            implicitWidth: 180
                            displayText: ""
                            model: qb.getLanguages()
                            delegate: Rectangle {
                                id: langcboxdel
                                width: parent.width
                                height: langcbox.height
                                Row {
                                    anchors.fill: parent
                                    leftPadding: 5
                                    Label {
                                        id: langcboxlabel
                                        text: modelData
                                        width: parent.width - langcboxcheck.width
                                        height: parent.height
                                        verticalAlignment: Qt.AlignVCenter
                                        horizontalAlignment: Qt.AlignLeft
                                    }
                                    CheckBox {
                                        id: langcboxcheck
                                        height: parent.height
                                        width: height
                                        onClicked: {
                                            if (checkState === Qt.Checked){
                                                console.log(langcbox.valueAt(index))
                                            } else {
                                                ////
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        Text{
                            id: lemmamodlabel
                            text: "lemma_mod"
                        }
                        // Checkable Lemma (Mod.) CBox
                        ComboBox {
                            id: lemmamodcbox
                            implicitWidth: 180
                            displayText: ""
                            model: qb.getTableNames()
                            delegate: Rectangle {
                                id: lemmamodcboxdel
                                width: parent.width
                                height: lemmamodcbox.height
                                Row {
                                    anchors.fill: parent
                                    leftPadding: 5
                                    Label {
                                        id: lemmamodcboxlabel
                                        text: modelData
                                        width: parent.width - lemmamodcboxcheck.width
                                        height: parent.height
                                        verticalAlignment: Qt.AlignVCenter
                                        horizontalAlignment: Qt.AlignLeft
                                    }
                                    CheckBox {
                                        id: lemmamodcboxcheck
                                        height: parent.height
                                        width: height
                                        checkState: lemmamodcbox.valueAt(index) === 'aimer' ? Qt.Checked : Qt.Unchecked
                                        onClicked: {
                                            if (checkState === Qt.Checked){
                                                qb.setQueryTabs(lemmamodcbox.valueAt(index), "ADD")
                                            } else {
                                                qb.setQueryTabs(lemmamodcbox.valueAt(index), "REMOVE")
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        Rectangle {
                            Layout.columnSpan: 2
                            Layout.fillWidth: true
                            height: 1
                            color: "lightgrey"
                        }
                        Repeater {
                            id: replabel
                            model: qb.getColumnNames()
                            Text {
                                Layout.row: index + 5
                                Layout.column: 0
                                text: modelData
                            }
                        }
                        Repeater {
                            id: repcbox
                            model: qb.getColumnNames()
                            ComboBox {
                                Layout.row: index + 5
                                Layout.column: 1
                                implicitWidth: 180
                                currentIndex: 0
                                editable: true
                                model: qb.populateComboBox(modelData)
                                onCurrentTextChanged: {
                                    qb.setQbStrEntry(modelData, currentText)
                                }
                                onEditTextChanged: {
                                    qb.setQbStrEntry(modelData, editText)
                                }
                            }
                        }
                    }
                    ScrollBar.vertical: ScrollBar {}
                }
                /* Here begins the area for free text search.
                The first element is a toggle button which
                "activates" free text search. At the time,
                free text search is however not possible. */
                RowLayout {
                    CheckBox {
                        id: freetextcheck
                        checked: false
                        text: qsTr("Enable Free Text Search")
                        onClicked: {
                            if (checkState === Qt.Checked){
                                freetext.enabled = true
                            } else {
                                freetext.enabled = false
                            }
                        }
                    }
    //                Image {
    //                    source: qb.getIconPath("info_icon_48x48")
    //                    Layout.preferredWidth: 20
    //                    Layout.preferredHeight: 20
    //                }
                }
                TextArea {
                    id: freetext
                    enabled: false
                    background: Rectangle {
                        implicitHeight: 100
                        implicitWidth: splitleft.width
                    }
                    placeholderText: qsTr("Insert your string here...")
                }
                /* End of free text search field.
                Here we have the Reset Fields & Start Query buttons. */
                RowLayout {
                    id: buttonlayout
                    spacing: 1
                    Layout.alignment: Qt.AlignHCenter
                    Button {
                        id: reset
                        text: "Reset Fields"
                        onClicked: {
                            resetRepCBoxContent(repcbox, qb.getColumnNames().length)
                            timeslider.first.value = timeslider.valueAt(0)
                            timeslider.second.value = timeslider.valueAt(1.0)
                        }
                        function resetRepCBoxContent(rep, replength) {
                            for (var i = 0; i < replength; i++) {
                                rep.itemAt(i).editText = ''
                                rep.itemAt(i).currentIndex = 0
                            }
                        }
                    }
                    Button {
                        id: startquery
                        text: "Start Query"
                        onClicked: {
                            if (qb.isEmpty("QBSTR")){
                                emptyqueryerror.visible = true
                            }
                            else {
                                emptyqueryerror.visible = false
                                qb.queryDB()
                                rephistory.model = qh.getQueryHistory()
                                rowcount.text = qb.getResLength()
                                qb.setTableModel()
                                qbtabtxtld.active = false
                                qbtabld.active = true
                            }
                        }
                    }
                }
                Text {
                    id: emptyqueryerror
                    Layout.alignment: Qt.AlignHCenter
                    text: qsTr("ERROR: Your query is empty!")
                    color: "#FF2929"
                    visible: false
                }
                /* End of page. */
            }
            // This is the top abstract level of the query visualization tool
            ColumnLayout {
                id: splitright
                Layout.topMargin: 20
                Item {
                    id: qbtabarea
                    Layout.fillHeight: true
                    Layout.fillWidth: true
                    Loader {
                        id:qbtabtxtld
                        anchors.centerIn: parent
                        sourceComponent: qbtabtxtcomp
                        active: true
                    }
                    Component {
                        id: qbtabtxtcomp
                        Text {
                            id: qbtabtxt
                            text: "The result of your query will appear here"
                            anchors.centerIn: parent
                            color: "gray"
                            font.pointSize: 22
                        }
                    }
                    Loader {
                        id: qbtabld
                        anchors.fill: parent
                        sourceComponent: qbtabcomp
                        active: false
                    }
                    BusyIndicator {
                        id: qbtabusy
                        anchors.centerIn: parent
                        running: qbtabld.status == Loader.Loading
                    }
                    Component {
                        id: qbtabcomp
                        Item {
                            anchors.fill: parent
                            HorizontalHeaderView {
                                id:qbtabheaderview
                                clip: true
                                syncView: qbtab
                                model: qb.getColumnNames() // comp_dates & manuscr_dates need to be included
                                delegate: Rectangle {
                                    implicitWidth: 160
                                    implicitHeight: 30
                                    color: "#75ADECFF"
                                    border.width: 1
                                    border.color: "#FFFFFF"
                                    Text {
                                        text: modelData
                                        width: parent.width*0.85
                                        elide: Text.ElideRight
                                        anchors.centerIn: parent
                                    }
                                }
                            }
                            TableView {
                                id: qbtab
                                anchors.top: qbtabheaderview.bottom
                                width: parent.width
                                height: parent.height - qbtabheaderview.implicitHeight
                                clip: true
                                model: PyQModel
                                delegate: Rectangle {
                                    implicitWidth: 160
                                    implicitHeight: 30
                                    color: model.row % 2 == 0 ? "#FAFAFA" : "#F0F0F0"
                                    border.width: 1
                                    border.color: "#FFFFFF"
                                    Text {
                                        text: display
                                        width: parent.width*0.85
                                        elide: Text.ElideRight
                                        anchors.centerIn: parent

                                    }
                                    TextEdit {
                                        id: boilerplatetextedit
                                        visible: false
                                    }
                                    MouseArea {
                                        anchors.fill: parent
                                        cursorShape: Qt.PointingHandCursor
                                        onClicked: {
                                            boilerplatetextedit.text = display
                                            boilerplatetextedit.selectAll()
                                            boilerplatetextedit.copy()
                                        }
                                        hoverEnabled: true
                                        ToolTip {
                                            id: tablecelltooltip
                                            delay: 1000
                                            visible: parent.containsMouse
                                            text: qsTr(display)
                                            background: Rectangle {
                                                color: "#fbef8a"
                                                border.color: "#000000"
                                            }
                                        }
                                    }
                                }
                                ScrollBar.vertical: ScrollBar { }
                                ScrollBar.horizontal: ScrollBar { }
                            }
                        }
                    }
                }
            }
        }
        Rectangle {
            Layout.fillWidth: true
            height: 25
            radius: 5
            border.color: "lightgray"
            color: "transparent"
            RowLayout {
                anchors.fill: parent
                Text {
                    id: rowcount
                    Layout.alignment: Qt.AlignRight
                    Layout.leftMargin: 10
                    Layout.rightMargin: 10
                    text: ""
                }
            }
        }
    }
    onClosing: {
        qb.logFromQML('END OF SESSION', 'INFO', true)
    }
}

