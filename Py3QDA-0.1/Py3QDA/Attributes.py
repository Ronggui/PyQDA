# -*- coding: utf-8 -*-

'''
Copyright (c) 2013 Colin Curtain

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Author: Colin Curtain (ccbogel)
https://github.com/ccbogel/PyQDA
'''

from PyQt5 import QtCore, QtWidgets, QtGui

#ADDIN
import datetime
from AddItem import Ui_Dialog_addItem
from ConfirmDelete import Ui_Dialog_confirmDelete
from AttributeType import Ui_Dialog_attrType
from Memo import Ui_Dialog_memo
#END ADDIN

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

class Ui_Dialog_Attributes(object):
    """ Attribute management. Create and delete attributes in the attributes table.
    """

    NAME_COLUMN = 0
    CLASS_COLUMN = 1
    MEMO_COLUMN = 2
    CASE_COLUMN = 3
    FILE_COLUMN = 4
    settings = None
    attributes = []

    def __init__(self, settings):
        self.settings = settings
        self.attributes = []

        cur = self.settings['conn'].cursor()
        cur.execute("select name, status, date, dateM, owner, memo, class from attributes")
        result = cur.fetchall()
        for row in result:
            self.attributes.append({'name':row[0], 'status':row[1], 'date':row[2], 'dateM':row[3], 'owner':row[4], 'memo':row[5], 'class':row[6],'case':'', 'file':''})

        cur.execute("select variable from caseAttr")
        result = cur.fetchall()
        for row in result:
            for att in self.attributes:
                if att['name'] == row[0]:
                    att['case'] = "Yes"
        cur.execute("select variable from fileAttr")
        result = cur.fetchall()
        for row in result:
            for att in self.attributes:
                if att['name'] == row[0]:
                    att['file'] = "Yes"

    def addAttribute(self):
        """ When add button pressed, open addItem dialog to get new attribute text.
        AddItem dialog checks for duplicate attribute name.
        New attribute is added to the model and database """

        Dialog_add = QtWidgets.QDialog()
        ui = Ui_Dialog_addItem(self.attributes)
        ui.setupUi(Dialog_add, "Attribute")
        Dialog_add.exec_()
        newText = ui.getNewItem()

        if newText is not None and newText !="":
            attrClass = ""
            Dialog_type = QtWidgets.QDialog()
            ui = Ui_Dialog_attrType()
            ui.setupUi(Dialog_type)
            ok = Dialog_type.exec_()
            if ok and ui.radioButton_char.isChecked():
                attrClass = "character"
            if ok and ui.radioButton_numeric.isChecked():
                attrClass = "numeric"

            # update attribute list and database
            item = {'name':newText.encode('raw_unicode_escape'), 'memo':"", 'owner':self.settings['codername'],
                    'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':"", 'status':1, 'class':attrClass}
            self.attributes.append(item)
            cur = self.settings['conn'].cursor()
            cur.execute("insert into attributes (name,status,date,dateM,owner,memo,class) values(?,?,?,?,?,?,?)"
                        ,(item['name'], item['status'], item['date'], item['dateM'], item['owner'],
                        item['memo'], item['class']))
            self.settings['conn'].commit()

            # update widget
            for attr in self.attributes:
                self.tableWidget.removeRow(0)

            self.fillTableWidget()

    def deleteAttribute(self):
        """ When delete button pressed, attribute is deleted from model and database """

        tableRowsToDelete = []  # for table widget ids
        namesToDelete = []

        for itemWidget in self.tableWidget.selectedItems():
            tableRowsToDelete.append(int(itemWidget.row()))
            namesToDelete.append(str(self.tableWidget.item(itemWidget.row(),0).text()))
            #print("X:"+ str(itemWidget.row()) + "  y:"+str(itemWidget.column()) +"  "+itemWidget.text() +"  id:"+str(self.tableWidget_codes.item(itemWidget.row(),3).text()))
        tableRowsToDelete.sort(reverse=True)

        if len(namesToDelete) == 0:
            return

        Dialog_confirmDelete = QtWidgets.QDialog()
        ui = Ui_Dialog_confirmDelete("\n".join(namesToDelete))
        ui.setupUi(Dialog_confirmDelete)
        ok = Dialog_confirmDelete.exec_()
        if ok:
            for r in tableRowsToDelete:
                self.tableWidget.removeRow(r)

            for name in namesToDelete:
                for attr in self.attributes:
                    if attr['name'] == name:
                        self.attributes.remove(attr)
                        cur = self.settings['conn'].cursor()
                        cur.execute("delete from attributes where name = ?", (name,))
                        cur.execute("delete from caseAttr where variable = ?", (name,))
                        cur.execute("delete from fileAttr where variable = ?", (name,))
                        self.settings['conn'].commit()

    def cellSelected(self):
        """ When the table widget memo cell is selected display the memo.
        Update memo text, or delete memo by clearing text.
        If a new memo also show in table widget by displaying YES in the memo column"""

        x = self.tableWidget.currentRow()
        y = self.tableWidget.currentColumn()

        if y == self.MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.attributes[x]['memo'])
            ui.setupUi(Dialog_memo, "Attribute memo " + self.attributes[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()

            if memo == "":
                self.tableWidget.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))

            # update attributes list and database
            self.attributes[x]['memo'] = str(memo).encode('raw_unicode_escape')
            cur = self.settings['conn'].cursor()
            cur.execute("update attributes set memo=? where name=?", (self.attributes[x]['memo'], self.attributes[x]['name']))
            self.settings['conn'].commit()

    def cellModified(self):
        """ If the attribute name has been changed in the table widget and update the database """
        NAME_COLUMN = 0
        x = self.tableWidget.currentRow()
        y = self.tableWidget.currentColumn()
        if y == NAME_COLUMN:
            newText = str(self.tableWidget.item(x, y).text()).strip().encode('raw_unicode_escape')

            # check that no other attribute has this text and this is is not empty
            update = True
            if newText == "":
                update = False
            for att in self.attributes:
                if att['name'] == newText:
                    update = False
            if update:
                #update attributes list and database
                cur = self.settings['conn'].cursor()
                cur.execute("update attributes set name=? where name=?", (newText, self.attributes[x]['name']))
                self.settings['conn'].commit()
                self.attributes[x]['name'] = newText
            else:  # put the original text in the cell
                self.tableWidget.item(x, y).setText(self.attributes[x]['name'])

    def fillTableWidget(self):
        """ Fill the table widget with attribute details """

        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Attribute","Class","Memo","Cases","Files"])
        for row, a in enumerate(self.attributes):
            self.tableWidget.insertRow(row)
            self.tableWidget.setItem(row, self.NAME_COLUMN, QtWidgets.QTableWidgetItem(a['name']))

            attrClass = a['class']
            if attrClass is not None and attrClass != "":
                item = QtWidgets.QTableWidgetItem(a['class'])
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidget.setItem(row, self.CLASS_COLUMN, item)

            mText = ""
            mtmp = a['memo']
            if mtmp is not None and mtmp != "":
                mText = "Yes"
            mitem = QtWidgets.QTableWidgetItem(mText)
            mitem.setFlags(mitem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(row, self.MEMO_COLUMN, mitem)
            citem = QtWidgets.QTableWidgetItem(a['case'])
            citem.setFlags(citem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(row, self.CASE_COLUMN, citem)
            fitem = QtWidgets.QTableWidgetItem(a['file'])
            fitem.setFlags(fitem.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(row, self.FILE_COLUMN, fitem)

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def setupUi(self, Dialog_Attributes):
        Dialog_Attributes.setObjectName(_fromUtf8("Dialog_Attributes"))
        Dialog_Attributes.resize(546, 569)
        self.pushButton_add = QtWidgets.QPushButton(Dialog_Attributes)
        self.pushButton_add.setGeometry(QtCore.QRect(10, 10, 98, 27))
        self.pushButton_add.setObjectName(_fromUtf8("pushButton_add"))
        self.pushButton_delete = QtWidgets.QPushButton(Dialog_Attributes)
        self.pushButton_delete.setGeometry(QtCore.QRect(120, 10, 98, 27))
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.tableWidget = QtWidgets.QTableWidget(Dialog_Attributes)
        self.tableWidget.setGeometry(QtCore.QRect(10, 50, 511, 511))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        #ADDIN
        self.fillTableWidget()
        self.pushButton_add.clicked.connect(self.addAttribute)
        self.pushButton_delete.clicked.connect(self.deleteAttribute)
        self.tableWidget.cellClicked.connect(self.cellSelected)
        self.tableWidget.cellChanged.connect(self.cellModified)
        #END ADDIN

        self.retranslateUi(Dialog_Attributes)
        QtCore.QMetaObject.connectSlotsByName(Dialog_Attributes)

    def retranslateUi(self, Dialog_Attributes):
        Dialog_Attributes.setWindowTitle(_translate("Dialog_Attributes", "Attributes", None))
        self.pushButton_add.setText(_translate("Dialog_Attributes", "Add", None))
        self.pushButton_delete.setText(_translate("Dialog_Attributes", "Delete", None))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_Attributes = QtWidgets.QDialog()
    ui = Ui_Dialog_Attributes()
    ui.setupUi(Dialog_Attributes)
    Dialog_Attributes.show()
    sys.exit(app.exec_())
