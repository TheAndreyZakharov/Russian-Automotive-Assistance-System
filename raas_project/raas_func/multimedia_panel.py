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
from PyQt5.QtGui import QImage, QPixmap, QMovie, QFont
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
        self.top_time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.top_time_label.setGeometry(880, 0, 390, 40)
        self.update_top_clock()
        self.top_bar.hide()

    def update_top_clock(self):
        now = datetime.now()
        self.top_time_label.setText(now.strftime("%d.%m.%Y   %H:%M:%S"))

    def init_bottom_bar(self):
        self.bottom_bar = QFrame(self)
        self.bottom_bar.setGeometry(100, 640, 1180, 80)
        self.bottom_bar.setStyleSheet("background-color: rgba(0, 0, 0, 180);")

        music_label = QLabel("Music - Sample", self.bottom_bar)
        music_label.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        music_label.setGeometry(300, 5, 600, 30)
        music_label.setAlignment(Qt.AlignCenter)

        self.music_slider = QSlider(Qt.Horizontal, self.bottom_bar)
        self.music_slider.setGeometry(110, 45, 960, 10)
        self.music_slider.setValue(30)

        prev_btn = QPushButton("⏮", self.bottom_bar)
        prev_btn.setGeometry(1100, 30, 40, 30)
        next_btn = QPushButton("⏭", self.bottom_bar)
        next_btn.setGeometry(1140, 30, 40, 30)
        pause_btn = QPushButton("⏯", self.bottom_bar)
        pause_btn.setGeometry(1060, 30, 40, 30)

        for btn in [prev_btn, next_btn, pause_btn]:
            btn.setStyleSheet("color: white; font-size: 20px; background: none; border: none;")

        self.bottom_bar.hide()

    def init_sidebar(self):
        self.sidebar = QFrame(self)
        self.sidebar.setGeometry(0, 0, 100, 720)
        self.sidebar.setStyleSheet("background-color: rgba(0, 0, 0, 150);")

        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(5, 20, 5, 20)
        layout.setSpacing(15)

        buttons = [
            ("Заставка", self.show_welcome_screen),
            ("Домой", lambda: self.stack.setCurrentWidget(self.main_screen)),
            ("Настройки", lambda: None),
            ("Телефон", lambda: None),
            ("SMS", lambda: None)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setFixedSize(90, 50)
            btn.setStyleSheet("background-color: #222; color: white; font-size: 14px; border-radius: 10px;")
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.sidebar.raise_()
        self.sidebar.hide()

    def show_welcome_screen(self):
        self.welcome_screen.move(0, -720)
        self.stack.setCurrentWidget(self.welcome_screen)
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
        animation = QPropertyAnimation(self.welcome_screen, b"pos")
        animation.setDuration(700)
        animation.setStartValue(self.welcome_screen.pos())
        animation.setEndValue(QPoint(0, -720))
        animation.finished.connect(lambda: self.stack.setCurrentWidget(self.main_screen))
        animation.start()
        self._welcome_animation = animation

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
        layout = QVBoxLayout(self.main_screen)

        bg_label = QLabel()
        bg_pix = QPixmap(self.main_bg)
        bg_label.setPixmap(bg_pix.scaled(1280, 720, Qt.KeepAspectRatioByExpanding))
        bg_label.setScaledContents(True)
        layout.addWidget(bg_label)

        overlay = QWidget()
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 90);")
        vbox = QVBoxLayout(overlay)

        icon_row = QHBoxLayout()
        icon_row.addWidget(self.create_icon_button("Настройки", "#007ACC"))
        btn_functions = self.create_icon_button("Функции", "#4CAF50")
        btn_functions.clicked.connect(lambda: self.stack.setCurrentWidget(self.functions_screen))
        icon_row.addWidget(btn_functions)
        icon_row.addWidget(self.create_icon_button("Карта", "#FF9800"))
        vbox.addLayout(icon_row)

        layout.addWidget(overlay)
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