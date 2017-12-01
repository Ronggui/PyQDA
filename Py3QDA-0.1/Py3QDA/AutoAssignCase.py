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


class Ui_Dialog_autoassign(object):
    """ This dialog gets the start and end mark text to allow file text to be automatically assigned to the
    currently selected case.
    It requires the name of the selected case.
    Methods return the startmark text and the endmark text """

    # ADDIN
    caseName = ""

    def __init__(self, caseName):
        self.caseName = caseName

    def getStartMark(self):
        return str(self.lineEdit_startmark.text())

    def getEndMark(self):
        return str(self.lineEdit_endmark.text())
    #END ADDIN

    def setupUi(self, Dialog_autoassign):
        Dialog_autoassign.setObjectName(_fromUtf8("Dialog_autoassign"))
        Dialog_autoassign.resize(345, 203)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_autoassign)
        self.buttonBox.setGeometry(QtCore.QRect(30, 150, 291, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lineEdit_startmark = QtWidgets.QLineEdit(Dialog_autoassign)
        self.lineEdit_startmark.setGeometry(QtCore.QRect(110, 60, 151, 27))
        self.lineEdit_startmark.setObjectName(_fromUtf8("lineEdit_startmark"))
        self.lineEdit_endmark = QtWidgets.QLineEdit(Dialog_autoassign)
        self.lineEdit_endmark.setGeometry(QtCore.QRect(110, 100, 151, 27))
        self.lineEdit_endmark.setObjectName(_fromUtf8("lineEdit_endmark"))
        self.label_startmark = QtWidgets.QLabel(Dialog_autoassign)
        self.label_startmark.setGeometry(QtCore.QRect(30, 60, 71, 17))
        self.label_startmark.setObjectName(_fromUtf8("label_startmark"))
        self.label_endmark = QtWidgets.QLabel(Dialog_autoassign)
        self.label_endmark.setGeometry(QtCore.QRect(30, 100, 71, 17))
        self.label_endmark.setObjectName(_fromUtf8("label_endmark"))
        self.label = QtWidgets.QLabel(Dialog_autoassign)
        self.label.setGeometry(QtCore.QRect(30, 27, 41, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_case = QtWidgets.QLabel(Dialog_autoassign)
        self.label_case.setGeometry(QtCore.QRect(80, 27, 241, 17))
        self.label_case.setObjectName(_fromUtf8("label_case"))

        self.retranslateUi(Dialog_autoassign)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog_autoassign.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog_autoassign.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_autoassign)

    def retranslateUi(self, Dialog_autoassign):
        Dialog_autoassign.setWindowTitle(_translate("Dialog_autoassign", "Auto assign cases", None))
        self.label_startmark.setText(_translate("Dialog_autoassign", "Start mark", None))
        self.label_endmark.setText(_translate("Dialog_autoassign", "End mark", None))
        self.label.setText(_translate("Dialog_autoassign", "Case:", None))
        self.label_case.setText(_translate("Dialog_autoassign", self.caseName, None))  # CHANGED


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_autoassign = QtWidgets.QDialog()
    ui = Ui_Dialog_autoassign()
    ui.setupUi(Dialog_autoassign)
    Dialog_autoassign.show()
    sys.exit(app.exec_())
