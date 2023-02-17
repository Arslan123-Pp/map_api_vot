import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QPushButton, QInputDialog
from PyQt5.QtCore import Qt


SCREEN_SIZE = [700, 640]


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, *SCREEN_SIZE)
        self.ll_x = 37.530887
        self.ll_y = 55.703118
        self.ll = f'{self.ll_x},{self.ll_y}'
        self.btn = QPushButton('Искать', self)
        self.btn.move(100, 500)
        self.btn.resize(200, 50)
        self.btn.clicked.connect(self.run)

        self.btnpi = QPushButton('Выкл П.И', self)
        self.btnpi.move(550, 500)
        self.btnpi.resize(150, 50)
        self.btnpi.clicked.connect(self.pi)
        self.pi = True
        self.pi_txt = ''

        self.btnsh = QPushButton('Схема', self)
        self.btnsh.move(30, 550)
        self.btnsh.resize(150, 50)
        self.btnsh.clicked.connect(self.maap)

        self.btnr = QPushButton('Сброс результата', self)
        self.btnr.move(330, 500)
        self.btnr.resize(200, 50)
        self.btnr.clicked.connect(self.erase)

        self.btnsh = QPushButton('Схема', self)
        self.btnsh.move(30, 550)
        self.btnsh.resize(150, 50)
        self.btnsh.clicked.connect(self.maap)

        self.btnsp = QPushButton('Спутник', self)
        self.btnsp.move(230, 550)
        self.btnsp.resize(150, 50)
        self.btnsp.clicked.connect(self.sputnik)

        self.btngb = QPushButton('Гибрид', self)
        self.btngb.move(420, 550)
        self.btngb.resize(150, 50)
        self.btngb.clicked.connect(self.gibrid)
        self.pts = []
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.p = 0.01
        self.spn = None
        self.zoom = 0.1
        self.s = 0.001
        self.v = 'map'
        self.f = True
        self.fl = True
        self.address = QLabel(self)
        self.address.move(10, 600)
        self.address2 = QLabel(self)
        self.address2.move(10, 620)
        self.getImage()
        self.setWindowTitle('Maps API')

    def pi(self):
        self.pi = not self.pi
        if self.pi:
            self.btnpi.setText('Выкл П.И')
        else:
            self.btnpi.setText('Вкл П.И')
        self.getImage()

    def run(self):
        ll, ok_pressed = QInputDialog.getText(self, "Координаты", "Введите координаты")
        if ok_pressed:
            self.ll = ll
            self.f = True
            self.fl = True
            self.getImage()

    def sputnik(self):
        self.v = 'sat'
        self.getImage()

    def gibrid(self):
        self.v = 'sat,skl'
        self.getImage()

    def maap(self):
        self.v = 'map'
        self.getImage()

    def erase(self):
        if self.fl and self.pts:
            self.pts = self.pts[:-1]
            self.fl = False
            self.f = False
            self.address.setText('')
            self.getImage()

    def getImage(self):
        self.spn = f'{self.p},{self.p}'
        self.s = round(self.p, 3)
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.ll,
            "format": "json"}

        response = requests.get(geocoder_api_server, params=geocoder_params)

        if not response:
            pass

        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        spn = self.get_spn(json_response)

        toponym_coodrinates = toponym["Point"]["pos"]
        tlg, tlt = toponym_coodrinates.split(" ")
        if self.f is True:
            s = toponym['metaDataProperty']['GeocoderMetaData']['Address']
            self.address.setText(f"{s['formatted']}")
            self.address.adjustSize()
            try:
                self.pi_txt = s['postal_code']
            except Exception:
                self.pi_txt = 'None'
            if f'{tlg},{tlt},pm2dgm2' not in self.pts:
                self.pts.append(f'{tlg},{tlt},pm2dgm2')
            map_request = \
                f"http://static-maps.yandex.ru/1.x/?ll={tlg},{tlt}&spn={spn}&pt={'~'.join(self.pts)}&l={self.v}"
            self.spn = spn
            self.ll = f'{tlg},{tlt}'
            self.p = float(spn.split(',')[0])
        else:
            map_request = \
                f"http://static-maps.yandex.ru/1.x/?ll={self.ll}&spn={self.spn}&pt={'~'.join(self.pts)}&l={self.v}"
        response = requests.get(map_request)
        if self.pi and self.address.text():
            self.address2.setText(f"Почтовый индекс: {self.pi_txt}")
            self.address2.adjustSize()
        else:
            self.address2.setText('')
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

    def get_spn(self, json_response):
        try:
            crds = \
                json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
            lc = crds['boundedBy']['Envelope']['lowerCorner'].split()
            uc = crds['boundedBy']['Envelope']['upperCorner'].split()
            x = str(abs(float(uc[0]) - float(lc[0])))
            y = str(abs(float(uc[1]) - float(lc[1])))
            return f'{x},{y}'
        except Exception:
            return '1,1'

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            if self.p - self.zoom > 0:
                self.p -= self.zoom
                self.f = False
                self.getImage()
        if event.key() == Qt.Key_S:
            if self.p + self.zoom < 100:
                print(1)
                self.p += self.zoom
                self.f = False
                self.getImage()
        y, x = map(float, self.ll.split(','))
        if event.key() == Qt.Key_Right:
            if y + self.s < 100:
                self.ll = f'{y + self.s},{x}'
                self.f = False
                self.getImage()
        if event.key() == Qt.Key_Left:
            if y - self.s > 0:
                self.ll = f'{y - self.s},{x}'
                self.f = False
                self.getImage()
        if event.key() == Qt.Key_Down:
            if x - self.s > 0:
                self.ll = f'{y},{x - self.s}'
                self.f = False
                self.getImage()
        if event.key() == Qt.Key_Up:
            if x + self.s < 100:
                self.ll = f'{y},{x + self.s}'
                self.f = False
                self.getImage()

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())