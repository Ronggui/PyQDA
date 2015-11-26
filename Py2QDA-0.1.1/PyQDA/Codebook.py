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
from CodeColors import CodeColors
import os
#ENDADDIN

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


class Ui_Dialog_codebook(object):
    """ Shows a codebook of codes and memos """

    #ADDIN
    settings = None
    codes = []
    codeColors = CodeColors()
    log = ""

    # descends are not used yet
    orderByCodeAscendSQL = "select freecode.name, codecat.name, freecode.memo, freecode.id, freecode.color from freecode\
         left outer join treecode on treecode.cid=freecode.id left outer join codecat on treecode.catid=codecat.catid\
          group by freecode.name order by upper(freecode.name)"

    orderByCodeDescSQL = "select freecode.name, codecat.name, freecode.memo, freecode.id, freecode.color from freecode\
         left outer join treecode on treecode.cid=freecode.id left outer join codecat on treecode.catid=codecat.catid\
          group by freecode.name order by upper(freecode.name) desc"

    orderByCategoryAscendSQL = "select freecode.name, codecat.name, freecode.memo, freecode.id, freecode.color from freecode\
         left outer join treecode on treecode.cid=freecode.id left outer join codecat on treecode.catid=codecat.catid\
          group by freecode.name order by upper(codecat.name), upper(freecode.name)"

    orderByCategoryDescSQL = "select freecode.name, codecat.name, freecode.memo, freecode.id, freecode.color from freecode\
         left outer join treecode on treecode.cid=freecode.id left outer join codecat on treecode.catid=codecat.catid\
          group by freecode.name order by upper(codecat.name), upper(freecode.name) desc"

    def __init__(self, settings):
        self.settings = settings
        self.codes = []
        self.log = ""

        #set up the codes list
        cur = self.settings['conn'].cursor()
        cur.execute(self.orderByCodeAscendSQL)
        result = cur.fetchall()
        for row in result:
            self.codes.append({'name':row[0], 'category':row[1], 'memo':row[2],
                 'id':row[3], 'color':row[4]})

    def sort(self):
        """ Sort the table in ascending order by code or by category """

        tableSQL = self.orderByCodeAscendSQL
        sortByField = self.pushButton_sort.text()

        if sortByField == "Sorted by category":
            sortByField == ""
            self.pushButton_sort.setText("Sorted by code")
            tableSQL = self.orderByCodeAscendSQL

        if sortByField == "Sorted by code":
            self.pushButton_sort.setText("Sorted by category")
            tableSQL = self.orderByCategoryAscendSQL

        for row in self.codes:
            self.tableWidget.removeRow(0)

        self.codes = []
        cur = self.settings['conn'].cursor()
        cur.execute(tableSQL)
        result = cur.fetchall()
        for row in result:
            self.codes.append({'name':row[0], 'category':row[1], 'memo':row[2], 'id':row[3], 'color':row[4]})
        self.fillTableWidget()

    def export(self):
        """ Export file to a plain text file, filename will have .txt ending """

        fileName = self.settings['projectName'] + "_codebook.txt"

        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(None,"Select directory to save file",os.getenv('HOME'), options)
        if directory:
            fileName = directory + "/" + fileName
            #print ("Exporting:  to " + fileName)

            filedata = ""
            for code in self.codes:
                category = code['category']
                if category is None:
                    category = ""
                memo = code['memo']
                if memo is None: memo = ""
                filedata += "Code: "+ code['name']+", Category:"+ category + "\r\n" + memo + "\r\n"

            f = open(fileName, 'w')
            f.write(filedata)
            f.close()
            self.log += "Codebook: " + fileName + " exported\n"
            QtGui.QMessageBox.information(None,"File Export",str(fileName)+" exported")

    def fillTableWidget(self):
        """ Fill the table widget with the model details """

        CODE_COLUMN = 0
        CAT_COLUMN = 1
        MEMO_COLUMN = 2
        ID_COLUMN = 3

        #code, cat, memo,id
        self.tableWidget.setColumnCount(4)
        self.tableWidget.setHorizontalHeaderLabels(["Code", "Category", "Memo", "id"])
        for row, code in enumerate(self.codes):
            self.tableWidget.insertRow(row)
            #self.tableWidget.setItem(row, CODE_COLUMN, QtGui.QTableWidgetItem(code['name']))

            colnametmp = code['color']
            if colnametmp is None: colnametmp = ""
            codeItem = QtGui.QTableWidgetItem(code['name'])
            codeItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            colorHex = self.codeColors.getHexFromName(colnametmp)
            if colorHex != "":
                codeItem.setBackground(QtGui.QBrush(QtGui.QColor(colorHex)))
            self.tableWidget.setItem(row, CODE_COLUMN, codeItem)

            category = code['category']
            if category is None: category = ""
            catItem = QtGui.QTableWidgetItem(category)
            catItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(row, CAT_COLUMN, catItem)
            memo = code['memo']
            if memo is None: memo = ""
            memoItem = QtGui.QTableWidgetItem(str(memo))
            memoItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(row, MEMO_COLUMN, memoItem)
            id_ = code['id']
            if id_ is None:
                id_ = ""
            self.tableWidget.setItem(row, ID_COLUMN, QtGui.QTableWidgetItem(str(id_)))

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        if not self.settings['showIDs']:
            self.tableWidget.hideColumn(ID_COLUMN)

    def getLog(self):
        """ Get details of file movments """

        return self.log

    # END ADD IN

    def setupUi(self, Dialog_codebook):
        Dialog_codebook.setObjectName(_fromUtf8("Dialog_codebook"))
        Dialog_codebook.setWindowModality(QtCore.Qt.ApplicationModal)
        Dialog_codebook.resize(696, 494)
        self.gridLayout = QtGui.QGridLayout(Dialog_codebook)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.buttonBox = QtGui.QDialogButtonBox(Dialog_codebook)
        #self.buttonBox.setGeometry(QtCore.QRect(568, 10, 101, 27))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 0, 2)
        self.pushButton_export = QtGui.QPushButton(Dialog_codebook)
        #self.pushButton_export.setGeometry(QtCore.QRect(450, 10, 121, 27))
        self.pushButton_export.setObjectName(_fromUtf8("pushButton_export"))
        self.gridLayout.addWidget(self.pushButton_export, 0, 1)
        self.pushButton_sort = QtGui.QPushButton(Dialog_codebook)
        #self.pushButton_sort.setGeometry(QtCore.QRect(20, 10, 141, 27))
        self.pushButton_sort.setObjectName(_fromUtf8("pushButton_sort"))
        self.gridLayout.addWidget(self.pushButton_sort, 0, 0)
        self.tableWidget = QtGui.QTableWidget(Dialog_codebook)
        #self.tableWidget.setGeometry(QtCore.QRect(20, 50, 651, 431))
        self.gridLayout.addWidget(self.tableWidget,1,0,1,3)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        self.retranslateUi(Dialog_codebook)

        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog_codebook.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog_codebook.reject)

        #ADDIN
        self.pushButton_sort.clicked.connect(self.sort)
        self.pushButton_export.clicked.connect(self.export)
        self.fillTableWidget()
        # END ADDIN

        QtCore.QMetaObject.connectSlotsByName(Dialog_codebook)

    def retranslateUi(self, Dialog_codebook):
        Dialog_codebook.setWindowTitle(_translate("Dialog_codebook", "Codebook", None))
        self.pushButton_export.setText(_translate("Dialog_codebook", "Export to file", None))
        self.pushButton_sort.setText(_translate("Dialog_codebook", "Sorted by code", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog_codebook = QtGui.QDialog()
    ui = Ui_Dialog_codebook()
    ui.setupUi(Dialog_codebook)
    Dialog_codebook.show()
    sys.exit(app.exec_())

