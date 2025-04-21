import os
from PyQt5.QtGui import QPixmap

img_path = r"C:\Proj\raas_project\raas_func\static\photos\front_light.jpg"

print("Exists:", os.path.exists(img_path))
pixmap = QPixmap(img_path)

if pixmap.isNull():
    print("❌ QPixmap не смог загрузить файл")
else:
    print("✅ QPixmap успешно загрузил картинку")
