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
        self.tp = QLineEdit('Москва ул Ленина', self)
        self.tp.move(20, 500)
        self.tp.resize(150, 25)
        self.btn = QPushButton('Искать', self)
        self.btn.move(200, 500)
        self.btn.resize(150, 50)
        self.btn.clicked.connect(self.getImage)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(600, 450)
        self.getImage()
        self.setWindowTitle('Maps API')

    def getImage(self):
        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"

        geocoder_params = {
            "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
            "geocode": self.tp.text(),
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

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={tlg},{tlt}&spn={spn}&pt={tlg},{tlt},pm2dgm2&l=map"
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

    def closeEvent(self, event):
        os.remove(self.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    ex.show()
    sys.exit(app.exec())