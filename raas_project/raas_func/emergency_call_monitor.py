import carla
import time
import threading
from PyQt5.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt

class EmergencyCallMonitor(QWidget):
    def __init__(self, world, vehicle, multimedia_panel):
        super().__init__()
        self.world = world
        self.vehicle = vehicle
        self.panel = multimedia_panel
        self.monitor_active = True
        self.accident_detected = False

        # Настройки порогов
        self.speed_drop_threshold = 30.0  # резкое падение скорости (км/ч)
        self.angle_change_threshold = 60.0  # резкое изменение курса (градусы)

        self.last_speed = 0.0
        self.last_yaw = vehicle.get_transform().rotation.yaw

        # Таймер проверки состояния машины
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.monitor_vehicle)
        self.check_timer.start(200)  # каждые 0.2 секунды

        # Окно аварийного вызова
        self.init_emergency_window()

    def init_emergency_window(self):
        self.emergency_window = QWidget(self.panel)
        self.emergency_window.setGeometry(360, 160, 700, 400)
        self.emergency_window.setStyleSheet("background-color: rgba(0, 0, 0, 200); border: 2px solid red; border-radius: 20px;")

        vbox = QVBoxLayout(self.emergency_window)

        self.emergency_label = QLabel("Обнаружено ДТП!\nВызвать экстренные службы (112)?")
        self.emergency_label.setStyleSheet("color: white; font-size: 26px; font-weight: bold;")
        self.emergency_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.emergency_label)

        self.timer_label = QLabel("Автоматический вызов через: 60 сек")
        self.timer_label.setStyleSheet("color: white; font-size: 20px; margin-top: 10px;")
        self.timer_label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(self.timer_label)

        hbox = QHBoxLayout()
        self.call_button = QPushButton("Вызвать")
        self.cancel_button = QPushButton("Отклонить")
        self.call_button.setStyleSheet("background-color: green; color: white; font-size: 20px; padding: 10px;")
        self.cancel_button.setStyleSheet("background-color: red; color: white; font-size: 20px; padding: 10px;")
        hbox.addWidget(self.call_button)
        hbox.addWidget(self.cancel_button)
        vbox.addLayout(hbox)

        self.call_button.clicked.connect(self.start_emergency_call)
        self.cancel_button.clicked.connect(self.cancel_emergency)

        self.emergency_window.hide()

        # Таймер автозвонка
        self.auto_call_timer = QTimer()
        self.auto_call_timer.timeout.connect(self.update_auto_call_timer)
        self.auto_call_seconds_left = 60

        # Таймер отображения времени вызова
        self.call_duration_timer = QTimer()
        self.call_duration_timer.timeout.connect(self.update_call_timer)
        self.call_seconds = 0

    def monitor_vehicle(self):
        if not self.monitor_active:
            return

        velocity = self.vehicle.get_velocity()
        speed = (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5 * 3.6  # в км/ч
        yaw = self.vehicle.get_transform().rotation.yaw

        speed_drop = self.last_speed - speed
        yaw_change = abs(self.last_yaw - yaw)

        if (speed_drop > self.speed_drop_threshold or yaw_change > self.angle_change_threshold) and self.last_speed > 30:
            if not self.accident_detected:
                print("[!] Accident detected. Showing emergency call window.")
                self.show_emergency_window()


        self.last_speed = speed
        self.last_yaw = yaw

    def show_emergency_window(self):
        self.accident_detected = True
        self.auto_call_seconds_left = 60
        self.timer_label.setText(f"Автоматический вызов через: {self.auto_call_seconds_left} сек")
        self.emergency_window.show()
        self.auto_call_timer.start(1000)  # каждую секунду обновляем обратный отсчет

    def update_auto_call_timer(self):
        self.auto_call_seconds_left -= 1
        if self.auto_call_seconds_left > 0:
            self.timer_label.setText(f"Автоматический вызов через: {self.auto_call_seconds_left} сек")
        else:
            self.start_emergency_call()

    def start_emergency_call(self):
        print("[*] Emergency call initiated to 112.")
        self.auto_call_timer.stop()
        self.emergency_label.setText("Вызов 112...\nВремя: 0 сек")
        self.timer_label.hide()
        self.call_seconds = 0
        self.call_duration_timer.start(1000)
        self.call_button.hide()
        self.cancel_button.setText("Сбросить")

    def update_call_timer(self):
        self.call_seconds += 1
        self.emergency_label.setText(f"Вызов 112...\nВремя: {self.call_seconds} сек")

    def cancel_emergency(self):
        print("[*] Emergency call cancelled or ended.")
        self.auto_call_timer.stop()
        self.call_duration_timer.stop()
        self.emergency_window.hide()
        self.accident_detected = False
        self.emergency_label.setText("Обнаружено ДТП!\nВызвать экстренные службы (112)?")
        self.timer_label.setText("Автоматический вызов через: 60 сек")
        self.timer_label.show()
        self.call_button.show()
        self.cancel_button.setText("Отклонить")

    def stop(self):
        self.monitor_active = False
        self.check_timer.stop()
        self.call_duration_timer.stop()
        self.auto_call_timer.stop()
        self.emergency_window.hide()
