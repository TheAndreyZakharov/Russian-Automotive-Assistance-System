# spawn_vehicle.py

import carla
import random
import time

def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    blueprint_library = world.get_blueprint_library()

    # Use Nissan Patrol (or similar model name)
    vehicle_bp = blueprint_library.filter('vehicle.nissan.patrol_2021')[0]

    spawn_points = world.get_map().get_spawn_points()
    spawn_point = random.choice(spawn_points)

    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)

    if vehicle:
        print("[+] Nissan Patrol spawned.")
    else:
        print("[-] Failed to spawn vehicle.")

    # Let the car exist while other scripts run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Cleanup...")
    finally:
        if vehicle:
            vehicle.destroy()
            print("[*] Vehicle destroyed.")

if __name__ == "__main__":
    main()
