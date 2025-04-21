import carla
import time
import math

def main():
    # Connect to CARLA server
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    # Get the first available vehicle
    vehicles = world.get_actors().filter('vehicle.*')
    if not vehicles:
        print("[-] No vehicle found. Please run spawn_vehicle.py first.")
        return

    vehicle = vehicles[0]
    print(f"[+] Connected to vehicle: {vehicle.type_id}")

    # Attach spectator (camera) above the car
    spectator = world.get_spectator()
    vehicle_transform = vehicle.get_transform()
    spectator.set_transform(carla.Transform(
        vehicle_transform.location + carla.Location(z=10),
        carla.Rotation(pitch=-90))
    )

    # Setup LiDAR sensor
    lidar_bp = blueprint_library.find('sensor.lidar.ray_cast')
    lidar_bp.set_attribute('range', '20')
    lidar_bp.set_attribute('rotation_frequency', '10')
    lidar_bp.set_attribute('points_per_second', '10000')

    lidar_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    lidar_sensor = world.spawn_actor(lidar_bp, lidar_transform, attach_to=vehicle)

    def lidar_callback(point_cloud):
        close_points = 0

        for detection in point_cloud:
            x = detection.point.x
            y = detection.point.y
            z = detection.point.z

            distance = math.sqrt(x**2 + y**2 + z**2)
            angle = math.degrees(math.atan2(y, x))

            # Check if point is in front of car and close enough, ignore low ground noise
            if -30 < angle < 30 and distance < 15.0 and -1.5 < z < 1.5:
                close_points += 1

        # If enough close points detected, apply brake
        if close_points > 10:
            print("[!] Obstacle ahead! Forcing brake.")
            control = vehicle.get_control()
            control.brake = 1.0
            control.throttle = 0.0
            vehicle.apply_control(control)

    # Start LiDAR stream
    lidar_sensor.listen(lambda data: lidar_callback(data))

    print("[*] Emergency braking system active.")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n[!] Stopping emergency braking system...")
    finally:
        if lidar_sensor.is_listening:
            lidar_sensor.stop()
        lidar_sensor.destroy()
        print("[*] Cleanup complete.")

if __name__ == '__main__':
    main()
