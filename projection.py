#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from math import sqrt, sin, cos, pi, degrees, radians, exp, acos, asin, tan, atan, fabs, floor, atanh, sinh
from ellipsoid import Ellipsoid


class Projection(ABC):
    def __init__(self, el: Ellipsoid):
        self.name = "No"
        self.ellipsoid = el
        self.a = el.a
        self.e = el.eps
        self.k0 = 0.9996
        self.b = el.b  # малая полуось эллипсоида
        self.e2 = self.e * self.e
        self.e3 = self.e2 * self.e
        self.e4 = self.e3 * self.e
        self.e6 = self.e4 * self.e2
        self.e_2 = self.e ** 2 / (1 - self.e ** 2)
        self.e_4 = self.e_2 * self.e_2
        self.e_6 = self.e_4 * self.e_2
        self.e_8 = self.e_6 * self.e_2
        self.n = (self.a - self.b) / (self.a + self.b)

    @staticmethod
    def getZone(lon: float):
        """ //Нумерация зоны от долготы -180°
            (Например Екатеринбург в 41 зоне) соответствут зонам UTM
        """
        return floor(lon + 180) // 6 + 1

    @staticmethod
    def getDistanceOnPlane(x1: float, y1: float, x2: float, y2: float):
        return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2))

    @abstractmethod
    def geo_to_metre(self, lat: float, lon: float, deg=False, zone=0):
        pass

    @abstractmethod
    def metre_to_geo(self, x: float, y: float, deg=False, zone=0):
        pass

    # возвращает широту и долготу  по  x, y и уровню z тайла
    def tile_to_degree(self, x, y, z):
        lon = x / (1 << z) * 360 - 180
        z2 = 1 << (z - 1)
        south_hemisphere = y > z2
        if south_hemisphere:
            y = y - z2
        b = atan(sinh(pi * (1 - y / z2)))  # Первое приближение широты
        b2 = 0
        while True:
            e = self.e
            b2 = asin(1 - (1 + sin(b)) * pow(1 - e * sin(b), e) / (exp(2 * pi * (1 - y / z2)) * pow(1 + e * sin(b), e)))
            if fabs(b2 - b) < 1e-8:
                break
            else:
                b = b2
        if south_hemisphere:
            lat = -b2
        else:
            lat = b2
        lat = degrees(lat)
        return lat, lon

    # возвращает x и y тайла по уровню z, широте и долготе
    def degree_to_tile(self, lat, lon, z):
        x = floor((lon + 180) / 360 * (1 << z))
        b = radians(lat)
        y = floor((1 - (atanh(sin(b)) - self.e * atanh(self.e * sin(b))) / pi) * (1 << (z - 1)))
        return x, y


class MercatorPro(Projection):
    def __init__(self, el: Ellipsoid):
        # Projection.__init__(self, el)
        super().__init__(el)
        self.name = "Меркатора"

    def iterBr(self, x, brn):
        return asin(1 - (1 + sin(brn)) * pow(1 - self.e * sin(brn), self.e) / (
                    exp(2 * x / self.a) * pow(1 + self.e * sin(brn), self.e)))

    def geo_to_metre(self, lat: float, lon: float, deg=False, zone=0):
        if deg:
            lat = radians(lat)
            lon = radians(lon)
        y = self.a * lon
        x = self.a * (atanh(sin(lat)) - self.e * atanh(self.e * sin(lat)))
        return x, y

    def metre_to_geo(self, x: float, y: float, deg=False, zone=0):
        lon = y / self.a
        south_hemisphere = x < 0
        x = fabs(x)
        brn = atan(sinh(x / self.a))  # Первое приближение широты
        brn1 = 0
        while True:
            brn1 = self.iterBr(x, brn)
            if fabs(brn1 - brn) < 1e-8:
                break
            else:
                brn = brn1
        if south_hemisphere:
            lat = -brn1
        else:
            lat = brn1
        if deg:
            lat = degrees(lat)
            lon = degrees(lon)
        return lat, lon


