import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QPushButton, QInputDialog
from PyQt5.QtCore import Qt


SCREEN_SIZE = [600, 600]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.ll = '37.530887,55.703118'
        self.btn = QPushButton('Написать координаты', self)
        self.btn.move(200, 500)
        self.btn.resize(200, 50)
        self.btn.clicked.connect(self.run)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.p = 0.001
        self.spn = f'{self.p},{self.p}'
        self.zoom = 0.001
        self.getImage()
        self.setWindowTitle('Maps API')

    def run(self):
        ll, ok_pressed = QInputDialog.getText(self, "Введите координаты", "Введите координаты")
        if ok_pressed:
            self.ll = ll
            self.getImage()

    def getImage(self):
        self.spn = f'{self.p},{self.p}'
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.ll}&spn={self.spn}&l=map"
        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.map_file = "map.png"
        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.pixmap = QPixmap(self.map_file)
        self.image.setPixmap(self.pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Down:
            if self.p - self.zoom > 0:
                self.p -= self.zoom
                self.getImage()
        if event.key() == Qt.Key_Up:
            if self.p + self.zoom < 80:
                self.p += self.zoom
                self.getImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())