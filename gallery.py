from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
import sys
import mainwindow

app = QApplication(sys.argv)
QApplication.setApplicationDisplayName('YP Gallery')
ico = QIcon('./resources/map.png')
app.setWindowIcon(ico)
window = mainwindow.MainWindow()
window.show()
sys.exit(app.exec_())
