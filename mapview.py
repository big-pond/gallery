# -*- coding: utf-8 -*-

import cf
from math import degrees
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize, QRectF
from PyQt5.QtGui import QCursor, QImage, QBitmap
from PyQt5.QtWidgets import QGraphicsView, QRubberBand, QMessageBox
from mapscene import MapScene


class MapView(QGraphicsView):
    COORD_UNIT = cf.PIXEL
    sendMouseMoveXY = pyqtSignal(float, float)
    sendCoordinates = pyqtSignal(float, float, float)
    sendLatLon = pyqtSignal(float, float)
    sendFilterCoordinames = pyqtSignal(float, float, float, float)

    def __init__(self, parent=None):
        super(MapView, self).__init__(parent)
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        self.horizontalScrollBar().setCursor(Qt.ArrowCursor)
        self.verticalScrollBar().setCursor(Qt.ArrowCursor)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selectRect = False
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.rbStart = QPoint()

    def getDisplayedMapRect(self):
        topleft = self.mapToScene(self.rect().topLeft())
        botright = self.mapToScene(self.rect().bottomRight())
        return QRectF(topleft, botright)

    def mousePressEvent(self, event):
        p = self.mapToScene(event.pos())
        mapscene = self.scene()
        lat, lon = mapscene.pixel_to_degree(p.x(), p.y())
        

        if event.button() == Qt.LeftButton:
            if self.selectRect:
                self.rbStart = event.pos()
                self.rubberBand.setGeometry(QRect(self.rbStart, QSize()))
                self.rubberBand.show()
            else: 
                self.setDragMode(QGraphicsView.ScrollHandDrag)
        if event.button() == Qt.RightButton:
            self.sendLatLon.emit(lat, lon)
        super(MapView, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        super(MapView, self).mouseReleaseEvent(event)
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
            topleft = self.mapToScene(self.rect().topLeft())
            botright = self.mapToScene(self.rect().bottomRight())
            rf = QRectF(topleft, botright)
            self.scene().updateTiles(rf)
        if self.selectRect:
            p1 = self.rubberBand.geometry().bottomLeft()
            p1 = self.mapToScene(p1)
            p2 = self.rubberBand.geometry().topRight()
            p2 = self.mapToScene(p2)
            mapscene = self.scene()
            lat1, lon1 = mapscene.pixel_to_degree(p1.x(), p1.y())
            lat2, lon2 = mapscene.pixel_to_degree(p2.x(), p2.y())
            self.rubberBand.hide()
            self.selectRect = False
            # print(f'x1={p1.x()}, y1={p1.y()}, x2={p2.x()}, y2={p2.y()}')
            self.sendFilterCoordinames.emit(lat1, lon1, lat2, lon2)

    def mouseMoveEvent(self, event):
        QGraphicsView.mouseMoveEvent(self, event)
        if self.selectRect:
            self.rubberBand.setGeometry(QRect(self.rbStart, event.pos()).normalized())
        p = self.mapToScene(event.pos())
        self.sendMouseMoveXY.emit(p.x(), p.y())
        mapscene = self.scene()
        x, y = mapscene.pixel_to_rad(p.x(), p.y())
        scale = mapscene.calculateScale(x)
        if MapView.COORD_UNIT == cf.PIXEL:
            x = p.x()
            y = p.y()
        elif MapView.COORD_UNIT == cf.METRE:
            x, y = self.scene().pixel_to_metre(p.x(), p.y())
        elif MapView.COORD_UNIT == cf.DEG or MapView.COORD_UNIT == cf.DEGMIN or MapView.COORD_UNIT == cf.DEGMINSEC:
            x = degrees(x)
            y = degrees(y)
        elif MapView.COORD_UNIT == cf.RAD:
            None
        self.sendCoordinates.emit(x, y, scale)  # посылаются координаты в датуме карты
