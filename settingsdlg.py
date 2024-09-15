#!/usr/bin/env python3
# -*-coding: utf-8 -*-

from PyQt5.QtWidgets import (QLabel, QLineEdit, QDialog, QFileDialog, QGridLayout, QDialogButtonBox, 
                             QToolButton)
import df


class SettingsDlg(QDialog):
    def __init__(self, parent=None):
        super(SettingsDlg, self).__init__(parent)
        gl = QGridLayout()
        gl.setVerticalSpacing(2)
        gl.addWidget(QLabel(self.tr("Base path for photo")), 0, 0)
        self.leBasePath = QLineEdit()
        gl.addWidget(self.leBasePath, 0, 1)
        tbBasePath = QToolButton()
        tbBasePath.setText('...')
        gl.addWidget(tbBasePath, 0, 2)
        tbBasePath.clicked.connect(self.selectBasePhotoDir)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        gl.addWidget(self.buttonBox, 1, 0, 1, 2)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.setLayout(gl)
        self.setWindowTitle('Settings)')
        self.leBasePath.setText(df.base_photo_path)

    def accept(self) -> None:
        if df.base_photo_path!= self.leBasePath.text():
            df.base_photo_path = self.leBasePath.text()
        QDialog.accept(self)

    def selectBasePhotoDir(self):
        dir = QFileDialog.getExistingDirectory(self, self.tr("Select directory"), self.leBasePath.text(),
                                               QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if dir:
            self.leBasePath.setText(dir)
