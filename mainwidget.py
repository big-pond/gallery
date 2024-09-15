#!/usr/bin/env python3
 
import sys
import os
from pathlib import Path

import df
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QSplitter, QMessageBox, \
                            QApplication, QTableView, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from mapwidget import MapWidget
from mapdescript import OSMDescript
 
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
 
    def initUI(self):
        hbox = QHBoxLayout(self)
        self.tableview = QTableView()
        mapdescr = OSMDescript()
        self.mapwidget = MapWidget(mapdescr)
        scene = QGraphicsScene() 
        self.imageview = QGraphicsView()
        self.imageview.setScene(scene)
        self.mapwidget.mapView.sendLatLon.connect(self.takeCoordinate)
 
        sp1 = QSplitter(Qt.Horizontal)
        sp1.addWidget(self.mapwidget)
        sp1.addWidget(self.imageview)
        sp1.setSizes([100, 200])
 
        sp2 = QSplitter(Qt.Vertical)
        sp2.addWidget(sp1)
        sp2.addWidget(self.tableview)
 
        hbox.addWidget(sp2)
        self.setLayout(hbox)
        self.img_scale = 1.0
        self.show()

    def writeTabSettings(self, settings):
        settings.beginGroup("Tab")
        index = self.tableview.currentIndex()
        if index.isValid():
            settings.setValue("index_row", index.row())
            settings.setValue("index_col", index.column())
        settings.endGroup()

    def readTabSettings(self, settings):
        settings.beginGroup("Tab")
        row = settings.value('index_row', -1, type=int)
        col = settings.value('index_col', -1, type=int)
        settings.endGroup()
        return row, col

    def tableRowChanged(self, current, previous):
        model = self.tableview.model()
        if current:
            path1 = model.record(current.row()).value('image')
            lt = model.record(current.row()).value('lat')
            ln = model.record(current.row()).value('lon')
            if path1:
                path = str(Path(df.base_photo_path, path1))
                self.showImage(path)
            lat = None
            lon = None
            if lt:
                lt = str(lt).replace(',','.')
                lat = float(lt)
            if ln:
                lt = str(lt).replace('.','.')
                lon = float(ln)
            if lat and lon:
                self.mapwidget.getMapScene().setPhotoPos(lat, lon)
                self.mapwidget.getMapScene().setVisiblePhotoPos(True)
                self.mapwidget.mapGoTo(lat, lon)
            else:
                self.mapwidget.getMapScene().setVisiblePhotoPos(False)
            self.mapwidget.getMapScene().update()
    
    def takeCoordinate(self, lat, lon):
        index = self.tableview.currentIndex()
        if index.isValid():
            row = index.row()
            ret = QMessageBox.question(self, '', self.tr('Write coordinates to the current row of the table?'),
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if ret == QMessageBox.Yes:
                model = self.tableview.model()
                model.setData(model.index(row,6), lat)
                model.setData(model.index(row,7), lon)

    def showImage(self, image_path):
        if os.path.isfile(image_path):
            self.imageview.scale(1/self.img_scale, 1/self.img_scale)
            self.imageview.scene().clear()
            pixmap = QPixmap(image_path)
            item = QGraphicsPixmapItem(pixmap)
            w1 = self.imageview.rect().width()
            w2 = pixmap.rect().width()
            h1 = self.imageview.rect().height()
            h2 = pixmap.rect().height()
            self.img_scale = w1/w2
            ratio = h1/h2
            if ratio<self.img_scale:
                self.img_scale = ratio
            self.imageview.scene().addItem(item)
            self.imageview.scale(self.img_scale, self.img_scale)
        else:
            print(f'image {image_path} not found')
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWidget()
    sys.exit(app.exec_())