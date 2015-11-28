#!/usr/bin/python
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

"""
Main loop and main view.
"""

import sys
import datetime
import sqlite3
from PyQt4 import QtGui
#from PyQt4 import QtCore
from Codes import Ui_Dialog_codes
from Categories import Ui_Dialog_cats
from FileCategories import Ui_Dialog_fcats
from Settings import Ui_Dialog_settings
from ManageFiles import Ui_Dialog_manageFiles
from ManageJournals import Ui_Dialog_manageJournals
from Cases import Ui_Dialog_cases
from Memo import Ui_Dialog_memo
from Codebook import Ui_Dialog_codebook
from Attributes import Ui_Dialog_Attributes
from AssignAttributes import Ui_Dialog_assignAttributes
from ImportAttributes import ImportAttributes
from Information import Ui_Dialog_information
from ReportCodings import Ui_Dialog_reportCodings
from SQL import Ui_Dialog_sql
from CodingSummary import CodingSummary


class MainView(QtGui.QMainWindow):
    """
    Main GUI window.
    SQLite databases need extension .rqda
    """

    qdaFileName = ""  # directory and file name
    logWidget = None

    settings = {"conn": None, "directory": "", "projectName": "", "showIDs":False,
    "codername": "default", "codertable": "coding", "font": "", "size": ""}
    project = {"databaseversion": "", "date": "", "dateM": "", "memo": "",
    "about": "", "imagDir": ""}

    def __init__(self):
        super(MainView, self).__init__()
        self.statusBar().showMessage('Ready')
        self.move(10, 10)
        self.resize(700, 500)
        self.setWindowTitle('Main')
        self.menu()
        self.logWidget = MainWidget(self)
        self.setCentralWidget(self.logWidget)
        self.show()

    def menu(self):
        menubar = self.menuBar()

        # project menu
        newProjectAction = QtGui.QAction('Create new project', self)
        newProjectAction.triggered.connect(self.newProject)
        newProjectAction.setStatusTip('Create new project')

        openProjectAction = QtGui.QAction('Open project', self)
        openProjectAction.triggered.connect(self.openProject)
        openProjectAction.setStatusTip('Open project')

        memoAction = QtGui.QAction('Project memo', self)
        memoAction.triggered.connect(self.projectMemo)
        memoAction.setStatusTip('Project memo')

        closeProjectAction = QtGui.QAction('Close project', self)
        closeProjectAction.triggered.connect(self.closeProject)
        closeProjectAction.setStatusTip('Close current project')

        settingsAction = QtGui.QAction('Settings', self)
        settingsAction.triggered.connect(self.setSettings)
        settingsAction.setStatusTip('Settings')

        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit')
        exitAction.triggered.connect(self.quitApplication)

        projectMenu = menubar.addMenu('&Project')
        projectMenu.addAction(newProjectAction)
        projectMenu.addAction(openProjectAction)
        projectMenu.addAction(memoAction)
        projectMenu.addAction(closeProjectAction)
        projectMenu.addAction(settingsAction)
        projectMenu.addAction(exitAction)

        # file cases and journals menu
        manageFileAction = QtGui.QAction('Manage files', self)
        manageFileAction.triggered.connect(self.manageFiles)
        manageFileAction.setStatusTip('manage files')

        fileCategoryAction = QtGui.QAction('File categories', self)
        fileCategoryAction.triggered.connect(self.fileCategories)
        fileCategoryAction.setStatusTip('manage file categories')

        journalAction = QtGui.QAction('Manage journals', self)
        journalAction.triggered.connect(self.journals)
        journalAction.setStatusTip('Manage journals')

        casesAction = QtGui.QAction('Manage cases', self)
        casesAction.triggered.connect(self.manageCases)
        casesAction.setStatusTip('Cases')

        fileMenu = menubar.addMenu('&Files and Cases')
        fileMenu.addAction(manageFileAction)
        fileMenu.addAction(casesAction)
        fileMenu.addAction(fileCategoryAction)
        fileMenu.addAction(journalAction)

        # codes menu
        codesAction = QtGui.QAction('Codes', self)
        codesAction.triggered.connect(self.manageCodes)
        codesAction.setStatusTip('Codes')

        categoriesAction = QtGui.QAction('Categories', self)
        categoriesAction.triggered.connect(self.codeCategories)
        categoriesAction.setStatusTip('Categories')

        codebookAction = QtGui.QAction('Codebook', self)
        codebookAction.triggered.connect(self.showCodebook)
        codebookAction.setStatusTip('Codebook')

        codesMenu = menubar.addMenu('&Coding')
        codesMenu.addAction(codesAction)
        codesMenu.addAction(categoriesAction)
        codesMenu.addAction(codebookAction)

        #attributes menu
        attrAction = QtGui.QAction('Manage attributes', self)
        attrAction.triggered.connect(self.manageAttributes)
        attrAction.setStatusTip('Manage Attributes')

        attrAssignAction = QtGui.QAction('Assign attributes', self)
        attrAssignAction.triggered.connect(self.assignAttributes)
        attrAssignAction.setStatusTip('Assign Attributes')

        attrImportAction = QtGui.QAction('Import attributes', self)
        attrImportAction.triggered.connect(self.importAttributes)
        attrImportAction.setStatusTip('Import Attributes')

        attrMenu = menubar.addMenu('Attributes')
        attrMenu.addAction(attrAction)
        attrMenu.addAction(attrAssignAction)
        attrMenu.addAction(attrImportAction)

        # reports menu
        repCodeAction = QtGui.QAction('Coding reports', self)
        repCodeAction.triggered.connect(self.repCoding)
        repCodeAction.setStatusTip('Coding reports')

        repSummaryAction = QtGui.QAction('Coding summary', self)
        repSummaryAction.triggered.connect(self.repSummary)
        repSummaryAction.setStatusTip('coding summary')

        repSqlAction = QtGui.QAction('SQL statements', self)
        repSqlAction.triggered.connect(self.repSql)
        repSqlAction.setStatusTip('SQL statements')

        reportsMenu = menubar.addMenu('Reports')
        reportsMenu.addAction(repCodeAction)
        reportsMenu.addAction(repSummaryAction)
        reportsMenu.addAction(repSqlAction)

        # help menu
        helpAction = QtGui.QAction('Help', self)
        helpAction.triggered.connect(self.help)
        helpAction.setStatusTip('Help')

        aboutAction = QtGui.QAction('About', self)
        aboutAction.triggered.connect(self.about)
        aboutAction.setStatusTip('About PyQDA')

        helpMenu = menubar.addMenu("Help")
        helpMenu.addAction(helpAction)
        helpMenu.addAction(aboutAction)

    def repSql(self):
        """ Run SQL statements on database """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        Dialog_s = QtGui.QDialog()
        ui = Ui_Dialog_sql(self.settings)
        ui.setupUi(Dialog_s)
        Dialog_s.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("SQL statements")


    def repCoding(self):
        """ report on coding dialog """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Coding report")
        Dialog_c = QtGui.QDialog()
        ui = Ui_Dialog_reportCodings(self.settings)
        ui.setupUi(Dialog_c)
        Dialog_c.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def repSummary(self):
        """ A summary of each code by code count, average characters and average word count """

        CodingSummary(self.settings)

    def help(self):
        """ Help dialog """

        self.statusBar().showMessage("Help")
        Dialog_help = QtGui.QDialog()
        ui = Ui_Dialog_information("Help", "Help.html")
        ui.setupUi(Dialog_help)
        Dialog_help.exec_()
        self.statusBar().showMessage("Ready")

    def about(self):
        """ About dialog """

        self.statusBar().showMessage("About PyQDA")
        Dialog_about = QtGui.QDialog()
        ui = Ui_Dialog_information("About", "About.html")
        ui.setupUi(Dialog_about)
        Dialog_about.exec_()
        self.statusBar().showMessage("Ready")

    def manageAttributes(self):
        """ Create, edit, delete, rename attributes """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Manage Attributes")
        Dialog_manageAttributes = QtGui.QDialog()
        ui = Ui_Dialog_Attributes(self.settings)
        ui.setupUi(Dialog_manageAttributes)
        Dialog_manageAttributes.exec_()
        self.statusBar().showMessage("Ready")

    def assignAttributes(self):
        """ Assign attributes to files and cases """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Assign Attributes")
        Dialog_assAttributes = QtGui.QDialog()
        ui = Ui_Dialog_assignAttributes(self.settings)
        ui.setupUi(Dialog_assAttributes)
        Dialog_assAttributes.exec_()
        self.statusBar().showMessage("Ready")

    def importAttributes(self):
        """ Import attributes and assign to cases or files """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        impAttr = ImportAttributes(self.settings)
        if impAttr.getLog() != "":
            self.logWidget.textEdit.append(ImportAttributes.getLog())

    def manageCases(self):
        """ Create, edit, delete, rename cases, add cases to files or parts of
        files, add memos to cases """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return

        self.statusBar().showMessage("Manage cases")
        Dialog_manageCases = QtGui.QDialog()
        ui = Ui_Dialog_cases(self.settings)
        ui.setupUi(Dialog_manageCases)
        Dialog_manageCases.exec_()
        self.statusBar().showMessage("Ready")

    def manageFiles(self):
        """ Create text files or import files from odt, docx, html and
        plain text. rename, delete and add memos to files """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Manage files")
        Dialog_manageFiles = QtGui.QDialog()
        ui = Ui_Dialog_manageFiles(self.settings)
        ui.setupUi(Dialog_manageFiles)
        Dialog_manageFiles.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def fileCategories(self):
        """ Create, edit and delete file categories """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Manage file categories")
        Dialog_fileCategories = QtGui.QDialog()
        ui = Ui_Dialog_fcats(self.settings)
        ui.setupUi(Dialog_fileCategories)
        Dialog_fileCategories.exec_()
        self.statusBar().showMessage("Ready")

    def journals(self):
        """ Create journals """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Journals")
        Dialog_manageJournals = QtGui.QDialog()
        ui = Ui_Dialog_manageJournals(self.settings)
        ui.setupUi(Dialog_manageJournals)
        Dialog_manageJournals.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def manageCodes(self):
        """ Create edit and delete codes.
        Apply and remove codes and annotations to the text in text files. """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Codes")
        Dialog_codes = QtGui.QDialog()
        ui = Ui_Dialog_codes(self.settings)
        ui.setupUi(Dialog_codes, self.settings)
        Dialog_codes.exec_()

        self.statusBar().showMessage("Ready")

    def codeCategories(self):
        """ Create, delete and edit code categories """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Categories")
        Dialog_cats = QtGui.QDialog()
        ui = Ui_Dialog_cats(self.settings)
        ui.setupUi(Dialog_cats)
        Dialog_cats.exec_()
        self.statusBar().showMessage("Ready")

    def showCodebook(self):
        """ A codebook is made up of memos attached to codes - rules when to apply codes. """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.statusBar().showMessage("Codebook")
        self.Dialog_codebook = QtGui.QDialog()
        ui = Ui_Dialog_codebook(self.settings)
        ui.setupUi(self.Dialog_codebook)
        self.Dialog_codebook.exec_()
        if ui.getLog() != "":
            self.logWidget.textEdit.append(ui.getLog())
        self.statusBar().showMessage("Ready")

    def quitApplication(self):
        """ Quit the application and close database connection """

        quit_msg = "Are you sure you want to quit?"
        reply = QtGui.QMessageBox.question(self, 'Message', quit_msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            if self.settings['conn'] is not None:
                self.settings['conn'].commit()
                self.settings['conn'].close()
            QtGui.qApp.quit()

    def newProject(self):
        """ Create a new Sqlite rqda project """

        if self.settings['projectName'] == "":
            self.statusBar().showMessage("Create new project")
            self.qdaFileName = str(QtGui.QFileDialog.getSaveFileName(self, "Enter project name", self.settings['directory'], ".rqda").toUtf8()).decode("utf-8")
            if self.qdaFileName == "":
                QtGui.QMessageBox.warning(None, "Project","No project created.")
                return

            if self.qdaFileName.find(".rqda") == -1:
                self.qdaFileName = self.qdaFileName + ".rqda"

            self.settings['projectName'] = self.qdaFileName.rpartition('/')[2]
            self.settings['directory'] = self.qdaFileName.rpartition('/')[0]

            try:
                self.settings['conn'] = sqlite3.connect(self.qdaFileName)  # create new Db
                cur = self.settings['conn'].cursor()
                cur.execute("CREATE TABLE project (databaseversion text, date text,dateM text, memo text,about text, imageDir text);")
                cur.execute("CREATE TABLE source (name text, id integer, file text, memo text, owner text, date text, dateM text, status integer);")
                cur.execute("CREATE TABLE fileAttr (variable text, value text, fileID integer, date text, dateM text, owner text, status integer);")
                cur.execute("CREATE TABLE filecat  (name text,fid integer, catid integer, owner text, date text, dateM text,memo text, status integer);")
                cur.execute("CREATE TABLE annotation (fid integer,position integer,annotation text, owner text, date text,dateM text, status integer);")
                cur.execute("CREATE TABLE attributes (name text, status integer, date text, dateM text, owner text,memo text, class text);")
                cur.execute("CREATE TABLE caseAttr (variable text, value text, caseID integer, date text, dateM text, owner text, status integer);")
                cur.execute("CREATE TABLE caselinkage  (caseid integer, fid integer, selfirst real, selend real, status integer, owner text, date text, memo text);")
                cur.execute("CREATE TABLE cases  (name text, memo text, owner text,date text,dateM text, id integer, status integer);")
                cur.execute("CREATE TABLE codecat  (name text, cid integer, catid integer, owner text, date text, dateM text,memo text, status integer);")
                cur.execute("CREATE TABLE coding  (cid integer, fid integer,seltext text, selfirst real, selend real, status integer, owner text, date text, memo text);")
                cur.execute("CREATE TABLE coding2  (cid integer, fid integer,seltext text, selfirst real, selend real, status integer, owner text, date text, memo text);")
                cur.execute("CREATE TABLE freecode  (name text, memo text, owner text,date text,dateM text, id integer, status integer, color text);")
                cur.execute("CREATE TABLE image (name text, id integer, date text, dateM text, owner text,status integer);")
                cur.execute("CREATE TABLE imageCoding (cid integer,iid integer,x1 integer, y1 integer, x2 integer, y2 integer, memo text, date text, dateM text, owner text,status integer);")
                cur.execute("CREATE TABLE journal (name text, journal text, date text, dateM text, owner text,status integer);")
                cur.execute("CREATE TABLE treecode  (cid integer, catid integer, date text, dateM text, memo text, status integer, owner text);")
                cur.execute("CREATE TABLE treefile  (fid integer, catid integer, date text,dateM text, memo text, status integer,owner text);")
                cur.execute("INSERT INTO project VALUES(?,?,?,?,?,?)", ('DBVersion:0.1',datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y"),'','','Database created by PyQDA based on RQDA',''))
                self.settings['conn'].commit()
                self.logWidget.textEdit.append("\nNew project: "+self.qdaFileName+" created.")
            except:
                self.logWidget.textEdit.append("\nProblems creating Db\n" + self.qdaFileName)
                self.closeProject()
        self.statusBar().showMessage("Ready")

    def setSettings(self):
        """ Change default settings - the coder name, coder table, font**, font size** TODO """

        self.statusBar().showMessage("Settings")
        Dialog_settings = QtGui.QDialog()
        ui = Ui_Dialog_settings(self.settings)
        ui.setupUi(Dialog_settings)
        Dialog_settings.exec_()
        self.statusBar().showMessage("Ready")
        msg = "Coder:" + self.settings['codername'] + ", CoderTable:"+  self.settings['codertable'] + ", "
        msg += "Font:" + self.settings['font'] + " " + str(self.settings['size'])
        msg += ", ShowIDs:" + str(self.settings['showIDs'])
        self.logWidget.textEdit.append("Settings: " + msg)

    def projectMemo(self):
        """ Give the entire project a memo """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project first.")
            return
        Dialog_memo = QtGui.QDialog()
        ui = Ui_Dialog_memo(self.project['memo'])
        ui.setupUi(Dialog_memo, "Project memo " + self.settings['projectName'])
        Dialog_memo.exec_()
        self.project['memo'] = ui.getMemo()
        cur = self.settings['conn'].cursor()
        cur.execute("update project set memo=?", [str(self.project['memo'])])
        self.settings['conn'].commit()
        self.logWidget.textEdit.append("Project memo entered")

    def openProject(self):
        """ Open an existing project """

        if self.settings['projectName'] != "":
            self.closeProject()

        self.statusBar().showMessage("Open project")
        self.qdaFileName = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file', self.settings['directory']).toUtf8()).decode("utf-8")
        if self.qdaFileName == "":
            return
        if len(self.qdaFileName) > 4 and self.qdaFileName[-5:] == ".rqda":
            try:
                self.settings['conn'] = sqlite3.connect(self.qdaFileName)
            except:
                self.settings['conn'] = None
        if self.settings['conn'] is None:
            QtGui.QMessageBox.warning(None, "Cannot open file", self.qdaFileName + " is not an .rqda file")
            self.qdaFileName = ""
        else:
            # get and display some project details
            self.settings['projectName'] = self.qdaFileName.rpartition('/')[2]
            self.logWidget.textEdit.append("Opening: " + self.qdaFileName)
            self.setWindowTitle(self.settings['projectName'])
            cur = self.settings['conn'].cursor()
            cur.execute('select sqlite_version()')
            self.logWidget.textEdit.append("SQLite version: " + str(cur.fetchone()))
            cur.execute("select databaseversion, date, dateM, memo, about, imageDir from project")
            result = cur.fetchone()
            self.project['databaseversion'] = result[0]
            self.project['date'] = result[1]
            self.project['dateM'] = result[2]
            self.project['memo'] = result[3]
            self.project['about'] = result[4]
            self.project['imageDir'] = result[5]
            self.logWidget.textEdit.append("DBVersion:" + str(self.project['databaseversion']) + "\n"
                                            + "Date: " + str(self.project['date']) + "\n"
                                            + "About: " + str(self.project['about']) + "\n"
                                            + "Image Directory: " + str(self.project['imageDir']) + "\n"
                                            + "Coder:" + str(self.settings['codername'])
                                            + "   Table:" + str(self.settings['codertable']) + "\n")

        self.setCentralWidget(self.logWidget)
        self.statusBar().showMessage("Ready")

    def closeProject(self):
        """ CLose an open project """

        if self.settings["projectName"] == "":
            QtGui.QMessageBox.warning(None, "No Project","You need to load or create a project.")
            return
        self.setCentralWidget(self.logWidget)
        self.logWidget.textEdit.append("Closing project: " + self.settings['projectName'] + "\n")
        try:
            self.settings['conn'].commit()
            self.settings['conn'].close()
        except:
            pass
        self.conn = None
        self.qdaFileName = ""
        self.settings['projectName'] = ""
        self.project = {"databaseversion": "", "date": "", "dateM": "",
        "memo": "", "about": "", "imagDir": ""}
        self.setWindowTitle("Main")


class MainWidget(QtGui.QWidget):
    textEdit = None

    def __init__(self, parent):
        super(MainWidget, self).__init__(parent)

        self.layout = QtGui.QVBoxLayout(self)
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.layout.addWidget(self.textEdit)


def main():
    app = QtGui.QApplication(sys.argv)
    mainview = MainView()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
