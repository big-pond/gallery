from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QPaintDevice, QIcon
from PyQt5.QtWidgets import (QMainWindow, QMessageBox, QDialog, QLabel)
from PyQt5.QtSql import QSqlDatabase, QSqlQuery, QSqlTableModel

import ui_mainwindow

import df
import cf

from mapview import MapView
from mainwidget import MainWidget
from settingsdlg import SettingsDlg
from addphotodlg import AddPhotoDlg


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__()
        self.ui = ui_mainwindow.Ui_MainWindow()
        self.ui.setupUi(self)
        self.xdotpersm = self.metric(QPaintDevice.PdmPhysicalDpiX) * 0.3937008
        self.mainwidget = MainWidget()
        self.setCentralWidget(self.mainwidget)

        maintoolbar = self.addToolBar('dataEditToolBar')
        maintoolbar.setObjectName('dataEditToolBar')
        maintoolbar.addAction(self.ui.actionSubmit)
        maintoolbar.addSeparator()
        maintoolbar.addAction(self.ui.actionRevert)
        maintoolbar.addSeparator()
        maintoolbar.addAction(self.ui.actionTurnCW)
        maintoolbar.addAction(self.ui.actionTurnCCW)
        maintoolbar.addSeparator()
        maintoolbar.addAction(self.ui.actionSelect_by_coordinates)
        maintoolbar.addAction(self.ui.actionClear_filter)


        self.ui.actionSettings.triggered.connect(self.settings)
        self.ui.actionQuit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.about)
        self.ui.actionAbout_Qt.triggered.connect(self.aboutQt)

        self.ui.actionAddPhoto.triggered.connect(self.addPhoto)
        self.ui.actionDeletePhoto.triggered.connect(self.delPhoto)

        self.ui.actionTurnCW.triggered.connect(self.turnCW)
        self.ui.actionTurnCCW.triggered.connect(self.turnCCW)

        self.ui.actionSelect_by_coordinates.triggered.connect(self.startFilterCoordinates)
        self.mainwidget.mapwidget.mapView.sendFilterCoordinames.connect(self.filterCoordonates)
        self.ui.actionClear_filter.triggered.connect(self.clearFilter)

        self.mainwidget.mapwidget.mapView.sendCoordinates.connect(self.displayCoordinates)
        self.ui.menuCoordinate_system.triggered.connect(self.setSysCoord)
        self.ui.actionDeg.setData(cf.DEG)
        self.ui.actionDegMin.setData(cf.DEGMIN)
        self.ui.actionDegMinSec.setData(cf.DEGMINSEC)
        self.ui.actionPixels.setData(cf.PIXEL)
        self.ui.actionMeters.setData(cf.METRE)
        self.ui.actionRad.setData(cf.RAD)
        self.ui.actionPixels.setChecked(True)
       
        self.lbCoord = QLabel('B:0.0 L:0.0')
        self.lbScale = QLabel('1:1')
        self.copyright = '<p><span style="font-size:10pt; color:#000055;">Copyright &copy; 2024 Yri Popov</span></p>'
        self.ui.statusbar.addWidget(self.lbCoord)
        self.ui.statusbar.addWidget(self.lbScale)
        row, col = self.readSettings()
        if self.openDataBase('gallery.db'):
            self.setWindowTitle('gallery.db')
            model = QSqlTableModel(db=self.db)
            model.setTable("photo")
            model.select()
            model.setEditStrategy(QSqlTableModel.OnManualSubmit)
            model.dataChanged.connect(self.dataChanged)
            self.ui.actionSubmit.setEnabled(False)
            self.ui.actionRevert.setEnabled(False)
            self.mainwidget.tableview.setModel(model)
            self.mainwidget.tableview.selectionModel().currentRowChanged.connect(self.mainwidget.tableRowChanged)
            self.ui.actionSubmit.triggered.connect(self.submitData)
            self.ui.actionRevert.triggered.connect(self.revertData)
            if row>=0 and col>=0:
                while model.canFetchMore():
                    model.fetchMore()
                self.mainwidget.tableview.setCurrentIndex(self.mainwidget.tableview.model().index(row, col))


    def readSettings(self):
        settings = QSettings('{0}.ini'.format('gallery'), QSettings.IniFormat)
        settings.beginGroup('MainWindow')
        cnt = settings.contains("geometry")
        if cnt:
            self.restoreGeometry(settings.value('geometry', ''))
        cnt = settings.contains("windowState")
        if cnt:
            self.restoreState(settings.value('windowState', ''))
        settings.endGroup()

        settings.beginGroup('Files')
        df.base_photo_path = settings.value('base_photo_path', df.base_photo_path, type=str)
        settings.endGroup()

        self.mainwidget.mapwidget.readMapsSettings(settings)
        row, col = self.mainwidget.readTabSettings(settings)
        return row, col

    def writeSettings(self):
        settings = QSettings('{0}.ini'.format('gallery'), QSettings.IniFormat)
        settings.beginGroup('MainWindow')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('windowState', self.saveState())
        settings.endGroup()

        settings.beginGroup('Files')
        settings.setValue('base_photo_path', df.base_photo_path)
        settings.endGroup()

        self.mainwidget.mapwidget.writeMapsSettings(settings)
        self.mainwidget.writeTabSettings(settings)

    def closeEvent(self, event):
        if self.mainwidget.tableview.model().isDirty():
            ret = QMessageBox.question(self, '', self.tr('The data has been changed.\nDo you want to save the changes?'),
                                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ret == QMessageBox.Yes:
                self.submitData() 
         
        self.writeSettings()
        super(MainWindow, self).closeEvent(event)

    def settings(self):
        setdlg = SettingsDlg()
        setdlg.exec()
       
    def openDataBase(self, filename):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName(filename)
        result = self.db.open()
        return result
        
    def addPhoto(self):
        adddlg = AddPhotoDlg(self.mainwidget.tableview.model(), self.mainwidget.tableview.currentIndex())
        self.mainwidget.tableview.currentIndex
        if adddlg.exec()==QDialog.Accepted:
            pass

    def delPhoto(self):
        print("delete photo")

    def submitData(self):
        self.mainwidget.tableview.model().submitAll()
        self.ui.actionSubmit.setEnabled(False)
        self.ui.actionRevert.setEnabled(False)
    
    def revertData(self):
        self.mainwidget.tableview.model().revertAll()
        self.ui.actionSubmit.setEnabled(False)
        self.ui.actionRevert.setEnabled(False)

    def dataChanged(self, topLeft, bottomRight):
        self.ui.actionSubmit.setEnabled(True)
        self.ui.actionRevert.setEnabled(True)

    def setSysCoord(self, action):
        if self.ui.actionPixels != action:
            self.ui.actionPixels.setChecked(False)
        if self.ui.actionDeg != action:
            self.ui.actionDeg.setChecked(False)
        if self.ui.actionDegMin != action:
            self.ui.actionDegMin.setChecked(False)
        if self.ui.actionDegMinSec != action:
            self.ui.actionDegMinSec.setChecked(False)
        if self.ui.actionMeters != action:
            self.ui.actionMeters.setChecked(False)
        if self.ui.actionRad != action:
            self.ui.actionRad.setChecked(False)
        MapView.COORD_UNIT = action.data()

    def getUnitCoord(self):
        uc = self.ui.actionPixels.data()
        if self.ui.actionDeg.isChecked():
            uc = self.ui.actionDeg.data()
        elif self.ui.actionDegMin.isChecked():
            uc = self.ui.actionDegMin.data()
        elif self.ui.actionDegMinSec.isChecked():
            uc = self.ui.actionDegMinSec.data()
        elif self.ui.actionMeters.isChecked():
            uc = self.ui.actionMeters.data()
        elif self.ui.actionRad.isChecked():
            uc = self.ui.actionRad.data()
        return uc

    def displayCoordinates(self, x, y, scale):
        if self.ui.actionPixels.isChecked():
            self.lbCoord.setText("X: {} Y: {}".format(x, y))
        elif self.ui.actionDegMinSec.isChecked():
            self.lbCoord.setText(cf.degLatLonToDmsStr(x, y))
        elif self.ui.actionDegMin.isChecked():
            self.lbCoord.setText(cf.degLatLonToDmStr(x, y))
        elif self.ui.actionDeg.isChecked():
            self.lbCoord.setText(cf.degLatLonToDegStr(x, y))
        elif self.ui.actionMeters.isChecked():
            self.lbCoord.setText("X: {:.2f}  Y: {:.2f}".format(x, y))
        elif self.ui.actionRad.isChecked():
            self.lbCoord.setText(cf.radLatLonToRadStr(x, y))
        self.lbScale.setText(self.tr(
            "Scale:   {:.2f} м/пиксел;   {:.2f} м/см;    1 : {:.0f}".format(scale, scale * self.xdotpersm,
                                                                            scale * self.xdotpersm * 100)))

    def turnCW(self):
        self.mainwidget.imageview.rotate(90)

    def turnCCW(self):
        self.mainwidget.imageview.rotate(-90)

    def startFilterCoordinates(self):
        self.mainwidget.mapwidget.mapView.selectRect = True

    def filterCoordonates(self, lat1, lon1, lat2, lon2):
        self.ui.actionSelect_by_coordinates.setChecked(False)
        # print(f'lat1={lat1}, lon1={lon1}, lat2={lat2}, lon2={lon2}')
        model = self.mainwidget.tableview.model()
        filter = f'lat>{lat1} AND lat<{lat2} AND lon>{lon1} AND lon<{lon2}'
        model.setFilter(filter)
        model.select()

    def clearFilter(self):
        model = self.mainwidget.tableview.model()
        model.setFilter('')
        model.select()

    def about(self):
        query = QSqlQuery("SELECT count(*) FROM photo", self.mainwidget.tableview.model().database())
        query.first()
        totalCount = query.record().value(0)
        QMessageBox.about(self, 'About',
'''<h2 align="center"><font color="#008000">gallery 1.0</font></h2>
<p align="center"><font color="#000080" face="Times New Roman" size="4">
<b>Photos on the map</b></font></p><p>Poto total count: {0}</p><p>{1}</p>
'''.format(totalCount, self.copyright))

    def aboutQt(self):
        QMessageBox.aboutQt(self)

    def setEnbleAction(self):
        pass