class GKPro(Projection):
    def __init__(self, el: Ellipsoid):
        Projection.__init__(self, el)
        self.name = "Гаусса-Крюгера"

    def geo_to_metre(self, lat: float, lon: float, deg=False, zone=0):
        if deg:
            lat = radians(lat)
            lon = radians(lon)
        sinB = sin(lat)
        sin2B = sinB * sinB
        sin4B = sin2B * sin2B
        sin6B = sin2B * sin4B
        L = degrees(lon)
        n = zone
        if n == 0:
            n = Projection.getZone(L)
        if n > 30:
            n -= 30
        else:  # if(zone>0&&zone<31)
            n += 30

        loncm = 6 * n - 3 if n < 31 else 6 * n - 363
        l = radians(L - loncm)
        l2 = l * l
        sx1 = l2 * (109500 - 574700 * sin2B + 863700 * sin4B - 398600 * sin6B)
        sx2 = l2 * (278194 - 830174 * sin2B + 572434 * sin4B - 16010 * sin6B + sx1)
        sx3 = l2 * (672483.4 - 811219.9 * sin2B + 5420 * sin4B - 10.6 * sin6B + sx2)
        sx4 = l2 * (1594561.25 + 5336.535 * sin2B + 26.79 * sin4B + 0.149 * sin6B + sx3)
        sy1 = l2 * (79690 - 866190 * sin2B + 1730360 * sin4B - 945460 * sin6B)
        sy2 = l2 * (270806 - 1523417 * sin2B + 1327645 * sin4B - 21701 * sin6B + sy1)
        sy3 = l2 * (1070204.16 - 2136826.66 * sin2B + 17.98 * sin4B - 11.99 * sin6B + sy2)
        sy4 = l * cos(lat) * (6378245 + 21346.1415 * sin2B + 107.159 * sin4B + 0.5977 * sin6B + sy3)

        x = 6367558.4968 * lat - sin(2 * lat) * (16002.89 + 66.9607 * sin2B + 0.3515 * sin4B - sx4)
        y = ((5 + 10 * n) * 100000) + sy4
        return x, y

    def metre_to_geo(self, x: float, y: float, deg=False, zone=0):
        n = zone
        if n == 0:
            n = int(y * 1.0e-6)
        elif n > 30:
            n -= 30
        else:  # if(zone>0&&zone<31)
            n += 30
        betta = x / 6367558.4968
        sinbetta = sin(betta)
        sin2betta = sinbetta * sinbetta
        sin4betta = sin2betta * sin2betta
        B0 = betta + sin(2 * betta) * (0.00252588685 - 0.0000149186 * sin2betta + 0.00000011904 * sin4betta)
        z0 = (y - (10 * n + 5) * 100000.0) / (6378245 * cos(B0))
        z02 = z0 * z0
        sinB0 = sin(B0)
        sin2B0 = sinB0 * sinB0
        sin4B0 = sin2B0 * sin2B0
        sin6B0 = sin2B0 * sin4B0
        sb1 = z02 * (0.01672 - 0.0063 * sin2B0 + 0.01188 * sin4B0 - 0.00328 * sin6B0)
        sb2 = z02 * (0.042858 - 0.025318 * sin2B0 + 0.014346 * sin4B0 - 0.001264 * sin6B0 - sb1)
        sb3 = z02 * (0.10500614 - 0.04559916 * sin2B0 + 0.00228901 * sin4B0 - 0.00002987 * sin6B0 - sb2)
        DB = -z02 * sin(2 * B0) * (0.251684631 - 0.003369263 * sin2B0 + 0.000011276 * sin4B0 - sb3)
        sl1 = z02 * (0.0038 + 0.0524 * sin2B0 + 0.0482 * sin4B0 + 0.0032 * sin6B0)
        sl2 = z02 * (0.01225 + 0.09477 * sin2B0 + 0.03282 * sin4B0 - 0.00034 * sin6B0 - sl1)
        sl3 = z02 * (0.0420025 + 0.1487407 * sin2B0 + 0.005942 * sin4B0 - 0.000015 * sin6B0 - sl2)
        sl4 = z02 * (0.16778975 + 0.16273586 * sin2B0 - 0.0005249 * sin4B0 - 0.00000846 * sin6B0 - sl3)
        l = z0 * (1 - 0.0033467108 * sin2B0 - 0.0000056002 * sin4B0 - 0.0000000187 * sin6B0 - sl4)
        lat = B0 + DB
        loncm = 3
        if n < 31:
            loncm = 6 * n - 3;
        else:
            loncm = 6 * n - 3 - 360
        lon = radians(loncm) + l  # lon = 6*(n-0.5)/57.29577951+l;
        if deg:
            lat = degrees(lat)
            lon = degrees(lon)
        return lat, lon


