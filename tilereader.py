#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from queue import Queue
from PyQt5.QtCore import QObject, QTimer, QUrl, pyqtSignal

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest


class TileReader(QObject):
    sendUpdateTileRect = pyqtSignal(int, int, int)

    def __init__(self, cache_dir, parent=None):
        super(QObject, self).__init__()
        self.cache = QNetworkDiskCache(self)
        self.cache.setCacheDirectory(cache_dir)
        self.manager = QNetworkAccessManager(self)
        self.manager.setCache(self.cache)
        self.request = QNetworkRequest()
        self.timer = QTimer(self)
        self.queue = Queue()
        self.tiles = dict()
        self.urlbase = ''
        self.cacheloadcontrol = QNetworkRequest.PreferCache
        # Скачивание  по  сигналу  таймера
        self.timer.timeout.connect(self.download)
        self.manager.finished.connect(self.handleNetworkReply)

    def setTimeOut(self, ms):
        self.timer.start(ms)

    def setCacheSize(self, size):
        self.cache.setMaximumCacheSize(size * 1024 * 1024)

    def setUrlBase(self, urlbase):
        self.urlbase = urlbase

    def download(self):
        if not self.queue.empty():
            key = self.queue.get()
            x, y, z = TileReader.posFromKey(key)
            url = self.getTileURL(x, y, z)
            self.request.setUrl(QUrl(url))
            self.request.setRawHeader("User-Agent".encode(), "GPX on map".encode())
            self.request.setAttribute(QNetworkRequest.User, key)
            self.request.setAttribute(QNetworkRequest.CacheLoadControlAttribute, self.cacheloadcontrol)
            self.manager.get(self.request)

    def handleNetworkReply(self, reply):
        img = QImage()
        key = reply.request().attribute(QNetworkRequest.User)
        if not reply.error():
            img.load(reply, '')
        else:
            print("err", reply.error(), key)
        reply.deleteLater()
        if not img.isNull():
            pxm = QPixmap.fromImage(img)
            self.tiles[key] = pxm  # вместо   saveTileToCache(key, pxm);
            x, y, z = TileReader.posFromKey(key)
            self.sendUpdateTileRect.emit(x, y, z)

    def placeKeyTileToQueue(self, x, y, z):
        key = '{}&{}&{}'.format(x, y, z)
        self.queue.put(key)

    def getTileURL(self, x, y, z):
        return '{}/{}/{}/{}.png'.format(self.urlbase, z, x, y) # http://tile.openstreetmap.org  urlbase+"/"+z+"/"+x+"/"+y+".png"

    @staticmethod
    def posFromKey(key):
        x, y, z = key.split('&')
        return int(x), int(y), int(z)
