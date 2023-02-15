import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QPushButton


SCREEN_SIZE = [600, 600]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.ll = QLineEdit('37.530887,55.703118', self)
        self.spn = QLineEdit('0.002,0.002', self)
        self.ll.move(20, 500)
        self.spn.move(20, 550)
        self.ll.resize(150, 25)
        self.spn.resize(150, 25)
        self.btn = QPushButton('Отобразить', self)
        self.btn.move(200, 500)
        self.btn.resize(150, 50)
        self.btn.clicked.connect(self.getImage)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.getImage()
        self.setWindowTitle('Maps API')

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={self.ll.text()}&spn={self.spn.text()}&l=map"
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

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())