class UTMPro(Projection):
    def __init__(self, el: Ellipsoid):
        Projection.__init__(self, el)
        self.name = "UTM"

    def geo_to_metre(self, lat: float, lon: float, deg=False, zone=0):
        londeg = lon
        if not deg:
            londeg = degrees(lon)  # долгота в градусах
        if deg:
            lat = radians(lat)
            lon = radians(lon)
        m = zone;
        if m == 0:
            m = 31 + int(londeg / 6)

        lon0 = radians(6 * m - 183)
        sinlt = sin(lat)
        sin2lt = sinlt * sinlt
        a = self.a
        n = self.n
        n2 = n * n
        n3 = n2 * n
        n4 = n3 * n
        n5 = n4 * n
        nu = self.a / sqrt(1 - self.e2 * sin2lt)
        p = lon - lon0
        A = a * (1 - n + 5 / 4 * (n2 - n3) + 81 / 64 * (n4 - n5))
        B = 3 / 2 * a * (n - n2 + 7 / 8 * (n3 - n4) + 55 / 64 * n5)
        C = 15 / 16 * a * (n2 - n3 + 3 / 4 * (n4 - n5))
        D = 35 / 48 * a * (n3 - n4 + 11 / 16 * n5)
        E = 315 / 512 * a * (n4 - n5)
        S = A * lat - B * sin(2 * lat) + C * sin(4 * lat) - D * sin(6 * lat) + E * sin(8 * lat)
        coslt = cos(lat)
        cos2lt = coslt * coslt
        cos3lt = cos2lt * coslt
        cos4lt = cos3lt * coslt
        cos5lt = cos4lt * coslt
        cos6lt = cos5lt * coslt
        cos7lt = cos6lt * coslt
        cos8lt = cos7lt * coslt
        tanlt = tan(lat)
        tan2lt = tanlt * tanlt
        tan4lt = tan2lt * tan2lt
        tan6lt = tan4lt * tan2lt
        k0 = self.k0
        T1 = S * k0
        T2 = nu * sinlt * coslt * k0 * 0.5
        T3 = nu * sinlt * cos3lt * k0 / 24 * (5 - tan2lt + 9 * self.e_2 * cos2lt + 4 * self.e_4 * cos4lt)
        T4 = (nu * sinlt * cos5lt * k0 / 720 * (61 - 58 * tan2lt + tan4lt
                                                + 270 * self.e_2 * cos2lt - 330 * tan2lt * self.e_2 * cos2lt
                                                + 445 * self.e_4 * cos4lt + 324 * self.e_6 * cos6lt - 680 * tan2lt * self.e_4 * cos4lt
                                                + 88 * self.e_8 * cos8lt - 600 * tan2lt * self.e_6 * cos6lt - 192 * tan2lt * self.e_8 * cos8lt))
        T5 = nu * sinlt * cos7lt * k0 / 40320 * (1385 - 3111 * tan2lt + 543 * tan4lt - tan6lt)
        T6 = nu * cos(lat) * k0
        T7 = nu * cos3lt * k0 / 6 * (1 - tan2lt + self.e_2 * cos2lt)
        T8 = (nu * cos5lt * k0 / 120 * (5 - 18 * tan2lt + tan4lt + 14 * self.e_2 * cos2lt
                                        - 58 * tan2lt * self.e_2 * cos2lt + 13 * self.e_4 * cos4lt
                                        + 4 * self.e_6 * cos6lt - 64 * tan2lt * self.e_4 * cos4lt - 24 * tan2lt * self.e_6 * cos6lt))
        T9 = nu * cos7lt * k0 / 5040 * (61 - 479 * tan2lt + 179 * tan4lt - tan6lt)

        y = T1 + p * p * T2 + T3 * p * p * p * p + T4 * p * p * p * p * p * p + T5 * p * p * p * p * p * p * p * p

        x = T6 * p + T7 * p * p * p + T8 * p * p * p * p * p + T9 * p * p * p * p * p * p * p
        x += 500000
        x += m * 1.e6
        return x, y

    def metre_to_geo(self, x: float, y: float, deg=False, zone=0):
        m = zone
        if zone == 0:
            m = int(x * 1e-6)
        k0 = self.k0
        M = y / k0
        mu = M / (self.a * (1 - self.e2 * 0.25 - 3 * self.e4 / 64 - 5 * self.e6 / 256))
        pow1e2 = sqrt(1 - self.e2)
        e1 = (1 - pow1e2) / (1 + pow1e2)
        J1 = (3 * self.e * 0.5 - 27 * self.e3 / 32)
        J2 = (21 * self.e2 / 16 - 55 * self.e4 / 32)
        J3 = (151 * self.e3 / 96)
        J4 = (1097 * self.e4 / 512)

        fp = mu + J1 * sin(2 * mu) + J2 * sin(4 * mu) + J3 * sin(6 * mu) + J4 * sin(8 * mu)
        C1 = self.e_2 * cos(fp) * cos(fp)
        T1 = tan(fp) * tan(fp)
        R1 = self.a * (1 - self.e2) / pow(1 - self.e2 * sin(fp) * sin(fp), 1.5)
        N1 = self.a / sqrt(1 - self.e2 * sin(fp) * sin(fp))
        xloc = x - m * 1.e6
        D = (500000 - xloc) / (N1 * k0)

        Q1 = N1 * tan(fp) / R1
        Q2 = 0.5 * D * D
        Q3 = (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * self.e_2) * D * D * D * D / 24
        Q4 = (61 + 90 * T1 + 298 * C1 + 45 * T1 * T1 - 3 * C1 * C1 - 252 * self.e_2) * D * D * D * D * D * D / 720
        lat = fp - Q1 * (Q2 - Q3 + Q4)
        Q6 = (1 + 2 * T1 + C1) * D * D * D / 6
        Q7 = (5 - 2 * C1 + 28 * T1 - 3 * C1 * C1 + 8 * self.e_2 + 24 * T1 * T1) * D * D * D * D * D / 120

        lon0 = radians(6 * m - 183)
        lon = lon0 - (D - Q6 + Q7) / cos(fp)
        if deg:
            lat = degrees(lat)
            lon = degrees(lon)
        return lat, lon


