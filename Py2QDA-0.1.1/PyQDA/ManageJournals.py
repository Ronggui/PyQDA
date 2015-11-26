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

from PyQt4 import QtCore, QtGui
#ADDIN
from Memo import Ui_Dialog_memo
from ConfirmDelete import Ui_Dialog_confirmDelete
import datetime
import os
#END ADDIN

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_Dialog_manageJournals(object):
    """    View, import, export, rename and delete journals.    """

    #ADDIN
    NAME_COLUMN = 0
    DATE_COLUMN = 1
    journals = []
    settings = None
    textDialog = None
    log = ""

    def __init__(self, settings):
        self.journals = []
        self.settings = settings
        self.log = ""
        cur = self.settings['conn'].cursor()
        cur.execute("select name, journal, date, dateM, owner, status from journal")
        result = cur.fetchall()
        for row in result:
            self.journals.append({'name':row[0], 'journal':row[1], 'date':row[2], 'dateM':row[3], 'owner':row[4], 'status':row[5]})

    def viewJournal(self):
        """ View and edit journal contents """

        x = self.tableWidget_journals.currentRow()
        Dialog_memo = QtGui.QDialog()
        ui = Ui_Dialog_memo(self.journals[x]['journal'])
        ui.setupUi(Dialog_memo, self.journals[x]['name'] +" "+ self.journals[x]['owner'] +", "+self.journals[x]['date'])
        Dialog_memo.exec_()
        # update model and database
        newText = ui.getMemo()
        newText = newText.decode('unicode-escape')
        try:
            pass
            newText = newText.decode("utf-8", "replace")
        except UnicodeDecodeError:
            print("unicode error")
        if newText != self.journals[x]['journal']:
            self.journals[x]['journal'] = newText
            cur = self.settings['conn'].cursor()
            cur.execute("update journal set journal=? where name=?", (newText, self.journals[x]['name']))
            self.settings['conn'].commit()

    def createJournal(self):
        """ Create a new journal by entering text into the dialog """

        Dialog_text = QtGui.QDialog()
        ui = Ui_Dialog_memo("")
        ui.setupUi(Dialog_text, "New journal")
        Dialog_text.exec_()
        newText = ui.getMemo()
        journalName = ui.getFilename()

        if journalName is None or journalName == "":
            QtGui.QMessageBox.warning(None, "Warning", "No journal name selected")
            return
        #check for non-unique filename
        if any(d['name'] == journalName for d in self.journals):
            QtGui.QMessageBox.warning(None, "Warning", str(journalName) + " is already in use")
            return

        # update database
        newJrnl = {'name':journalName, 'journal': newText, 'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':"", 'status':1}
        cur = self.settings['conn'].cursor()
        cur.execute("insert into journal(name,journal,owner,date,dateM,status) values(?,?,?,?,?,?)",
                    (newJrnl['name'],newJrnl['journal'],newJrnl['owner'],newJrnl['date'],newJrnl['dateM'],newJrnl['status']))
        self.settings['conn'].commit()
        self.log += "Journal " + newJrnl['name'] + " created\n"

        # clear and refill table widget
        for r in self.journals:
            self.tableWidget_journals.removeRow(0)
        self.journals.append(newJrnl)
        for row, itm in enumerate(self.journals):
            self.tableWidget_journals.insertRow(row)
            item = QtGui.QTableWidgetItem(itm['name'])
            self.tableWidget_journals.setItem(row, self.NAME_COLUMN, item)
            item = QtGui.QTableWidgetItem(itm['date'])
            self.tableWidget_journals.setItem(row, self.DATE_COLUMN, item)
        self.tableWidget_journals.resizeColumnsToContents()
        self.tableWidget_journals.resizeRowsToContents()

    def exportJournal(self):
        """ Export journal to a plain text file, filename will have .txt ending """

        x = self.tableWidget_journals.currentRow()
        fileName = self.journals[x]['name']
        fileName += ".txt"
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(None, "Select directory to save file", os.getenv('HOME'), options)
        if directory:
            fileName = directory + "/" + fileName
            print ("Exporting:  to " + fileName)
            data = self.journals[x]['journal']
            f = open(fileName, 'w')
            f.write(data)
            f.close()
            self.log += "Journal " + fileName + " exported"
            QtGui.QMessageBox.information(None, "Journal Export", str(fileName)+" exported\n")

    def deleteJournal(self):
        """ Delete journal from database and update model and widget """

        x = self.tableWidget_journals.currentRow()
        journalName = self.journals[x]['name']
        #print(("Delete row: " + str(x)))
        Dialog_confirmDelete = QtGui.QDialog()
        ui = Ui_Dialog_confirmDelete(self.journals[x]['name'])
        ui.setupUi(Dialog_confirmDelete)
        ok = Dialog_confirmDelete.exec_()

        if ok:
            cur = self.settings['conn'].cursor()
            cur.execute("delete from journal where name = ?", [journalName])
            self.settings['conn'].commit()
            for item in self.journals:
                if item['name'] == journalName:
                    self.journals.remove(item)
            self.tableWidget_journals.removeRow(x)
            self.log += "Journal " + journalName + " deleted\n"

    def cellModified(self):
        """ If the journal name has been changed in the table widget update the database """

        x = self.tableWidget_journals.currentRow()
        y = self.tableWidget_journals.currentColumn()
        if y == self.NAME_COLUMN:
            newName = str(self.tableWidget_journals.item(x, y).text()).strip().encode('raw_unicode_escape')
            # check that no other journal has this name and it is not empty
            update = True
            if newName == "":
                update = False
            for c in self.journals:
                if c['name'] == newName:
                    update = False
            if update:
                # update source list and database
                cur = self.settings['conn'].cursor()
                cur.execute("update journal set name=? where name=?", (newName, self.journals[x]['name']))
                self.settings['conn'].commit()
                self.journals[x]['name'] = newName
            else:  # put the original text in the cell
                self.tableWidget_journals.item(x, y).setText(self.journals[x]['name'])

    def getLog(self):
        """ Get details of file movments """
        return self.log

    # END ADDIN

    def setupUi(self, Dialog_manageJournals):
        Dialog_manageJournals.setObjectName(_fromUtf8("Dialog_manageJournals"))
        Dialog_manageJournals.resize(519, 410)
        self.tableWidget_journals = QtGui.QTableWidget(Dialog_manageJournals)
        self.tableWidget_journals.setGeometry(QtCore.QRect(10, 50, 491, 341))
        self.tableWidget_journals.setObjectName(_fromUtf8("tableWidget_journals"))
        self.tableWidget_journals.setColumnCount(0)
        self.tableWidget_journals.setRowCount(0)
        self.pushButton_view = QtGui.QPushButton(Dialog_manageJournals)
        self.pushButton_view.setGeometry(QtCore.QRect(10, 10, 81, 27))
        self.pushButton_view.setObjectName(_fromUtf8("pushButton_view"))
        self.pushButton_delete = QtGui.QPushButton(Dialog_manageJournals)
        self.pushButton_delete.setGeometry(QtCore.QRect(330, 10, 81, 27))
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.pushButton_create = QtGui.QPushButton(Dialog_manageJournals)
        self.pushButton_create.setGeometry(QtCore.QRect(100, 10, 81, 27))
        self.pushButton_create.setObjectName(_fromUtf8("pushButton_create"))
        self.pushButton_export = QtGui.QPushButton(Dialog_manageJournals)
        self.pushButton_export.setGeometry(QtCore.QRect(190, 10, 81, 27))
        self.pushButton_export.setObjectName(_fromUtf8("pushButton_export"))

        self.retranslateUi(Dialog_manageJournals)
        QtCore.QMetaObject.connectSlotsByName(Dialog_manageJournals)

        #ADDIN
        self.tableWidget_journals.setColumnCount(2)  #name id
        self.tableWidget_journals.setHorizontalHeaderLabels(["Name","Date"])
        self.tableWidget_journals.setSelectionMode( QtGui.QAbstractItemView.SingleSelection )

        for row, details in enumerate(self.journals):
            self.tableWidget_journals.insertRow(row)
            self.tableWidget_journals.setItem(row, self.NAME_COLUMN, QtGui.QTableWidgetItem(details['name']))
            item = QtGui.QTableWidgetItem(details['date'])
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget_journals.setItem(row, self.DATE_COLUMN, item)

        self.tableWidget_journals.verticalHeader().setVisible(False)
        self.tableWidget_journals.resizeColumnsToContents()
        self.tableWidget_journals.resizeRowsToContents()

        self.tableWidget_journals.itemChanged.connect(self.cellModified)
        self.pushButton_view.clicked.connect(self.viewJournal)
        self.pushButton_create.clicked.connect(self.createJournal)
        self.pushButton_export.clicked.connect(self.exportJournal)
        self.pushButton_delete.clicked.connect(self.deleteJournal)

        #END ADDIN


    def retranslateUi(self, Dialog_manageJournals):
        Dialog_manageJournals.setWindowTitle(_translate("Dialog_manageJournals", "Journals", None))
        self.pushButton_view.setText(_translate("Dialog_manageJournals", "View", None))
        self.pushButton_delete.setText(_translate("Dialog_manageJournals", "Delete", None))
        self.pushButton_create.setText(_translate("Dialog_manageJournals", "Create", None))
        self.pushButton_export.setText(_translate("Dialog_manageJournals", "Export", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog_manageJournals = QtGui.QDialog()
    ui = Ui_Dialog_manageJournals()
    ui.setupUi(Dialog_manageJournals)
    Dialog_manageJournals.show()
    sys.exit(app.exec_())

