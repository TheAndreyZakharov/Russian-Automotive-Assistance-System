import carla
import time
import sys
from database_logger import DatabaseLogger

class DriverFatigueMonitor:
    def __init__(self, vehicle, window=None):

        self.db = DatabaseLogger()

        self.vehicle = vehicle
        self.window = window  # GUI окно для вывода предупреждений

        self.trip_start_time = time.time()
        self.last_driver_input_time = time.time()
        self.last_steer = 0.0

        self.rapid_steering_events = 0
        self.lane_departure_count = 0

        self.last_warning_time = 0
        self.warning_interval = 60  # минимальный интервал между предупреждениями

        # Пороги
        self.max_lane_departures = 100
        self.max_rapid_steering = 200

    def update_driver_input(self, throttle, brake, steer, lane_keeping_enabled, cruise_enabled):
        now = time.time()

        if throttle > 0 or brake > 0 or abs(steer) > 0.05:
            self.last_driver_input_time = now

        # Резкое изменение руля — только статистика
        steer_diff = abs(steer - self.last_steer)
        if steer_diff > 0.7:
            self.rapid_steering_events += 1
        self.last_steer = steer

        # Отсутствие действий при движении
        if self.vehicle_is_moving(throttle, brake):
            if now - self.last_driver_input_time > 60:
                self._warn("Отсутствие действий водителя более 60 секунд. Сделайте паузу.", "no_input")
                self.last_driver_input_time = now
        elif cruise_enabled and lane_keeping_enabled:
            if now - self.last_driver_input_time > 60:
                self._warn("Круиз и удержание полосы активны. Пожалуйста, держите руки на руле.", "autonomy")
                self.last_driver_input_time = now

        # Длительное вождение
        if now - self.trip_start_time > 100 * 60:
            if now - self.last_warning_time > self.warning_interval:
                self._warn("Вы ведёте более 100 минут. Сделайте перерыв.", "long_drive")
                self.last_warning_time = now

        # Сработки по статистике
        if self.rapid_steering_events >= self.max_rapid_steering:
            self._warn("Частые резкие повороты рулём. Возможна усталость.", "steering")
            self.rapid_steering_events = 0

        if self.lane_departure_count >= self.max_lane_departures:
            self._warn("Вы часто пересекаете разметку без поворотника. Сделайте паузу.", "lane_departure")
            self.lane_departure_count = 0

    def register_lane_departure(self, left_signal_on, right_signal_on):
        if not (left_signal_on or right_signal_on):
            self.lane_departure_count += 1

    def vehicle_is_moving(self, throttle, brake):
        return throttle > 0 or brake > 0

    def _warn(self, message, category):
        self.db.log_fatigue_warning(message, category)
        if self.window:
            self.window.show_fatigue_warning(message)
        else:
            print("[!] Усталость: " + message)

    def reset(self):
        self.trip_start_time = time.time()
        self.last_driver_input_time = time.time()
        self.last_steer = 0.0
        self.rapid_steering_events = 0
        self.lane_departure_count = 0
        self.last_warning_time = 0


# Тестирование 
def main():
    print("[*] Driver Fatigue Monitor started. Нажмите Ctrl+C для выхода.")
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()

    vehicles = world.get_actors().filter('vehicle.*')
    if not vehicles:
        print("[-] Машина не найдена.")
        return

    vehicle = vehicles[0]
    print(f"[+] Подключено к машине: {vehicle.type_id} (ID {vehicle.id})")

    monitor = DriverFatigueMonitor(vehicle)

    try:
        while True:
            control = vehicle.get_control()
            lights = vehicle.get_light_state()

            lane_keeping = False
            cruise = False

            monitor.update_driver_input(
                throttle=control.throttle,
                brake=control.brake,
                steer=control.steer,
                lane_keeping_enabled=lane_keeping,
                cruise_enabled=cruise
            )

            if abs(control.steer) > 0.3:
                monitor.register_lane_departure(
                    left_signal_on=bool(lights & carla.VehicleLightState.LeftBlinker),
                    right_signal_on=bool(lights & carla.VehicleLightState.RightBlinker)
                )

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[!] Завершение мониторинга усталости.")

if __name__ == "__main__":
    main()
