import sys
import os
import subprocess
import carla
import pygame
import cv2
import numpy as np
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame, QSlider
)
from PyQt5.QtGui import QImage, QPixmap, QMovie, QFont, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint
from camera_360_view import Camera360
from datetime import datetime


class RAASPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAAS Multimedia Panel")
        self.setFixedSize(1280, 720)

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PARENT_DIR = os.path.dirname(BASE_DIR)
        self.static_dir = os.path.join(PARENT_DIR, "static", "photos")
        self.start_gif = os.path.join(self.static_dir, "start_video.gif")
        self.exit_gif = os.path.join(self.static_dir, "exit_video.gif")
        self.main_bg = os.path.join(self.static_dir, "gradient_background.jpg")
        self.car_bg = os.path.join(self.static_dir, "car_background.jpg")

        self.stack = QStackedWidget(self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.stack)

        self.bg_underlay = QLabel(self)
        self.bg_underlay.setPixmap(QPixmap(self.main_bg).scaled(1280, 720, Qt.KeepAspectRatioByExpanding))
        self.bg_underlay.setGeometry(0, 0, 1280, 720)
        self.bg_underlay.lower()

        self.init_loading_screen()
        self.init_welcome_screen()
        self.init_main_screen()
        self.init_functions_screen()
        self.init_exit_screen()
        self.init_sidebar()
        self.init_top_bar()
        self.init_bottom_bar()

        self.stack.currentChanged.connect(self.update_interface_visibility)
        self.stack.setCurrentWidget(self.loading_screen)

        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        vehicle_list = self.world.get_actors().filter('vehicle.*')
        if not vehicle_list:
            print("[-] Машина не найдена.")
            sys.exit()
        self.vehicle = sorted(vehicle_list, key=lambda v: v.id)[0]

        self.modules = {
            "360 View": {"active": False, "object": None},
            "Mirror Alerts": {"active": True, "proc": None}
        }
        self.modules["Mirror Alerts"]["proc"] = subprocess.Popen(["python", "mirror_alert_toggle.py"])

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(33)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_top_clock)
        self.clock_timer.start(1000)

        QTimer.singleShot(7000, lambda: self.stack.setCurrentWidget(self.welcome_screen))

    def update_interface_visibility(self):
        current = self.stack.currentWidget()
        if current in [self.loading_screen, self.exit_screen, self.welcome_screen]:
            self.sidebar.hide()
            self.top_bar.hide()
            self.bottom_bar.hide()
        else:
            self.sidebar.show()
            self.top_bar.show()
            self.bottom_bar.show()

    def init_top_bar(self):
        self.top_bar = QFrame(self)
        self.top_bar.setGeometry(0, 0, 1280, 40)
        self.top_bar.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        self.top_time_label = QLabel(self.top_bar)
        self.top_time_label.setStyleSheet("color: white; font-size: 18px; padding-right: 10px;")
        self.top_time_label.setAlignment(Qt.AlignCenter)
        self.top_time_label.setGeometry(140, 0, 1140, 40)
        self.update_top_clock()
        self.top_bar.hide()

    def update_top_clock(self):
        now = datetime.now()
        self.top_time_label.setText(now.strftime("%d.%m.%Y   %H:%M:%S"))

    def init_bottom_bar(self):
        self.bottom_bar = QFrame(self)
        self.bottom_bar.setGeometry(140, 640, 1140, 80)
        self.bottom_bar.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        # Иконка слева (обложка музыки)
        music_icon = QLabel(self.bottom_bar)
        music_icon.setGeometry(10, 5, 70, 70)
        music_pix = QPixmap(os.path.join(self.static_dir, "music_record.jpg")).scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        music_icon.setPixmap(music_pix)

        # Название и исполнитель
        title_label = QLabel("Now Playing", self.bottom_bar)
        title_label.setGeometry(90, 10, 150, 25)
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")

        artist_label = QLabel("Music Sample", self.bottom_bar)
        artist_label.setGeometry(90, 35, 150, 20)
        artist_label.setStyleSheet("color: white; font-size: 14px;")

        # Ползунок перемотки
        self.music_slider = QSlider(Qt.Horizontal, self.bottom_bar)
        self.music_slider.setGeometry(250, 20, 450, 10)  # поднимаем выше (y: 35 → 20)
        self.music_slider.setValue(30)
        self.music_slider.setStyleSheet(""
            "QSlider::groove:horizontal { height: 6px; background: gray; border-radius: 3px; }"
            "QSlider::handle:horizontal { background: white; border-radius: 10px; width: 14px; margin: -5px 0; }"
        "")

        # Метки времени
        time_start_label = QLabel("0:55", self.bottom_bar)
        time_start_label.setGeometry(250, 35, 50, 20)
        time_start_label.setStyleSheet("color: white; font-size: 12px;")

        time_end_label = QLabel("3:03", self.bottom_bar)
        time_end_label.setGeometry(650, 35, 50, 20)
        time_end_label.setAlignment(Qt.AlignRight)
        time_end_label.setStyleSheet("color: white; font-size: 12px;")

        # Панель управления музыкой (в виде изображения)
        controls_label = QLabel(self.bottom_bar)
        controls_label.setGeometry(720, 10, 220, 60)
        controls_pix = QPixmap(os.path.join(self.static_dir, "music_bar.jpg")).scaled(220, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        controls_label.setPixmap(controls_pix)

        # Иконка громкости
        volume_label = QLabel(self.bottom_bar)
        volume_label.setGeometry(950, 10, 180, 60)
        volume_pix = QPixmap(os.path.join(self.static_dir, "volume.jpg")).scaled(180, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        volume_label.setPixmap(volume_pix)

        self.bottom_bar.hide()

    def init_sidebar(self):
        self.sidebar = QFrame(self)
        self.sidebar.setGeometry(0, 0, 140, 720)
        self.sidebar.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(10, 20, 5, 20)
        layout.setSpacing(20)

        buttons = [
            ("Заставка", "background.jpg", self.show_welcome_screen),
            ("Домой", "home.jpg", lambda: self.stack.setCurrentWidget(self.main_screen)),
            ("Настройки", "settings.jpg", lambda: None),
            ("Телефон", "phone.jpg", lambda: None),
            ("SMS", "messeges.jpg", lambda: None)
        ]

        for name, img_file, callback in buttons:
            btn = QPushButton()
            btn.setFixedSize(120, 120)
            btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")

            vbox = QVBoxLayout(btn)
            vbox.setContentsMargins(0, 0, 0, 0)
            vbox.setSpacing(4)
            vbox.setAlignment(Qt.AlignCenter)

            # Загружаем и делаем скругление
            img_path = os.path.join(self.static_dir, img_file)
            pix = QPixmap(img_path).scaled(100, 100, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            rounded = QPixmap(pix.size())
            rounded.fill(Qt.transparent)

            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addRoundedRect(0, 0, pix.width(), pix.height(), 20, 20)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pix)
            painter.end()

            icon_label = QLabel()
            icon_label.setPixmap(rounded)
            icon_label.setFixedSize(100, 100)
            icon_label.setAlignment(Qt.AlignCenter)

            text_label = QLabel(name)
            text_label.setAlignment(Qt.AlignCenter)
            text_label.setStyleSheet("color: white; font-size: 16px;")

            vbox.addWidget(icon_label)
            vbox.addWidget(text_label)

            btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.sidebar.raise_()
        self.sidebar.hide()


    def show_welcome_screen(self):
        # Перемещаем экран выше перед тем, как вставить в стек
        self.welcome_screen.move(0, -720)
        self.stack.setCurrentWidget(self.welcome_screen)

        # Анимация: экран опускается вниз
        anim = QPropertyAnimation(self.welcome_screen, b"pos")
        anim.setDuration(700)
        anim.setStartValue(QPoint(0, -720))
        anim.setEndValue(QPoint(0, 0))
        anim.start()
        self._welcome_animation = anim

    def init_loading_screen(self):
        self.loading_screen = QWidget()
        layout = QVBoxLayout(self.loading_screen)
        layout.setContentsMargins(0, 0, 0, 0)

        self.movie_label = QLabel()
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie_label.setFixedSize(1280, 720)

        movie = QMovie(self.start_gif)
        movie.setScaledSize(self.movie_label.size())
        self.movie_label.setMovie(movie)
        movie.start()

        layout.addWidget(self.movie_label)
        self.stack.addWidget(self.loading_screen)

    def init_welcome_screen(self):
        self.welcome_screen = QWidget(self)
        self.welcome_screen.setFixedSize(1280, 720)
        layout = QVBoxLayout(self.welcome_screen)
        layout.setContentsMargins(0, 0, 0, 0)

        self.welcome_bg = QLabel(self.welcome_screen)
        bg_pix = QPixmap(self.car_bg)
        self.welcome_bg.setPixmap(bg_pix.scaled(1280, 720, Qt.KeepAspectRatioByExpanding))
        self.welcome_bg.setGeometry(0, 0, 1280, 720)

        self.date_label = QLabel(self.welcome_screen)
        self.date_label.setStyleSheet("""
            color: white;
            font-size: 28px;
            background-color: rgba(0, 0, 0, 100);
        """)
        self.date_label.setAlignment(Qt.AlignCenter)
        self.date_label.setGeometry(440, 10, 400, 50)

        self.clock_label = QLabel(self.welcome_screen)
        self.clock_label.setStyleSheet("""
            color: white;
            font-size: 56px;
            font-weight: bold;
            background-color: rgba(0, 0, 0, 100);
        """)
        self.clock_label.setAlignment(Qt.AlignCenter)
        self.clock_label.setGeometry(440, 50, 400, 80)

        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_clock)
        self.time_timer.start(1000)
        self.update_clock()

        self.stack.addWidget(self.welcome_screen)

    def update_clock(self):
        now = datetime.now()
        self.date_label.setText(now.strftime("%d.%m.%Y"))
        self.clock_label.setText(now.strftime("%H:%M:%S"))

    def mousePressEvent(self, event):
        if self.stack.currentWidget() == self.welcome_screen:
            self._swipe_start = event.pos()

    def mouseReleaseEvent(self, event):
        if self.stack.currentWidget() == self.welcome_screen and hasattr(self, '_swipe_start'):
            delta = self._swipe_start.y() - event.pos().y()
            if delta > 100:
                self.animate_welcome_to_main()

    def animate_welcome_to_main(self):
        anim = QPropertyAnimation(self.welcome_screen, b"pos")
        anim.setDuration(700)
        anim.setStartValue(self.welcome_screen.pos())
        anim.setEndValue(QPoint(0, -720))
        anim.finished.connect(lambda: self.stack.setCurrentWidget(self.main_screen))
        anim.start()
        self._welcome_animation = anim

    def init_exit_screen(self):
        self.exit_screen = QWidget()
        layout = QVBoxLayout(self.exit_screen)
        layout.setContentsMargins(0, 0, 0, 0)

        self.exit_movie_label = QLabel()
        self.exit_movie_label.setAlignment(Qt.AlignCenter)
        self.exit_movie_label.setFixedSize(1280, 720)

        movie = QMovie(self.exit_gif)
        movie.setScaledSize(self.exit_movie_label.size())
        self.exit_movie_label.setMovie(movie)

        layout.addWidget(self.exit_movie_label)
        self.stack.addWidget(self.exit_screen)

    def init_main_screen(self):
        self.main_screen = QWidget()

        # Установка фоновой картинки
        bg_label = QLabel(self.main_screen)
        bg_label.setGeometry(0, 0, 1280, 720)
        bg_pix = QPixmap(self.main_bg)
        bg_label.setPixmap(bg_pix.scaled(1280, 720, Qt.KeepAspectRatioByExpanding))
        bg_label.setScaledContents(True)

        # Прозрачный слой с иконками — точно в центре
        icon_overlay = QWidget(self.main_screen)
        icon_overlay.setGeometry(140, 100, 1080, 520)  # Оставим место сверху/снизу
        icon_overlay.setStyleSheet("background-color: transparent;")

        grid_layout = QVBoxLayout(icon_overlay)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(50)
        grid_layout.setAlignment(Qt.AlignCenter)

        app_data = [
            ("Функции", "functions.jpg", lambda: self.stack.setCurrentWidget(self.functions_screen)),
            ("Обзор 360", "cameras.jpg", lambda: print("Обзор 360")),
            ("Карты", "map.jpg", lambda: print("Карты")),
            ("Климат Контроль", "climate.jpg", lambda: print("Климат")),
            ("Музыка", "music.jpg", lambda: print("Музыка")),
            ("Браузер", "browser.jpg", lambda: print("Браузер")),
        ]

        for i in range(0, len(app_data), 3):
            row = QHBoxLayout()
            row.setSpacing(60)
            row.setAlignment(Qt.AlignCenter)
            for name, icon_file, callback in app_data[i:i+3]:
                btn = QPushButton()
                btn.setFixedSize(200, 200)
                btn.setStyleSheet("QPushButton { background-color: transparent; border: none; }")

                vbox = QVBoxLayout(btn)
                vbox.setContentsMargins(0, 0, 0, 0)
                vbox.setSpacing(8)
                vbox.setAlignment(Qt.AlignCenter)

                icon = QLabel()
                pix = QPixmap(os.path.join(self.static_dir, icon_file)).scaled(140, 140, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

                # Создаём скруглённую маску
                rounded = QPixmap(pix.size())
                rounded.fill(Qt.transparent)

                painter = QPainter(rounded)
                painter.setRenderHint(QPainter.Antialiasing)
                path = QPainterPath()
                path.addRoundedRect(0, 0, pix.width(), pix.height(), 30, 30)
                painter.setClipPath(path)
                painter.drawPixmap(0, 0, pix)
                painter.end()

                icon.setPixmap(rounded)
                icon.setFixedSize(140, 140)
                icon.setAlignment(Qt.AlignCenter)

                label = QLabel(name)
                label.setStyleSheet("color: white; font-size: 16px;")
                label.setAlignment(Qt.AlignCenter)

                vbox.addWidget(icon)
                vbox.addWidget(label)
                btn.clicked.connect(callback)
                row.addWidget(btn)

            grid_layout.addLayout(row)

        self.stack.addWidget(self.main_screen)





    def init_functions_screen(self):
        self.functions_screen = QWidget()
        layout = QVBoxLayout(self.functions_screen)

        back_btn = QPushButton("\u2190 Назад")
        back_btn.setFixedSize(200, 40)
        back_btn.setStyleSheet("background-color: #555; color: white; font-size: 16px;")
        back_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.main_screen))

        self.view_btn = QPushButton("360 View [OFF]")
        self.mirror_btn = QPushButton("Mirror Alerts [ON]")
        for btn in (self.view_btn, self.mirror_btn):
            btn.setFixedSize(200, 40)
            btn.setStyleSheet("background-color: #444; color: white; font-size: 16px;")
        self.view_btn.clicked.connect(self.toggle_360_view)
        self.mirror_btn.clicked.connect(self.toggle_mirror_alerts)

        self.display = QLabel()
        self.display.setFixedSize(960, 540)
        self.display.setStyleSheet("background-color: black; border: 2px solid gray;")

        layout.addWidget(self.view_btn)
        layout.addWidget(self.mirror_btn)
        layout.addWidget(self.display, alignment=Qt.AlignCenter)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.stack.addWidget(self.functions_screen)

    def create_icon_button(self, text, color):
        btn = QPushButton(text)
        btn.setFixedSize(150, 150)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                font-weight: bold;
                border-radius: 15px;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #555;
            }}
        """)
        return btn

    def toggle_360_view(self):
        mod = self.modules["360 View"]
        if not mod["active"]:
            mod["object"] = Camera360(self.world, self.vehicle)
            mod["object"].start()
            mod["active"] = True
            text = "360 View [ON]"
        else:
            mod["object"].stop()
            mod["object"] = None
            mod["active"] = False
            text = "360 View [OFF]"
            self.display.clear()
        self.view_btn.setText(text)

    def toggle_mirror_alerts(self):
        mod = self.modules["Mirror Alerts"]
        if mod["proc"]:
            mod["proc"].terminate()
            mod["proc"].wait()
        if mod["active"]:
            mod["proc"] = subprocess.Popen(["python", os.path.abspath(os.path.join("..", "main_func", "side_mirror_cameras.py"))])
            mod["active"] = False
            self.mirror_btn.setText("Mirror Alerts [OFF]")
        else:
            mod["proc"] = subprocess.Popen(["python", "mirror_alert_toggle.py"])
            mod["active"] = True
            self.mirror_btn.setText("Mirror Alerts [ON]")

    def update_display(self):
        if self.modules["360 View"]["active"]:
            surface = self.modules["360 View"]["object"].get_surface()
            if surface:
                raw = pygame.image.tostring(surface, "RGB")
                w, h = surface.get_size()
                qimg = QImage(raw, w, h, QImage.Format_RGB888)
                self.display.setPixmap(QPixmap.fromImage(qimg))

    def closeEvent(self, event):
        event.ignore()
        for name, mod in self.modules.items():
            if name == "360 View" and mod["active"]:
                mod["object"].stop()
            if name == "Mirror Alerts" and mod["proc"]:
                mod["proc"].terminate()
                mod["proc"].wait()
        self.stack.setCurrentWidget(self.exit_screen)
        self.exit_movie_label.movie().start()
        QTimer.singleShot(5000, QApplication.instance().quit)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RAASPanel()
    window.show()
    sys.exit(app.exec_())