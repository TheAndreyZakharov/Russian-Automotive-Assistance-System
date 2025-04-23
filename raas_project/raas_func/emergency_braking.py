import carla
import math
import time

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    vehicle = world.get_actors().filter('vehicle.*')[0]

    vehicle.set_autopilot(False)
    print(f"Connected to vehicle: {vehicle.type_id}")

    blueprint_library = world.get_blueprint_library()

    lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
    lidar_bp.set_attribute('range', '50')
    lidar_bp.set_attribute('rotation_frequency', '20')
    lidar_bp.set_attribute('points_per_second', '300000')

    lidar_transform = carla.Transform(carla.Location(x=2.5, z=1.2))
    lidar_sensor = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)

    braking = False

    def apply_emergency_brake():
        control = carla.VehicleControl()
        control.throttle = 0.0
        control.brake = 1.0
        vehicle.apply_control(control)

    def release_brake():
        control = carla.VehicleControl()
        control.brake = 0.0
        vehicle.apply_control(control)

    def get_speed():
        v = vehicle.get_velocity()
        return math.sqrt(v.x**2 + v.y**2 + v.z**2) * 3.6

    stop_time = None  # отслеживаем момент полной остановки

    def lidar_callback(data):
        nonlocal braking, stop_time

        min_distance = float('inf')
        obstacle_detected = False

        for point in data:
            x, y, z = point.point.x, point.point.y, point.point.z
            distance = math.sqrt(x ** 2 + y ** 2 + z ** 2)

            if x > 0.5 and abs(y) < 2.0 and -0.5 < z < 2.0:
                obstacle_detected = True
                if distance < min_distance:
                    min_distance = distance

        speed = get_speed()

        if speed <= 60:
            critical_distance = max(speed / 10, 5)

            if obstacle_detected and min_distance <= critical_distance and not braking:
                braking = True
                stop_time = None
                print(f"[!] Obstacle detected at {min_distance:.2f}m | Speed: {speed:.1f} km/h | BRAKING!")
                apply_emergency_brake()

            elif braking and speed < 0.5:
                if stop_time is None:
                    stop_time = time.time()
                elif time.time() - stop_time > 1.0:
                    print("[*] Vehicle fully stopped. Releasing brake.")
                    braking = False
                    release_brake()

        elif braking:
            print("[*] Speed too high, emergency braking disengaged.")
            braking = False
            release_brake()
            stop_time = None


    lidar_sensor.listen(lambda data: lidar_callback(data))

    print("Emergency braking system active!")

    try:
        while True:
            time.sleep(0.02)

    except KeyboardInterrupt:
        print("Shutting down.")

    finally:
        lidar_sensor.stop()
        lidar_sensor.destroy()
        release_brake()
        print("Sensor destroyed, clean exit.")


if __name__ == '__main__':
    main()