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
from CodeColors import CodeColors
from SelectFile import Ui_Dialog_selectfile
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

class Ui_Dialog_reportCodings(object):
    """ Get reports on coding using a range of variables """

    #ADDIN
    CODE_COLUMN = 0
    CAT_COLUMN = 1
    ID_COLUMN = 2
    settings = None
    codes = []
    codeColors = CodeColors()
    log = ""

    orderByCodeAscendSQL = "select freecode.name, codecat.name, freecode.id, freecode.color from freecode "\
         "left join treecode on treecode.cid=freecode.id left join codecat on treecode.catid=codecat.catid "\
          "group by freecode.name order by upper(freecode.name)"

    orderByCodeDescendSQL = "select freecode.name, codecat.name, freecode.id, freecode.color from freecode "\
         "left join treecode on treecode.cid=freecode.id left join codecat on treecode.catid=codecat.catid "\
          "group by freecode.name order by upper(freecode.name) desc"

    orderByCategoryAscendSQL = "select freecode.name, codecat.name, freecode.id, freecode.color from freecode "\
         "left join treecode on treecode.cid=freecode.id left join codecat on treecode.catid=codecat.catid "\
          "group by freecode.name order by upper(codecat.name), upper(freecode.name)"

    orderByCategoryDescendSQL = "select freecode.name, codecat.name, freecode.id, freecode.color from freecode "\
         "left join treecode on treecode.cid=freecode.id left join codecat on treecode.catid=codecat.catid "\
          "group by freecode.name order by upper(codecat.name) desc, upper(freecode.name) desc"

    # variables for search restrictions
    fileIDs = ""
    caseIDs = ""

    # results for file outputs
    plainTextResults = ""
    htmlResults = ""

    def __init__(self, settings):
        self.settings = settings
        self.codes = []
        self.log = ""
        self.qfont = QtGui.QFont()
        self.qfont.setPointSize(self.settings['fontSize'])

        #set up default codes list
        cur = self.settings['conn'].cursor()
        cur.execute(self.orderByCategoryAscendSQL)
        result = cur.fetchall()
        for row in result:
            self.codes.append({'name':row[0], 'category':row[1], 'id':row[2], 'color':row[3]})

    def cellSelected(self):
        """ Select all codes of selected categories.
        This is flexible, holding ctrl key down allows further codes of other categories to be selected. """

        x = self.tableWidget.currentRow()
        y = self.tableWidget.currentColumn()
        if y != self.CAT_COLUMN:
            return
        catText = str(self.tableWidget.item(x, y).text())
        #print(x,y, catText)
        self.tableWidget.item(x, y).setSelected(False)
        for row, code in enumerate(self.codes):
            if code['category'] == catText:
                self.tableWidget.item(row, self.CODE_COLUMN).setSelected(True)

    def exportTextFile(self):
        """ Export file to a plain text file, filename will have .txt ending """

        fileName = QtWidgets.QFileDialog.getSaveFileName(None,"Save text file", os.getenv('HOME'))[0]
        if fileName:
            fileName += ".txt"
            #print (("Exporting:  to " + fileName))
            filedata = self.plainTextResults
            f = open(fileName, 'w', encoding="utf8")
            f.write(filedata)
            f.close()
            self.log += "Search Results exported to " + fileName + "\n"
            QtWidgets.QMessageBox.information(None, "Text file Export", str(fileName) + " exported")

    def exportHtmlFile(self):
        """ Export file to html file """

        fileName = QtWidgets.QFileDialog.getSaveFileName(None,"Save html file", os.getenv('HOME'))[0]
        if fileName:
            fileName += ".html"
            #print (("Exporting:  to " + fileName))
            filedata = "<html>\n<head>\n<title>" + self.settings['projectName'] + "</title>\n</head>\n<body>\n"
            #filedata += str(self.htmlResults.encode('utf-8'))
            modData = ""
            for c in self.htmlResults:
                if ord(c) < 128:
                    modData += c
                else:
                    modData += "&#" + str(ord(c)) + ";"
            filedata += modData
            filedata += "</body>\n</html>"
            f = open(fileName, 'w')
            f.write(filedata)
            f.close()
            self.log += "Search Results exported to " + fileName + "\n"
            QtWidgets.QMessageBox.information(None, "Html file Export", str(fileName) + " exported")

    def search(self):
        """ Search for selected codings.
        There are two main search pathways.
        The default is based on file selection and can be restricted using the file selection dialog.
        The second pathway is based on case selection and can be resctricted using the case selection dialog.
        If cases are selected this overrides (ignores) and file selections that the user has entered.
         """

        if not(self.checkBox_coder1.isChecked()) and not(self.checkBox_coder2.isChecked()):
            QtWidgets.QMessageBox.warning(None, "No coder","No coder has been selected.")
            return

        self.htmlResults = ""
        self.plainTextResults = ""

        # get search text
        searchText = self.lineEdit.text()
        unic_err = False
        try:
            searchText = str(searchText)
        except UnicodeEncodeError as e:
            unic_err = True
            QtWidgets.QMessageBox.warning(None, "Unicode encode error", str(e) +"\nPlease use different search text." \
            "\nThe problem character(s) have been replaced with Wildcards for this search.")
        if unic_err is True:
            # use sql wildcards
            newText = ""
            for c in searchText:
                try:
                    newText += str(c)
                except UnicodeEncodeError as e:
                    newText += "_"
            searchText = newText

        # get selected codes
        codeIDs = ""
        for itemWidget in self.tableWidget.selectedItems():
            codeIDs += "," + self.tableWidget.item(itemWidget.row(), self.ID_COLUMN).text()
        if len(codeIDs) == 0:
            QtWidgets.QMessageBox.warning(None, "No codes","No codes have been selected.")
            return
        codeIDs = codeIDs[1:]

        # get file ids
        if self.fileIDs == "": # unless already selected via selectFiles method
            filenames = []
            cur = self.settings['conn'].cursor()
            cur.execute("select id, name, status from source")
            result = cur.fetchall()
            for row in result:
                filenames.append({'id': row[0], 'name': row[1], 'status': row[2]})
                self.fileIDs += "," + str(row[0])
            if len(self.fileIDs) > 0:
                self.fileIDs = self.fileIDs[1:]

        searchResults = []
        searchString = ""
        cur = self.settings['conn'].cursor()
        if self.caseIDs == "": # no selected case ids
            sql = "select freecode.name, color, source.name, selfirst, selend, seltext from coding "
            sql += " join freecode on cid = freecode.id join source on fid = source.id "
            sql += " where freecode.id in (" + str(codeIDs) + ") "
            sql += " and source.id in (" + str(self.fileIDs) + ") "
            #print(sql)
            if self.checkBox_coder1.isChecked():
                if searchText == "":
                    cur.execute(sql)
                else:
                    sql = sql + "and seltext like ?"
                    #print(sql)
                    cur.execute(sql,["%"+str(searchText)+"%"])
                result = cur.fetchall()
                for row in result:
                    searchResults.append(row)

                if sql.find("seltext like ?") > 0:
                    sql = sql.replace("seltext like ?", "seltext like \"%" + searchText + "%\"")
                searchString = sql

            if self.checkBox_coder2.isChecked():
                sql = "select freecode.name, color, source.name, selfirst, selend, seltext from coding2 "
                sql += " join freecode on cid = freecode.id join source on fid = source.id "
                sql += " where freecode.id in (" + str(codeIDs) + ") "
                sql += " and source.id in (" + str(self.fileIDs) + ") "
                #print(sql)
                if searchText == "":
                    cur.execute(sql)
                else:
                    sql = sql + " and seltext like ?"
                    #print(sql)
                    cur.execute(sql,["%"+str(searchText)+"%"])
                result = cur.fetchall()
                for row in result:
                    searchResults.append(row)

                if sql.find("seltext like ?") > 0:
                    sql = sql.replace("seltext like ?", "seltext like \"%" + searchText + "%\"")
                searchString += "\n" + sql

        else: # cases have been selected via selectCases method, file selection is ignored
            if self.checkBox_coder1.isChecked():
                sql = "select freecode.name, color, cases.name, coding.selfirst, coding.selend, seltext from coding "
                sql += " join freecode on cid = freecode.id "
                sql += " join (caselinkage join cases on cases.id = caselinkage.caseid) on coding.fid = caselinkage.fid "
                sql += " where freecode.id in (" + str(codeIDs) + ") "
                sql += " and caselinkage.caseid in (" + str(self.caseIDs) + ") "
                if searchText != "":
                    sql += "and seltext like ?"
                sql += " group by cases.name, coding.selfirst, coding.selend" # need to group by or can get multiple results
                #print(sql)
                if searchText == "":
                    cur.execute(sql)
                else:
                    cur.execute(sql,["%"+str(searchText)+"%"])
                result = cur.fetchall()
                for row in result:
                    searchResults.append(row)

                if sql.find("seltext like ?") > 0:
                    sql = sql.replace("seltext like ?", "seltext like \"%" + searchText + "%\"")
                searchString = sql

            if self.checkBox_coder2.isChecked():
                sql = "select freecode.name, color, cases.name, coding2.selfirst, coding2.selend, seltext from coding2 "
                sql += " join freecode on cid = freecode.id "
                sql += " join (caselinkage join cases on cases.id = caselinkage.caseid) on coding2.fid = caselinkage.fid "
                sql += " where freecode.id in (" + str(codeIDs) + ") "
                sql += " and caselinkage.caseid in (" + str(self.caseIDs) + ") "
                if searchText != "":
                    sql += "and seltext like ?"
                sql += " group by cases.name, coding2.selfirst, coding2.selend" # need to group by or can get multiple results
                #print(sql)
                if searchText == "":
                    cur.execute(sql)
                else:
                    cur.execute(sql,["%"+str(searchText)+"%"])
                result = cur.fetchall()
                for row in result:
                    searchResults.append(row)

                if sql.find("seltext like ?") > 0:
                    sql = sql.replace("seltext like ?", "seltext like \"%" + searchText + "%\"")
                searchString += "\n" + sql

        # add to text edit with some formatting
        self.textEdit.clear()
        fileOrCase = "File"
        if self.caseIDs != "":
            fileOrCase = "Case"
        CODENAME = 0
        COLOR = 1
        FILEORCASENAME = 2
        #SELFIRST = 3
        #SELEND = 4
        SELTEXT = 5
        self.plainTextResults += "Search queries:\n" + searchString + "\n\n"
        searchString = searchString.replace("&","&amp;")
        searchString = searchString.replace("<","&lt;")
        searchString = searchString.replace(">","&gt;")
        searchString = searchString.replace("\"","&quot;")
        self.htmlResults += "<h1>Search queries</h1>\n"
        self.htmlResults += "<p>" + searchString + "</p>"
        self.htmlResults += "<h2>Results</h2>"

        for row in searchResults:
            colorhex = self.codeColors.getHexFromName(row[COLOR])
            if colorhex == "":
                colorhex = "#CCCCCC"
            title = "<h3><span style=\"background-color:" + colorhex + "\">"+row[CODENAME] + "</span>, "
            title +=" "+ fileOrCase + ": " + row[FILEORCASENAME] + "</h3>"
            self.textEdit.appendHtml(title)
            self.textEdit.appendPlainText(row[SELTEXT] + "\n")

            self.htmlResults += "<p>" + title + "<br />"
            tmpHtml = row[SELTEXT].replace("&","&amp;")
            tmpHtml = tmpHtml.replace("<","&lt;")
            tmpHtml = tmpHtml.replace(">","&gt;")
            #self.htmlResults += row[SELTEXT] + "</p>\n"
            self.htmlResults += tmpHtml + "</p>\n"
            self.plainTextResults += row[CODENAME] +", " + fileOrCase +": " + row[FILEORCASENAME] +"\n"
            self.plainTextResults += row[SELTEXT] + "\n\n"

    def selectFiles(self):
        """ When select file button is pressed a dialog of filenames is presented to the user.
        The selected files are then used when searching for codings
        If files are selected, then selected cases are cleared.
        The default is all file IDs.
        To revert to default after files are selected,
        the user must press select files button then cancel the dialog.
         """

        filenames = []
        self.fileIDs = ""
        self.caseIDs = "" # clears any case selections
        cur = self.settings['conn'].cursor()
        cur.execute("select id, name, status from source")
        result = cur.fetchall()
        for row in result:
            filenames.append({'id': row[0], 'name': row[1], 'status': row[2]})
            self.fileIDs += "," + str(row[0])
        if len(self.fileIDs) > 0:
            self.fileIDs = self.fileIDs[1:]

        Dialog_selectfile = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(filenames)
        ui.setupUi(Dialog_selectfile, "Select file(s) to view", "many")
        ok = Dialog_selectfile.exec_()
        if ok:
            tmp_IDs = ""
            selectedFiles = ui.getSelected() # list of dictionaries
            for row in selectedFiles:
                tmp_IDs += "," + str(row['id'])
            if len(tmp_IDs) > 0:
                self.fileIDs = tmp_IDs[1:]

    def selectCases(self):
        """ When select case button is pressed a dialog of case names is presented to the user.
        The selected cases are then used when searching for codings.
        If cases are selected, then selected files are cleared.
        If neither are selected the default is all files are selected.
         """

        casenames = []
        self.fileIDs = ""
        self.caseIDs = "" # default for all cases and allows the file selection search method to occur
        cur = self.settings['conn'].cursor()
        cur.execute("select id, name, status from cases")
        result = cur.fetchall()
        for row in result:
            casenames.append({'id': row[0], 'name': row[1], 'status': row[2]})

        Dialog_selectcase = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(casenames)
        ui.setupUi(Dialog_selectcase, "Select case(s) to view", "many")
        ok = Dialog_selectcase.exec_()
        if ok:
            tmp_IDs = ""
            selectedCases = ui.getSelected() # list of dictionaries
            for row in selectedCases:
                tmp_IDs += "," + str(row['id'])
            if len(tmp_IDs) > 0:
                self.caseIDs = tmp_IDs[1:]

    def sortTable(self):

        sortByField = self.pushButton_sort.text()
        if sortByField == "Sorted by category":
            self.pushButton_sort.setText("Sorted by code")
        if sortByField == "Sorted by code":
            self.pushButton_sort.setText("Sorted by category")
        self.refillCodeTable()

    def sortDirection(self):

        sortByDirection = self.pushButton_sortDirection.text()
        if sortByDirection == "Descending":
            self.pushButton_sortDirection.setText("Ascending")
        if sortByDirection == "Ascending":
            self.pushButton_sortDirection.setText("Descending")
        self.refillCodeTable()

    def refillCodeTable(self):
        """ Refill the codes and categories table based on sort direction and
         sort by code or category """

        tableSQL = ""
        sortDirection = self.pushButton_sortDirection.text()
        sortField = self.pushButton_sort.text()
        if sortDirection == "Ascending":
            if sortField == "Sorted by code":
                tableSQL = self.orderByCodeAscendSQL
            else:
                tableSQL = self.orderByCategoryAscendSQL
        else: # sort descending
            if sortField == "Sorted by code":
                tableSQL = self.orderByCodeDescendSQL
            else:
                tableSQL = self.orderByCategoryDescendSQL

        for row in self.codes:
            self.tableWidget.removeRow(0)
        self.codes = []
        cur = self.settings['conn'].cursor()
        cur.execute(tableSQL)
        result = cur.fetchall()
        for row in result:
            self.codes.append({'name':row[0], 'category':row[1], 'id':row[2], 'color':row[3]})
        self.fillTableWidget()

    def fillTableWidget(self):
        """ Fill the table widget with the model details """

        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(["Code", "Category", "id"])
        for row, code in enumerate(self.codes):
            self.tableWidget.insertRow(row)
            #self.tableWidget.setItem(row, CODE_COLUMN, QtWidgets.QTableWidgetItem(code['name']))

            colnametmp = code['color']
            if colnametmp is None: colnametmp = ""
            codeItem = QtWidgets.QTableWidgetItem(code['name'])
            codeItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            colorHex = self.codeColors.getHexFromName(colnametmp)
            if colorHex != "":
                codeItem.setBackground(QtGui.QBrush(QtGui.QColor(colorHex)))
            self.tableWidget.setItem(row, self.CODE_COLUMN, codeItem)

            category = code['category']
            if category is None: category = ""
            catItem = QtWidgets.QTableWidgetItem(category)
            catItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(row, self.CAT_COLUMN, catItem)
            id_ = code['id']
            if id_ is None:
                id_ = ""
            self.tableWidget.setItem(row, self.ID_COLUMN, QtWidgets.QTableWidgetItem(str(id_)))

        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()
        if not self.settings['showIDs']:
            self.tableWidget.hideColumn(self.ID_COLUMN)

    def getLog(self):
        """ Get details of file movments """
        return self.log

    #END ADDIN

    def setupUi(self, Dialog_reportCodings):
        Dialog_reportCodings.setObjectName(_fromUtf8("Dialog_reportCodings"))
        Dialog_reportCodings.setWindowModality(QtCore.Qt.ApplicationModal)
        w = QtWidgets.QApplication.desktop().width()
        h = QtWidgets.QApplication.desktop().height()
        if w > 1200: w = 1200
        if h > 800: h = 800
        Dialog_reportCodings.resize(w-20, h-60)
        self.pushButton_exporttext = QtWidgets.QPushButton(Dialog_reportCodings)
        self.pushButton_exporttext.setGeometry(QtCore.QRect(700, 40, 121, 27))
        self.pushButton_exporttext.setObjectName(_fromUtf8("pushButton_exporttext"))
        #ADDIN SPLITTER
        self.splitter = QtWidgets.QSplitter(Dialog_reportCodings)
        self.splitter.setGeometry(QtCore.QRect(10, 90, w - 40, h - 200))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))

        #END ADDIN
        self.tableWidget = QtWidgets.QTableWidget(self.splitter) # ADDED splitter
        self.tableWidget.setGeometry(QtCore.QRect(10, 90, 331, 391))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tableWidget.sizePolicy().hasHeightForWidth())
        self.tableWidget.setSizePolicy(sizePolicy)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.pushButton_sort = QtWidgets.QPushButton(Dialog_reportCodings)
        self.pushButton_sort.setGeometry(QtCore.QRect(20, 10, 141, 27))
        self.pushButton_sort.setObjectName(_fromUtf8("pushButton_sort"))
        self.pushButton_sortDirection = QtWidgets.QPushButton(Dialog_reportCodings)
        self.pushButton_sortDirection.setGeometry(QtCore.QRect(20, 40, 141, 27))
        self.pushButton_sortDirection.setObjectName(_fromUtf8("pushButton_sortDirection"))
        self.textEdit = QtWidgets.QPlainTextEdit(self.splitter) # added plain and splitter
        self.textEdit.setGeometry(QtCore.QRect(550, 90, 841, 391))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.textEdit.setFont(self.qfont)
        self.pushButton_exporthtml = QtWidgets.QPushButton(Dialog_reportCodings)
        self.pushButton_exporthtml.setGeometry(QtCore.QRect(700, 10, 121, 27))
        self.pushButton_exporthtml.setObjectName(_fromUtf8("pushButton_exporthtml"))
        self.checkBox_coder1 = QtWidgets.QCheckBox(Dialog_reportCodings)
        self.checkBox_coder1.setGeometry(QtCore.QRect(180, 14, 91, 22))
        self.checkBox_coder1.setObjectName(_fromUtf8("checkBox_coder1"))
        self.checkBox_coder2 = QtWidgets.QCheckBox(Dialog_reportCodings)
        self.checkBox_coder2.setGeometry(QtCore.QRect(180, 43, 91, 22))
        self.checkBox_coder2.setObjectName(_fromUtf8("checkBox_coder2"))
        self.lineEdit = QtWidgets.QLineEdit(Dialog_reportCodings)
        self.lineEdit.setGeometry(QtCore.QRect(280, 40, 131, 27))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.label = QtWidgets.QLabel(Dialog_reportCodings)
        self.label.setGeometry(QtCore.QRect(291, 16, 111, 17))
        self.label.setObjectName(_fromUtf8("label"))
        self.pushButton_fileselect = QtWidgets.QPushButton(Dialog_reportCodings)
        self.pushButton_fileselect.setGeometry(QtCore.QRect(430, 10, 111, 27))
        self.pushButton_fileselect.setObjectName(_fromUtf8("pushButton_fileselect"))
        self.pushButton_fileselect.setToolTip("Select files of interest.\nTo clear - press the button and select Cancel.\nFile selection overrides any case selections.")
        self.pushButton_caseselect = QtWidgets.QPushButton(Dialog_reportCodings)
        self.pushButton_caseselect.setGeometry(QtCore.QRect(430, 40, 111, 27))
        self.pushButton_caseselect.setObjectName(_fromUtf8("pushButton_caseselect"))
        self.pushButton_caseselect.setToolTip("Select cases of interest.\nTo clear selection - press the button and select Cancel\nCase selection overrides any file selection\n")
        self.pushButton_search = QtWidgets.QPushButton(Dialog_reportCodings)
        self.pushButton_search.setGeometry(QtCore.QRect(560, 10, 71, 61))
        self.pushButton_search.setObjectName(_fromUtf8("pushButton"))

        self.retranslateUi(Dialog_reportCodings)
        QtCore.QMetaObject.connectSlotsByName(Dialog_reportCodings)

        #ADDIN
        self.sortTable()
        if self.settings['codertable'] == "coding":
            self.checkBox_coder1.setChecked(True)
        else:
            self.checkBox_coder2.setChecked(True)
        self.pushButton_sort.clicked.connect(self.sortTable)
        self.pushButton_sortDirection.clicked.connect(self.sortDirection)
        self.pushButton_search.clicked.connect(self.search)
        self.tableWidget.cellClicked.connect(self.cellSelected)
        self.pushButton_fileselect.clicked.connect(self.selectFiles)
        self.pushButton_caseselect.clicked.connect(self.selectCases)
        self.pushButton_exporttext.clicked.connect(self.exportTextFile)
        self.pushButton_exporthtml.clicked.connect(self.exportHtmlFile)
        # END ADDIN

    def retranslateUi(self, Dialog_reportCodings):
        Dialog_reportCodings.setWindowTitle(_translate("Dialog_reportCodings", "Report codings", None))
        self.pushButton_exporttext.setText(_translate("Dialog_reportCodings", "Export text file", None))
        self.pushButton_sort.setText(_translate("Dialog_reportCodings", "Sorted by category", None))
        self.pushButton_sortDirection.setText(_translate("Dialog_reportCodings", "Ascending", None))
        self.pushButton_exporthtml.setText(_translate("Dialog_reportCodings", "Export html file", None))
        self.checkBox_coder1.setText(_translate("Dialog_reportCodings", "Coder 1", None))
        self.checkBox_coder2.setText(_translate("Dialog_reportCodings", "Coder 2", None))
        self.label.setText(_translate("Dialog_reportCodings", "Search for text:", None))
        self.pushButton_fileselect.setText(_translate("Dialog_reportCodings", "File selection", None))
        self.pushButton_caseselect.setText(_translate("Dialog_reportCodings", "Case selection", None))
        self.pushButton_search.setText(_translate("Dialog_reportCodings", "Search", None))