if __name__ == '__main__':
    elwgs = Ellipsoid()
    mercproj = MercatorPro(elwgs)
    lat, lon = 52.3333333, 42.5
    #    lat, lon = 52.185585, 42.662703  #сарай
    #    lat, lon = 56.75815615, 60.30841396 #оз. Чусовское .308 на O4125
    print('----Mercaror-elwgs---')
    x, y = mercproj.geo_to_metre(lat, lon, deg=True, zone=0)
    print('x={0:.1f} y={1:.1f}'.format(x, y))
    lat, lon = mercproj.metre_to_geo(x, y, True, 0)
    print('lat={0:.5f} lon={1:.5f}'.format(lat, lon))
    print('----tile_to_degree----')
    lat = 52.26444431  # Перекресток у Скопинки
    lon = 42.52015100
    print('Перекресток у Скопинки lat={0:.5f} lon={1:.5f}'.format(lat, lon))
    z = 12
    x, y = mercproj.degree_to_tile(lat, lon, z)
    print('x={0} y={1} z={2}'.format(x, y, z))
    z = 13
    x, y = mercproj.degree_to_tile(lat, lon, z)
    print('x={0} y={1} z={2}'.format(x, y, z))
    z = 14
    x, y = mercproj.degree_to_tile(lat, lon, z)
    print('x={0} y={1} z={2}'.format(x, y, z))
    z = 15
    x, y = mercproj.degree_to_tile(lat, lon, z)
    print('x={0} y={1} z={2}'.format(x, y, z))
    lat, lon = mercproj.tile_to_degree(x, y, z)
    print('lat={0:.5f} lon={1:.5f}'.format(lat, lon))

    elsph = Ellipsoid("Sph6378137", 6378137, 6378137)
    mercproj = MercatorPro(elsph)
    lat, lon = 52.3333333, 42.5
    print('----Mercaror-elsph-6378137---')
    x, y = mercproj.geo_to_metre(lat, lon, deg=True, zone=0)
    print('x={0:.1f} y={1:.1f}'.format(x, y))
    lat, lon = mercproj.metre_to_geo(x, y, True, 0)
    print('lat={0:.5f} lon={1:.5f}'.format(lat, lon))
    elsph0 = Ellipsoid("Sph6371000", 6371000, 6371000)
    mercproj = MercatorPro(elsph0)
    lat, lon = 52.3333333, 42.5
    print('----Mercaror-elsph-6371000----')
    x, y = mercproj.geo_to_metre(lat, lon, deg=True, zone=0)
    print('x={0:.1f} y={1:.1f}'.format(x, y))
    lat, lon = mercproj.metre_to_geo(x, y, True, 0)
    print('lat={0:.5f} lon={1:.5f}'.format(lat, lon))

    elkras = Ellipsoid('Krasovsky', 6378245, 1.0 / 298.3);
    gkproj = GKPro(elkras)
    lat, lon = 52.3333333, 42.5
    print('----GK----')
    x, y = gkproj.geo_to_metre(lat, lon, deg=True, zone=0)
    print('x={0:.1f} y={1:.1f}'.format(x, y))
    lat, lon = gkproj.metre_to_geo(x, y, True, 0)
    print('lat={0:.5f} lon={1:.5f}'.format(lat, lon))

    utmproj = UTMPro(elwgs)
    lat, lon = 52.3333333, 42.5
    print('----UTM----')
    x, y = utmproj.geo_to_metre(lat, lon, deg=True, zone=0)
    print('x={0:.1f} y={1:.1f}'.format(x, y))
    lat, lon = utmproj.metre_to_geo(x, y, True, 0)
    print('lat={0:.5f} lon={1:.5f}'.format(lat, lon))
    print('----Projection----')
    print(Projection.getDistanceOnPlane(100, 100, 200, 200))
