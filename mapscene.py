#!/usr/bin/env python3
# -*-coding: utf-8 -*-

from PyQt5.QtCore import Qt, QRect, QRectF, QPointF
from PyQt5.QtGui import QTransform, QPen, QBrush, QImage, QColor
from PyQt5.QtWidgets import QGraphicsScene

from tilereader import TileReader

from math import degrees, atan2, pi


class MapScene(QGraphicsScene):
    VIEW, INSERT_PNT, APPEND_PNT, SELECT_PNT, DRAG_PNT = range(5)

    def __init__(self, projection, parent=None):
        super(MapScene, self).__init__(parent)
        self.projection = projection
        # self.datawdg = datawdg
        self.transf = QTransform()  # метры карты в единицы сцены (единица сцены соответствует 1 пикселю тайла)
        self.backtransf = QTransform()  # единицы  сцены в метры карты
        self.tile_width = 256
        self.tile_height = 256
        self.tilereader: TileReader
        self.z = 1  # уровень для тайлов [0-20]
        self.mapmode = MapScene.VIEW
        self.drawtileborders = False
        self.photo_pos = QPointF(0,0)
        self.visible_photo_pos = False
        # self.datawdg.ui.tvTrack.selectionModel().currentChanged.connect(self.drawCurrentTrackPos)

    def setTileReader(self, val):
        self.tilereader = val
        self.tilereader.sendUpdateTileRect.connect(self.updateTileRect)

    def setLevel(self, val):
        self.z = val
        self.calibrate()

    def setVisiblePhotoPos(self, visible: bool):
        self.visible_photo_pos = visible

    def setPhotoPos(self, lat, lon):
        self.photo_pos.setX(lat)
        self.photo_pos.setY(lon)

    def calibrate(self):
        # находим длину окружности по экватору
        eqlen = self.projection.ellipsoid.getEquatorLength()
        eqlen05 = 0.5 * eqlen
        # находим количество строк тайлов (равно количчеству колонок) для уровня level
        rowcol = (1 << self.z)  # rowcol = (1 << (level-1))
        h = self.tile_height * rowcol
        w = self.tile_width * rowcol
        self.setSceneRect(0, 0, w, h)
        self.transf.reset()
        self.transf.rotate(-90)
        self.transf.scale(h / eqlen, w / eqlen)
        self.transf.translate(-eqlen05, eqlen05)
        self.backtransf = self.transf.inverted()[0]

    def calculateScale(self, lat):  # lat - в радианах
        el = self.projection.ellipsoid.getParallelLength(lat)
        rowcol = (1 << self.z)  # rowcol = (1 << (level-1));
        return el / (rowcol * self.tile_width)

    def pixel_to_metre(self, X, Y):
        return self.backtransf.map(X, Y)  # return x,y

    def metre_to_pixel(self, x, y):
        return self.transf.map(x, y)  # return X, Y

    def pixel_to_degree(self, X, Y):
        x, y = self.backtransf.map(X, Y)
        return self.projection.metre_to_geo(x, y, True)  # return lat, lon

    def degree_to_pixel(self, lat, lon):
        x, y = self.projection.geo_to_metre(lat, lon, True)
        return self.transf.map(x, y)  # return X, Y

    def pixel_to_rad(self, X, Y):
        x, y = self.backtransf.map(X, Y)
        return self.projection.metre_to_geo(x, y)  # lat, lon

    def rad_to_pixel(self, lat, lon):
        x, y = self.projection.geo_to_metre(lat, lon)
        return self.transf.map(x, y)  # return X, Y

    def setViewTileBorders(self, visibility):
        self.drawtileborders = visibility
        self.update()

    def drawTileBorders(self, painter, rect):
        th = self.tile_height
        tw = self.tile_width
        startcol = int(rect.x() / tw)
        startrow = int(rect.y() / th)
        endcol = int((rect.x() + rect.width()) / tw)
        endrow = int((rect.y() + rect.height()) / th)
        pen = QPen()
        pen.setColor(Qt.gray)
        pen.setWidth(0)
        painter.save()
        painter.setPen(pen)
        for y in range(startrow, endrow + 1):
            for x in range(startcol, endcol + 1):
                if (y >= 0) and (x >= 0) and (x < (1 << self.z)) and (y < (1 << self.z)):
                    tilerect = QRect(x * tw, y * th, tw, th)
                    painter.drawText(tilerect.x() + tw / 4, tilerect.y() + th / 2,
                                     'z={} x={} y={}'.format(self.z, x, y))
                    painter.drawRect(tilerect)
        painter.restore()

    def drawBackground(self, painter, rect):
        if self.tilereader.tiles:
            for z in range(self.z + 1):
                self.drawTileLayer(painter, rect, z)
        if self.drawtileborders:
            self.drawTileBorders(painter, rect)
        if self.visible_photo_pos:
            painter.save()
            pen = QPen()
            pen.setColor(Qt.red)
            pen.setWidth(2)
            painter.setBrush(QBrush(Qt.green))
            x, y = self.degree_to_pixel(self.photo_pos.x(), self.photo_pos.y())
            painter.drawEllipse(QRectF(x, y, 6, 6))
            painter.restore()


    def updateTiles(self, r):
        startcol = int(r.x() / self.tile_width)
        startrow = int(r.y() / self.tile_height)
        colcount = int(r.width() / self.tile_width) + 1
        rowcount = int(r.height() / self.tile_height) + 1
        for y in range(startrow, startrow + rowcount + 1):
            for x in range(startcol, startcol + colcount + 1):
                # проверка x и y на выход за максимпльные значения строк и колонок
                self.tilereader.placeKeyTileToQueue(x, y, self.z)

    def updateTileRect(self, x, y, z):
        rect = QRectF(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height)
        self.update(rect)

    def drawTileLayer(self, painter, rect, z):
        n = self.z - z
        mnog = (1 << abs(n))
        # print('n {}, mnog {}, z {}'.format(n, mnog, z))
        th = self.tile_height
        tw = self.tile_width
        if n >= 0:  # тайлы слоя увеличиваются
            mnog = 1. / mnog
        startcol = int(rect.x() / tw * mnog)
        startrow = int(rect.y() / th * mnog)
        endcol = int((rect.x() + rect.width()) / tw * mnog)
        endrow = int((rect.y() + rect.height()) / th * mnog)
        max_row_col = 1 << z
        if endcol > max_row_col:
            endcol = max_row_col
        if endrow > max_row_col:
            endrow = max_row_col
        # print('x:{}-{}, y:{}-{}'.format(startcol, endcol, startrow, endrow))
        for y in range(startrow, endrow + 1):
            for x in range(startcol, endcol + 1):
                key = '{}&{}&{}'.format(x, y, z)  # key = defineKey(x, y, z);
                if key in self.tilereader.tiles:
                    tilerect = self.tileRect(x, y, z)
                    painter.drawPixmap(tilerect, self.tilereader.tiles[key])
                else:
                    if (z == self.z) and (y >= 0) and (x >= 0) and (x < (1 << z)) and (y < (1 << z)):
                        pen = QPen()
                        pen.setColor(Qt.red)
                        painter.save()
                        painter.setPen(pen)
                        painter.setOpacity(0.3)
                        tilerect = QRect(x * tw, y * th, tw, th)  # tileRect(x, y, z);
                        painter.drawText(round(tilerect.x() + tw / 2 - 20), round(tilerect.y() + th / 2 - 20), "no tile")
                        painter.restore()

    def tileRect(self, x, y, z):
        n = self.z - z
        mnog = (1 << abs(n))
        th = self.tile_height
        tw = self.tile_width
        if n >= 0:  # тайлы слоя увеличиваются
            r = QRect(x * tw * mnog, y * th * mnog, tw * mnog, th * mnog)
        else:
            r = QRect(int(x * tw / mnog), int(y * th / mnog), int(tw / mnog), int(th / mnog))
        return r



if __name__ == '__main__':
    projection = None
    ms = MapScene(projection)
    ms.setLevel(10)
