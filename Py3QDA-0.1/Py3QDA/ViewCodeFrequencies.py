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

from PyQt5 import QtCore, QtGui, QtWidgets

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

class Ui_Dialog_vcf(object):
    """ Displays a table of code frequencies for selected code categories.
    Code categories are the column headings, relevant codes are underneath each heading
     ordered by most frequent to least frequent.
     Requires a list of dictionaries with category-named keys and values are lists of codes.
     """

    data = None

    def __init__(self, data):
        self.data = data

    def setupUi(self, Dialog_vcf):
        Dialog_vcf.setObjectName(_fromUtf8("Dialog_vcf"))
        Dialog_vcf.resize(882, 589)
        self.gridLayout = QtWidgets.QGridLayout(Dialog_vcf)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tableWidget = QtWidgets.QTableWidget(Dialog_vcf)
        self.tableWidget.setObjectName(_fromUtf8("tableView"))
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)

        keys = list(self.data.keys())
        self.tableWidget.setColumnCount(len(keys))
        self.tableWidget.setHorizontalHeaderLabels(keys)
        rows = 0
        for key in keys:
            if len(self.data[key]) > rows:
                rows = len(self.data[key])
        self.tableWidget.setRowCount(rows)

        for col, key in enumerate(keys):
            for row, value in enumerate(self.data[key]):
                newItem = QtWidgets.QTableWidgetItem(value)
                newItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.tableWidget.setItem(row, col, newItem)

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

        self.retranslateUi(Dialog_vcf)
        QtCore.QMetaObject.connectSlotsByName(Dialog_vcf)

    def retranslateUi(self, Dialog_vcf):
        Dialog_vcf.setWindowTitle(_translate("Dialog_vcf", "Code Frequencies", None))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_vcf = QtWidgets.QDialog()
    ui = Ui_Dialog_vcf({"code":['10', '20']})
    ui.setupUi(Dialog_vcf)
    Dialog_vcf.show()
    sys.exit(app.exec_())
