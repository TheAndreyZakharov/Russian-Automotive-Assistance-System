import carla
import random
import time

def main():
    print("[*] Подключение к серверу Carla...")
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    blueprint_library = world.get_blueprint_library()
    patrol_blueprints = blueprint_library.filter('vehicle.nissan.patrol_2021')

    if not patrol_blueprints:
        print("[-] Nissan Patrol не найден в библиотеке.")
        return

    vehicle_bp = patrol_blueprints[0]

    if vehicle_bp.has_attribute("color"):
        vehicle_bp.set_attribute("color", "0,0,0")

    spawn_points = world.get_map().get_spawn_points()
    if not spawn_points:
        print("[-] Нет доступных точек спавна.")
        return

    spawn_point = random.choice(spawn_points)
    vehicle = world.try_spawn_actor(vehicle_bp, spawn_point)

    if vehicle:
        print(f"[+] Машина заспавнена: {vehicle.type_id} (ID {vehicle.id})")
    else:
        print("[-] Не удалось заспавнить машину.")
        return

    try:
        print("[*] Машина активна. Нажмите Ctrl+C для завершения...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Завершение работы...")
    finally:
        if vehicle:
            vehicle.destroy()
            print("[*] Машина уничтожена.")

if __name__ == "__main__":
    main()