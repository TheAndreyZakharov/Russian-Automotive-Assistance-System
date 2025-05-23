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
from PyQt5.QtGui import QImage, QPixmap, QMovie, QPainter, QPainterPath
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QPoint, QThread, pyqtSignal
from camera_360_view import Camera360
from emergency_call_monitor import EmergencyCallMonitor
from adaptive_cruise_control import AdaptiveCruiseControl
from driver_fatigue_monitor import DriverFatigueMonitor
from smart_parking import SmartParkingModule
from emergency_braking import AutoBrakingSystem
from database_logger import DatabaseLogger
from camera_recorder import CameraBufferRecorder
from datetime import datetime

class ParkingThread(QThread):
    finished = pyqtSignal()

    def __init__(self, smart_parking_module):
        super().__init__()
        self.smart_parking_module = smart_parking_module
        self.stop_requested = False

    def run(self):
        self.smart_parking_module.execute_parking(thread=self)
        self.finished.emit()


class RAASPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RAAS Multimedia Panel")
        self.setFixedSize(1280, 720)

        self.db = DatabaseLogger()
        self.db.log_system_event("start")

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
        self.init_app_screens()
        self.init_sidebar()
        self.init_top_bar()
        self.init_bottom_bar()
        self.init_smart_parking_screen()
        self.init_cruise_control_screen()

        self.stack.currentChanged.connect(self.update_interface_visibility)
        self.init_view360_screen()
        self.stack.setCurrentWidget(self.loading_screen)

        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(10.0)
        self.world = self.client.get_world()
        vehicle_list = self.world.get_actors().filter('vehicle.*')
        if not vehicle_list:
            print("[-] Машина не найдена.")
            sys.exit()
        self.vehicle = sorted(vehicle_list, key=lambda v: v.id)[0]
        self.cruise_control = AdaptiveCruiseControl(self.vehicle, self.world)

        self.recorder = CameraBufferRecorder(
            camera_keys=["front", "back", "left", "right"], 
            buffer_seconds=60, 
            post_seconds=60
        )
        self.cam360 = Camera360(self.world, self.vehicle, recorder=self.recorder)
        self.cam360.start()
        self.modules = {
            "360 View": {"active": True, "object": self.cam360},
            "Mirror Alerts": {"active": True, "proc": None}
        }
        self.modules["Mirror Alerts"]["proc"] = subprocess.Popen(["python", "mirror_alert_toggle.py"])

        self.emergency_monitor = EmergencyCallMonitor(self.world, self.vehicle, self)

        self.cruise_control = AdaptiveCruiseControl(self.vehicle, self.world)

        self.fatigue_monitor = DriverFatigueMonitor(self.vehicle, self)
        self.fatigue_active = False

        self.smart_parking_module = SmartParkingModule(self.world, self.vehicle)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.auto_braking = AutoBrakingSystem(self.world, self.vehicle, self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(33)

        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_top_clock)
        self.clock_timer.start(1000)

        self.reverse_check_timer = QTimer()
        self.reverse_check_timer.timeout.connect(self.check_reverse_gear)
        self.reverse_check_timer.start(500)  # каждые полсекунды

        QTimer.singleShot(7000, lambda: self.stack.setCurrentWidget(self.welcome_screen))

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        QTimer.singleShot(1000, self.setFocus)

        def keyPressEvent(self, event):
            print(f"[DEBUG] Key pressed: {event.key()}")
            if event.key() == Qt.Key_P:
                self.stop_parking()

        def stop_parking(self):
            if hasattr(self, 'parking_thread') and self.parking_thread.isRunning():
                self.parking_thread.stop_requested = True
                print("[*] Парковка отменена пользователем через STOP или клавишу P")

        self.installEventFilter(self)
        def eventFilter(self, obj, event):
            if event.type() == event.KeyPress and event.key() == Qt.Key_P:
                print("[GLOBAL] Key P pressed")
                self.stop_parking()
                return True
            return super().eventFilter(obj, event)
        
        # === Восстановление состояний из БД
        states = self.db.get_last_states()

        if states.get("fatigue_monitor") == "ON":
            self.fatigue_btn.setChecked(True)
            self.toggle_fatigue_monitor(True)

        if states.get("emergency_monitor") == "OFF":
            self.emergency_btn.setChecked(False)
            self.toggle_emergency_monitor(False)

        if states.get("mirror_alerts") == "OFF":
            self.mirror_btn.setChecked(False)
            self.toggle_mirror_alerts(False)

        if states.get("lane_assist") == "ON":
            self.lane_btn.setChecked(True)
            self.toggle_lane_assist(True)

        if states.get("auto_braking") == "ON":
            self.brake_btn.setChecked(True)
            self.toggle_auto_braking(True)


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

        # === Управление камерами 360 ===
        if self.should_cam360_be_always_on():
            if not self.modules["360 View"]["active"]:
                self.modules["360 View"]["object"] = self.cam360
                self.modules["360 View"]["object"].start()
                self.modules["360 View"]["active"] = True
        else:
            # Если мы на экране обзора — включаем камеры
            if current == self.view360_screen:
                if not self.modules["360 View"]["active"]:
                    self.modules["360 View"]["object"] = self.cam360
                    self.modules["360 View"]["object"].start()
                    self.modules["360 View"]["active"] = True
            else:
                # Если не на экране и не требуется по условиям — выключаем
                if self.modules["360 View"]["active"]:
                    self.modules["360 View"]["object"].stop()
                    self.modules["360 View"]["object"] = None
                    self.modules["360 View"]["active"] = False


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
            ("Настройки", "settings.jpg", lambda: self.stack.setCurrentWidget(self.app_screens["settings"])),
            ("Телефон", "phone.jpg", lambda: self.stack.setCurrentWidget(self.app_screens["phone"])),
            ("SMS", "messeges.jpg", lambda: self.stack.setCurrentWidget(self.app_screens["messeges"]))
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
            ("Обзор 360", "cameras.jpg", lambda: self.stack.setCurrentWidget(self.view360_screen)),
            ("Smart парковка", "smart_parking.jpg", lambda: self.stack.setCurrentWidget(self.app_screens["smart_parking"])),
            ("Cruise control", "cruise_control.jpg", lambda: self.stack.setCurrentWidget(self.app_screens["cruise_control"])),
            ("Карты", "map.jpg", lambda: self.stack.setCurrentWidget(self.app_screens["map"])),
            ("Музыка", "music.jpg", lambda: self.stack.setCurrentWidget(self.app_screens["music"])),
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
        main_layout = QHBoxLayout(self.functions_screen)
        main_layout.setContentsMargins(150, 50, 150, 20)
        main_layout.setSpacing(100)  # отступ между двумя колонками

        left_column = QVBoxLayout()
        left_column.setSpacing(20)

        right_column = QVBoxLayout()
        right_column.setSpacing(20)

        # === АЛЕРТ подтверждения (по центру)
        self.confirm_box = QWidget(self)
        self.confirm_box.setStyleSheet("background-color: rgba(0,0,0,180); border: 2px solid white; border-radius: 10px;")
        self.confirm_box.setGeometry(470, 250, 480, 120)
        self.confirm_box.hide()
        self.confirm_box.raise_()

        vbox = QVBoxLayout(self.confirm_box)
        vbox.setContentsMargins(20, 20, 20, 20)

        self.confirm_label = QLabel("Вы уверены, что хотите отключить функцию?")
        self.confirm_label.setStyleSheet("color: white; font-size: 16px;")
        vbox.addWidget(self.confirm_label)

        btns = QHBoxLayout()
        yes_btn = QPushButton("Да")
        no_btn = QPushButton("Нет")
        yes_btn.setStyleSheet("background-color: #4CAF50; color: white; padding: 6px 16px; font-size: 14px;")
        no_btn.setStyleSheet("background-color: #777; color: white; padding: 6px 16px; font-size: 14px;")
        btns.addStretch()
        btns.addWidget(yes_btn)
        btns.addWidget(no_btn)
        btns.addStretch()
        vbox.addLayout(btns)

        yes_btn.clicked.connect(self.confirm_disable)
        no_btn.clicked.connect(self.cancel_disable)

        self.confirmation_timer = QTimer()
        self.confirmation_timer.setSingleShot(True)
        self.confirmation_timer.timeout.connect(self.cancel_disable)
        self.pending_toggle = None

        # --- Первая строка: слепые зоны
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        desc1 = QLabel("Уведомления слепых зон")
        desc1.setStyleSheet("color: white; font-size: 18px;")
        desc1.setFixedWidth(300)

        self.mirror_btn = QPushButton("ON")
        self.mirror_btn.setFixedSize(80, 40)
        self.mirror_btn.setCheckable(True)
        self.mirror_btn.setChecked(True)
        self.mirror_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
            QPushButton:!checked {
                background-color: #777;
            }
        """)
        self.mirror_btn.clicked.connect(lambda: self.handle_toggle(self.mirror_btn, self.toggle_mirror_alerts))

        row1.addWidget(desc1)
        row1.addWidget(self.mirror_btn)
        row1.addStretch()

        left_column.addLayout(row1)

        # --- Вторая строка: аварийный вызов 112
        row2 = QHBoxLayout()
        row2.setSpacing(20)

        desc2 = QLabel("Автоматический вызов 112")
        desc2.setStyleSheet("color: white; font-size: 18px;")
        desc2.setFixedWidth(300)

        self.emergency_btn = QPushButton("ON")
        self.emergency_btn.setFixedSize(80, 40)
        self.emergency_btn.setCheckable(True)
        self.emergency_btn.setChecked(True)
        self.emergency_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
            QPushButton:!checked {
                background-color: #777;
            }
        """)
        self.emergency_btn.clicked.connect(lambda: self.handle_toggle(self.emergency_btn, self.toggle_emergency_monitor))

        row2.addWidget(desc2)
        row2.addWidget(self.emergency_btn)
        row2.addStretch()

        left_column.addLayout(row2)


        # --- Третья строка: Lane Keeping Assist
        row3 = QHBoxLayout()
        row3.setSpacing(20)

        desc3 = QLabel("Удержание в полосе")
        desc3.setStyleSheet("color: white; font-size: 18px;")
        desc3.setFixedWidth(300)

        self.lane_btn = QPushButton("OFF")
        self.lane_btn.setFixedSize(80, 40)
        self.lane_btn.setCheckable(True)
        self.lane_btn.setChecked(False)
        self.lane_btn.setStyleSheet("""
            QPushButton {
                background-color: #777;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
        """)
        self.lane_btn.clicked.connect(lambda: self.handle_toggle(self.lane_btn, self.toggle_lane_assist))

        row3.addWidget(desc3)
        row3.addWidget(self.lane_btn)
        row3.addStretch()

        left_column.addLayout(row3)

        # --- Четвёртая строка: Контроль усталости
        row4 = QHBoxLayout()
        row4.setSpacing(20)

        desc4 = QLabel("Контроль усталости водителя")
        desc4.setStyleSheet("color: white; font-size: 18px;")
        desc4.setFixedWidth(300)

        self.fatigue_btn = QPushButton("OFF")
        self.fatigue_btn.setFixedSize(80, 40)
        self.fatigue_btn.setCheckable(True)
        self.fatigue_btn.setChecked(False)
        self.fatigue_btn.setStyleSheet("""
            QPushButton {
                background-color: #777;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
        """)
        self.fatigue_btn.clicked.connect(lambda: self.handle_toggle(self.fatigue_btn, self.toggle_fatigue_monitor))

        row4.addWidget(desc4)
        row4.addWidget(self.fatigue_btn)
        row4.addStretch()

        left_column.addLayout(row4)


        # --- Пятая строка: авто-торможение
        row5 = QHBoxLayout()
        row5.setSpacing(20)

        desc5 = QLabel("Автоматическое торможение")
        desc5.setStyleSheet("color: white; font-size: 18px;")
        desc5.setFixedWidth(300)

        self.brake_btn = QPushButton("OFF")
        self.brake_btn.setFixedSize(80, 40)
        self.brake_btn.setCheckable(True)
        self.brake_btn.setChecked(False)
        self.brake_btn.setStyleSheet("""
            QPushButton {
                background-color: #777;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:checked {
                background-color: #4CAF50;
            }
        """)
        self.brake_btn.clicked.connect(lambda: self.handle_toggle(self.brake_btn, self.toggle_auto_braking))

        row5.addWidget(desc5)
        row5.addWidget(self.brake_btn)
        row5.addStretch()
        left_column.addLayout(row5)

        main_layout.addLayout(left_column)
        main_layout.addLayout(right_column)
        self.stack.addWidget(self.functions_screen)


    def init_view360_screen(self):
        self.view360_screen = QWidget()

        main_layout = QHBoxLayout(self.view360_screen)
        main_layout.setContentsMargins(140, 0, 0, 0)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setAlignment(Qt.AlignBottom)
        content_layout.setContentsMargins(0, 0, 0, 100)
        content_layout.setSpacing(20)

        # Контейнер для двух частей
        display_container = QWidget()
        display_container.setFixedSize(1100, 540)
        display_layout = QHBoxLayout(display_container)
        display_layout.setContentsMargins(0, 0, 0, 0)
        display_layout.setSpacing(10)

        # === Левая часть: 360 камера
        left_display_container = QWidget(display_container)
        left_display_container.setFixedSize(540, 540)
        left_display_container.setStyleSheet("background-color: black; border: 2px solid gray;")
        left_layout = QVBoxLayout(left_display_container)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.display_left = QLabel()
        self.display_left.setFixedSize(540, 540)
        self.display_left.setStyleSheet("background-color: transparent;")
        self.display_left.setParent(left_display_container)
        left_layout.addWidget(self.display_left)

        # === Прозрачные кнопки-области
        self.cam_buttons = {}
        cam_zones = {
            "front": (145, 0, 275, 120),
            "back": (145, 420, 275, 120),
            "left": (10, 130, 120, 280),
            "right": (430, 130, 110, 280),
        }

        for cam, (x, y, w, h) in cam_zones.items():
            btn = QPushButton(left_display_container)
            btn.setGeometry(x, y, w, h)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0);
                    border: 2px solid rgba(255, 255, 255, 60);
                }
                QPushButton:hover {
                    border: 2px solid white;
                }
            """)
            btn.clicked.connect(lambda _, n=cam: self.set_selected_camera(n))
            btn.raise_()  # Поверх QLabel
            self.cam_buttons[cam] = btn

        # === Правая часть: одиночная камера
        self.display_right = QLabel()
        self.display_right.setFixedSize(540, 540)
        self.display_right.setStyleSheet("background-color: black; border: 2px solid gray;")

        display_layout.addWidget(left_display_container)
        display_layout.addWidget(self.display_right)
        content_layout.addWidget(display_container)

        main_layout.addWidget(content)
        self.stack.addWidget(self.view360_screen)

        self.selected_camera = "front"


    def set_selected_camera(self, camera_name):
        self.selected_camera = camera_name

    def check_reverse_gear(self):
        control = self.vehicle.get_control()

        if control.reverse:
            if self.stack.currentWidget() != self.view360_screen:
                self.set_selected_camera("back")
                self.stack.setCurrentWidget(self.view360_screen)
            self._was_in_reverse = True

            # Остановим все таймеры на случай повторного включения задней
            if hasattr(self, "_reverse_timer"):
                self._reverse_timer.stop()
            if hasattr(self, "_front_timer"):
                self._front_timer.stop()
            if hasattr(self, "_exit_timer"):
                self._exit_timer.stop()

        else:
            if getattr(self, "_was_in_reverse", False) and self.stack.currentWidget() == self.view360_screen:
                self._was_in_reverse = False

                # 2 секунды — оставляем заднюю
                self._reverse_timer = QTimer()
                self._reverse_timer.setSingleShot(True)
                self._reverse_timer.timeout.connect(self._switch_to_front_camera)
                self._reverse_timer.start(2000)

    def _switch_to_front_camera(self):
        self.set_selected_camera("front")

        self._front_timer = QTimer()
        self._front_timer.setSingleShot(True)
        self._front_timer.timeout.connect(self._exit_view360_after_front)
        self._front_timer.start(5000)

    def _exit_view360_after_front(self):
        self.stack.setCurrentWidget(self.main_screen)

    def toggle_emergency_monitor(self, enabled):
        self.db.log_function_state("emergency_monitor", "ON" if enabled else "OFF")
        if enabled:
            self.emergency_monitor.monitor_active = True
            print("[*] Emergency Call Monitor enabled.")
            self.emergency_btn.setText("ON")
            self.emergency_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
        else:
            self.emergency_monitor.monitor_active = False
            print("[*] Emergency Call Monitor disabled.")
            self.emergency_btn.setText("OFF")
            self.emergency_btn.setStyleSheet("""
                QPushButton {
                    background-color: #777;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)

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
        self.update_interface_visibility()
        return btn


    def toggle_360_view(self):
        mod = self.modules["360 View"]
        if not mod["active"]:
            mod["object"] = self.cam360
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

    def toggle_mirror_alerts(self, enabled):
        self.db.log_function_state("mirror_alerts", "ON" if enabled else "OFF")
        mod = self.modules["Mirror Alerts"]

        if enabled:
            if mod["proc"]:
                mod["proc"].terminate()
                mod["proc"].wait()
            mod["proc"] = subprocess.Popen(["python", "mirror_alert_toggle.py"])
            mod["active"] = True
            self.mirror_btn.setText("ON")
            self.mirror_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
        else:
            if mod["proc"]:
                mod["proc"].terminate()
                mod["proc"].wait()
            mod["proc"] = subprocess.Popen(["python", os.path.abspath(os.path.join("..", "main_func", "side_mirror_cameras.py"))])
            mod["active"] = False
            self.mirror_btn.setText("OFF")
            self.mirror_btn.setStyleSheet("""
                QPushButton {
                    background-color: #777;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)

    def handle_toggle(self, button, callback):
        if button.isChecked():
            button.setText("ON")
            button.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
            callback(True)
        else:
            button.setChecked(True)
            self.pending_toggle = (button, callback)
            self.confirm_label.setText("Вы уверены, что хотите отключить функцию?")
            self.confirm_box.show()
            self.confirmation_timer.start(20000)

    def confirm_disable(self):
        if self.pending_toggle:
            button, callback = self.pending_toggle
            button.setChecked(False)
            callback(False)
        self.confirm_box.hide()
        self.pending_toggle = None
        self.confirmation_timer.stop()

    def cancel_disable(self):
        self.confirm_box.hide()
        self.pending_toggle = None
        self.confirmation_timer.stop()

    def update_display(self):
        self.cruise_control.update()
        if self.modules["360 View"]["active"]:
            surface = self.modules["360 View"]["object"].get_surface()
            if surface:
                raw = pygame.image.tostring(surface, "RGB")
                w, h = surface.get_size()
                qimg = QImage(raw, w, h, QImage.Format_RGB888)
                if self.modules["360 View"]["active"]:
                    cam360 = self.modules["360 View"]["object"]
                    surface_360 = cam360.get_surface()
                    if surface_360:
                        raw_360 = pygame.image.tostring(surface_360, "RGB")
                        w, h = surface_360.get_size()
                        img_360 = QImage(raw_360, w, h, QImage.Format_RGB888)
                        self.display_left.setPixmap(QPixmap.fromImage(img_360))

                    selected = self.selected_camera
                    surface_cam = cam360.image_data.get(selected)
                    if surface_cam:
                        raw_sel = pygame.image.tostring(surface_cam, "RGB")
                        w, h = surface_cam.get_size()
                        img_sel = QImage(raw_sel, w, h, QImage.Format_RGB888)
                        pixmap_sel = QPixmap.fromImage(img_sel).scaled(540, 540, Qt.KeepAspectRatio)
                        self.display_right.setPixmap(pixmap_sel)

        if hasattr(self, "cruise_toggle_btn"):
            if self.cruise_control.enabled:
                self.cruise_toggle_btn.setText("Cruise ON")
            else:
                self.cruise_toggle_btn.setText("Cruise OFF")
            self.update_cruise_speed_label()

        if self.fatigue_active:
            control = self.vehicle.get_control()
            self.fatigue_monitor.update_driver_input(
                throttle=control.throttle,
                brake=control.brake,
                steer=control.steer,
                lane_keeping_enabled=self.lane_btn.isChecked(),
                cruise_enabled=self.cruise_control.enabled
            )
            lights = self.vehicle.get_light_state()
            left_signal = bool(lights & carla.VehicleLightState.LeftBlinker)
            right_signal = bool(lights & carla.VehicleLightState.RightBlinker)
            if abs(control.steer) > 0.3:
                self.fatigue_monitor.register_lane_departure(
                    left_signal_on=left_signal,
                    right_signal_on=right_signal
                )

        if self.stack.currentWidget() == self.app_screens["smart_parking"]:
            images = self.smart_parking_module.get_processed_images()
            for name, img in images.items():
                if name in self.parking_cam_labels:
                    h, w, ch = img.shape
                    bytes_per_line = ch * w
                    qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(qimg)
                    self.parking_cam_labels[name].setPixmap(pixmap)

        if self.stack.currentWidget() == self.app_screens["smart_parking"]:
            images = self.smart_parking_module.get_processed_images()
            for name, img in images.items():
                if name in self.parking_cam_labels:
                    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb.shape
                    qimg = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
                    self.parking_cam_labels[name].setPixmap(QPixmap.fromImage(qimg))

            if self.smart_parking_module.VALID_PARKING_POINT:
                self.park_button.setText("Выполнить парковку")
                self.park_button.setEnabled(True)
            else:
                self.park_button.setText("Поиск места...")
                self.park_button.setEnabled(False)


    def init_smart_parking_screen(self):
        self.smart_parking_screen = QWidget()
        self.smart_parking_screen.setStyleSheet("background-color: transparent;")

        self.parking_cam_labels = {}
        cam_w, cam_h = 320, 240

        # === Контейнер для размещения камер ===
        camera_zone = QWidget(self.smart_parking_screen)
        camera_zone.setGeometry(150, 50, 1100, 700)  # x, y, w, h

        def create_cam_label(name, x, y):
            label = QLabel(camera_zone)
            label.setGeometry(x, y, cam_w, cam_h)
            label.setStyleSheet("background-color: black; border: 2px solid white;")
            label.setAlignment(Qt.AlignCenter)
            label.setText(f"{name.upper()}")
            self.parking_cam_labels[name] = label

        create_cam_label("front", 380, 0)
        create_cam_label("back", 380, cam_h)
        create_cam_label("left", 60, cam_h/2)
        create_cam_label("right", 60 + (2 * cam_w), cam_h/2)

        self.park_button = QPushButton("Поиск места...", self.smart_parking_screen)
        self.park_button.setEnabled(False)
        self.park_button.setFixedSize(280, 60)

        screen_width = 1280
        btn_x = int((screen_width - 280) / 2) + 50
        btn_y = 720 - 170
        self.park_button.move(btn_x, btn_y)

        self.park_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #777;
                color: white;
                border-radius: 10px;
            }
            QPushButton:enabled {
                background-color: #4CAF50;
            }
        """)
        self.park_button.clicked.connect(self.start_parking_thread)

        self.stack.addWidget(self.smart_parking_screen)
        self.app_screens["smart_parking"] = self.smart_parking_screen

        self.stop_button = QPushButton("Стоп", self.smart_parking_screen)
        self.stop_button.setFixedSize(100, 60)
        self.stop_button.move(btn_x + 300, btn_y)
        self.stop_button.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                background-color: #b22222;
                color: white;
                border-radius: 10px;
            }
        """)
        self.stop_button.clicked.connect(self.stop_parking)
        self.stop_button.hide()

    def start_parking_thread(self):
        self.park_button.setText("Идет парковка...")
        self.park_button.setEnabled(False)
        self.stop_button.show()

        self.parking_thread = ParkingThread(self.smart_parking_module)
        self.parking_thread.finished.connect(self.on_parking_finished)
        self.parking_thread.start()

    def on_parking_finished(self):
        self.park_button.setText("Поиск места..." if not self.smart_parking_module.VALID_PARKING_POINT else "Выполнить парковку")
        self.park_button.setEnabled(True)

    def stop_parking(self):
        if hasattr(self, 'parking_thread') and self.parking_thread.isRunning():
            self.parking_thread.stop_requested = True  # кастомный флаг
            print("[*] Парковка отменена пользователем.")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_P:
            self.stop_parking()

    def toggle_lane_assist(self, enabled):
        self.db.log_function_state("lane_assist", "ON" if enabled else "OFF")
        # Завершаем custom_control.py, если его окно открыто
        try:
            subprocess.run(['taskkill', '/f', '/fi', 'WINDOWTITLE eq RAAS Control Panel'], shell=True)
        except Exception as e:
            print(f"[!] Ошибка при завершении custom_control.py: {e}")

        if enabled:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            lane_script_path = os.path.join(BASE_DIR, "lane_keeping_assist.py")
            self.lane_assist_proc = subprocess.Popen(["python", lane_script_path])
            print("[*] Lane Keeping Assist запущен.")
            self.lane_btn.setText("ON")
            self.lane_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
        else:
            if hasattr(self, 'lane_assist_proc') and self.lane_assist_proc:
                self.lane_assist_proc.terminate()
                self.lane_assist_proc.wait()
                print("[*] Lane Keeping Assist остановлен.")

            # Запускаем custom_control.py обратно
            try:
                custom_control_path = os.path.abspath(os.path.join("..", "main_func", "custom_control.py"))
                subprocess.Popen(["python", custom_control_path])
                print("[*] custom_control.py запущен обратно.")
            except Exception as e:
                print(f"[!] Не удалось запустить custom_control.py: {e}")

            self.lane_btn.setText("OFF")
            self.lane_btn.setStyleSheet("""
                QPushButton {
                    background-color: #777;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)

    def toggle_fatigue_monitor(self, enabled):
        self.fatigue_active = enabled
        self.db.log_function_state("fatigue_monitor", "ON" if enabled else "OFF")
        if enabled:
            print("[*] Контроль усталости включен.")
            self.fatigue_btn.setText("ON")
            self.fatigue_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
        else:
            print("[*] Контроль усталости выключен.")
            self.fatigue_btn.setText("OFF")
            self.fatigue_btn.setStyleSheet("""
                QPushButton {
                    background-color: #777;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)


    def show_fatigue_warning(self, message):
        if hasattr(self, "_fatigue_alert") and self._fatigue_alert.isVisible():
            return  # Если уже показано — не дублируем

        self._fatigue_alert = QWidget(self)
        self._fatigue_alert.setGeometry(460, 260, 500, 200)
        self._fatigue_alert.setStyleSheet("""
            background-color: rgba(255, 165, 0, 220);
            border: 3px solid white;
            border-radius: 12px;
        """)

        layout = QVBoxLayout(self._fatigue_alert)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("Внимание, усталость")
        title.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        msg_label = QLabel(message)
        msg_label.setStyleSheet("color: white; font-size: 16px;")
        msg_label.setWordWrap(True)
        msg_label.setAlignment(Qt.AlignCenter)

        ok_btn = QPushButton("Хорошо")
        ok_btn.setFixedSize(180, 40)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: black;
                font-size: 16px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #eee;
            }
        """)
        ok_btn.clicked.connect(lambda: self._fatigue_alert.hide())

        layout.addWidget(title)
        layout.addWidget(msg_label)
        layout.addWidget(ok_btn, alignment=Qt.AlignCenter)

        self._fatigue_alert.show()


    def toggle_auto_braking(self, enabled):
        self.db.log_function_state("auto_braking", "ON" if enabled else "OFF")
        if enabled:
            self.auto_braking.start()
            print("[*] Auto braking system enabled.")
            self.brake_btn.setText("ON")
            self.brake_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
        else:
            self.auto_braking.stop()
            print("[*] Auto braking system disabled.")
            self.brake_btn.setText("OFF")
            self.brake_btn.setStyleSheet("""
                QPushButton {
                    background-color: #777;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
        self.update_interface_visibility()


    def init_cruise_control_screen(self):
        self.cruise_control_screen = QWidget()
        layout = QVBoxLayout(self.cruise_control_screen)
        layout.setContentsMargins(150, 50, 20, 20)

        title = QLabel("Адаптивный Круиз-Контроль")
        title.setStyleSheet("color: white; font-size: 24px;")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Отображение текущей скорости круиза
        self.speed_label = QLabel("Скорость удержания: 0 км/ч")
        self.speed_label.setStyleSheet("color: white; font-size: 20px;")
        layout.addWidget(self.speed_label, alignment=Qt.AlignCenter)

        self.cruise_toggle_btn = QPushButton("Cruise OFF")
        self.cruise_toggle_btn.setFixedSize(200, 60)
        self.cruise_toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: #777;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #888;
            }
        """)
        self.cruise_toggle_btn.clicked.connect(self.toggle_cruise_control)
        layout.addWidget(self.cruise_toggle_btn, alignment=Qt.AlignCenter)

        # Кнопки регулировки скорости
        row = QHBoxLayout()

        self.decrease_btn = QPushButton("-5 км/ч")
        self.decrease_btn.setFixedSize(120, 60)
        self.decrease_btn.setStyleSheet("""
            QPushButton {
                background-color: #777;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #888;
            }
        """)
        self.decrease_btn.clicked.connect(self.decrease_cruise_speed)

        self.increase_btn = QPushButton("+5 км/ч")
        self.increase_btn.setFixedSize(120, 60)
        self.increase_btn.setStyleSheet("""
            QPushButton {
                background-color: #777;
                color: white;
                font-size: 16px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #888;
            }
        """)
        self.increase_btn.clicked.connect(self.increase_cruise_speed)

        row.addWidget(self.decrease_btn)
        row.addWidget(self.increase_btn)
        layout.addLayout(row)

        layout.addLayout(row)
        layout.addStretch()

        self.stack.addWidget(self.cruise_control_screen)
        self.app_screens["cruise_control"] = self.cruise_control_screen

    def toggle_cruise_control(self):
        if not self.cruise_control.enabled:
            current_speed = self.cruise_control.get_speed(self.vehicle) * 3.6
            self.cruise_control.set_target_speed(current_speed)
            self.cruise_control.enable()
            self.cruise_toggle_btn.setText("Cruise ON")
        else:
            self.cruise_control.disable()
            self.cruise_toggle_btn.setText("Cruise OFF")
        self.update_cruise_speed_label()

        if self.cruise_control.enabled:
            self.cruise_toggle_btn.setText("Cruise ON")
            self.cruise_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)
        else:
            self.cruise_toggle_btn.setText("Cruise OFF")
            self.cruise_toggle_btn.setStyleSheet("""
                QPushButton {
                    background-color: #777;
                    color: white;
                    font-size: 16px;
                    border-radius: 8px;
                }
            """)

    def increase_cruise_speed(self):
        self.cruise_control.increase_speed()
        self.update_cruise_speed_label()

    def decrease_cruise_speed(self):
        self.cruise_control.decrease_speed()
        self.update_cruise_speed_label()

    def update_cruise_speed_label(self):
        if self.cruise_control.enabled:
            kmh = int(self.cruise_control.target_speed * 3.6)
            self.speed_label.setText(f"Скорость удержания: {kmh} км/ч")
        else:
            self.speed_label.setText("Скорость удержания: 0 км/ч")

    def should_cam360_be_always_on(self):
        return self.emergency_btn.isChecked() or self.brake_btn.isChecked()

    def closeEvent(self, event):
        event.ignore()
        for name, mod in self.modules.items():
            if name == "360 View" and mod["active"]:
                mod["object"].stop()
            if name == "Mirror Alerts" and mod["proc"]:
                mod["proc"].terminate()
                mod["proc"].wait()
        self.emergency_monitor.stop()
        self.stack.setCurrentWidget(self.exit_screen)
        self.exit_movie_label.movie().start()
        self.db.log_system_event("stop")
        QTimer.singleShot(5000, QApplication.instance().quit)

    def init_app_screens(self):
        self.app_screens = {}

        app_configs = {
            "map": {"img": "map_app.jpg", "x": 150, "y": 20, "w": 1050, "h": 580},
            "music": {"img": "music_app.jpg", "x": 150, "y": 20, "w": 1050, "h": 580},
            "settings": {"img": "settings_app.jpg", "x": 150, "y": 20, "w": 1050, "h": 580},
            "phone": {"img": "phone_app.jpg", "x": 150, "y": 20, "w": 1050, "h": 580},
            "messeges": {"img": "messeges_app.jpg", "x": 150, "y": 20, "w": 1050, "h": 580},
        }

        for name, config in app_configs.items():
            screen = QWidget()
            screen.setStyleSheet("background-color: black;")

            label = QLabel(screen)
            label.setGeometry(config["x"], config["y"], config["w"], config["h"])
            label.setPixmap(
                QPixmap(os.path.join(self.static_dir, config["img"]))
                .scaled(config["w"], config["h"], Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
            )

            self.stack.addWidget(screen)
            self.app_screens[name] = screen


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RAASPanel()
    window.show()
    sys.exit(app.exec_())