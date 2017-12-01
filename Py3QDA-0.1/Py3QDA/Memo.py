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
#ADDIN
import datetime
#END ADDIN

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_Dialog_memo(QtWidgets.QDialog):

    """
    Dialog to add memos to: files, codes, code categories and the project.
    Dialog is also used to manually enter file text
    Dialog is also used to view and edit existing file text.
    WARNING: exisiting coding and annotation positions will not be updated!
    """

    memo = ""  # the memo text
    filename = None  # for files created in PyQDA or to modify a filename
    Dialog_memo = None

    def __init__(self, memo, parent=None):
        super(QtWidgets.QDialog, self).__init__(parent)  # use this to overrride accept method
        if memo is not None:
            if isinstance(memo, bytes):
                self.memo = memo.decode("utf8")
            else:
                self.memo = memo

    def accepted(self):
        """ Accepted button overridden method """

        self.memo = self.plainTextEdit.toPlainText() # str
        #self.memo = str(self.memo.toUtf8()).decode('utf-8') ## unicode
        self.Dialog_memo.accept()

    def getMemo(self):
        """ Get the memo text """

        #return self.memo.encode('utf-8','replace')
        return self.memo ## unicode

    def getFilename(self):
        """ Get the filename for the manually entered new file """

        filename = self.lineEdit_filename.text()
        return filename.strip()

    def setupUi(self, Dialog_memo, title):
        self.title = title  #ADDIN
        self.Dialog_memo = Dialog_memo  # ADDIN
        Dialog_memo.setObjectName(_fromUtf8("Dialog_memo"))
        Dialog_memo.resize(650, 502)
        self.gridLayout = QtWidgets.QGridLayout(Dialog_memo)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog_memo)
        self.buttonBox.setGeometry(QtCore.QRect(390, 460, 231, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.gridLayout.addWidget(self.buttonBox, 2,0)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog_memo)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 20, 621, 421))
        self.plainTextEdit.setObjectName(_fromUtf8("plainTextEdit"))
        self.gridLayout.addWidget(self.plainTextEdit, 1, 0, 1, 2)
        if self.memo is not None:
            self.plainTextEdit.setPlainText(self.memo)

        self.label_filename = QtWidgets.QLabel(Dialog_memo)
        self.label_filename.setObjectName(_fromUtf8("label_filename"))
        self.lineEdit_filename = QtWidgets.QLineEdit(Dialog_memo)
        self.lineEdit_filename.setObjectName(_fromUtf8("lineEdit_filename"))

        if title[:8] == "New file" or title[:11] == "New journal":
            self.label_filename.setGeometry(QtCore.QRect(10, 10, 100, 20))
            self.plainTextEdit.setGeometry(QtCore.QRect(10, 40, 621, 421))
            self.gridLayout.addWidget(self.label_filename, 0, 0)
            self.label_filename.setText("Filename:")
            self.lineEdit_filename.setGeometry(QtCore.QRect(100, 10, 200, 24))
            self.gridLayout.addWidget(self.lineEdit_filename, 0, 1)
            if title[:11] == "New journal":
                self.lineEdit_filename.setText(str(datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")))
                self.lineEdit_filename.setText(str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        else:
            self.label_filename.setVisible(False)
            self.lineEdit_filename.hide()

        if title[:11] == "View file: ":
            self.label_filename.setVisible(True)
            self.label_filename.setGeometry(QtCore.QRect(10, 450, 400, 40))
            self.gridLayout.addWidget(self.label_filename, 2, 0)
            self.label_filename.setText("Warning: If codes or cases have been assigned to this file\nchanging the content will affect code and case positions")

        self.retranslateUi(Dialog_memo)
        self.buttonBox.accepted.connect(self.accepted)
        self.buttonBox.rejected.connect(Dialog_memo.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog_memo)

    def retranslateUi(self, Dialog_memo):
        Dialog_memo.setWindowTitle(QtWidgets.QApplication.translate("Dialog_memo", self.title, None, -1))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_memo = QtWidgets.QDialog()
    ui = Ui_Dialog_memo(memo="备忘录")
    ui.setupUi(Dialog_memo, title="备忘录")
    print(type(ui.getMemo()))
    Dialog_memo.show()
    sys.exit(app.exec_())
