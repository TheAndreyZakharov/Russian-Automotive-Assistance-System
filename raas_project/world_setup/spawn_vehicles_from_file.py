import carla
import random
import re

# === Настройки ===
INPUT_FILE = "vehicle_coords.txt"

# Список разрешённых моделей (с использованием точных Blueprint ID)
ALLOWED_VEHICLES = [
    "vehicle.audi.a2", "vehicle.audi.etron", "vehicle.audi.tt",  # Audi
    "vehicle.bmw.grandtourer",  # BMW
    "vehicle.chevrolet.impala",  # Chevrolet
    "vehicle.dodge.charger2020", "vehicle.dodge.policecharger2020", "vehicle.ford.crown",  # Dodge, Ford
    "vehicle.lincoln.mkz2020", "vehicle.mercedes.coupe2020", "vehicle.mini.coopers2021",  # Lincoln, Mercedes, Mini
    "vehicle.nissan.patrol2021", "vehicle.tesla.cybertruck", "vehicle.mercedes.sprinter",  # Nissan, Tesla, Mercedes
    "vehicle.audi.a2", "vehicle.audi.etron", "vehicle.audi.tt", "vehicle.bmw.grandtourer",  # Audi, BMW
    "vehicle.chevrolet.impala", "vehicle.dodge.policecharger", "vehicle.ford.mustang",  # Dodge, Ford
    "vehicle.jeep.wrangler", "vehicle.lincoln.mkz2017", "vehicle.mercedes.coupe",  # Jeep, Lincoln, Mercedes
    "vehicle.micro.microlino", "vehicle.mini.coopers", "vehicle.nissan.micra", "vehicle.seat.leon",  # Micro, Mini, Nissan, Seat
    "vehicle.tesla.model3", "vehicle.toyota.prius"  # Tesla, Toyota
]

def is_valid_vehicle(blueprint):
    """Фильтрует только разрешённые модели транспорта"""
    name = blueprint.id
    return name in ALLOWED_VEHICLES

def parse_coords_for_town(file_path, current_town):
    """Извлекает координаты из файла только для текущего города"""
    with open(file_path, "r") as f:
        lines = f.readlines()

    coords = []
    inside_section = False

    for line in lines:
        line = line.strip()

        if not line:
            continue
        if line.startswith("! Town"):
            # Проверяем, что это именно нужный город
            if line.strip() == f"! {current_town}":
                inside_section = True
                print(f"[DEBUG] Found city section: {current_town}")
            else:
                inside_section = False
            continue
        if not inside_section:
            continue
        if line.startswith("//") or line.startswith("#"):
            continue

        # Печатаем строки, которые обрабатываются
        print(f"[DEBUG] Processing line: {line}")

        match = re.findall(r"x=([-.\d]+), y=([-.\d]+), z=([-.\d]+), yaw=([-.\d]+)", line)
        if match:
            x, y, z, yaw = map(float, match[0])
            coords.append(carla.Transform(
                carla.Location(x=x, y=y, z=z + 0.5),  # поднимаем чуть выше
                carla.Rotation(yaw=yaw)
            ))

    return coords

def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    current_map = world.get_map().name.split("/")[-1]  # Например: "Town4"

    print(f"[+] Current map: {current_map}")

    spawn_points = parse_coords_for_town(INPUT_FILE, current_map)
    if not spawn_points:
        print(f"[-] No spawn points found for {current_map} in {INPUT_FILE}")
        return

    blueprint_library = world.get_blueprint_library()

    # Проверим, какие модели доступны
    print("[DEBUG] Available vehicle blueprints:")
    available_vehicles = [bp.id for bp in blueprint_library.filter("vehicle.*")]
    print(f"[DEBUG] Available vehicles: {available_vehicles}")

    # Фильтруем только разрешённые модели
    vehicle_blueprints = [bp for bp in blueprint_library.filter("vehicle.*") if is_valid_vehicle(bp)]

    # Если нет разрешённых моделей, выводим сообщение
    if not vehicle_blueprints:
        print(f"[-] No allowed vehicles found in the current map. Available: {available_vehicles}")
        return

    actors = []
    try:
        for transform in spawn_points:
            bp = random.choice(vehicle_blueprints)

            # Устанавливаем случайный цвет, если есть поддержка
            if bp.has_attribute("color"):
                color = random.choice(bp.get_attribute("color").recommended_values)
                bp.set_attribute("color", color)

            vehicle = world.try_spawn_actor(bp, transform)
            if vehicle:
                print(f"[+] Spawned: {vehicle.type_id} at {transform.location}")
                actors.append(vehicle)
            else:
                print("[-] Failed to spawn vehicle (possibly collision).")

    except Exception as e:
        print(f"[!] Error: {e}")

    finally:
        print(f"[i] Spawned {len(actors)} vehicles.")
        print("Press Ctrl+C to exit and remove vehicles.")

        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("[*] Cleaning up...")
            for actor in actors:
                actor.destroy()
            print("[*] All vehicles removed.")

if __name__ == "__main__":
    main()
