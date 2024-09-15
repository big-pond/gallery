#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from math import floor, log10
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon  # , QPainter, QBrush
from PyQt5.QtWidgets import QWidget, QToolButton, QComboBox, QHBoxLayout


class LevelWdg(QWidget):
    sendLevel = pyqtSignal(int)

    def __init__(self, parent=None):
        super(LevelWdg, self).__init__(parent)
        mined = 17
        self.tbPlus = QToolButton(self)
        self.tbPlus.setMinimumHeight(mined+2)
        self.tbPlus.setText('+')
        self.tbPlus.setIcon(QIcon(':/resources/plus_l.png'))
        self.tbPlus.setToolTip(self.tr('Следующий уровень'))
        self.tbPlus.setCursor(Qt.ArrowCursor)
        self.tbMinus = QToolButton(self)
        self.tbMinus.setMinimumHeight(mined+2)
        self.tbMinus.setText('-')
        self.tbMinus.setIcon(QIcon(":/resources/minus_l.png"))
        self.tbMinus.setToolTip(self.tr("Предыдущий уровень"))
        self.tbMinus.setCursor(Qt.ArrowCursor)
        self.cbLevel = QComboBox()
        self.cbLevel.setMinimumHeight(mined)
        self.cbLevel.setMinimumWidth(50)
        self.cbLevel.setCursor(Qt.ArrowCursor)
        for i in range(1, 21):
            self.cbLevel.addItem('z {}'.format(i))
        vbl = QHBoxLayout()
        vbl.addWidget(self.tbPlus)
        vbl.addWidget(self.cbLevel)
        vbl.addWidget(self.tbMinus)
        vbl.setSpacing(2)
        self.setLayout(vbl)
        self.setMinimumWidth(90)

        self.tbMinus.clicked.connect(self.prevLevel)
        self.tbPlus.clicked.connect(self.nextLevel)
        self.cbLevel.currentIndexChanged.connect(self.levelChanged)

    def setLevel(self, val):
        self.cbLevel.setCurrentIndex(val)

    def prevLevel(self):
        self.cbLevel.setCurrentIndex(self.cbLevel.currentIndex() - 1)

    def nextLevel(self):
        self.cbLevel.setCurrentIndex(self.cbLevel.currentIndex() + 1)

    def levelChanged(self, idx):
        self.sendLevel.emit(idx)
        self.tbPlus.setEnabled(idx < self.cbLevel.count() - 1)
        self.tbMinus.setEnabled(idx > 0)

    def getLevel(self):
        return self.cbLevel.currentIndex()