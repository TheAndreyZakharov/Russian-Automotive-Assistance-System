import carla
import math
import time
import threading
from database_logger import DatabaseLogger

class AutoBrakingSystem:
    def __init__(self, world, vehicle):
        self.vehicle = vehicle
        self.world = world
        self.lidar_sensor = None
        self.braking = False
        self.db = DatabaseLogger()
        self.stop_time = None
        self.running = False

    def apply_emergency_brake(self):
        control = carla.VehicleControl()
        control.throttle = 0.0
        control.brake = 1.0
        self.vehicle.apply_control(control)

    def release_brake(self):
        control = carla.VehicleControl()
        control.brake = 0.0
        self.vehicle.apply_control(control)

    def get_speed(self):
        v = self.vehicle.get_velocity()
        return math.sqrt(v.x**2 + v.y**2 + v.z**2) * 3.6

    def lidar_callback(self, data):
        if not self.running:
            return

        min_distance = float('inf')
        obstacle_detected = False

        for point in data:
            x, y, z = point.point.x, point.point.y, point.point.z
            distance = math.sqrt(x ** 2 + y ** 2 + z ** 2)

            if x > 0.5 and abs(y) < 2.0 and -0.5 < z < 2.0:
                obstacle_detected = True
                if distance < min_distance:
                    min_distance = distance

        speed = self.get_speed()

        if speed <= 60:
            critical_distance = max(speed / 10, 5)

            if obstacle_detected and min_distance <= critical_distance and not self.braking:
                self.braking = True
                self.stop_time = None
                print(f"[!] Obstacle detected at {min_distance:.2f}m | Speed: {speed:.1f} km/h | BRAKING!")
                self.apply_emergency_brake()
                self.db.log_emergency_brake(speed_kmh=speed, distance_m=min_distance)

            elif self.braking and speed < 0.5:
                if self.stop_time is None:
                    self.stop_time = time.time()
                elif time.time() - self.stop_time > 1.0:
                    print("[*] Vehicle fully stopped. Releasing brake.")
                    self.braking = False
                    self.release_brake()

        elif self.braking:
            print("[*] Speed too high, emergency braking disengaged.")
            self.braking = False
            self.release_brake()
            self.stop_time = None

    def start(self):
        if self.running:
            return
        blueprint_library = self.world.get_blueprint_library()
        lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
        lidar_bp.set_attribute('range', '50')
        lidar_bp.set_attribute('rotation_frequency', '20')
        lidar_bp.set_attribute('points_per_second', '300000')

        transform = carla.Transform(carla.Location(x=2.5, z=1.2))
        self.lidar_sensor = self.world.spawn_actor(lidar_bp, transform, attach_to=self.vehicle)
        self.lidar_sensor.listen(self.lidar_callback)
        self.running = True
        print("[*] Auto braking system enabled.")

    def stop(self):
        if self.lidar_sensor:
            self.lidar_sensor.stop()
            self.lidar_sensor.destroy()
            self.release_brake()
            self.running = False
            print("[*] Auto braking system disabled.")
