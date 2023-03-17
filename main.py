import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QPushButton, QInputDialog
from PyQt5.QtCore import Qt
import math


SCREEN_SIZE = [700, 640]


def lonlat_distance(a, b):
    degree_to_meters_factor = 111 * 1000
    a_lon, a_lat = a
    b_lon, b_lat = b
    radians_lattitude = math.radians((a_lat + b_lat) / 2)
    lat_lon_factor = math.cos(radians_lattitude)
    dx = abs(a_lon - b_lon) * degree_to_meters_factor * lat_lon_factor
    dy = abs(a_lat - b_lat) * degree_to_meters_factor
    distance = math.sqrt(dx * dx + dy * dy)
    return distance


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

        self.btnpi = QPushButton('Выкл адрес и П.И', self)
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
        self.p = 15
        self.spn = None
        self.zoom = 1
        self.s = 0.001
        self.v = 'map'
        self.f = True
        self.fl = True
        self.address = QLabel(self)
        self.address.move(10, 600)
        self.address2 = QLabel(self)
        self.address2.move(10, 620)
        self.adr_txt = ''
        self.llp = self.ll
        self.pts.append(f'{37.530822},{55.702952},pm2dgm2')
        self.getImage()
        self.setWindowTitle('Maps API')

    def pi(self):
        self.pi = not self.pi
        if self.pi:
            self.btnpi.setText('Выкл адрес и П.И')
        else:
            self.btnpi.setText('Вкл адрес и П.И')
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
        if self.pts:
            self.pts = self.pts[:-1]
            self.fl = False
            self.f = False
            self.address.setText('')
            self.getImage()

    def getImage(self):
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
        s = toponym['metaDataProperty']['GeocoderMetaData']['Address']
        if self.f is True:
            k, q, _ = self.pts[-1].split(',')
            geocoder_params1 = {
                "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
                "geocode": f'{k},{q}',
                "format": "json"}
            response1 = requests.get(geocoder_api_server, params=geocoder_params1)

            if not response1:
                pass

            json_response1 = response1.json()
            toponym1 = json_response1["response"]["GeoObjectCollection"][
                "featureMember"][0]["GeoObject"]
            s1 = toponym1['metaDataProperty']['GeocoderMetaData']['Address']
            self.address.setText(f"{s1['formatted']}")
            self.address.adjustSize()

            try:
                self.pi_txt = s1['postal_code']
            except Exception:
                self.pi_txt = 'None'
            map_request = \
                f"http://static-maps.yandex.ru/1.x/?ll={tlg},{tlt}&z={self.p}&pt={'~'.join(self.pts)}&l={self.v}"
            self.adr_txt = f"{s1['formatted']}"
            self.spn = spn
            self.ll = f'{tlg},{tlt}'
        else:
            map_request = \
                f"http://static-maps.yandex.ru/1.x/?ll={self.ll}&z={self.p}&pt={'~'.join(self.pts)}&l={self.v}"
        response = requests.get(map_request)
        if self.pi:
            self.address.setText(self.adr_txt)
            self.address2.setText(f"Почтовый индекс: {self.pi_txt}")
            self.address2.adjustSize()
        else:
            self.adr_txt = f"{s1['formatted']}"
            if 'postal_code' in s:
                self.pi_txt = s1['postal_code']
            else:
                self.pi_txt = 'None'
            self.address.setText('')
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
        if event.key() == Qt.Key_S:
            if self.p - self.zoom > 0:
                self.p -= self.zoom
                self.s *= 2.5
                self.f = False
                self.getImage()
        if event.key() == Qt.Key_W:
            if self.p + self.zoom < 24:
                self.s /= 2.5
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            if 600 > x > 0 and 450 > y > 0:
                px, py = map(float, self.ll.split(','))
                dy = 225 - y
                dx = x - 300
                coord_to_geo_x, coord_to_geo_y = 0.0000428, 0.0000428
                x1 = px + dx * coord_to_geo_x * 2 ** (15 - self.p)
                y1 = py + dy * coord_to_geo_y * math.cos(math.radians(py)) * 2 ** (15 - self.p)
                self.pts.append(f'{x1},{y1},pm2dgm2')
                self.llp = f'{x1},{y1}'
                self.f = True
                self.getImage()
        if event.button() == Qt.RightButton:
            x, y = event.x(), event.y()
            if 600 > x > 0 and 450 > y > 0:
                px, py = map(float, self.ll.split(','))
                dy = 225 - y
                dx = x - 300
                coord_to_geo_x, coord_to_geo_y = 0.0000428, 0.0000428
                x1 = px + dx * coord_to_geo_x * 2 ** (15 - self.p)
                y1 = py + dy * coord_to_geo_y * math.cos(math.radians(py)) * 2 ** (15 - self.p)
                search_api_server = "https://search-maps.yandex.ru/v1/"
                api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

                search_params = {
                    "apikey": api_key,
                    "text": 'организация',
                    "lang": "ru_RU",
                    'spn': '0.005,0.005',
                    'rspn': 1,
                    "ll": f'{x1},{y1}',
                    "type": "biz"
                }

                response = requests.get(search_api_server, params=search_params)
                if not response:
                    pass

                json_response = response.json()
                mn = 100000
                name = ''
                for organization in json_response["features"]:

                    org_name = organization["properties"]["CompanyMetaData"]["name"]
                    org_address = organization["properties"]["CompanyMetaData"]["address"]
                    point = organization["geometry"]["coordinates"]
                    dst = lonlat_distance(point, [x1, y1])
                    if dst < mn:
                        mn = dst
                        name = f'{org_address}, {org_name}'
                if mn != 100000:
                    self.address.setText(name)

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())