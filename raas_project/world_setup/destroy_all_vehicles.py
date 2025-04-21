# destroy_all_vehicles.py

import carla

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)

    world = client.get_world()
    vehicles = world.get_actors().filter('vehicle.*')

    if not vehicles:
        print("[*] No vehicles to destroy.")
        return

    print(f"[*] Found {len(vehicles)} vehicles. Destroying...")

    for vehicle in vehicles:
        vehicle.destroy()

    print("[+] All vehicles destroyed.")

if __name__ == '__main__':
    main()
