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
import os

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_Dialog_information(QtWidgets.QDialog):
    """
    Dialog to display details information PyQDA development, version and license.
    """

    title = ""
    informationText = ""
    Dialog_information = None

    def __init__(self, title, filename, parent = None):
        """ Display information text in dialog """

        super(QtWidgets.QDialog, self).__init__(parent)  # use this to overrride accept method
        self.title = title
        scriptdir = os.path.dirname(os.path.abspath(__file__))
        htmlFile = os.path.join(scriptdir, filename)
        try:
            with open(htmlFile, 'r') as f:
                self.informationText = f.read()
        except:
            self.informationText = "Cannot open file."

    def accepted(self):
        """ Accepted button overridden method """
        self.information = self.textEdit.toPlainText()
        self.information = str(self.information.toUtf8()).decode('utf-8')
        self.Dialog_information.accept()

    def setupUi(self, Dialog_information, ):
        self.Dialog_information = Dialog_information
        Dialog_information.setObjectName(_fromUtf8("Dialog_information"))
        Dialog_information.setWindowTitle(self.title)
        Dialog_information.resize(800, 502)
        self.gridLayout = QtWidgets.QGridLayout(Dialog_information)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))

        self.textEdit = QtWidgets.QTextBrowser(Dialog_information)
        self.textEdit.setOpenExternalLinks(True)
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.textEdit.setHtml(self.informationText)
        self.textEdit.setReadOnly(True)
        self.gridLayout.addWidget(self.textEdit, 0, 0)

        '''self.retranslateUi(Dialog_information)

    def retranslateUi(self, Dialog_information):
        Dialog_information.setWindowTitle(QtWidgets.QApplication.translate("Dialog_information", self.title, None, QtWidgets.QApplication.UnicodeUTF8))
'''

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_information = QtWidgets.QDialog()
    ui = Ui_Dialog_information("title", "filename")
    ui.setupUi(Dialog_information)
    Dialog_information.show()
    sys.exit(app.exec_())
