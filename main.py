#!/usr/bin/python3

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtGui import QImage
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QFile
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkRequest
from PyQt5.QtNetwork import QNetworkReply
from PyQt5.QtNetwork import QNetworkAccessManager
from PyQt5.QtCore import QTemporaryFile
from interface import Ui_MainWindow


class MainWin2(QMainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.button_upload.clicked.connect(self.on_button_upload_clicked_1)
        self.ui.button_browse.clicked.connect(self.on_button_browse_clicked_1)
        self.ui.button_del.clicked.connect(self.on_button_del_clicked_1)

        self.ui.radio_width.toggled.connect(self.on_radio_width_toggled)
        self.ui.radio_height.toggled.connect(self.on_radio_height_toggled)
        self.ui.radio_both.toggled.connect(self.on_radio_both_toggled)
        self.ui.radio_noscale.toggled.connect(self.on_radio_dontscale_toggled)

        self.show()
        self.nam = 0
        self.rep = 0
        self.req = 0
        self.f = 0
        self.filecount = 0

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.accept()

    def dropEvent(self, e):
        for item in e.mimeData().urls():
            self.ui.listWidget.addItem(item.toLocalFile())
        if self.ui.check_autostart.isChecked():
            self.on_button_upload_clicked_1()

    def on_button_upload_clicked_1(self):
        self.filecount = self.ui.listWidget.count()
        self.processfile(0)

    def on_button_del_clicked_1(self):
        list = self.ui.listWidget.selectedItems()
        for item in list:
            self.ui.listWidget.takeItem(self.ui.listWidget.row(item))

    def on_button_browse_clicked_1(self):
        list = QFileDialog.getOpenFileNames()
        for item in list[0]:
            self.ui.listWidget.addItem(QListWidgetItem(item))

    def on_radio_width_toggled(self):
        self.ui.spin_width.setEnabled(True)
        self.ui.spin_height.setEnabled(False)

    def on_radio_height_toggled(self):
        self.ui.spin_width.setEnabled(False)
        self.ui.spin_height.setEnabled(True)

    def on_radio_both_toggled(self):
        self.ui.spin_width.setEnabled(True)
        self.ui.spin_height.setEnabled(True)

    def on_radio_dontscale_toggled(self):
        self.ui.spin_width.setEnabled(False)
        self.ui.spin_height.setEnabled(False)

    def processfile(self, i):
        print("processfile_start " + str(self.filecount - self.ui.listWidget.count()))
        if self.ui.listWidget.count() == 0:
            return

        file = str(self.ui.listWidget.item(i).text())
        image = QImage(file)

        if self.ui.radio_noscale.isChecked():
            pass
        elif self.ui.radio_both.isChecked():
            image = image.scaled(self.ui.spin_width.value(), self.ui.spin_height.value(), Qt.IgnoreAspectRatio,
                                 Qt.SmoothTransformation)
        elif self.ui.radio_width.isChecked():
            w = self.ui.spin_width.value()
            image = image.scaledToWidth(w, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        elif self.ui.radio_height.isChecked():
            h = self.ui.spin_height.value()
            image = image.scaledToHeight(h, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.f = QTemporaryFile()
        self.f.open()
        image.save(self.f, 'JPG')
        self.f.seek(0)

        url = QUrl("ftp://" + self.ui.line_host.text() + "/" + self.ui.line_dir.text() + "/"
                   + self.ui.line_prefix.text() + str(self.ui.spin_start_num.value()) + self.ui.line_suffix.text())
        url.setUserName(self.ui.line_user.text())
        url.setPassword(self.ui.line_pass.text())
        url.setPort(self.ui.spin_port.value())

        try:
            self.ui.listWidget.takeItem(0)
            self.ui.spin_start_num.setValue(self.ui.spin_start_num.value() + 1)
            self.nam = QNetworkAccessManager()
            self.rep = self.nam.put(QNetworkRequest(url), self.f)
            self.rep.finished.connect(self.isfinished)
            self.rep.error.connect(self.getError)
            if self.filecount != 0:
                self.progress = int((self.filecount - self.ui.listWidget.count()) / (0.01 * self.filecount))
            self.ui.progressBar.setValue(self.progress)
        except Exception as e:
            print("Exception " + str(e))
        print("end")

    def getError(self):
        print("error")

    def isfinished(self):
        print("finished")
        self.f.close()
        self.processfile(0)


app = QApplication(sys.argv)
win = MainWin2()
sys.exit(app.exec_())
