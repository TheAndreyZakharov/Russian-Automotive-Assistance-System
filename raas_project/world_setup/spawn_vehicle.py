import carla
import random
import time

def main():
    print("[*] Connecting to the Carla server...")
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    blueprint_library = world.get_blueprint_library()
    mkz_blueprints = blueprint_library.filter('vehicle.lincoln.mkz_2020')
    # ('vehicle.nissan.patrol_2021')
    
    if not mkz_blueprints:
        print("[-] Lincoln MKZ 2020 not found in the blueprint library.")
        return

    vehicle_bp = mkz_blueprints[0]

    if vehicle_bp.has_attribute("color"):
        vehicle_bp.set_attribute("color", "0,0,0")  # Set color to black

    spawn_points = world.get_map().get_spawn_points()
    if not spawn_points:
        print("[-] No available spawn points found.")
        return

    spawn_point = random.choice(spawn_points)
    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)

    if vehicle:
        print(f"[+] Vehicle spawned successfully: {vehicle.type_id} (ID {vehicle.id})")
    else:
        print("[-] Failed to spawn the vehicle.")
        return

    try:
        print("[*] Vehicle is active. Press Ctrl+C to exit...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
    finally:
        if vehicle:
            vehicle.destroy()
            print("[*] Vehicle destroyed.")

if __name__ == "__main__":
    main()
