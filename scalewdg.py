#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import floor, log10
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush
from PyQt5.QtWidgets import QWidget


class ScaleWdg(QWidget):
    def __init__(self, parent=None):
        super(ScaleWdg, self).__init__(parent)
        self.mtopix = 0.0
        self.m = 0.0  # единица масштаба
        self.l = 0.0  # длина линии m метров в пикселях
        self.sm = ''
        self.h_del = 8  # высота деления шкалы (pix)
        self.xstart = 5  # координата x начала масштабной линии
        self.y_l = 28  # координата y масштабной линии
        self.setGeometry(0, 0, 120, self.y_l + 4)

    def setScale(self, mtopix):  # /*, const double& scale*/
        self.mtopix = mtopix  # /*/scale*/;
        m_in_100pix = mtopix * 100.0
        pst = floor(log10(m_in_100pix))  # показатель степени
        x = m_in_100pix / pow(10, pst)  # x (10;1)
        if x >= 10.0:
            self.m = 10.0
        elif 10.0 > x >= 7.5:
            self.m = 7.5
        elif 7.5 > x >= 5.0:
            self.m = 5.0
        elif 5.0 > x >= 2.5:
            self.m = 2.5
        elif 2.5 > x >= 1.0:
            self.m = 1.0
        self.m *= pow(10, pst)
        self.l = self.m / self.mtopix

        self.setFixedWidth(int(self.l) + 40)
        if self.m >= 5000:
            self.sm = '{:.1f} км'.format(self.m * 0.001)
        else:
            self.sm = '{:.0f} м'.format(self.m)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(Qt.white)
        painter.setBrush(QBrush(Qt.white))
        r = painter.fontMetrics().boundingRect(self.sm)
        painter.setOpacity(0.7)
        painter.drawRect(0, 0, round(self.xstart + self.l + r.width() / 2), self.y_l + 4)
        painter.setOpacity(1)
        painter.setPen(Qt.black)
        painter.drawLine(self.xstart, self.y_l, round(self.xstart + self.l), self.y_l)
        painter.drawLine(self.xstart, self.y_l, self.xstart, self.y_l - self.h_del)  # первое деление
        painter.drawLine(round(self.xstart + self.l), self.y_l, round(self.xstart + self.l), self.y_l - self.h_del)  # второе деление
        painter.drawText(self.xstart, self.y_l - r.height() - 2, '0')
        painter.drawText(round(self.xstart + self.l - r.width() / 2), self.y_l - r.height() - 2, self.sm)
        painter.end()
