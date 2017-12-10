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
import re
from AddItem import Ui_Dialog_addItem
from ConfirmDelete import Ui_Dialog_confirmDelete
from Memo import Ui_Dialog_memo
from SelectFile import Ui_Dialog_selectfile
from AutoAssignCase import Ui_Dialog_autoassign
from ViewCodeFrequencies import Ui_Dialog_vcf
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


class Ui_Dialog_cases(object):
    """    Create, edit and delete cases.
    Assign entire text files or portions of files to cases.
    Assign attributes to cases.    """

    #ADDIN
    NAME_COLUMN = 0
    MEMO_COLUMN = 1
    ID_COLUMN = 2
    headerLabels = ["Name", "Memo", "Id"]

    settings = None
    source = []
    sourceText = ""  #file text
    cases = []
    caseLinks = []
    selectedCase = None
    selectedFile = None
    caseTextViewed = []

    def __init__(self, settings):
        self.settings = settings
        self.source = []
        self.cases = []
        self.caseLinks = []

        cur = self.settings['conn'].cursor()
        cur.execute("select name, id, file, memo, owner, date, dateM, status from source")
        result = cur.fetchall()
        for row in result:
            self.source.append({'name':row[0], 'id':row[1], 'file':row[2], 'memo':row[3], 'owner':row[4], 'date':row[5],
                                 'dateM':row[6], 'status':row[7]})
        cur.execute("select name, memo, owner, date, dateM, id, status from cases")
        result = cur.fetchall()
        for row in result:
            self.cases.append({'name':row[0], 'memo':row[1], 'owner':row[2], 'date':row[3], 'dateM':row[4], 'id':row[5], 'status':row[6]})

    def addCase(self):
        """ When add case button pressed, open addItem dialog to get new case text.
        AddItem dialog checks for duplicate case name.
        New case is added to the model and database """

        Dialog_addCase = QtWidgets.QDialog()
        ui = Ui_Dialog_addItem(self.cases)
        ui.setupUi(Dialog_addCase, "Case")
        Dialog_addCase.exec_()
        newCaseText = ui.getNewItem()
        if newCaseText is not None:
            #update case list and database
            # need to generate a new id as the RQDA database does not have an autoincrement id field
            newid = 1
            for fc in self.cases:
                if fc['id'] >= newid: newid = fc['id']+1
            item = {'name':newCaseText, 'memo':"", 'owner':self.settings['codername'],
                     'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':"", 'id':newid, 'status':1}
            self.cases.append(item)
            cur = self.settings['conn'].cursor()
            cur.execute("insert into cases (name,memo,owner,date,dateM,id,status) values(?,?,?,?,?,?,?)"
                        ,(item['name'],item['memo'],item['owner'],item['date'],item['dateM'],item['id'],item['status']))
            self.settings['conn'].commit()

            #update table widget
            for c in self.cases:
                self.tableWidget_cases.removeRow(0)
            self.fillTableWidget_cases()

    def deleteCase(self):
        """ When delete button pressed, case is deleted from model and database """

        tableRowsToDelete = []  # for table widget ids
        caseNamesToDelete = ""  # for confirmDelete Dialog
        idsToDelete = []  # for ids for cases and db

        for itemWidget in self.tableWidget_cases.selectedItems():
            tableRowsToDelete.append(int(itemWidget.row()))
            idsToDelete.append(int(self.tableWidget_cases.item(itemWidget.row(), self.ID_COLUMN).text()))
            caseNamesToDelete = caseNamesToDelete+"\n" + str(self.tableWidget_cases.item(itemWidget.row(),self.NAME_COLUMN).text())
            #print("X:"+ str(itemWidget.row()) + "  y:"+str(itemWidget.column()) +"  "+itemWidget.text() +"  id:"+str(self.tableWidget_codes.item(itemWidget.row(),3).text()))
        tableRowsToDelete.sort(reverse=True)

        if len(caseNamesToDelete) == 0:
            return

        Dialog_confirmDelete = QtWidgets.QDialog()
        ui = Ui_Dialog_confirmDelete(caseNamesToDelete)
        ui.setupUi(Dialog_confirmDelete)
        ok = Dialog_confirmDelete.exec_()
        if ok:
            for r in tableRowsToDelete:
                self.tableWidget_cases.removeRow(r)

            for id in idsToDelete:
                for c in self.cases:
                    if c['id'] == id:
                        self.cases.remove(c)
                        cur = self.settings['conn'].cursor()
                        #print(str(id) + "  "+ str(type(id)))
                        cur.execute("delete from cases where id = ?", [id])
                        cur.execute("delete from caselinkage where caseid = ?", [id])
                        cur.execute("delete from caseAttr where caseid = ?", [id])
                        self.settings['conn'].commit()

    def cellModified(self):
        """ If the case name has been changed in the table widget update the database """

        x = self.tableWidget_cases.currentRow()
        y = self.tableWidget_cases.currentColumn()
        if y == self.NAME_COLUMN:
            newText = str(self.tableWidget_cases.item(x, y).text()).strip()

            # check that no other case name has this text and this is not empty
            update = True
            if newText == "":
                update = False
            for c in self.cases:
                if c['name'] == newText:
                    update = False

            if update:
                # update database model
                cur = self.settings['conn'].cursor()
                cur.execute("update cases set name=? where id=?", (newText, self.cases[x]['id']))
                self.settings['conn'].commit()
                self.cases[x]['name'] = newText
            else:  # put the original text in the cell
                self.tableWidget_cases.item(x, y).setText(self.cases[x]['name'])

    def cellSelected(self):
        """ When the table widget memo cell is selected display the memo.
        Update memo text, or delete memo by clearing text.
        If a new memo also show in table widget by displaying YES in the memo column """

        x = self.tableWidget_cases.currentRow()
        y = self.tableWidget_cases.currentColumn()

        if x == -1:
            self.selectedCase = None
            self.textEd.clear()
            self.caseLinks = []
        else:
            self.selectedCase = self.cases[x]
            # clear case text viewed if the caseid has changed
            if self.caseTextViewed != [] and self.caseTextViewed[0]['caseid'] != self.selectedCase['id']:
                self.caseTextViewed = []
                self.caseLinks = []
                self.textEd.clear()

            self.unlight()
            #print("Selected case: " + str(self.selectedCase['id']) +" "+self.selectedCase['name'])

            # get caselinks for this file
            if self.selectedFile is not None:
                #print("File Selected: " + str(self.selectedFile['id'])+"  "+self.selectedFile['file'])
                self.caseLinks = []
                cur = self.settings['conn'].cursor()
                cur.execute("select caseid, fid, selfirst, selend, status, owner, date, memo from caselinkage where fid = ? and caseid = ?",
                            [self.selectedFile['id'], self.selectedCase['id']])
                result = cur.fetchall()
                for row in result:
                    self.caseLinks.append({'caseid':row[0], 'fid':row[1], 'selfirst':row[2], 'selend':row[3], 'status':row[4], 'owner':row[5],
                                        'date':row[6], 'memo':row[7]})
            self.highlight()

        if y == self.MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.cases[x]['memo'])
            ui.setupUi(Dialog_memo, "File memo " + self.cases[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()

            if memo == "":
                self.tableWidget_cases.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget_cases.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))

            # update cases list and database
            self.cases[x]['memo'] = str(memo)
            cur = self.settings['conn'].cursor()
            cur.execute("update cases set memo=? where id=?", (self.cases[x]['memo'], self.cases[x]['id']))
            self.settings['conn'].commit()

    def fillTableWidget_cases(self):
        """ Fill the table widget with case details """

        self.tableWidget_cases.setColumnCount(len(self.headerLabels))
        self.tableWidget_cases.setHorizontalHeaderLabels(self.headerLabels)
        for row, c in enumerate(self.cases):
            self.tableWidget_cases.insertRow(row)
            self.tableWidget_cases.setItem(row, self.NAME_COLUMN, QtWidgets.QTableWidgetItem(c['name']))
            memotmp = c['memo']
            if memotmp is not None and memotmp != "":
                self.tableWidget_cases.setItem(row, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            cid = c['id']
            if cid is None:
                cid = ""
            self.tableWidget_cases.setItem(row, self.ID_COLUMN, QtWidgets.QTableWidgetItem(str(cid)))

        self.tableWidget_cases.verticalHeader().setVisible(False)
        self.tableWidget_cases.resizeColumnsToContents()
        self.tableWidget_cases.resizeRowsToContents()
        self.tableWidget_cases.hideColumn(self.ID_COLUMN)

    def addFileToCase(self):
        """ When select file button is pressed a dialog of filenames is presented to the user.
        The entire text of the selected file is then added to the selected case
         """

        x = self.tableWidget_cases.currentRow()
        if x == -1:
            QtWidgets.QMessageBox.warning(None, 'Warning',"No case was selected", QtWidgets.QMessageBox.Ok)
            return

        Dialog_selectfile = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(self.source)
        ui.setupUi(Dialog_selectfile,"Select entire file for case: " + self.cases[x]['name'], "single")
        ok = Dialog_selectfile.exec_()
        if ok:
            casefile = ui.getSelected()
            newlink = {'caseid':self.cases[x]['id'], 'fid':casefile['id'], 'selfirst':0, 'selend':len(casefile['file']), 'status':1, 'owner':self.settings['codername'],
                        'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'memo':""}

            cur = self.settings['conn'].cursor()
            # check for an existing duplicated linkage first
            cur.execute("select * from caselinkage where caseid = ? and fid=? and selfirst=? and selend=?",
                         (newlink['caseid'], newlink['fid'], newlink['selfirst'], newlink['selend']))
            result = cur.fetchall()
            if len(result) > 0:
                QtWidgets.QMessageBox.warning(None,"Already Linked", "This file has already been linked to this case", QtWidgets.QMessageBox.Ok)
                return

            cur.execute("insert into caselinkage (caseid, fid, selfirst, selend, status, owner, date, memo) values(?,?,?,?,?,?,?,?)"
                        ,(newlink['caseid'],newlink['fid'],newlink['selfirst'],newlink['selend'],newlink['status'],newlink['owner'],newlink['date'], newlink['memo']))
            self.settings['conn'].commit()

    def selectFile(self):
        """ When open file button is pressed a dialog of filenames is presented to the user.
        The selected file is then used to view and for assigning text portions to cases
         """

        # clear table_widget selection - save confusion of loading file text and not having it highlighted for a currently selected case
        self.tableWidget_cases.clearSelection()
        self.caseLinks = []

        Dialog_selectfile = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(self.source)
        ui.setupUi(Dialog_selectfile,"Select file to view", "single")
        ok = Dialog_selectfile.exec_()
        if ok:
            #selectedFile is dictionary with id and name
            self.selectedFile = ui.getSelected()
            self.label_fileName.setText("File: " + self.selectedFile['name'])
            self.textEd.setPlainText(self.selectedFile['file'])
            self.caseTextViewed = []
            self.pushButton_mark.setEnabled(True)
            self.pushButton_unmark.setEnabled(True)

    def unlight(self):
        """ Remove all text highlighting from current file """

        if self.selectedFile is None:
            return
        cursor = self.textEd.textCursor()
        try:
            cursor.setPosition(0, QtWidgets.QTextCursor.MoveAnchor)
            cursor.setPosition(len(self.selectedFile['file']), QtWidgets.QTextCursor.KeepAnchor)
            cursor.setCharFormat(QtGui.QTextCharFormat())
        except:
            pass
            #print(("unlight, text length" +str(len(self.textEd.toPlainText()))))

    def highlight(self):
        """ Apply text highlighting to current file.
        Highlight text of selected case with red underlining.
        """

        format_ = QtGui.QTextCharFormat()
        #format_.setForeground(QtWidgets.QColor("#990000"))
        cursor = self.textEd.textCursor()

        for item in self.caseLinks:
            try:
                cursor.setPosition(int(item['selfirst']), QtWidgets.QTextCursor.MoveAnchor)
                cursor.setPosition(int(item['selend']), QtWidgets.QTextCursor.KeepAnchor)
                format_.setFontUnderline(True)
                format_.setUnderlineColor(QtCore.Qt.red)
                cursor.setCharFormat(format_)
            except:
                print(sys.__displayhook__(None))
                print("highlight, text length" +str(len(self.textEd.toPlainText())))
                print(item['selfirst'], item['selend'])

    def view(self):
        """ View all of the text associated with this case """

        row = self.tableWidget_cases.currentRow()
        if row == -1:
            return
        self.pushButton_mark.setEnabled(False)
        self.pushButton_unmark.setEnabled(False)
        self.label_fileName.setText("Viewing text of case: " + str(self.cases[row]['name']))
        self.textEd.clear()
        self.caseTextViewed = []
        cur = self.settings['conn'].cursor()
        cur.execute("select caseid, fid, selfirst, selend, status, owner, date, memo from caselinkage where caseid = ? order by fid, selfirst",
                    [self.selectedCase['id'],])
        result = cur.fetchall()
        for row in result:
            caseText = ""
            sourcename = ""
            for src in self.source:
                if src['id'] == row[1]:
                    caseText = src['file'][int(row[2]):int(row[3])]
                    sourcename = src['name']
            self.caseTextViewed.append({'caseid':row[0], 'fid':row[1], 'selfirst':row[2],
            'selend':row[3], 'status':row[4], 'owner':row[5], 'date':row[6], 'memo':row[7],
            'text':caseText, 'sourcename':sourcename})

        for c in self.caseTextViewed:
            #self.textEd.appendPlainText("File: " + sourcename + " Text: " + str(int(c['selfirst']))+":"+str(int(c['selend'])))
            self.textEd.appendHtml("<b>" + "File: " + c['sourcename'] + " Text: " +
            str(int(c['selfirst'])) + ":" + str(int(c['selend'])) + "</b>")
            self.textEd.appendPlainText(c['text'])

    def profileMat(self):
        """get profile matrix and show in a QTableWidget"""
        selectedRows = [e.row() for e in self.tableWidget_cases.selectedIndexes()]
        selectedCases = [self.cases[i]['name'] for i in selectedRows]
        if len(selectedRows) == 0:
            return
        selectedCases = list(set(selectedCases)) # when case memo are selected, duplicated case names are included
        cur = self.settings['conn'].cursor()
        cur.execute("select name, id, cid from freecode, coding where coding.cid=freecode.id and freecode.status=1 group by cid order by name")
        result = cur.fetchall()
        codes = []
        codeIds = []
        for code in result:
            codes.append(code[0])
            codeIds.append(code[1])
        Mat = {}
        for case in selectedCases:
            val = []
            for code in codes:
                cur.execute("select count(coding.fid) as n from coding, freecode where coding.cid=freecode.id and freecode.name=? and coding.fid in \
                    (select fid from caselinkage, cases where caselinkage.caseid=cases.id and cases.name=?)", (code, case))
                result = cur.fetchall()
                for n in result:
                    val.append(str(n[0]))
            Mat[case] = val
        Dialog_vcf = QtWidgets.QDialog()
        ui = Ui_Dialog_vcf(Mat)
        ui.setupUi(Dialog_vcf)
        ui.tableWidget.setVerticalHeaderLabels(codes)
        # hack to display code names
        Dialog_vcf.exec_()

    def mark(self):
        """ Mark selected text in file with currently selected case """

        if self.selectedFile is None:
            return
        row = self.tableWidget_cases.currentRow()
        if row == -1:
            return

        #selectedText = self.textEd.textCursor().selectedText()
        selstart = self.textEd.textCursor().selectionStart()
        selend = self.textEd.textCursor().selectionEnd()
        #add new item to caselinkage, add to database and update GUI
        item = {'caseid':int(self.cases[row]['id']), 'fid':int(self.selectedFile['id']), 'selfirst':selstart, 'selend':selend, 'status':1,
                'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'memo':""}
        self.caseLinks.append(item)
        self.highlight()

        cur = self.settings['conn'].cursor()
        # check for an existing duplicated linkage first
        cur.execute("select * from caselinkage where caseid = ? and fid=? and selfirst=? and selend=?",
                     (item['caseid'], item['fid'], item['selfirst'], item['selend']))
        result = cur.fetchall()
        if len(result) > 0:
            QtWidgets.QMessageBox.warning(None,"Already Linked","This segment has already been linked to this case", QtWidgets.QMessageBox.Ok)
            return

        cur.execute("insert into caselinkage (caseid,fid, selfirst, selend, status, owner, date, memo) values(?,?,?,?,?,?,?,?)"
                    ,(item['caseid'],item['fid'],item['selfirst'],item['selend'], item['status'],item['owner'],item['date'],item['memo']))
        self.settings['conn'].commit()

    def unmark(self):
        """ Remove case marking from selected text in selected file """

        if self.selectedFile is None:
            return
        if len(self.caseLinks) == 0:
            return

        location = self.textEd.textCursor().selectionStart()
        unmarked = None
        for item in self.caseLinks:
            if location >= item['selfirst'] and location <= item['selend']:
                unmarked = item
        if unmarked is None:
            return

        # delete from db, remove from coding and update highlights
        cur = self.settings['conn'].cursor()
        cur.execute("delete from caselinkage where fid=? and caseid = ? and selfirst =? and selend =?",
                    (unmarked['fid'], unmarked['caseid'], unmarked['selfirst'], unmarked['selend']))
        self.settings['conn'].commit()
        if unmarked in self.caseLinks:
            self.caseLinks.remove(unmarked)
        self.unlight()
        self.highlight()

    def automark(self):
        """ Automark text in one or more files with selected case """

        row = self.tableWidget_cases.currentRow()
        if row == -1:
            QtWidgets.QMessageBox.warning(None, 'Warning', "No case was selected", QtWidgets.QMessageBox.Ok)
            return

        Dialog_selectfile = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(self.source)
        ui.setupUi(Dialog_selectfile,"Select file(s) to assign case", "many") # many has no real meaning but is not 'single'
        ok = Dialog_selectfile.exec_()
        if not ok:
            return
        files = ui.getSelected()
        if len(files) == 0:
            QtWidgets.QMessageBox.warning(None, 'Warning', "No file was selected", QtWidgets.QMessageBox.Ok)
            return

        dialog =  QtWidgets.QDialog()
        ui = Ui_Dialog_autoassign(self.cases[row]['name'])
        ui.setupUi(dialog)
        ok = dialog.exec_()
        if not ok:
            return

        startMark = ui.getStartMark()
        endMark = ui.getEndMark()
        if startMark == "" or endMark == "":
            QtWidgets.QMessageBox.warning(None, 'Warning', "Cannot have blank text marks", QtWidgets.QMessageBox.Ok)
            return

        warnings = 0
        for file in files:
            cur = self.settings['conn'].cursor()
            cur.execute("select name, id, file, memo, owner, date, dateM, status from source where id=?",[file['id']])
            currentfile = cur.fetchone()
            text = currentfile[2]
            textStarts = [match.start() for match in re.finditer(re.escape(startMark), text)]
            textEnds = [match.start() for match in re.finditer(re.escape(endMark), text)]
            #print(textStarts, textEnds)

            #add new code linkage items to database
            for startPos in textStarts:
                selend = -1  #temp
                textEndIterator = 0
                try:
                    while startPos >= textEnds[textEndIterator]:
                        textEndIterator += 1
                except IndexError:
                    # could not find end mark
                    textEndIterator = -1
                    warnings += 1

                if textEndIterator >= 0:
                    selend = textEnds[textEndIterator]

                    item = {'caseid':int(self.cases[row]['id']), 'fid':int(file['id']), 'selfirst':startPos, 'selend':selend, 'status':1,
                    'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'memo':""}

                    cur = self.settings['conn'].cursor()
                    cur.execute("insert into caselinkage (caseid,fid,selfirst,selend,status,owner,date,memo) values(?,?,?,?,?,?,?,?)"
                        ,(item['caseid'], item['fid'], item['selfirst'], item['selend'], item['status'],
                          item['owner'], item['date'], item['memo']))
                    self.settings['conn'].commit()

        if warnings > 0:
            QtWidgets.QMessageBox.warning(None, 'Warning',str(warnings)+" end mark did not match up", QtWidgets.QMessageBox.Ok)

        self.tableWidget_cases.clearSelection()

    #END ADDIN


    def setupUi(self, Dialog_cases):
        Dialog_cases.setObjectName(_fromUtf8("Dialog_cases"))
        w = QtWidgets.QApplication.desktop().width()
        h = QtWidgets.QApplication.desktop().height()
        if w > 1200: w = 1200
        if h > 800: h = 800
        Dialog_cases.resize(w, h-80)
        Dialog_cases.move(20, 20)

        self.pushButton_add = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_add.setGeometry(QtCore.QRect(10, 10, 98, 27))
        self.pushButton_add.setObjectName(_fromUtf8("pushButton_add"))
        self.pushButton_delete = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_delete.setGeometry(QtCore.QRect(260, 10, 98, 27))
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.pushButton_addfiles = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_addfiles.setGeometry(QtCore.QRect(110, 10, 131, 27))
        self.pushButton_addfiles.setObjectName(_fromUtf8("pushButton_addfiles"))
        self.pushButton_addfiles.setToolTip("Add entire file to selected case")
        self.pushButton_view = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_view.setGeometry(QtCore.QRect(10, 50, 98, 27))
        self.pushButton_view.setObjectName(_fromUtf8("pushButton_view"))
        self.pushButton_profile = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_profile.setGeometry(QtCore.QRect(110, 50, 131, 27))
        self.pushButton_profile.setObjectName(_fromUtf8("pushButton_profile"))
        self.pushButton_profile.setToolTip("Profile matrix of the selected cases")
        self.pushButton_openfile = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_openfile.setGeometry(QtCore.QRect(380, 10, 98, 27))
        self.pushButton_openfile.setObjectName(_fromUtf8("pushButton_openfile"))
        self.pushButton_openfile.setToolTip("Open a file to assign file portions to a case")
        self.pushButton_autoassign = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_autoassign.setGeometry(QtCore.QRect(480, 10, 151, 27))
        self.pushButton_autoassign.setObjectName(_fromUtf8("pushButton_autoassign"))
        self.pushButton_autoassign.setToolTip("Assign selected case to portions of files using start and end marks")
        self.pushButton_unmark = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_unmark.setGeometry(QtCore.QRect(500, 50, 131, 27))
        self.pushButton_unmark.setObjectName(_fromUtf8("pushButton_unmark"))
        self.pushButton_mark = QtWidgets.QPushButton(Dialog_cases)
        self.pushButton_mark.setGeometry(QtCore.QRect(380, 50, 111, 27))
        self.pushButton_mark.setObjectName(_fromUtf8("pushButton_mark"))

        #ADDIN
        self.splitter = QtWidgets.QSplitter(Dialog_cases)
        self.splitter.setGeometry(QtCore.QRect(10, 90, w - 20, h - 200))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        #ENDADDIN
        
        self.tableWidget_cases = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget_cases.setGeometry(QtCore.QRect(10, 90, 461, h - 200))
        self.tableWidget_cases.setObjectName(_fromUtf8("tableWidget_cases"))
        self.tableWidget_cases.setColumnCount(0)
        self.tableWidget_cases.setRowCount(0)
        self.tableWidget_cases.setSortingEnabled(True)
        #self.pushButton_attributes = QtWidgets.QPushButton(Dialog_cases)
        #self.pushButton_attributes.setGeometry(QtCore.QRect(110, 50, 131, 27))
        #self.pushButton_attributes.setObjectName(_fromUtf8("pushButton_attributes"))

        # ADDIN
        self.pushButton_mark.setEnabled(False)
        self.pushButton_unmark.setEnabled(False)

        self.label_fileName = QtWidgets.QLabel(Dialog_cases)
        self.label_fileName.setGeometry(QtCore.QRect(650, 10, w - 550, 30))
        self.label_fileName.setObjectName(_fromUtf8("label_fileName"))
        self.label_fileName.setText("File: Not selected")

        self.fillTableWidget_cases()

        self.textEd = QtWidgets.QPlainTextEdit(self.splitter)
        self.textEd.setReadOnly(True)
        self.textEd.setGeometry(QtCore.QRect(500, 90, w - 550, h-200))
        self.textEd.setObjectName(_fromUtf8("textEd"))
        self.textEd.setPlainText("")
        self.textEd.setAutoFillBackground(True)

        self.pushButton_add.clicked.connect(self.addCase)
        self.pushButton_delete.clicked.connect(self.deleteCase)
        self.tableWidget_cases.itemChanged.connect(self.cellModified)
        self.tableWidget_cases.cellClicked.connect(self.cellSelected)
        self.pushButton_addfiles.clicked.connect(self.addFileToCase)
        self.pushButton_openfile.clicked.connect(self.selectFile)
        self.pushButton_mark.clicked.connect(self.mark)
        self.pushButton_unmark.clicked.connect(self.unmark)
        self.pushButton_autoassign.clicked.connect(self.automark)
        self.pushButton_view.clicked.connect(self.view)
        self.pushButton_profile.clicked.connect(self.profileMat)

        # END ADDIN

        self.retranslateUi(Dialog_cases)
        QtCore.QMetaObject.connectSlotsByName(Dialog_cases)


    def retranslateUi(self, Dialog_cases):
        Dialog_cases.setWindowTitle(_translate("Dialog_cases", "Cases", None))
        self.pushButton_add.setText(_translate("Dialog_cases", "Add case", None))
        self.pushButton_delete.setText(_translate("Dialog_cases", "Delete case", None))
        self.pushButton_addfiles.setText(_translate("Dialog_cases", "Add File to case", None))
        self.pushButton_view.setText(_translate("Dialog_cases", "View case", None))
        self.pushButton_openfile.setText(_translate("Dialog_cases", "Open file", None))
        self.pushButton_autoassign.setText(_translate("Dialog_cases", "Auto assign file text", None))
        self.pushButton_unmark.setText(_translate("Dialog_cases", "Unmark file text", None))
        self.pushButton_mark.setText(_translate("Dialog_cases", "Mark file text", None))
        self.pushButton_profile.setText(_translate("Dialog_cases", "Profile matrix", None))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_cases = QtWidgets.QDialog()
    ui = Ui_Dialog_cases()
    ui.setupUi(Dialog_cases)
    Dialog_cases.show()
    sys.exit(app.exec_())
