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
from PyQt5.Qt import QHelpEvent
import datetime
from operator import itemgetter
from CodeColors import CodeColors
from ColorSelector import Ui_Dialog_colorselect
from Memo import Ui_Dialog_memo
from AddItem import Ui_Dialog_addItem
from ConfirmDelete import Ui_Dialog_confirmDelete
from SelectFile import Ui_Dialog_selectfile
import re

#from FixUnicode import FixUnicode
#END

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s


class Ui_Dialog_codes(object):
    """
    Code management. Add, delete codes. Mark and unmark text. Add memos and
    colors to codes.
    """

    #ADDIN
    NAME_COLUMN = 0
    COLOR_COLUMN = 1
    MEMO_COLUMN = 2
    ID_COLUMN = 3
    headerLabels = ["Code", "Color", "Memo", "id"]

    settings = None
    freecode = []
    codeColors = CodeColors()
    filenames = []
    filename = {}  # contains filename and file id returned from SelectFile
    sourceText = None
    coding = []
    annotations = []

    eventFilter = None

    def __init__(self, settings):
        self.freecode = []
        self.filenames = []
        self.fileId = '' # file Id of the open file in Editor
        self.annotations = []
        self.settings = settings

        cur = self.settings['conn'].cursor()
        cur.execute("select name, memo, owner, date, dateM, id, status, color from freecode")
        result = cur.fetchall()
        for row in result:
            self.freecode.append({'name': row[0], 'memo': row[1], 'owner': row[2],
            'date': row[3], 'dateM':row[4], 'id': row[5], 'status': row[6], 'color': row[7]})

        cur.execute("select id, name, status from source")
        result = cur.fetchall()
        for row in result:
            self.filenames.append({'id': row[0], 'name': row[1], 'status': row[2]})

        cur.execute("select fid, position, annotation, owner, date, dateM, status from annotation")
        result = cur.fetchall()
        for row in result:
            self.annotations.append({'fid': row[0], 'position': row[1], 'annotation': row[2], 'owner': row[3], 'date': row[4], 'dateM': row[5], 'status': row[6]})

    def cellSelected(self):
        """ When cell selected in table widget, do something: change a code
        colour, change a code memo """

        x = self.tableWidget_codes.currentRow()
        y = self.tableWidget_codes.currentColumn()

        if y == self.COLOR_COLUMN:
            #print(self.freecode[x]['color'])
            Dialog_colorselect = QtWidgets.QDialog()
            ui = Ui_Dialog_colorselect(self.freecode[x]['color'])
            ui.setupUi(Dialog_colorselect)
            ok = Dialog_colorselect.exec_()
            if ok:
                selectedColor = ui.getColor()
                if selectedColor is not None:
                    item = QtWidgets.QTableWidgetItem()  # an empty item, used to have color name
                    item.setBackground(QtGui.QBrush(QtGui.QColor(selectedColor['hex'])))
                    self.tableWidget_codes.setItem(x, self.COLOR_COLUMN, item)
                    self.tableWidget_codes.clearSelection()

                    #update freecode list, database and currently viewed file
                    self.freecode[x]['color'] = selectedColor['colname']
                    cur = self.settings['conn'].cursor()
                    cur.execute("update freecode set color=? where id=?", (self.freecode[x]['color'], self.freecode[x]['id']))
                    self.settings['conn'].commit()
                    self.unlight()
                    self.highlight()

        if y == self.MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.freecode[x]['memo'])
            ui.setupUi(Dialog_memo, "Code memo " + self.freecode[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()

            if memo == "":
                self.tableWidget_codes.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget_codes.setItem(x, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))

            #update freecode list and database
            self.freecode[x]['memo'] = str(memo)
            cur = self.settings['conn'].cursor()
            cur.execute("update freecode set memo=? where id=?", (self.freecode[x]['memo'], self.freecode[x]['id']))
            self.settings['conn'].commit()

    def cellModified(self):
        """ When a code name is changed in the table widget update the details in model
        and database """

        x = self.tableWidget_codes.currentRow()
        y = self.tableWidget_codes.currentColumn()
        if y == self.NAME_COLUMN:
            #newCodeText = str(self.tableWidget_codes.item(x, y).text())
            newCodeText = self.tableWidget_codes.item(x, y).text()
            # check that no other code has this text and this is is not empty
            update = True
            if newCodeText == "":
                update = False
            for c in self.freecode:
                if c['name'] == newCodeText:
                    update = False
            if update:
                #update freecode list and database
                self.freecode[x]['name'] = newCodeText
                cur = self.settings['conn'].cursor()
                cur.execute("update freecode set name=? where id=?", (newCodeText, self.freecode[x]['id']))
                self.settings['conn'].commit()
                # update filter for tooltip
                self.eventFilter.setCodes(self.coding, self.freecode)

            else:  #put the original text in the cell
                self.tableWidget_codes.item(x, y).setText(self.freecode[x]['name'])

    def addCode(self):
        """ open addItem dialog to get new code text.
        AddItem dialog checks for duplicate code name.
        New code is added to the model and database """

        Dialog_addCode = QtWidgets.QDialog()
        ui = Ui_Dialog_addItem(self.freecode)
        ui.setupUi(Dialog_addCode, "Code")
        Dialog_addCode.exec_()
        newCodeText = ui.getNewItem()
        if newCodeText is not None:
            # update freecode list and database
            # need to generate a new id as the RQDA database does not have an autoincrement id field
            newid = 1
            for fc in self.freecode:
                if fc['id'] >= newid: newid = fc['id']+1
            item = {'name':newCodeText, 'memo':"", 'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':"", 'id':newid, 'status':1, 'color':""}
            self.freecode.append(item)
            cur = self.settings['conn'].cursor()
            cur.execute("insert into freecode (name,memo,owner,date,dateM,id,status,color) values(?,?,?,?,?,?,?,?)"
                        ,(item['name'],item['memo'],item['owner'],item['date'],item['dateM'],item['id'],item['status'],item['color']))
            self.settings['conn'].commit()

            # update table widget
            for codes in self.freecode:
                self.tableWidget_codes.removeRow(0)
            self.fillTableWidget_codes()

    def deleteCode(self):
        """ When delete button pressed, code is deleted from model and database """

        tableRowsToDelete = []  # for table widget ids
        codeNamesToDelete = ""  # for confirmDelete Dialog
        idsToDelete = []  # for ids for freecode and db

        for itemWidget in self.tableWidget_codes.selectedItems():
            tableRowsToDelete.append(int(itemWidget.row()))
            idsToDelete.append(int(self.tableWidget_codes.item(itemWidget.row(), self.ID_COLUMN).text()))
            codeNamesToDelete = codeNamesToDelete+"\n" + self.tableWidget_codes.item(itemWidget.row(), self.NAME_COLUMN).text()
            #codeNamesToDelete = codeNamesToDelete.decode("utf-8")
            #print("X:"+ str(itemWidget.row()) + "  y:"+str(itemWidget.column()) +"  "+itemWidget.text() +"  id:"+str(self.tableWidget_codes.item(itemWidget.row(),3).text()))
        tableRowsToDelete.sort(reverse=True)

        if len(codeNamesToDelete) == 0:
            return

        Dialog_confirmDelete = QtWidgets.QDialog()
        ui = Ui_Dialog_confirmDelete(codeNamesToDelete)
        ui.setupUi(Dialog_confirmDelete)
        ok = Dialog_confirmDelete.exec_()
        if ok:
            for r in tableRowsToDelete:
                self.tableWidget_codes.removeRow(r)

            for id in idsToDelete:
                for code in self.freecode:
                    if code['id'] == id:
                        self.freecode.remove(code)
                        cur = self.settings['conn'].cursor()
                        #print(str(id) + "  "+ str(type(id)))
                        cur.execute("delete from coding where cid = ?", [id])
                        cur.execute("delete from coding2 where cid = ?", [id])
                        cur.execute("delete from freecode where id = ?", [id])
                        cur.execute("delete from treecode where cid=?", [id])
                        self.settings['conn'].commit()
            # remove coding in relation to the deleted code
            self.update_coding()
            # update filter for tooltip and text edit
            self.eventFilter.setCodes(self.coding, self.freecode)
            self.unlight()
            self.highlight()

    def update_coding(self):
        self.coding = []
        cur = self.settings['conn'].cursor()
        codingsql = "select cid, fid, seltext, selfirst, selend, status, owner, date, memo from coding"
        if self.settings['codertable'] == "coding2":
            codingsql = "select cid, fid, seltext, selfirst, selend, status, owner, date, memo from coding2"
        codingsql = codingsql + " where fid = ? and status = 1"
        cur.execute(codingsql, [self.fileId])
        result = cur.fetchall()
        for row in result:
            self.coding.append({'cid': row[0], 'fid': row[1], 'seltext': row[2], 'selfirst': row[3], 'selend':row[4], 'status':row[5], 'owner': row[6], 'date': row[7], 'memo': row[8]})

    def selectFile(self):
        """ When select file button is pressed a dialog of filenames is presented to the user.
        The selected file is then used to view and do coding
         """

        Dialog_selectfile = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(self.filenames)
        ui.setupUi(Dialog_selectfile, "Select file to view", "single")
        ok = Dialog_selectfile.exec_()
        if ok:
            #filename is dictionary with id and name
            self.filename = ui.getSelected()
            cur = self.settings['conn'].cursor()
            cur.execute("select name, id, file, memo, owner, date, dateM, status from source where id=?",[self.filename['id']])
            result = cur.fetchone()
            self.sourceText = result[2]
            self.fileId = int(result[1])
            self.label_fileName.setText("File "+ str(result[1]) + " : " + result[0])

            #get codings for this file and coder
            self.coding = []
            codingsql = "select cid, fid, seltext, selfirst, selend, status, owner, date, memo from coding"
            if self.settings['codertable'] == "coding2":
                codingsql = "select cid, fid, seltext, selfirst, selend, status, owner, date, memo from coding2"
            codingsql = codingsql + " where fid = ? and status = 1"
            cur.execute(codingsql, [self.fileId])
            result = cur.fetchall()
            for row in result:
                self.coding.append({'cid': row[0], 'fid': row[1], 'seltext': row[2], 'selfirst': row[3], 'selend':row[4], 'status':row[5], 'owner': row[6], 'date': row[7], 'memo': row[8]})

            self.textEd.setPlainText(self.sourceText)
            # update filter for tooltip
            self.eventFilter.setCodes(self.coding, self.freecode)

            # redo formatting
            self.unlight()
            self.highlight()
        else:
            self.textEd.clear()

    def unlight(self):
        """ Remove all text highlighting from current file """
        if self.sourceText is None:
            print("No file is open.")
        else:
            cursor = self.textEd.textCursor()
            cursor.setPosition(0, QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(len(self.sourceText), QtGui.QTextCursor.KeepAnchor)
            cursor.setCharFormat(QtGui.QTextCharFormat())

    def highlight(self):
        """ Apply text highlighting to current file.
        If no colour has been assigned to a code, those coded text fragments are coloured gray """

        fmt = QtGui.QTextCharFormat()
        cursor = self.textEd.textCursor()

        # add coding highlights
        for item in self.coding:
            cursor.setPosition(int(item['selfirst']), QtGui.QTextCursor.MoveAnchor)
            cursor.setPosition(int(item['selend']), QtGui.QTextCursor.KeepAnchor)

            freecodeindex = list(map(itemgetter('id'), self.freecode)).index(item['cid'])
            # map return an iter in py3
            colors = CodeColors()
            colorhex = colors.getHexFromName(self.freecode[freecodeindex]['color'])
            if colorhex == "":
                colorhex = "#CCCCCC"
            fmt.setBackground(QtGui.QBrush(QtGui.QColor(colorhex)))
            # highlight codes with memos - these are italicised
            if item['memo'] is not None and item['memo'] != "":
                fmt.setFontItalic(True)
            else:
                fmt.setFontItalic(False)
                fmt.setFontWeight(QtGui.QFont.Normal)
            cursor.setCharFormat(fmt)

        # add annotation marks - these are in bold
        textLength = len(self.textEd.toPlainText())
        for note in self.annotations:
            if len(self.filename.keys()) > 0: # it will be zero if using autocode and no file is loaded
                if note['fid'] == self.filename['id']:
                    cursor.setPosition(int(note['position']), QtGui.QTextCursor.MoveAnchor)
                    if note['position'] + 1 > textLength:
                        pass
                    cursor.setPosition(int(note['position'] + 1), QtGui.QTextCursor.KeepAnchor)
                    formatB = QtGui.QTextCharFormat()
                    formatB.setFontWeight(QtGui.QFont.Bold)
                    cursor.mergeCharFormat(formatB)

    def mark(self):
        """ Mark selected text in file with currently selected code.
       Need to check for multiple same codes at same selfirst and selend
       """

        if self.filename == {}:
            QtWidgets.QMessageBox.warning(None, 'Warning', "No file was selected", QtWidgets.QMessageBox.Ok)
            return
        row = self.tableWidget_codes.currentRow()
        if row == -1:
            QtWidgets.QMessageBox.warning(None, 'Warning', "No code was selected", QtWidgets.QMessageBox.Ok)
            return

        selectedText = self.textEd.textCursor().selectedText()
        #selectedText = unicode(selectedText)
        selstart = self.textEd.textCursor().selectionStart()
        selend = self.textEd.textCursor().selectionEnd()
        #add new item to coding, add to database and update GUI
        item = {'cid':int(self.freecode[row]['id']), 'fid':int(self.filename['id']),
        'seltext':selectedText, 'selfirst':selstart, 'selend':selend,
        'owner':self.settings['codername'], 'memo':"", 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'status':1}
        self.coding.append(item)
        self.highlight()
        cur = self.settings['conn'].cursor()

        # check for an existing duplicated marking first
        cur.execute("select * from " + self.settings['codertable'] + " where cid = ? and fid=? and selfirst=? and selend=?",
                     (item['cid'], item['fid'], item['selfirst'], item['selend']))
        result = cur.fetchall()
        if len(result) > 0:
            QtWidgets.QMessageBox.warning(None,"Already Coded", "This segment has already been coded with this code", QtWidgets.QMessageBox.Ok)
            return

        cur.execute("insert into "+self.settings['codertable']+" (cid,fid,seltext,selfirst,selend,owner,memo,date,status) values(?,?,?,?,?,?,?,?,?)"
                    ,(item['cid'], item['fid'], item['seltext'], item['selfirst'], item['selend'], item['owner'], item['memo'], item['date'],item['status']))
        self.settings['conn'].commit()
        # update filter for tooltip
        self.eventFilter.setCodes(self.coding, self.freecode)

    def codeInLabel(self):
        """ When coded text is clicked on, the code name is displayed in the label above the text
        edit widget. """

        labelText = "Code: "
        self.label_code.setText(labelText)
        pos = self.textEd.textCursor().position()
        for item in self.coding:
            if item['selfirst'] <= pos and item['selend'] >= pos:
                # print str(item['selfirst'])+"  "+str(item['selend'])
                for code in self.freecode:
                    if code['id'] == item['cid']:
                        labelText = "Code: " + code['name']
        self.label_code.setText(labelText)

    def unmark(self):
        """ Remove code marking from selected text in file """

        if self.filename == {}:
            return
        location = self.textEd.textCursor().selectionStart()
        #print location
        unmarked = None
        for item in self.coding:
            #print item['selfirst'], item['selend']
            if location >= item['selfirst'] and location <= item['selend']:
                unmarked = item
        if unmarked is None:
            return

        # delete from db, remove from coding and update highlights
        cur = self.settings['conn'].cursor()
        cur.execute("delete from " + self.settings['codertable'] + " where cid=? and selfirst =? and selend =?",
                    (unmarked['cid'], unmarked['selfirst'], unmarked['selend']))
        self.settings['conn'].commit()
        if unmarked in self.coding:
            self.coding.remove(unmarked)

        # update filter for tooltip and update code colours
        self.eventFilter.setCodes(self.coding, self.freecode)
        self.unlight()
        self.highlight()

    def codeMemo(self):
        """ Add a memo to the selected code """

        if self.filename == {}:
            QtWidgets.QMessageBox.warning(None, 'Warning', "No file was selected", QtWidgets.QMessageBox.Ok)
            return
        location = self.textEd.textCursor().selectionStart()
        codehere = None
        for item in self.coding:
            if location >= item['selfirst'] and location <= item['selend']:
                codehere = item
        if codehere is None:
            return

        Dialog_memo = QtWidgets.QDialog()
        ui = Ui_Dialog_memo(codehere['memo'])
        ui.setupUi(Dialog_memo, "Memo the code here <" + str(codehere['selfirst']) + " - " + str(codehere['selend']) +"> ")
        Dialog_memo.exec_()
        memo = ui.getMemo()
        cur = self.settings['conn'].cursor()
        cur.execute("update " + self.settings['codertable'] + " set memo=? where cid=? and selfirst =? and selend =?",
                    (memo, codehere['cid'], codehere['selfirst'], codehere['selend']))
        self.settings['conn'].commit()

        # why are these here ?
        self.unlight()
        self.highlight()

    def annotate(self):
        """ Add an annotation: or memo text to the current cursor position.
        The position is at a point infornt of the cursor.
        Annotations are displayed as a bolded character when text is highlighted """

        annotation = ""
        details = ""
        item = None
        if self.filename == {}:
            QtWidgets.QMessageBox.warning(None, 'Warning', "No file was selected", QtWidgets.QMessageBox.Ok)
            return
        selstart = self.textEd.textCursor().selectionStart()
        textLength = len(self.textEd.toPlainText())
        if selstart >= textLength:
            return

        for note in self.annotations:
            if note['position'] == selstart and note['fid'] == self.filename['id']:
                item = note  # use existing annotation
                details = item['owner']+ " "+item['date']

        # add new item to annotations, add to database and update GUI
        if item is None:
            #item = {'fid': int(self.filename['id']), 'position': selstart, 'annotation': str(annotation), 'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':None, 'status':1}
            item = {'fid': int(self.filename['id']), 'position': selstart, 'annotation': annotation, 'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':None, 'status':1}

        Dialog_memo = QtWidgets.QDialog()
        ui = Ui_Dialog_memo(item['annotation'])
        ui.setupUi(Dialog_memo, "Annotation: " + details)
        Dialog_memo.exec_()
        item['annotation'] = ui.getMemo()

        # if blank then delete the annotation
        if item['annotation'] == "":
            cur = self.settings['conn'].cursor()
            cur.execute("delete from annotation where position = ?", (item['position'], ))  # note comma, this is a tuple
            self.settings['conn'].commit()
            for note in self.annotations:
                if note['position'] == item['position'] and note['fid'] == item['fid']:
                    self.annotations.remove(note)
            self.unlight()
            self.highlight()

        if item['annotation'] != "":
            self.annotations.append(item)
            self.highlight()
            cur = self.settings['conn'].cursor()
            ##cur.execute("insert into annotation"+" (fid,position,annotation,owner,date,dateM,status) values(?,?,?,?,?,?,?)"
            ##            ,(item['fid'],item['position'],item['annotation'].encode('raw_unicode_escape'),item['owner'],item['date'],item['dateM'],item['status']))
            cur.execute("insert into annotation"+" (fid,position,annotation,owner,date,dateM,status) values(?,?,?,?,?,?,?)"
                        ,(item['fid'],item['position'],item['annotation'], item['owner'],item['date'],item['dateM'],item['status']))
            self.settings['conn'].commit()

    def autocode(self):
        """ Autocode text in one file or all files with selected code """

        row = self.tableWidget_codes.currentRow()
        if row == -1:
            QtWidgets.QMessageBox.warning(None, 'Warning',"No code was selected", QtWidgets.QMessageBox.Ok)
            return

        #text, ok = QtWidgets.QInputDialog.getText(None, 'Autocode a word or phrase', 'Phrase:')
        # dialog too narrow, so code below
        dialog =  QtWidgets.QInputDialog(None)
        dialog.setWindowTitle("Autocode")
        dialog.setInputMode( QtWidgets.QInputDialog.TextInput)
        dialog.setLabelText("Autocode a word or phrase with:\n" + str(self.freecode[row]['name']))
        dialog.resize(200, 20)
        ok = dialog.exec_()
        if not ok:
            return

        findText = str(dialog.textValue())
        if findText == "" or findText is None:
            return

        dialog_context = QtWidgets.QInputDialog(None)
        dialog_context.setWindowTitle("Autocode context")
        dialog_context.setInputMode( QtWidgets.QInputDialog.IntInput)
        dialog_context.setIntValue(50)
        dialog_context.setIntMinimum(0)
        dialog_context.setIntMaximum(200)
        dialog_context.setLabelText("How many nearby words words are included?")
        dialog_context.resize(200, 20)
        ok = dialog_context.exec_()
        if not ok:
            return
        context = dialog_context.intValue()

        Dialog_selectfile = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(self.filenames)
        ui.setupUi(Dialog_selectfile,"Select file to view", "many")  # many has no meaning but is not 'single'
        ok = Dialog_selectfile.exec_()
        if not ok:
            return
        files = ui.getSelected()
        if len(files) == 0:
            return

        for file in files:
            cur = self.settings['conn'].cursor()
            cur.execute("select name, id, file, memo, owner, date, dateM, status from source where id=?",[file['id']])
            currentfile = cur.fetchone()
            text = currentfile[2]
            textStarts = [match.start() for match in re.finditer(re.escape(findText), text)]

            #add new items to database
            for startPos in textStarts:
                startPos = startPos - context
                endPos = startPos + len(findText) + context*2
                if startPos < 0:
                    startPos = 0
                if endPos > len(text):
                    endPos = len(text)
                seltext = text[startPos:endPos]
                item = {'cid':int(self.freecode[row]['id']), 'fid':int(file['id']), 'seltext':seltext, 'selfirst':startPos,
                         'selend':endPos, 'owner':self.settings['codername'], 'memo':"",
                          'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'status':1}
                #print item
                cur = self.settings['conn'].cursor()
                cur.execute("insert into " + self.settings['codertable'] + " (cid,fid,seltext,selfirst,selend,owner,memo,date,status) values(?,?,?,?,?,?,?,?,?)"
                    ,(item['cid'], item['fid'], item['seltext'],
                    item['selfirst'], item['selend'], item['owner'], item['memo'], item['date'],
                    item['status']))
                self.settings['conn'].commit()

                # if this is the currently open file update the coding list and GUI
                if "id" in self.filename and file['id'] == self.filename['id']:
                    self.coding.append(item)
            self.highlight()

    def fillTableWidget_codes(self):

        """ Fill the table widget with the model details """

        self.tableWidget_codes.setColumnCount(len(self.headerLabels))
        self.tableWidget_codes.setHorizontalHeaderLabels(self.headerLabels)
        for row, code in enumerate(self.freecode):
            self.tableWidget_codes.insertRow(row)
            self.tableWidget_codes.setItem(row, self.NAME_COLUMN, QtWidgets.QTableWidgetItem(code['name']))
            colnametmp = code['color']
            if colnametmp is None:
                colnametmp = ""
            item = QtWidgets.QTableWidgetItem()  # an empty item, used to have color name
            colorHex = self.codeColors.getHexFromName(colnametmp)
            if colorHex != "":
                item.setBackground(QtGui.QBrush(QtGui.QColor(colorHex)))
            self.tableWidget_codes.setItem(row, self.COLOR_COLUMN, item)
            mtmp = code['memo']
            if mtmp is not None and mtmp != "":
                self.tableWidget_codes.setItem(row, self.MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            cid = code['id']
            if cid is None:
                cid = ""
            self.tableWidget_codes.setItem(row, self.ID_COLUMN, QtWidgets.QTableWidgetItem(str(cid)))

        self.tableWidget_codes.verticalHeader().setVisible(False)
        self.tableWidget_codes.resizeColumnsToContents()
        self.tableWidget_codes.resizeRowsToContents()
        if not self.settings['showIDs']:
            self.tableWidget_codes.hideColumn(self.ID_COLUMN)
    #END ADDIN

    def setupUi(self, Dialog_codes, settings):
        Dialog_codes.setObjectName(_fromUtf8("Dialog_codes"))
        #w = QtWidgets.QApplication.desktop().width()
        #h = QtWidgets.QApplication.desktop().height()
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        h = sizeObject.height()
        w = sizeObject.width()
        #print ("w" + str(w)+" h"+str(h))
        w = min([w * 0.8, 1200])
        h =min([h*0.8, 800])
        #if w > 1200: w = 1200
        #if h > 800: h = 800
        #if h > 600: h = 600  #temporary for testing to allow me to view the console while program runs
        Dialog_codes.resize(w, h - 80)
        Dialog_codes.move(20, 20)

        self.pushButton_add = QtWidgets.QPushButton(Dialog_codes)
        self.pushButton_add.setGeometry(QtCore.QRect(10, 10, 98, 27))
        self.pushButton_add.setObjectName(_fromUtf8("pushButton_add"))
        self.pushButton_delete = QtWidgets.QPushButton(Dialog_codes)
        self.pushButton_delete.setGeometry(QtCore.QRect(130, 10, 98, 27))
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.pushButton_viewfile = QtWidgets.QPushButton(Dialog_codes)
        self.pushButton_viewfile.setGeometry(QtCore.QRect(250, 10, 98, 27))
        self.pushButton_viewfile.setObjectName(_fromUtf8("pushButton_viewfile"))
        #self.pushButton_memo = QtWidgets.QPushButton(Dialog_codes)
        #self.pushButton_memo.setGeometry(QtCore.QRect(370, 10, 98, 27))
        #self.pushButton_memo.setObjectName(_fromUtf8("pushButton_memo"))
        self.pushButton_annotate = QtWidgets.QPushButton(Dialog_codes)
        self.pushButton_annotate.setGeometry(QtCore.QRect(10, 50, 98, 27))
        self.pushButton_annotate.setObjectName(_fromUtf8("pushButton_annotate"))
        self.pushButton_autocode = QtWidgets.QPushButton(Dialog_codes)
        self.pushButton_autocode.setGeometry(QtCore.QRect(130, 50, 98, 27))
        self.pushButton_autocode.setObjectName(_fromUtf8("pushButton_autocode"))
        self.pushButton_unmark = QtWidgets.QPushButton(Dialog_codes)
        self.pushButton_unmark.setGeometry(QtCore.QRect(250, 50, 98, 27))
        self.pushButton_unmark.setObjectName(_fromUtf8("pushButton_unmark"))
        self.pushButton_mark = QtWidgets.QPushButton(Dialog_codes)
        self.pushButton_mark.setGeometry(QtCore.QRect(370, 50, 98, 27))
        self.pushButton_mark.setObjectName(_fromUtf8("pushButton_mark"))
        #ADDIN SPLITTER
        self.splitter = QtWidgets.QSplitter(Dialog_codes)
        self.splitter.setGeometry(QtCore.QRect(10, 90, w - 20, h - 200))
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        #END ADDIN

        #self.tableWidget_codes = QtWidgets.QTableWidget(Dialog_codes)
        self.tableWidget_codes = QtWidgets.QTableWidget(self.splitter) # ADDED splitter
        self.tableWidget_codes.setGeometry(QtCore.QRect(10, 90, 461, h - 200))
        self.tableWidget_codes.setObjectName(_fromUtf8("tableWidget_codes"))
        self.tableWidget_codes.setColumnCount(0)
        self.tableWidget_codes.setRowCount(0)
        self.tableWidget_codes.setSelectionMode( QtWidgets.QAbstractItemView.SingleSelection )

        #ADDIN
        self.fillTableWidget_codes()
        self.textEd = QtWidgets.QPlainTextEdit(self.splitter)
        self.textEd.setReadOnly(True)
        self.textEd.setGeometry(QtCore.QRect(500, 90, w - 550, h - 200))
        self.textEd.setObjectName(_fromUtf8("textEd"))
        self.textEd.setPlainText("")
        self.textEd.setAutoFillBackground(True)
        self.textEd.setToolTip("jj")
        self.textEd.setMouseTracking(True) #
        self.eventFilter = TT_EventFilter()
        self.textEd.installEventFilter(self.eventFilter)

        self.label_coder = QtWidgets.QLabel(Dialog_codes)
        self.label_coder.setGeometry(QtCore.QRect(500, 0, w - 550, 30))
        self.label_coder.setObjectName(_fromUtf8("label_coder"))
        self.label_coder.setText("Coder: " + settings['codername'] + "   Coder table: " + settings['codertable'])
        self.label_fileName = QtWidgets.QLabel(Dialog_codes)
        self.label_fileName.setGeometry(QtCore.QRect(500, 25, w - 550, 30))
        self.label_fileName.setObjectName(_fromUtf8("label_fileName"))
        self.label_fileName.setText("File: Not selected")
        self.label_code = QtWidgets.QLabel(Dialog_codes)
        self.label_code.setGeometry(QtCore.QRect(500, 50, w - 550, 30))
        self.label_code.setObjectName(_fromUtf8("label_code"))
        self.label_code.setText("Code: ")

        self.tableWidget_codes.cellClicked.connect(self.cellSelected)
        self.tableWidget_codes.itemChanged.connect(self.cellModified)
        self.pushButton_add.clicked.connect(self.addCode)
        self.pushButton_delete.clicked.connect(self.deleteCode)
        self.pushButton_viewfile.clicked.connect(self.selectFile)
        self.pushButton_mark.clicked.connect(self.mark)
        self.pushButton_unmark.clicked.connect(self.unmark)
        #self.pushButton_memo.clicked.connect(self.codeMemo)
        self.pushButton_annotate.clicked.connect(self.annotate)
        self.pushButton_autocode.clicked.connect(self.autocode)
        self.textEd.cursorPositionChanged.connect(self.codeInLabel)

        #END ADDIN

        self.retranslateUi(Dialog_codes)
        QtCore.QMetaObject.connectSlotsByName(Dialog_codes)


    def retranslateUi(self, Dialog_codes):
        Dialog_codes.setWindowTitle(QtWidgets.QApplication.translate("Dialog_codes", "Codes", None, 1))
        self.pushButton_add.setText(QtWidgets.QApplication.translate("Dialog_codes", "Add", None, 1))
        self.pushButton_delete.setText(QtWidgets.QApplication.translate("Dialog_codes", "Delete", None, 1))
        self.pushButton_viewfile.setText(QtWidgets.QApplication.translate("Dialog_codes", "View File", None, 1))
        #self.pushButton_memo.setText(QtWidgets.QApplication.translate("Dialog_codes", "Memo", None, 1))
        self.pushButton_annotate.setText(QtWidgets.QApplication.translate("Dialog_codes", "Annotate", None, 1))
        self.pushButton_autocode.setText(QtWidgets.QApplication.translate("Dialog_codes", "Auto Code", None, 1))
        self.pushButton_unmark.setText(QtWidgets.QApplication.translate("Dialog_codes", "Unmark", None, 1))
        self.pushButton_mark.setText(QtWidgets.QApplication.translate("Dialog_codes", "Mark", None, 1))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_codes = QtWidgets.QDialog()
    ui = Ui_Dialog_codes()
    ui.setupUi(Dialog_codes)
    Dialog_codes.show()
    sys.exit(app.exec_())


class TT_EventFilter(QtCore.QObject):
    """ Used to add a dynmic tooltip for the textEdit.
    The tool top text is changed according to its position in the text.
    If over a coded section the codename is displayed in the tooltip. """
    coding = None
    freecodes = None

    def setCodes(self, coding, codes):
        self.coding = coding
        self.freecodes = codes
        for item in self.coding:
            for c in self.freecodes:
                if item['cid'] == c['id']:
                    item['name'] = c['name']

    def eventFilter(self, receiver, event):
        #QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), tip)
        if event.type() == QtCore.QEvent.ToolTip:
            helpEvent = QHelpEvent(event)
            cursor = QtGui.QTextCursor()
            cursor = receiver.cursorForPosition(helpEvent.pos())
            pos = cursor.position()
            receiver.setToolTip("")
            displayText = ""
            if isinstance(self.coding, list):
                # self.coding can be None if not file is open
                for item in self.coding:
                    if item['selfirst'] <= pos and item['selend'] >= pos:
                        if displayText == "":
                            displayText = item['name']
                        else: # can have multiple codes on same selected area
                            displayText += "\n" + item['name']
            if displayText != "":
                receiver.setToolTip(displayText)

        #Call Base Class Method to Continue Normal Event Processing
        return super(TT_EventFilter,self).eventFilter(receiver, event)
