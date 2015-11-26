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
from CodeColors import CodeColors
import re

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_Dialog_colorselect(QtGui.QDialog):
    #ADDIN
    colors = CodeColors()
    prevColorName = None
    selectedColor = None

    def __init__(self, prevColorName, parent=None):
        super(QtGui.QDialog, self).__init__(parent)  # use this to overrride accept method
        if prevColorName is not None:
            self.prevColorName = re.sub("\d+", "", prevColorName)  #regex to remove digits present in original RQDA

    def colorSelected(self):
        """ Get colour selection from table widget """
        x = self.tableWidget.currentRow()
        y = self.tableWidget.currentColumn()
        self.selectedColor = self.colors.getSelectorColor(x, y)
        self.label.setText(self.selectedColor['colname'])

        palette = QtGui.QPalette(self.label)
        c = QtGui.QColor(self.selectedColor["hex"])
        palette.setColor(QtGui.QPalette.Window, c)
        self.label.setPalette(palette)
        self.label.setAutoFillBackground(True)  # very important

    def getColor(self):
        """ Get the selected colour name """
        return self.selectedColor

    def accept(self):
        """ Overrriden accept button """
        self.thisDialog.accept()

    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(400, 333)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(290, 20, 81, 241))
        self.buttonBox.setOrientation(QtCore.Qt.Vertical)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(50, 40, 151, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.tableWidget = QtGui.QTableWidget(Dialog)
        self.tableWidget.setGeometry(QtCore.QRect(30, 90, 346, 227))
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setRowCount(10)
        self.tableWidget.setColumnCount(10)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.SingleSelection)

        for i in range (0, 10):
            self.tableWidget.setRowHeight(i, 22)
            self.tableWidget.setColumnWidth(i, 34)
            for j in range (0, 10):
                item = QtGui.QTableWidgetItem()
                #item.setFlags(QtCore.Qt.ItemIsSelectable) #ruins selection dont use
                codeColor = self.colors.x11_short[i * 10 + j]
                item.setBackground(QtGui.QBrush(QtGui.QColor(codeColor['hex'])))
                self.tableWidget.setItem(i, j, item)
                if codeColor['colname'] == self.prevColorName:
                    self.label.setText(self.prevColorName)
                    palette = QtGui.QPalette(self.label)
                    c = QtGui.QColor(codeColor["hex"])
                    palette.setColor(QtGui.QPalette.Window, c)
                    self.label.setPalette(palette)
                    self.label.setAutoFillBackground(True)  # very important

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.tableWidget.cellClicked.connect(self.colorSelected)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Colour Selector", None, QtGui.QApplication.UnicodeUTF8))
        #self.label.setText(QtGui.QApplication.translate("Dialog", "_____", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Dialog = QtGui.QDialog()
    ui = Ui_Dialog_colorselect()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

