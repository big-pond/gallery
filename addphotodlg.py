import ui_addphotodlg
import os 
import df
from pathlib import Path
from PyQt5.QtGui     import QIcon, QPixmap
from PyQt5.QtCore    import Qt, QFile, pyqtSignal
from PyQt5.QtWidgets import (QDialog, QFileDialog, QMessageBox, QLineEdit, QLabel)

class AddPhotoDlg(QDialog):
    def __init__(self, model, index, parent=None):
        super(AddPhotoDlg, self).__init__(parent)
        self.ui = ui_addphotodlg.Ui_AddPhotoDlg()
        self.ui.setupUi(self)
        self.model = model
        self.index = index
        print(self.index.row(), self.index.column())
        self.extension = 'png'
        self.ui.tbSelectPhoto.clicked.connect(self.selectPhoto)

    def selectPhoto(self):
        img, extension = QFileDialog.getOpenFileName(self, "Select photo", os.getcwd(),
            "Image (*.png *.jpg)",
            options=QFileDialog.Options())
        self.ui.leSelectedFile.setText(img)
        filename, self.extension = os.path.splitext(img)
        if img:
            pixmapImagen = QPixmap(img).scaled(self.ui.lbImage.width(), self.ui.lbImage.height(),
                               Qt.KeepAspectRatio,
                               Qt.SmoothTransformation)
            self.ui.lbImage.setPixmap(pixmapImagen)   


    def accept(self) -> None:
        filename = self.ui.leSelectedFile.text()
        copied_file = self.ui.leNewFileName.text()
        if copied_file:
            copied_file = copied_file + self.extension
            copy_to = str(Path(df.base_photo_path, copied_file))
            print(filename, copy_to)
            qf = QFile(filename)
            if qf.copy(copy_to):
                row = self.index.row()
                self.model.insertRows(row, 1)
                if self.ui.leTitle.text():
                    self.model.setData(self.model.index(row, 1), self.ui.leTitle.text())
                if self.ui.teDescr.toPlainText():
                    self.model.setData(self.model.index(row, 2), self.ui.teDescr.toPlainText())
                if self.ui.sbYear.value()>0:
                    self.model.setData(self.model.index(row, 3), self.ui.sbYear.value())
                if self.ui.sbMonth.value()>0:
                    self.model.setData(self.model.index(row, 4), self.ui.sbMonth.value())
                if self.ui.sbDay.value()>0:
                    self.model.setData(self.model.index(row, 5), self.ui.sbDay.value())
                if self.ui.sbLat.value()>0:
                    self.model.setData(self.model.index(row, 6), self.ui.sbLat.value())
                if self.ui.sbLon.value()>0:
                    self.model.setData(self.model.index(row, 7), self.ui.sbLon.value())
                self.model.setData(self.model.index(row, 8), copied_file)
        return super().accept()