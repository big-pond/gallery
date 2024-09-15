#!/usr/bin/env python3
# -*-coding: utf-8 -*-

from math import radians
from PyQt5.QtCore import QPointF, QRect, QRectF
from PyQt5.QtWidgets import QWidget, QVBoxLayout
import df
from mapscene import MapScene
from mapview import MapView
from scalewdg import ScaleWdg
from levelwdg import LevelWdg
from tilereader import TileReader
from ellipsoid import Ellipsoid
from projection import MercatorPro


class MapWidget(QWidget):
    def __init__(self, mapdescr, parent=None):
        super(MapWidget, self).__init__(parent)
        self.mapdescr = mapdescr
        self.setWindowTitle(mapdescr.name)
        self.tilereader = TileReader(mapdescr.name)
        self.tilereader.setCacheSize(mapdescr.cache_size)
        self.tilereader.setTimeOut(mapdescr.timeout)
        self.tilereader.urlbase = mapdescr.urlbase
        self.tilereader.cacheloadcontrol = mapdescr.tile_source
        self.mapView = MapView()
        vbl = QVBoxLayout()
        vbl.setContentsMargins(0, 0, 0, 0)
        vbl.addWidget(self.mapView)
        self.setLayout(vbl)
        self.levelwdg = LevelWdg(self)
        self.levelwdg.setGeometry(QRect(6, 6, 120, 30))
        self.scalewdg = ScaleWdg(self)
        self.scalewdg.move(6, 40)
        self.scalewdg.setScale(611)
        projection = MercatorPro(Ellipsoid(df.S6378137, 6378173, 0))
        self.mapScene = MapScene(projection)
        self.mapScene.setTileReader(self.tilereader)
        self.mapView.setScene(self.mapScene)
        self.levelwdg.sendLevel.connect(self.gotoLayer)
        self.setGeometry(QRect(0, 0, mapdescr.width, mapdescr.height))
        self.mapGoTo(mapdescr.lat, mapdescr.lon, mapdescr.z)

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        if self.mapScene is None:
            return
        displayed_rect = self.getDisplayedMapRect()
        self.mapScene.updateTiles(displayed_rect)

    def writeMapsSettings(self, settings):
        settings.beginGroup("Map")
        settings.setValue("level", self.mapScene.z)
        lat, lon = self.getMapPosition()
        settings.setValue("map_position_lat", lat)
        settings.setValue("map_position_lon", lon)
        settings.endGroup()

    def readMapsSettings(self, settings):
        settings.beginGroup("Map")
        z = settings.value("level", type=int)
        lat = settings.value("map_position_lat", type=float)
        lon = settings.value("map_position_lon", type=float)
        self.mapGoTo(lat, lon, z)
        settings.endGroup()

       
    def setTileSource(self, cacheloadcontrol):
        self.tilereader.cacheloadcontrol = cacheloadcontrol

    def mapGoTo(self, lat, lon, z=-1):
        if z >= 0:
            self.mapScene.setLevel(z)
            self.levelwdg.setLevel(z)
            self.scalewdg.setScale(self.mapScene.calculateScale(radians(lat)))
        X, Y = self.mapScene.degree_to_pixel(lat, lon)
        self.mapView.centerOn(X, Y)
        r = self.mapView.getDisplayedMapRect()
        self.mapScene.updateTiles(r)

    def gotoLayer(self, z):
        lat, lon = self.getMapPosition()
        self.mapScene.setLevel(z)
        self.scalewdg.setScale(self.mapScene.calculateScale(radians(lat)))
        X, Y = self.mapScene.degree_to_pixel(lat, lon)
        self.mapView.centerOn(X, Y)
        r = self.mapView.getDisplayedMapRect()
        self.mapScene.updateTiles(r)

    def getMapScene(self):
        return self.mapScene

    def getDisplayedMapRect(self):
        topleft = self.mapView.mapToScene(self.mapView.rect().topLeft())
        botright = self.mapView.mapToScene(self.mapView.rect().bottomRight())
        return QRectF(topleft, botright)

    def getDisplayedMapRectCenter(self):
        r = self.getDisplayedRect()
        return QPointF(r.x() + 0.5 * r.width(), r.y() + 0.5 * r.height())

    def getDisplayedMapRectCenterDeg(self):
        p = self.getDisplayedRectCenter()
        lat, lon = self.pixel_to_degree(p.x(), p.y())
        return lat, lon

    def getMapPosition(self):
        r = self.mapView.rect()
        p = self.mapView.mapToScene(r)
        X = (p[2].x() - p[0].x()) * 0.5 + p[0].x()
        Y = (p[2].y() - p[0].y()) * 0.5 + p[0].y()
        lat, lon = self.mapScene.pixel_to_degree(X, Y)
        return lat, lon

    def getLevel(self):
        return self.levelwdg.getLevel()

    def mapProperty(self):
        prop = '''Name: {0}
Datum: {1}
Projection: {2}
        '''.format(self.mapdescr.name, self.mapdescr.ellipsoid, self.mapdescr.projection)
        return prop
