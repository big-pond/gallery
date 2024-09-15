#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import fabs, floor, radians

LATITUDE, LONGITUDE = range(2)

# Формат отображения
DEG, DEGMIN, DEGMINSEC, FLOAT, RAD, METRE, PIXEL = range(7)

DPR = 6
DFW = DPR + 3
MPR = 5
MFW = MPR + 3
SPR = 2
SFW = SPR + 3

LatD_mask = '''09.900000°A'''  # Число знаков после точки должно быть равно DPR
LatDM_mask = '''09°09.90000'A'''  # Число знаков после точки должно быть равноMPR
LatDMS_mask = '''09°09'09.90"A'''  # Число знаков после точки должно быть равно SPR
LonD_mask = '''009.900000°A'''  # Число знаков после точки должно быть равно DPR
LonDM_mask = '''009°09.90000'A'''  # Число знаков после точки должно быть равно MPR
LonDMS_mask = '''009°09'09.90"A'''  # Число знаков после точки должно быть равно SPR


def degToDms(deg: float):
    sign = 1
    if deg < 0:
        sign = -1
        deg = fabs(deg)
    g = floor(deg)
    mf = (deg - g) * 60
    m = floor(mf)
    s = (mf - m) * 60
    return g, m, s, sign


def dmsToDeg(d, m, s, sign):
    deg = d + m * 60 + s * 3600
    if sign < 0:
        deg = -deg
    return deg


def degToDm(deg):
    sign = 1
    if deg < 0:
        sign = -1
        deg = fabs(deg)
    g = floor(deg)
    m = (deg - g) * 60
    return g, m, sign


def dmToDeg(d, m, sign):
    deg = d + m * 60
    if sign < 0:
        deg = -deg
    return deg


def latToDmsStr(lt: float):
    g, m, s, sign = degToDms(lt)
    hs = 'S' if sign == -1 else 'N'
    return '{0:02d}°{1:02d}\'{2:05.2f}"{3}'.format(g, m, s, hs)


def latToDmStr(lt: float):
    g, m, sign = degToDm(lt)
    hs = 'S' if sign == -1 else 'N'
    return "{0:02d}°{1:07.4f}'{2}".format(g, m, hs)


def latToDegStr(lt: float):
    deg = fabs(lt)
    hs = 'S' if lt < 0 else 'N'
    return "{0:09.6f}°{1}".format(deg, hs)


def latToStr(lt: float):
    return '{:09.6f}'.format(lt)


def latToStr1(lat, format):
    if format == DEG:
        return latToDegStr(lat)
    elif format == DEGMIN:
        return latToDmStr(lat)
    elif format == DEGMINSEC:
        return latToDmsStr(lat)
    elif format == FLOAT:
        return latToStr(lat)
    return


def latToRadStr(lt: float):
    rad = fabs(radians(lt))
    hs = 'S' if lt < 0 else 'N'
    return '{0:09.7f}{1}'.format(rad, hs)


def lonToDmsStr(ln: float):
    g, m, s, sign = degToDms(ln)
    hs = 'W' if sign == -1 else 'E'
    return '{0:03d}°{1:02d}\'{2:05.2f}"{3}'.format(g, m, s, hs)


def lonToDmStr(ln: float):
    g, m, sign = degToDm(ln)
    hs = 'W' if sign == -1 else 'E'
    return "{0:03d}°{1:07.4f}'{2}".format(g, m, hs)


def lonToDegStr(ln: float):
    deg = fabs(ln)
    hs = 'W' if ln < 0 else 'E'
    return "{0:010.6f}°{1}".format(deg, hs)


def lonToStr(ln: float):
    return '{:010.6f}'.format(ln)


def lonToStr1(lon, format):
    if format == DEG:
        return lonToDegStr(lon)
    elif format == DEGMIN:
        return lonToDmStr(lon)
    elif format == DEGMINSEC:
        return lonToDmsStr(lon)
    elif format == FLOAT:
        return lonToStr(lon)
    return


def lonToRadStr(ln: float):
    rad = fabs(radians(ln))
    hs = 'W' if ln < 0 else 'E'
    return '{0:09.7f}{1}'.format(rad, hs)


def degLatLonToDmsStr(lt: float, ln: float):
    return 'B: {0}  L: {1}'.format(latToDmsStr(lt), lonToDmsStr(ln))


def degLatLonToDmStr(lt: float, ln: float):
    return 'B: {0}  L: {1}'.format(latToDmStr(lt), lonToDmStr(ln))


def degLatLonToDegStr(lt: float, ln: float):
    return 'B: {0}  L: {1}'.format(latToDegStr(lt), lonToDegStr(ln))


def degLatLonToRadStr(lt: float, ln: float):
    return 'B: {0}  L: {1}'.format(latToRadStr(lt), lonToRadStr(ln))


def radLatLonToRadStr(lt: float, ln: float):
    hs1 = 'S' if lt < 0 else 'N'
    hs2 = 'W' if ln < 0 else 'E'
    return 'B: {0:09.7f}{1}  L: {2:09.7f}{3}'.format(lt, hs1, ln, hs2)


def secToHourMinSec(sec):  # Время выполнения такое же как и у secToHourMinSec1
    minutes = int(sec / 60)
    sec = int(sec - minutes * 60)
    hour = int(minutes / 60)
    minutes = int(minutes - hour * 60)
    return hour, minutes, sec


def secToHourMinSec1(sec):
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)
    return h, m, s


def getFormat(fc):
    if fc == DEG:
        return "0.000000°"
    elif fc == DEGMIN:
        return "00°00.0000'"
    elif fc == DEGMINSEC:
        return '''00°00'00.00"'''
    elif fc == FLOAT:
        return "0.000000"
    else:
        return "0.000000"


if __name__ == '__main__':
    x, y = 52.185585, 42.662703
    print(degToDms(x))
    print(degToDm(x))
    print(latToDmsStr(x))
    print(latToDmStr(x))
    print(latToDegStr(x))
    print(latToStr(x))
    print(latToRadStr(x))
    print(lonToDmsStr(y))
    print(lonToDmStr(y))
    print(lonToDegStr(y))
    print(lonToStr(y))
    print(lonToRadStr(y))
    print(degLatLonToDmsStr(x, y))
    print(degLatLonToDmStr(x, y))
    print(degLatLonToDegStr(x, y))
    print(degLatLonToRadStr(x, y))
    print(radLatLonToRadStr(radians(x), radians(y)))
    print(latToStr1(x, DEG))
    print(latToStr1(x, DEGMIN))
    print(latToStr1(x, DEGMINSEC))
    print(latToStr1(x, FLOAT))
    print(lonToStr1(y, DEG))
    print(lonToStr1(y, DEGMIN))
    print(lonToStr1(y, DEGMINSEC))
    print(lonToStr1(y, FLOAT))

    # start_time = time.time()
    # for i in range(100000):
    # secToHourMinSec(86200)
    # finish_time = time.time()
    # print("secToHourMinSec--- %s seconds ---" % (finish_time - start_time))    
    # for i in range(10000):
    # secToHourMinSec1(862000)
    # finish_time = time.time()
    # print("secToHourMinSec1--- %s seconds ---" % (finish_time - start_time))
