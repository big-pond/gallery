#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
import df


class MapDescript(ABC):
    def __init__(self):
        self.name = 'No name'
        self.ellipsoid = ''
        self.projection = ''
        self.urlbase = ''
        self.tile_source = 2  # QNetworkRequest::PreferCache
        self.timeout = 100
        self.cache_size = 50  # размер кэша в мегабайтах
        self.z_min = 0
        self.z_max = 19
        self.z = 0
        self.lat = 0.0
        self.lon = 0.0
        self.width = 256  # width map widget
        self.height = 256  # height map widget

    @abstractmethod
    def url(self, x: int, y: int, z: int):
        pass


class OSMDescript(MapDescript):
    def __init__(self):
        super().__init__()
        self.name = 'OSM'
        self.ellipsoid = df.S6378137
        self.projection = df.MERCATOR
        self.urlbase = 'https://b.tile.openstreetmap.org'

    def url(self, x, y, z):
        return '{}/{}/{}/{}.png'.format(self.urlbase, z, x, y)


class OTMDescript(MapDescript):
    def __init__(self):
        super().__init__()
        self.name = 'OTM'
        self.ellipsoid = df.S6378137
        self.projection = df.MERCATOR
        self.urlbase = 'https://a.tile.opentopomap.org'

    def url(self, x, y, z):
        return '{}/{}/{}/{}.png'.format(self.urlbase, z, x, y)
