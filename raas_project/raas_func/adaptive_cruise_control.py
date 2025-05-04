import carla
from database_logger import DatabaseLogger

class AdaptiveCruiseControl:
    def __init__(self, vehicle, world):
        self.vehicle = vehicle
        self.world = world
        self.enabled = False
        self.target_speed = 0.0  # м/с
        self.min_distance = 10.0  # метры
        self.db = DatabaseLogger()

    def set_target_speed(self, speed_kmh):
        self.target_speed = max(30.0, min(150.0, speed_kmh)) / 3.6

    def increase_speed(self):
        self.target_speed = min(self.target_speed + 5.0 / 3.6, 150.0 / 3.6)

    def decrease_speed(self):
        self.target_speed = max(self.target_speed - 5.0 / 3.6, 30.0 / 3.6)

    def enable(self):
        self.enabled = True
        speed = self.get_speed(self.vehicle) * 3.6
        self.db.log_cruise_control("enabled", speed)
        print("[+] Adaptive Cruise Control ENABLED")

    def disable(self):
        self.enabled = False
        speed = self.get_speed(self.vehicle) * 3.6
        self.db.log_cruise_control("disabled", speed)
        print("[-] Adaptive Cruise Control DISABLED")

    def update(self):
        if not self.enabled:
            return

        original_control = self.vehicle.get_control()

        # Проверка ручного торможения водителем
        if original_control.brake > 0.1:
            self.disable()
            return

        current_speed = self.get_speed(self.vehicle)
        desired_speed = self.target_speed

        # Если водитель нажимает газ и превышает целевую — не мешаем
        if original_control.throttle > 0.1 and current_speed > desired_speed + 1.0:
            return

        # Плавное управление скоростью
        new_throttle = 0.0
        new_brake = 0.0
        speed_diff = desired_speed - current_speed

        if abs(speed_diff) < 0.5:
            new_throttle = 0.2
        elif speed_diff > 0:
            new_throttle = min(0.6, 0.3 + 0.1 * speed_diff)
        else:
            new_brake = min(0.5, 0.2 + 0.1 * abs(speed_diff))

        # Применение управления
        new_control = carla.VehicleControl(
            throttle=new_throttle,
            brake=new_brake,
            steer=original_control.steer,
            hand_brake=original_control.hand_brake,
            reverse=original_control.reverse,
            manual_gear_shift=original_control.manual_gear_shift,
            gear=original_control.gear
        )

        self.vehicle.apply_control(new_control)

    def get_speed(self, vehicle):
        v = vehicle.get_velocity()
        return (v.x**2 + v.y**2 + v.z**2) ** 0.5

    def get_closest_vehicle_ahead(self):
        # Оставлено как заглушка, вдруг пригодится позже
        ego_transform = self.vehicle.get_transform()
        ego_location = ego_transform.location
        ego_forward = ego_transform.get_forward_vector()

        min_distance = float('inf')
        closest_vehicle = None

        for actor in self.world.get_actors().filter('vehicle.*'):
            if actor.id == self.vehicle.id:
                continue

            location = actor.get_location()
            direction = location - ego_location

            if ego_forward.dot(direction) > 0:
                distance = direction.length()
                if distance < min_distance:
                    min_distance = distance
                    closest_vehicle = actor

        return closest_vehicle, min_distance
