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
import sqlite3
import os

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

class Ui_Dialog_sql(object):
    """ A gui to allow the user to enter sql queries and return results."""

    settings = None
    sql = ""
    log = ""

    def __init__(self, settings):
        self.settings = settings

    def getLog(self):

        return self.log

    def exportFile(self):
        """ Export textedit results to a plain text file, filename will have .txt ending """

        fileName = QtWidgets.QFileDialog.getSaveFileName(None,"Save text file", os.getenv('HOME'))[0]
        if fileName:
            fileName += ".txt"
            #print (("Exporting:  to " + fileName))
            filedata = self.textEdit_results.toPlainText()
            f = open(fileName, 'w', encoding="utf-8")
            f.write(filedata)
            f.close()
            self.log += "Search Results exported to " + fileName + "\n"
            QtWidgets.QMessageBox.information(None, "Text file Export", str(fileName) + " exported")


    def getTreeItem(self):
        """ Get the selected tree item text and add to the sql text """

        itemText = self.treeWidget.currentItem().text(0)
        self.sql = self.textEdit_sql.toPlainText()
        self.sql += " " + itemText + " "
        self.textEdit_sql.setText(self.sql)

    def runSQL(self):
        """ Run the sql text and add the results to the results text edit """

        self.sql = self.textEdit_sql.toPlainText()
        self.textEdit_results.setText(self.sql+"\n")
        cur = self.settings['conn'].cursor()
        self.sql = str(self.sql)
        try:
            cur.execute(self.sql)
            results = cur.fetchall()
            for row in results:
                resultStr = ""
                for item in row:
                    tmp = ""
                    try:
                        tmp = str(item)
                    except: # unicode error most likely, so ignore those characters
                        for c in item:
                            if ord(c) < 128:
                                tmp += c
                    resultStr += str(tmp) + " "
                self.textEdit_results.append(resultStr)
        except sqlite3.OperationalError as e:
            self.textEdit_results.setText(str(e))

    def setupUi(self, Dialog_sql):
        Dialog_sql.setObjectName(_fromUtf8("Dialog_sql"))
        Dialog_sql.resize(947, 606)
        self.label = QtWidgets.QLabel(Dialog_sql)
        self.label.setGeometry(QtCore.QRect(20, 570, 171, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.pushButton_runSQL = QtWidgets.QPushButton(Dialog_sql)
        self.pushButton_runSQL.setGeometry(QtCore.QRect(500, 565, 98, 27))
        self.pushButton_runSQL.setObjectName(_fromUtf8("pushButton_go"))
        self.pushButton_export = QtWidgets.QPushButton(Dialog_sql)
        self.pushButton_export.setGeometry(QtCore.QRect(620, 565, 121, 27))
        self.pushButton_export.setObjectName(_fromUtf8("pushButton_export"))
        self.splitter_2 = QtWidgets.QSplitter(Dialog_sql)
        self.splitter_2.setGeometry(QtCore.QRect(10, 10, 921, 531))
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.treeWidget = QtWidgets.QTreeWidget(self.splitter_2)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("Tables"))
        self.treeWidget.setColumnCount(1)
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.textEdit_sql = QtWidgets.QTextEdit(self.splitter)
        self.textEdit_sql.setObjectName(_fromUtf8("textEdit_sql"))
        self.textEdit_sql.setText("select")
        self.textEdit_results = QtWidgets.QTextEdit(self.splitter)
        self.textEdit_results.setObjectName(_fromUtf8("textEdit_results"))
        self.splitter_2.setSizes([20, 180])
        self.splitter.setSizes([30, 170])

        #ADDIN
        tables = [
            ["source","name", "id", "file", "memo", "owner", "date", "dateM", "status"],
            ["fileAttr", "variable", "value", "fileID", "date", "dateM", "owner", "status"],
            ["filecat", "name", "fid", "catid", "owner", "date", "dateM","memo", "status"],
            ["annotation", "fid" ,"position" ,"annotation" , "owner" , "date" ,"dateM" , "status"],
            ["attributes", "name" , "status" , "date" , "dateM" , "owner" ,"memo" , "class"],
            ["caseAttr", "variable" , "value" , "caseID" , "date" , "dateM" , "owner" , "status"],
            ["caselinkage", "caseid" , "fid" , "selfirst" , "selend" , "status" , "owner" , "date" , "memo"],
            ["cases","name" , "memo" , "owner" ,"date" ,"dateM", "id" , "status"],
            ["codecat","name" , "cid" , "catid" , "owner", "date", "dateM", "memo" , "status"],
            ["coding", "cid" , "fid" ,"seltext" , "selfirst" , "selend" , "status" , "owner" , "date" , "memo"],
            ["coding2", "cid" , "fid" ,"seltext" , "selfirst" , "selend" , "status" , "owner" , "date" , "memo"],
            ["freecode","name" , "memo" , "owner" ,"date" ,"dateM", "id" , "status" , "color" ],
            ["journal", "name" , "journal" , "date" , "dateM" , "owner" ,"status"],
            ["treecode", "cid" , "catid" , "date" , "dateM" , "memo" , "status" , "owner"],
            ["treefile", "fid" , "catid" , "date" ,"dateM" , "memo" , "status" ,"owner"],
            ["project", "databaseversion" , "date" ,"dateM" , "memo" ,"about" , "imageDir"],
            ["image", "name" , "id" , "date" , "dateM" , "owner" ,"status"],
            ["imageCoding", "cid","iid","x1", "y1", "x2", "y2", "memo", "date", "dateM", "owner","status"],
            ["SQL", "from", "where", "like", "join", "left join"," group by", "order by"]
            ]

        for t in tables:
            top = QtWidgets.QTreeWidgetItem()
            top.setText(0, t[0])
            self.treeWidget.addTopLevelItem(top)
            for idx,f in enumerate(t):
                if idx > 0:
                    field = QtWidgets.QTreeWidgetItem()
                    if t[0] != "SQL":
                        field.setText(0, t[0]+"."+f)
                    else:
                        field.setText(0,f)
                    top.addChild(field)

        self.treeWidget.itemDoubleClicked.connect(self.getTreeItem)
        self.pushButton_runSQL.clicked.connect(self.runSQL)
        #END ADDIN

        self.retranslateUi(Dialog_sql)
        QtCore.QMetaObject.connectSlotsByName(Dialog_sql)

    def retranslateUi(self, Dialog_sql):
        Dialog_sql.setWindowTitle(_translate("Dialog_sql", "SQL_statements", None))
        self.label.setText(_translate("Dialog_sql", "RQDA: tables and fields", None))
        self.pushButton_export.setText(_translate("Dialog_sql", "Export to file", None))
        self.pushButton_runSQL.setText(_translate("Dialog_sql", "Run", None))
        self.pushButton_export.clicked.connect(self.exportFile)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_sql = QtWidgets.QDialog()
    ui = Ui_Dialog_sql({'conn':None})
    ui.setupUi(Dialog_sql)
    Dialog_sql.show()
    sys.exit(app.exec_())
