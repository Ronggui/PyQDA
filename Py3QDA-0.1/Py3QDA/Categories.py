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
from .CodeColors import CodeColors
from .ColorSelector import Ui_Dialog_colorselect
from .Memo import Ui_Dialog_memo
from .AddItem import Ui_Dialog_addItem
from .ConfirmDelete import Ui_Dialog_confirmDelete
from .SelectFile import Ui_Dialog_selectfile
from .ViewCodeFrequencies import Ui_Dialog_vcf

# requires python-igraph (0.6.5)
try:
    import igraph # use this module only if it is installed
except:
    pass
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

class Ui_Dialog_cats(object):
    """
    Code Category management.
    Shows a list of code categories which can be added to or deleted from.
    Show a list of codes which can be dragged into code categories
    Clicking on a category shows the linked codes.
    Several displays of codes and categories are available: network graphs and code frequencies
    """

    #ADDIN
    CODE_NAME_COLUMN = 0
    CODE_COLOR_COLUMN = 1
    CODE_MEMO_COLUMN = 2
    CODE_ID_COLUMN = 3
    CAT_NAME_COLUMN = 0
    CAT_MEMO_COLUMN = 1
    CAT_VIEW_COLUMN = 2
    CAT_ID_COLUMN = 3

    settings = None
    freecode = []  # the codes
    codeColors = CodeColors()
    cats = []  # codecategories
    treecode = []  # links codes to categories
    selectedCategoryId = -1  # if -1 all categories and codes are shown, if a category id then only that category and its codes are shown

    def __init__(self, settings):
        self.freecode = []
        self.cats = []
        self.treecode = []
        self.settings = settings

        cur = self.settings['conn'].cursor()
        cur.execute("select name, memo, owner, date, dateM, id, status, color from freecode")
        result = cur.fetchall()
        for row in result:
            self.freecode.append({'name':row[0], 'memo':row[1], 'owner':row[2], 'date':row[3], 'dateM':row[4], 'id':row[5], 'status':row[6], 'color':row[7]})

        cur.execute("select name, cid, catid, owner, date, dateM, memo, status from codecat")
        result = cur.fetchall()
        for row in result:
            self.cats.append({'name':row[0],'cid':row[1], 'catid':row[2], 'owner':row[3], 'date':row[4], 'dateM':row[5], 'memo':row[6], 'status':row[7]})

        cur.execute("select cid, catid, date, dateM, memo, status, owner from treecode")
        result = cur.fetchall()
        for row in result:
            self.treecode.append({'cid':row[0], 'catid':row[1], 'date':row[2], 'dateM':row[3], 'memo':row[4], 'status':row[5], 'owner':row[6]})

    def comboView(self):
        """ Select code and category view options """

        if len(self.tableWidget_cats.selectedItems()) == 0:
            QtWidgets.QMessageBox.warning(None, "No Categories","No categories selected.")
            return
        selection = str(self.comboBox.currentText())
        if selection[0:12] == "View graph: ":
            self.viewGraph(selection[12:])
        if selection == "View Code Frequency Table":
            self.viewFrequencyTable()

    def viewFrequencyTable(self):
        """ Create a table headed by selected categories, codes for each category are listed from most frequent to least """

        selectedCats = ""
        headers = []
        for itemWidget in self.tableWidget_cats.selectedItems():
            catid = str(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text())
            headers.append(str(self.tableWidget_cats.item(itemWidget.row(), self.CAT_NAME_COLUMN).text()))
            selectedCats += "," + catid
        selectedCats = selectedCats[1:]

        cur = self.settings['conn'].cursor()
        #sql = "select count(treecode.cid) as count, treecode.cid, freecode.name, treecode.catid, codecat.name from treecode "\
        sql = "select count(treecode.cid) as count, freecode.name, codecat.name from treecode "\
        "join codecat on treecode.catid=codecat.catid join freecode on freecode.id=treecode.cid "\
        " join "+ self.settings['codertable'] + " on " + self.settings['codertable'] + ".cid = treecode.cid "\
        " where treecode.catid in ("+ selectedCats +") "\
        " group by freecode.name, treecode.cid "\
        " order by codecat.name asc, count desc"

        cur.execute(sql)
        result = cur.fetchall()
        results = []
        for row in result:
            results.append(row)
        #print results

        listDictionaryResults = {}
        for heading in headers:
            listDictionaryResults[heading] = []
            for row in results:
                if heading == row[2]:
                    listDictionaryResults[heading].append(row[1] + " (" + str(row[0]) + ")")

        Dialog_vcf = QtWidgets.QDialog()
        ui = Ui_Dialog_vcf(listDictionaryResults)
        ui.setupUi(Dialog_vcf)
        Dialog_vcf.exec_()

    def viewGraph(self, layout):
        """ View node graph of selected codes and categories """

        try:
            tmp = igraph.Graph(0)
        except:
            QtWidgets.QMessageBox.warning(None, "igraph","igraph not installed.\nCannot create network graphs.")
            return

        selectedCats = ""
        vertices = []
        maxCatNum = 0
        for vnum, itemWidget in enumerate(self.tableWidget_cats.selectedItems()):
            catid = str(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text())
            name = str(self.tableWidget_cats.item(itemWidget.row(), self.CAT_NAME_COLUMN).text())
            selectedCats += "," + catid
            vertices.append({'vnum':vnum,'catid': int(catid), 'cid':-1, 'catname':name, 'codename':"", 'name':name.upper()})
            maxCatNum = vnum
        selectedCats = selectedCats[1:]
        maxCatNum += 1

        # get treecode with code and category names
        cur = self.settings['conn'].cursor()
        cur.execute("select treecode.cid, freecode.name, treecode.catid, codecat.name from treecode "\
        "join codecat on treecode.catid=codecat.catid join freecode on freecode.id=treecode.cid "\
        "where treecode.catid in ("+ selectedCats +")")
        result = cur.fetchall()
        edges = []
        e1NumAdjuster = 0 # decrease the vum is the same code appears more than once
        for vnum, row in enumerate(result):
            duplicateCode = False
            for code in vertices:
                if row[0] == code['cid']:
                    #print("have a duplicate: " + row[1])
                    e1NumAdjuster -= 1
                    duplicateCode = True
                    tmpEdge = {'e1':code['vnum'], 'e2': 0, 'cid':row[0], 'codename':row[1], 'catid':row[2], 'catname':row[3]}
                    # look at ONLY the category vertices
                    for catVertex in range(0, maxCatNum):
                        if vertices[catVertex]['catid'] == tmpEdge['catid']:
                            tmpEdge['e2'] = catVertex
                    edges.append(tmpEdge)

            if duplicateCode == False:
                #remove catname and code name from below and just keep name
                vertices.append({'vnum':vnum + maxCatNum + e1NumAdjuster ,'catid': int(row[2]), 'cid': int(row[0]), 'catname':"", 'codename':row[1], 'name':row[1]})
                tmpEdge = {'e1':vnum + maxCatNum + e1NumAdjuster, 'e2': 0, 'cid':row[0], 'codename':row[1], 'catid':row[2], 'catname':row[3]}
                # look at ONLY the category vertices
                for catVertex in range(0, maxCatNum):
                    if vertices[catVertex]['catid'] == tmpEdge['catid']:
                        tmpEdge['e2'] = catVertex
                edges.append(tmpEdge)

        vnames = []
        for item in vertices:
            vnames.append(item['name'])
        finalEdges = []
        for edge in edges:
            finalEdges.append((edge['e1'], edge['e2']))
        g = igraph.Graph(0)
        g.add_vertices(len(vertices))
        g.vs["name"] = vnames
        g.add_edges(finalEdges)
        #g.vs["label"] = g.vs["name"]
        visual_style = {}
        visual_style["vertex_label"] = g.vs["name"]
        visual_style["layout"] = g.layout(layout)
        visual_style["vertex_size"] = 20
        visual_style["vertex_label_size"] = 12
        visual_style["vertex_color"] = "yellow"
        visual_style["margin"] = [100,20,100,20] # t r b l
        visual_style["edge_color"] = "gray"
        visual_style["bbox"] = (900, 650)
        igraph.plot(g, **visual_style)

    def codesCellSelected(self):
        """ When colour or memo cells are selected in the table widget,
        open a memo dialog or colour selector dialog """

        x = self.tableWidget_codes.currentRow()
        y = self.tableWidget_codes.currentColumn()

        if y == self.CODE_COLOR_COLUMN:
            Dialog_colorselect = QtWidgets.QDialog()
            ui = Ui_Dialog_colorselect(self.freecode[x]['color'])
            ui.setupUi(Dialog_colorselect)
            ok = Dialog_colorselect.exec_()
            if ok:
                selectedColor = ui.getColor()
                if selectedColor!=None:
                    item = QtWidgets.QTableWidgetItem()  # an empty item, used to have color name
                    item.setBackground(QtGui.QBrush(QtGui.QColor(selectedColor['hex'])))
                    self.tableWidget_codes.setItem(x, self.CODE_COLOR_COLUMN, item)
                    self.tableWidget_codes.clearSelection()

                    #update freecode list and database
                    self.freecode[x]['color'] = selectedColor['colname']
                    cur = self.settings['conn'].cursor()
                    cur.execute("update freecode set color=? where id=?", (self.freecode[x]['color'], self.freecode[x]['id']))
                    self.settings['conn'].commit()

        if y == self.CODE_MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.freecode[x]['memo'])
            ui.setupUi(Dialog_memo, "Code memo " + self.freecode[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()

            if memo == "":
                self.tableWidget_codes.setItem(x, self.CODE_MEMO_COLUMN, QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget_codes.setItem(x, self.CODE_MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))

            #update freecode list and database
            self.freecode[x]['memo'] = str(memo)
            cur = self.settings['conn'].cursor()
            cur.execute("update freecode set memo=? where id=?", (self.freecode[x]['memo'], self.freecode[x]['id']))
            self.settings['conn'].commit()

    def codesCellModified(self):
        """ When a code name is changed in the table widget update the details in model and database """

        x = self.tableWidget_codes.currentRow()
        y = self.tableWidget_codes.currentColumn()
        if y == self.CODE_NAME_COLUMN:
            newCodeText = str(self.tableWidget_codes.item(x, y).text())
            # check that no other code has this text and this is is not empty
            update = True
            if newCodeText == "":
                update = False
            for c in self.freecode:
                if c['name'] == newCodeText:
                    update = False
            if update:
                # update freecode list and database
                cur = self.settings['conn'].cursor()
                cur.execute("update freecode set name=? where id=?", (newCodeText, self.freecode[x]['id']))
                self.settings['conn'].commit()
                self.freecode[x]['name'] = newCodeText

            else:  # put the original text in the cell
                self.tableWidget_codes.item(x, y).setText(self.freecode[x]['name'])

    def catsCellSelected(self):
        """ Open a memo dialog if a category memo cell is selected """

        x = self.tableWidget_cats.currentRow()
        y = self.tableWidget_cats.currentColumn()

        # category memo column
        if y == self.CAT_MEMO_COLUMN:
            Dialog_memo = QtWidgets.QDialog()
            ui = Ui_Dialog_memo(self.cats[x]['memo'])
            ui.setupUi(Dialog_memo, "Category memo " + self.cats[x]['name'])
            Dialog_memo.exec_()
            memo = ui.getMemo()

            if memo == "":
                self.tableWidget_cats.setItem(x, self.CAT_MEMO_COLUMN, QtWidgets.QTableWidgetItem())
            else:
                self.tableWidget_cats.setItem(x, self.CAT_MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))

            #update cats list and database
            self.cats[x]['memo'] = str(memo)
            cur = self.settings['conn'].cursor()
            cur.execute("update codecat set memo=? where catid=?", (self.cats[x]['memo'], self.cats[x]['catid']))
            self.settings['conn'].commit()

        # view codes for this category
        if y == self.CAT_VIEW_COLUMN:
            # important need to unselect all codes in tableWidget

            if self.selectedCategoryId == -1:  # all categories currently displayed, so change this to selected category
                self.pushButton_link.setEnabled(False)
                self.pushButton_unlink.setEnabled(True)
                self.selectedCategoryId = int(self.tableWidget_cats.item(x, self.CAT_ID_COLUMN).text())
                for (row, item) in enumerate(self.cats):
                    if self.selectedCategoryId != int(self.tableWidget_cats.item(row, self.CAT_ID_COLUMN).text()):
                        self.tableWidget_cats.hideRow(row)  # hide other categories

                # now show codes associated with this category
                for(row, item) in enumerate(self.freecode):
                    hide = True
                    for treeCodeItem in self.treecode:
                        #print(str(treeCodeItem['catid'])+" "+str(self.selectedCategoryId)+" co:"+str(treeCodeItem['cid'])+" "+str(item['id']))
                        if int(treeCodeItem['catid']) == self.selectedCategoryId and treeCodeItem['cid'] == item['id']:
                            hide = False
                    if hide:
                        self.tableWidget_codes.hideRow(row)
            else:
                self.selectedCategoryId = -1
                self.pushButton_link.setEnabled(True)
                self.pushButton_unlink.setEnabled(False)
                for (row, item) in enumerate(self.cats):
                    self.tableWidget_cats.showRow(row)
                for(row, item) in enumerate(self.freecode):
                    self.tableWidget_codes.showRow(row)

                # need to clear selection in category table when showing all rows
                # as there are no selected items but the previous view cell appears selected
                self.tableWidget_cats.clearSelection()

    def catsCellModified(self):
        """ When a category name is modified, update the model and database """

        x = self.tableWidget_cats.currentRow()
        y = self.tableWidget_cats.currentColumn()
        if y == self.CAT_NAME_COLUMN:
            newCatText = str(self.tableWidget_cats.item(x, y).text())
            # check that no other category has this text and this is is not empty
            update = True
            if newCatText == "":
                update = False
            for c in self.cats:
                if c['name'] == newCatText:
                    update = False
            if update:
                #update category list and database
                cur = self.settings['conn'].cursor()
                cur.execute("update codecat set name=? where catid=?", (newCatText, self.cats[x]['catid']))
                self.settings['conn'].commit()
                self.cats[x]['name'] = newCatText
            else:  #put the original text in the cell
                self.tableWidget_cats.item(x, y).setText(self.cats[x]['name'])

    def addCat(self):
        """ When button pressed, add a new category.
        Note: the addItem dialog does the checking for duplicate category names """

        Dialog_addCat = QtWidgets.QDialog()
        ui = Ui_Dialog_addItem(self.cats)
        ui.setupUi(Dialog_addCat, "Category")
        Dialog_addCat.exec_()
        newCatText = ui.getNewItem()
        if newCatText is not None:
            #add to database
            # need to generate a new id as the RQDA database does not have an autoincrement id field
            newid = 1
            for cat in self.cats:
                if cat['catid'] >= newid:
                    newid = cat['catid']+1
            item = {'name':newCatText,'cid':None, 'catid':newid, 'memo':"", 'owner':self.settings['codername'], 'date':datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"), 'dateM':"", 'status':1}
            self.cats.append(item)
            cur = self.settings['conn'].cursor()
            cur.execute("insert into codecat (name, cid, catid, memo, owner, date, dateM, status) values(?,?,?,?,?,?,?,?)"
                        ,(item['name'], item['cid'], item['catid'],item['memo'],item['owner'],item['date'],item['dateM'],item['status']))
            self.settings['conn'].commit()

            #update widget
            self.tableWidget_cats.insertRow(0)
            newItem = QtWidgets.QTableWidgetItem(item['name'])
            self.tableWidget_cats.setItem(0, self.CAT_NAME_COLUMN, newItem)
            newItem = QtWidgets.QTableWidgetItem(item['memo'])
            self.tableWidget_cats.setItem(0, self.CAT_MEMO_COLUMN, newItem)
            newItem = QtWidgets.QTableWidgetItem(str(item['catid']))
            self.tableWidget_cats.setItem(0, self.CAT_ID_COLUMN, newItem)
            self.tableWidget_cats.resizeColumnsToContents()
            self.tableWidget_cats.resizeRowsToContents()

    def deleteCat(self):
        """ When category highlighted and Delete button pressed. Delete category from model and database """

        tableRowsToDelete = []  # for table widget ids
        idsToDelete = []  # for ids for cats and db
        catNamesToDelete = ""  # for confirmDelete Dialog

        for itemWidget in self.tableWidget_cats.selectedItems():
            tableRowsToDelete.append(int(itemWidget.row()))
            idsToDelete.append(int(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text()))
            catNamesToDelete = catNamesToDelete+"\n" + str(self.tableWidget_cats.item(itemWidget.row(), self.CAT_NAME_COLUMN).text())
            #print("X:"+ str(itemWidget.row()) + "  y:"+str(itemWidget.column()) +"  "+itemWidget.text() +"  id:"+str(self.tableWidget_codes.item(itemWidget.row(),3).text()))
        if catNamesToDelete == "":
            return
        tableRowsToDelete.sort(reverse=True)

        Dialog_confirmDelete = QtWidgets.QDialog()
        ui = Ui_Dialog_confirmDelete(catNamesToDelete)
        ui.setupUi(Dialog_confirmDelete)
        ok = Dialog_confirmDelete.exec_()
        if ok:
            for r in tableRowsToDelete:
                self.tableWidget_cats.removeRow(r)

            if self.selectedCategoryId != -1:  # show all other categories and codes again
                self.selectedCategoryId = -1
                for (row, item) in enumerate(self.cats):
                    self.tableWidget_cats.showRow(row)
                for(row, item) in enumerate(self.freecode):
                    self.tableWidget_codes.showRow(row)

            for catid in idsToDelete:
                for item in self.cats:
                    if item['catid'] == catid:
                        self.cats.remove(item)
                        cur = self.settings['conn'].cursor()
                        #print(str(id) + "  "+ str(type(id)))
                        cur.execute("delete from treecode where catid = ?", [catid])
                        cur.execute("delete from codecat where catid = ?", [catid])
                        self.settings['conn'].commit()

    def link(self):
        """ Link one or more selected codes to one selected category when link button pressed"""

        if self.selectedCategoryId != -1:
            return
        catId = None
        codeIds = []

        # get the last (only) selected cat item
        for itemWidget in self.tableWidget_cats.selectedItems():
            catId = int(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text())
        if catId == None: return

        for itemWidget in self.tableWidget_codes.selectedItems():
            codeIds.append(int(self.tableWidget_codes.item(itemWidget.row(), self.CODE_ID_COLUMN).text()))
        if len(codeIds) == 0: return

        # update Db and treecode variable
        cur = self.settings['conn'].cursor()
        theDate = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
        for cid in codeIds:
            #check the link is not already in the Db
            cur.execute("select count(*) from treecode where cid=? and catid=?",(cid, catId))
            result = cur.fetchone()[0]
            self.settings['conn'].commit()
            if result == 0:
                cur.execute("insert into treecode (cid, catid, date, dateM, memo, status, owner) values(?,?,?,?,?,?,?)",
                        (cid, catId, theDate, theDate, "", 1, self.settings['codername']))
            else:
                return

        # update treecode list
        self.treecode = []
        cur.execute("select cid, catid, date, dateM, memo, status, owner from treecode")
        result = cur.fetchall()
        for row in result:
            self.treecode.append({'cid':row[0], 'catid':row[1], 'date':row[2], 'dateM':row[3], 'memo':row[4], 'status':row[5], 'owner':row[6]})
        self.settings['conn'].commit()

    def unlink(self):
        """ When button pressed, all selected codes are unlinked from the selected category """

        codeIds = []
        if self.selectedCategoryId == -1:
            return
        for itemWidget in self.tableWidget_codes.selectedItems():
            codeIds.append(int(self.tableWidget_codes.item(itemWidget.row(), self.CODE_ID_COLUMN).text()))
        if len(codeIds) == 0:
            return
        #print("Unlink: selCatView:"+str(self.selectedCategoryId)+"  codes:"+str(codeIds)) #temp
        # update Db and treecode variable
        cur = self.settings['conn'].cursor()
        for cid in codeIds:
            cur.execute("delete from treecode where cid=? and catid=?",(cid, self.selectedCategoryId))

        self.treecode = []
        cur.execute("select cid, catid, date, dateM, memo, status, owner from treecode")
        result = cur.fetchall()
        for row in result:
            self.treecode.append({'cid':row[0], 'catid':row[1], 'date':row[2], 'dateM':row[3], 'memo':row[4], 'status':row[5], 'owner':row[6]})
        self.settings['conn'].commit()

    def mergeCodes(self):
        """When merge codes button is pressed, merge two or more codes into one code.
        Note: there is no undo for this """

        removeCodes = []
        for itemWidget in self.tableWidget_codes.selectedItems():
            removeTemp = {'name':self.tableWidget_codes.item(itemWidget.row(), self.CODE_NAME_COLUMN).text(),'cid':int(self.tableWidget_codes.item(itemWidget.row(), self.CODE_ID_COLUMN).text())}
            # remove duplicate selections, have duplicates because tableWidget_codes is not row selection only
            addCode = True
            for remCode in removeCodes:
                if removeTemp == remCode:
                    addCode = False
            if addCode:
                removeCodes.append(removeTemp)
        if len(removeCodes) < 2:
            return

        Dialog_selectcode = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(removeCodes)
        ui.setupUi(Dialog_selectcode, "Merging, Select code to keep", "single")
        ok = Dialog_selectcode.exec_()
        if not(ok):
            return
        keepCode = ui.getSelected()
        #print(keepCode)
        #print(str(removeCodes))
        for code in removeCodes:
            if code['cid'] == keepCode['cid']:
                removeCodes.remove(code)  # exclude the kept code from the remove list
        #print(str(removeCodes))
        cur = self.settings['conn'].cursor()
        for code in removeCodes:
            cur.execute("update treecode set cid=? where cid=?", (keepCode['cid'] ,code['cid']))
            cur.execute("update coding set cid=? where cid=?", (keepCode['cid'] ,code['cid']))
            cur.execute("update coding2 set cid=? where cid=?", (keepCode['cid'] ,code['cid']))
            cur.execute("delete from freecode where id=?", (code['cid'],))

        #have to refresh self.tableWidget_codes and freecode list
        for row in self.freecode:
            self.tableWidget_codes.removeRow(0)

        cur.execute("select name, memo, owner, date, dateM, id, status, color from freecode")
        result = cur.fetchall()
        self.freecode = []
        for row in result:
            self.freecode.append({'name':row[0], 'memo':row[1], 'owner':row[2], 'date':row[3], 'dateM':row[4], 'id':row[5], 'status':row[6], 'color':row[7]})
        self.settings['conn'].commit()
        self.fillCodesTable()

    def mergeCats(self):
        """When merge categories button is pressed, merge two or more categories into one category.
        Note: there is no undo for this """

        removeCats = []
        for itemWidget in self.tableWidget_cats.selectedItems():
            removeTemp = {'name':self.tableWidget_cats.item(itemWidget.row(), self.CAT_NAME_COLUMN).text(),'catid':int(self.tableWidget_cats.item(itemWidget.row(), self.CAT_ID_COLUMN).text())}
            # remove duplicate selections, have duplicates because tableWidget_cats is not row selection only
            addCat = True
            for remCat in removeCats:
                if removeTemp == remCat:
                    addCat = False
            if addCat: removeCats.append(removeTemp)

        if len(removeCats) < 2:
            return

        Dialog_selectcat = QtWidgets.QDialog()
        ui = Ui_Dialog_selectfile(removeCats)
        ui.setupUi(Dialog_selectcat, "Merging, Select category to keep", "single")
        ok = Dialog_selectcat.exec_()
        if not(ok):
            return
        keepCat = ui.getSelected()
        print("Keeping category: " + str(keepCat))
        for cat in removeCats:
            if cat['catid'] == keepCat['catid']:
                removeCats.remove(cat)  # exclude the kept category from the remove list
        print("Removing categories: " + str(removeCats))

        cur = self.settings['conn'].cursor()
        for cat in removeCats:
            cur.execute("update treecode set catid=? where catid=?", (keepCat['catid'] ,cat['catid']))
            cur.execute("delete from codecat where catid=?", (cat['catid'],))

        # Refresh categories, treecat and self.tableWidget_cats
        for row in self.cats:
            self.tableWidget_cats.removeRow(0)

        self.cats = []
        cur.execute("select name, cid, catid, owner, date, dateM, memo, status from codecat")
        result = cur.fetchall()
        for row in result:
            self.cats.append({'name':row[0],'cid':row[1], 'catid':row[2], 'owner':row[3], 'date':row[4], 'dateM':row[5], 'memo':row[6], 'status':row[7]})

        self.treecode = []
        cur.execute("select cid, catid, date, dateM, memo, status, owner from treecode")
        result = cur.fetchall()
        for row in result:
            self.treecode.append({'cid':row[0], 'catid':row[1], 'date':row[2], 'dateM':row[3], 'memo':row[4], 'status':row[5], 'owner':row[6]})
        self.settings['conn'].commit()
        self.fillCatsTable()

    def fillCodesTable(self):
        """ Fill the codes table """

        self.tableWidget_codes.setColumnCount(4)
        self.tableWidget_codes.setHorizontalHeaderLabels(["Code","Color","Memo","Id"])
        for row, code in enumerate(self.freecode):
            self.tableWidget_codes.insertRow(row)
            self.tableWidget_codes.setItem(row, self.CODE_NAME_COLUMN, QtWidgets.QTableWidgetItem(code['name']))
            colnametmp = code['color']
            if colnametmp is None:
                colnametmp = ""
            item = QtWidgets.QTableWidgetItem()
            colorHex = self.codeColors.getHexFromName(colnametmp)
            if colorHex != "":
                item.setBackground(QtGui.QBrush(QtGui.QColor(colorHex)))
            self.tableWidget_codes.setItem(row, self.CODE_COLOR_COLUMN, item)
            mtmp = code['memo']
            if mtmp is not None and mtmp != "":
                self.tableWidget_codes.setItem(row, self.CODE_MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            cid = code['id']
            if cid is None:
                cid = ""
            self.tableWidget_codes.setItem(row, self.CODE_ID_COLUMN, QtWidgets.QTableWidgetItem(str(cid)))

        self.tableWidget_codes.verticalHeader().setVisible(False)
        self.tableWidget_codes.resizeColumnsToContents()
        self.tableWidget_codes.resizeRowsToContents()
        if not self.settings['showIDs']:
            self.tableWidget_codes.hideColumn(self.CODE_ID_COLUMN) # hide code ids

    def fillCatsTable(self):
        """ Fill categories table """

        self.tableWidget_cats.setColumnCount(4)
        self.tableWidget_cats.setHorizontalHeaderLabels(["Category", "Memo", "View linked", "CatID"])
        for row, code in enumerate(self.cats):
            self.tableWidget_cats.insertRow(row)
            self.tableWidget_cats.setItem(row, self.CAT_NAME_COLUMN, QtWidgets.QTableWidgetItem(code['name']))
            mtmp = code['memo']
            if mtmp is not None and mtmp != "":
                self.tableWidget_cats.setItem(row, self.CAT_MEMO_COLUMN, QtWidgets.QTableWidgetItem("Yes"))
            catid = code['catid']
            if catid is None:
                catid = ""
            self.tableWidget_cats.setItem(row, self.CAT_ID_COLUMN, QtWidgets.QTableWidgetItem(str(catid)))

        self.tableWidget_cats.verticalHeader().setVisible(False)
        self.tableWidget_cats.resizeColumnsToContents()
        self.tableWidget_cats.resizeRowsToContents()
        if not self.settings['showIDs']:
            self.tableWidget_cats.hideColumn(self.CAT_ID_COLUMN) # hide category ids

    #END ADDIN

    def setupUi(self, Dialog_cats):
        Dialog_cats.setObjectName(_fromUtf8("Dialog_cats"))
        #ADDIN
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        h = sizeObject.height() * 0.8
        w = sizeObject.width() * 0.8
        h = min([h, 1000])
        w = min([w, 2000])
        Dialog_cats.resize(w, h)
        Dialog_cats.move(20, 20)
        #END ADDIN
        self.pushButton_add = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_add.setGeometry(QtCore.QRect(10, 10, 98, 27))
        self.pushButton_add.setObjectName(_fromUtf8("pushButton_add"))
        self.pushButton_delete = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_delete.setGeometry(QtCore.QRect(130, 10, 98, 27))
        self.pushButton_delete.setObjectName(_fromUtf8("pushButton_delete"))
        self.pushButton_mergeCodes = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_mergeCodes.setGeometry(QtCore.QRect(570, 10, 111, 27))
        self.pushButton_mergeCodes.setObjectName(_fromUtf8("pushButton_mergeCodes"))
        self.pushButton_mergeCats = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_mergeCats.setGeometry(QtCore.QRect(690, 10, 151, 27))
        self.pushButton_mergeCats.setObjectName(_fromUtf8("pushButton_mergeCats"))
        self.pushButton_link = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_link.setGeometry(QtCore.QRect(10, 50, 98, 27))
        self.pushButton_link.setObjectName(_fromUtf8("pushButton_link"))
        self.pushButton_unlink = QtWidgets.QPushButton(Dialog_cats)
        self.pushButton_unlink.setGeometry(QtCore.QRect(130, 50, 98, 27))
        self.pushButton_unlink.setObjectName(_fromUtf8("pushButton_unlink"))
        self.comboBox = QtWidgets.QComboBox(Dialog_cats)
        self.comboBox.setGeometry(QtCore.QRect(240, 50, 301, 27))
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.comboBox.addItem(_fromUtf8(""))
        self.splitter = QtWidgets.QSplitter(Dialog_cats)
        #self.splitter.setGeometry(QtCore.QRect(10, 90, 831, 471))
        self.splitter.setGeometry(QtCore.QRect(10, 90, w - 20, h - 100)) # addin
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tableWidget_codes = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget_codes.setObjectName(_fromUtf8("tableWidget_codes"))
        self.tableWidget_codes.setColumnCount(0)
        self.tableWidget_codes.setRowCount(0)
        self.tableWidget_cats = QtWidgets.QTableWidget(self.splitter)
        self.tableWidget_cats.setObjectName(_fromUtf8("tableWidget_cats"))
        self.tableWidget_cats.setColumnCount(0)
        self.tableWidget_cats.setRowCount(0)
        self.label = QtWidgets.QLabel(Dialog_cats)
        self.label.setGeometry(QtCore.QRect(260, 20, 261, 17))
        self.label.setObjectName(_fromUtf8("label"))

        #ADDIN
        self.fillCodesTable()
        self.fillCatsTable()

        self.tableWidget_codes.cellClicked.connect(self.codesCellSelected)
        self.tableWidget_cats.cellClicked.connect(self.catsCellSelected)
        self.tableWidget_cats.itemChanged.connect(self.catsCellModified)
        self.tableWidget_codes.itemChanged.connect(self.codesCellModified)
        self.pushButton_add.clicked.connect(self.addCat)
        self.pushButton_delete.clicked.connect(self.deleteCat)
        self.pushButton_link.clicked.connect(self.link)
        self.pushButton_unlink.clicked.connect(self.unlink)
        self.pushButton_mergeCodes.clicked.connect(self.mergeCodes)
        self.pushButton_mergeCats.clicked.connect(self.mergeCats)
        #self.comboBox.activated[str].connect(self.comboView)
        self.comboBox.activated.connect(self.comboView)
        #END ADDIN

        self.retranslateUi(Dialog_cats)
        QtCore.QMetaObject.connectSlotsByName(Dialog_cats)

    def retranslateUi(self, Dialog_cats):
        Dialog_cats.setWindowTitle(_translate("Dialog_cats", "Categories", None))
        self.pushButton_add.setText(_translate("Dialog_cats", "Add", None))
        self.pushButton_delete.setText(_translate("Dialog_cats", "Delete", None))
        self.pushButton_mergeCodes.setText(_translate("Dialog_cats", "Merge Codes", None))
        self.pushButton_mergeCats.setText(_translate("Dialog_cats", "Merge Categories", None))
        self.pushButton_link.setText(_translate("Dialog_cats", "Link", None))
        self.pushButton_unlink.setText(_translate("Dialog_cats", "Unlink", None))
        self.comboBox.setItemText(0, _translate("Dialog_cats", "View graph: circle", None))
        self.comboBox.setItemText(1, _translate("Dialog_cats", "View graph: kamada_kawai", None))
        self.comboBox.setItemText(2, _translate("Dialog_cats", "View graph: lgl", None))
        self.comboBox.setItemText(3, _translate("Dialog_cats", "View graph: fruchterman_reingold", None))
        self.comboBox.setItemText(4, _translate("Dialog_cats", "View graph: random", None))
        self.comboBox.setItemText(5, _translate("Dialog_cats", "View graph: reingold_tilford", None))
        self.comboBox.setItemText(6, _translate("Dialog_cats", "View graph: reingold_tilford_circular", None))
        self.comboBox.setItemText(7, _translate("Dialog_cats", "View Code Frequency Table", None))
        self.label.setText(_translate("Dialog_cats", "View codes of selected categories", None))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog_cats = QtWidgets.QDialog()
    ui = Ui_Dialog_cats()
    ui.setupUi(Dialog_cats)
    Dialog_cats.show()
    sys.exit(app.exec_())
