#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import df

from math import sqrt, sin, cos, tan, pi, degrees, radians, acos, asin, atan, atan2, fabs


class Ellipsoid:
    def __init__(self, name=df.WGS84, a=6378245.0, b=6356863.019):  # по умолчанию Красовского
        self.name = name
        self.a = a
        self.b: float
        self.alpha: float  # полярное сжатие
        if b < 1:
            self.alpha = b
            self.b = a - a * self.alpha
        else:
            self.b = b
            self.alpha = (a - b) / a
        self.eps = sqrt(self.a ** 2 - self.b ** 2) / self.a  # эксцентриситет
        self.eps2 = 2 * self.alpha - self.alpha ** 2  # квадрат эксцентриситета
        self.eps_2 = (self.a ** 2 - self.b ** 2) / (self.b ** 2)  # квадрат второго эксцентриситета
        self.eps_ = sqrt(self.eps_2)  # второй эксцентриситет

    def N(self, lat):  # радиус кривизны первого вертикала, lat - широта, рад
        return self.a / sqrt(1 - self.eps2 * sin(lat) * sin(lat))

    def M(self, lat):  # радиус кривизны меридиана, lat - широта, рад
        return self.a * sqrt(1 - self.eps2) / pow(1 - self.eps2 * sin(lat) * sin(lat), 3 / 2)

    def mR(self, lat):  # средний радиус кривизны
        return self.a * sqrt(1 - self.eps2) / (1 - self.eps2 * sin(lat) * sin(lat))

    def lla_to_xyz(self, lat, lon, alt, deg=False):  # ГОСТ 51794-2001
        if deg:
            lat = radians(lat)
            lon = radians(lon)
        n = self.N(lat)
        x = (n + alt) * cos(lat) * cos(lon)
        y = (n + alt) * cos(lat) * sin(lon)
        z = ((1 - self.eps2) * n + alt) * sin(lat)
        return x, y, z

    def xyz_to_lla(self, x, y, z, deg=False):  # ГОСТ 51794-2001
        lat = float(0)
        lon = float(0)
        alt = float(0)
        D = sqrt(x * x + y * y)
        if D == 0:
            lat = pi / 2 * z / fabs(z)
            lon = float(0)
            sinlat = sin(lat)
            alt = z * sinlat - self.a * sqrt(1 - self.eps2 * sinlat * sinlat)
        elif D > 0:
            La = fabs(asin(y / D))  # !!!!!!!!ИСПРАВИТЬ В МОДУЛЯХ cpp отсутствует abs
            if y < 0 and x > 0:
                lon = 2 * pi - La
            elif y < 0 and x < 0:
                lon = pi + La
            elif y > 0 and x < 0:
                lon = pi - La
            elif y > 0 and x > 0:
                lon = La
            elif y == 0 and x > 0:
                lon = 0
            elif y == 0 and x < 0:
                lon = pi
            if z == 0:
                lat = 0
                alt = D - self.a
            else:
                r = sqrt(x * x + y * y + z * z)
                c = asin(z / r)
                p = self.eps2 * self.a / (2 * r)
                s1 = float(1)
                s2 = float(0)
                while fabs(s2 - s1) > 4.84814e-9:  # в 1 радиане 4,84814e-6 секунд (итерации до 1e-4"
                    s1 = s2  # то случае погрешность вычисления геодезической
                    lat = c + s1  # высоты не превышает 0,003 м.)
                    sinlat = sin(lat)
                    s2 = asin(p * sin(2 * lat) / sqrt(1 - self.eps2 * sinlat * sinlat))
                sinlat = sin(lat)
                alt = D * cos(lat) + z * sinlat - self.a * sqrt(1 - self.eps2 * sinlat * sinlat)
                if deg:
                    lat = degrees(lat)
                    lon = degrees(lon)
        return lat, lon, alt

    def getDistance3d(self, lat1, lon1, alt1, lat2, lon2, alt2, deg=False):
        x1, y1, z1 = self.lla_to_xyz(lat1, lon1, alt1, deg)
        x2, y2, z2 = self.lla_to_xyz(lat2, lon2, alt2, deg)
        return sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))

    def getDistanceEl(self, b1, l1, b2, l2, deg=False):
        dist = 0
        x1, y1, z1 = self.lla_to_xyz(b1, l1, 0, deg)
        x2, y2, z2 = self.lla_to_xyz(b2, l2, 0, deg)
        hord = sqrt((x1 - x2) * (x1 - x2) + (y1 - y2) * (y1 - y2) + (z1 - z2) * (z1 - z2))
        if (self.a > self.b):  # для эллипсоида
            # по сфере среднего радиуса кривизны
            if deg:
                b1 = radians(b1)
                b2 = radians(b2)
            r = self.mR(0.5 * (b1 + b2))
            alpha = 2.0 * asin(hord / (2.0 * r))
            dist = r * alpha
        else:  # для сферы
            alpha = 2.0 * asin(hord / (2.0 * self.a))
            dist = self.a * alpha
        return dist

    def getEquatorLength(self):
        return 2 * pi * self.a

    def getParallelLength(self, lat, deg=False):
        if deg:
            lat = radians(lat)
        return 2 * pi * self.a * cos(lat) / sqrt(1 - self.eps * self.eps * sin(lat) * sin(lat))

    def getVincentDistance(self, b1, l1, b2, l2):
        f = self.alpha
        L = radians(l2) - radians(l1)
        lambd = L
        U1 = atan((1 - f) * tan(radians(b1)))
        U2 = atan((1 - f) * tan(radians(b2)))
        cosU1 = cos(U1)
        cosU2 = cos(U2)
        sinU1 = sin(U1)
        sinU2 = sin(U2)
        # cos2alpha, sigma, sinsigma, cossigma, cossigmam2
        while True:
            sinlambda = sin(lambd)
            coslambda = cos(lambd)
            sinsigma = sqrt(cosU2 * sinlambda * cosU2 * sinlambda
                            + pow(cosU1 * sinU2 - sinU1 * cosU2 * coslambda, 2.))
            cossigma = sinU1 * sinU2 + cosU1 * cosU2 * coslambda
            sigma = atan2(sinsigma, cossigma)
            # sinalpha = (sinsigma==0.) ? 0. : (cosU1*cosU2*sinlambda)/sinsigma
            sinalpha = 0 if sinsigma == 0 else (cosU1 * cosU2 * sinlambda) / sinsigma
            cos2alpha = 1. - sinalpha * sinalpha
            # cossigmam2 = (cos2alpha==0.) ? 0. : cossigma - 2*sinU1*sinU2/cos2alpha
            cossigmam2 = 0 if cos2alpha == 0 else cossigma - 2 * sinU1 * sinU2 / cos2alpha
            C = f / 16 * cos2alpha * (4 + f * (4 - 3 * cos2alpha))
            lambda1 = L + (1 - C) * f * sinalpha * (sigma + C * sinsigma * (cossigmam2 + C * cossigma
                                                                            * (-1 + 2 * cossigmam2 * cossigmam2)))
            if fabs(lambd - lambda1) < 1.e-12:
                break
            else:
                lambd = lambda1
        u2 = cos2alpha * (self.a * self.a - self.b * self.b) / (self.b * self.b)
        A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
        B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
        dsigma = B * sinsigma * (cossigmam2 + 0.25 * B * (cossigma * (-1 + 2 * cossigmam2 * cossigmam2)
                                                          - (B / 6.) * cossigmam2 * (-3 + 4 * sinsigma * sinsigma)
                                                          * (-3 + 4 * cossigmam2 * cossigmam2)))
        azrad = atan2(cosU2 * sin(lambd), (cosU1 * sinU2 - sinU1 * cosU2 * cos(lambd)))
        if azrad < 0:
            azrad += pi * pi
        az1 = degrees(azrad)
        if az1 >= 360:
            az1 -= 360
        azrad = atan2(cosU1 * sin(lambd), (-sinU1 * cosU2 + cosU1 * sinU2 * cos(lambd))) + pi
        if azrad < 0:
            azrad += pi * pi
        az2 = degrees(azrad)
        if az2 >= 360:
            az2 -= 360
        return self.b * A * (sigma - dsigma)


if __name__ == '__main__':
    el = Ellipsoid()
    lat = 52
    lon = 42
    alt = 150
    x, y, z = el.lla_to_xyz(lat, lon, alt, True)
    print('x=', x, 'y=', y, 'z=', z)
    lat, lon, alt = el.xyz_to_lla(x, y, z, True)
    print('lat=', lat, 'lon=', lon, 'alt=', alt)
    lat = -52
    lon = 42
    alt = 150
    x, y, z = el.lla_to_xyz(lat, lon, alt, True)
    print('x=', x, 'y=', y, 'z=', z)
    lat, lon, alt = el.xyz_to_lla(x, y, z, True)
    print('lat=', lat, 'lon=', lon, 'alt=', alt)
    lat = -52
    lon = 318
    alt = 150
    x, y, z = el.lla_to_xyz(lat, lon, alt, True)
    print('x=', x, 'y=', y, 'z=', z)
    lat, lon, alt = el.xyz_to_lla(x, y, z, True)
    print('lat=', lat, 'lon=', lon, 'alt=', alt)
    lat = 52
    lon = 318
    alt = 150
    x, y, z = el.lla_to_xyz(lat, lon, alt, True)
    print('x=', x, 'y=', y, 'z=', z)
    lat, lon, alt = el.xyz_to_lla(x, y, z, True)
    print('lat=', lat, 'lon=', lon, 'alt=', alt)

    lat = 52
    lon = -42
    alt = 150
    x, y, z = el.lla_to_xyz(lat, lon, alt, True)
    print('x=', x, 'y=', y, 'z=', z)
    lat, lon, alt = el.xyz_to_lla(x, y, z, True)
    print('lat=', lat, 'lon=', lon, 'alt=', alt)

    lat1 = 52.3333
    lon1 = 42.5
    lat2 = 56.7902
    lon2 = 60.5978

    print('getDistance3d', el.getDistance3d(lat1, lon1, 0, lat2, lon2, 0, deg=True))
    print('getDistance3d', el.getDistance3d(lat1, lon1, 120, lat2, lon2, 300, True))
    print('getDistanceEl', el.getDistanceEl(lat1, lon1, lat2, lon2, True))
    print('getEquatorLength', el.getEquatorLength())
    print('getParalleLength', el.getParallelLength(lat1, True))
    print('getVincentDistance', el.getVincentDistance(lat1, lon1, lat2, lon2))
