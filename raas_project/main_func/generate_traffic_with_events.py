# generate_traffic_with_events.py

import carla
import random
import time
import threading

NUMBER_OF_VEHICLES = 40
NUMBER_OF_WALKERS = 30

def spawn_vehicle(world, blueprint_library, spawn_points):
    vehicles = []

    for i in range(min(NUMBER_OF_VEHICLES, len(spawn_points))):
        blueprint = random.choice(blueprint_library.filter('vehicle.*'))
        # Изменим часть машин на Nissan Patrol 2021
        if random.random() < 0.2:
            blueprint = blueprint_library.find('vehicle.nissan.patrol_2021')

        transform = spawn_points[i]
        vehicle = world.try_spawn_actor(blueprint, transform)
        if vehicle:
            vehicle.set_autopilot(True)
            vehicles.append(vehicle)
            print(f"[+] Spawned: {vehicle.type_id}")

    return vehicles


def random_braking_behavior(vehicle, interval=10):
    while True:
        time.sleep(random.uniform(interval, interval + 5))
        control = vehicle.get_control()
        print(f"[!] {vehicle.id} is simulating sudden brake!")
        control.brake = 1.0
        control.throttle = 0.0
        vehicle.apply_control(control)
        time.sleep(1.5)  # Hold brake
        control.brake = 0.0
        vehicle.set_autopilot(True)


def assign_random_braking(vehicles):
    for v in vehicles:
        if 'nissan.patrol_2021' in v.type_id:
            threading.Thread(target=random_braking_behavior, args=(v,), daemon=True).start()


def spawn_pedestrians(world, blueprint_library):
    walker_blueprints = blueprint_library.filter('walker.pedestrian.*')
    controller_bp = blueprint_library.find('controller.ai.walker')
    spawn_points = []

    for _ in range(NUMBER_OF_WALKERS):
        loc = world.get_random_location_from_navigation()
        if loc:
            spawn_points.append(carla.Transform(loc))

    walkers = []
    walker_controllers = []

    batch = []
    for spawn_point in spawn_points:
        walker_bp = random.choice(walker_blueprints)
        walker = world.try_spawn_actor(walker_bp, spawn_point)
        if walker:
            controller = world.try_spawn_actor(controller_bp, carla.Transform(), attach_to=walker)
            if controller:
                walkers.append(walker)
                walker_controllers.append(controller)

    for i in range(len(walkers)):
        walker_controllers[i].start()
        walker_controllers[i].go_to_location(world.get_random_location_from_navigation())
        walker_controllers[i].set_max_speed(1 + random.random())  # 1-2 m/s

    print(f"[+] Spawned {len(walkers)} pedestrians.")
    return walkers + walker_controllers


def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(20.0)
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)

    print("[*] Spawning vehicles...")
    vehicles = spawn_vehicle(world, blueprint_library, spawn_points)

    print("[*] Spawning pedestrians...")
    walkers = spawn_pedestrians(world, blueprint_library)

    print("[*] Assigning random braking to Nissan Patrols...")
    assign_random_braking(vehicles)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Cleaning up...")
        for v in vehicles:
            v.destroy()
        for w in walkers:
            w.destroy()
        print("[*] All actors destroyed.")

if __name__ == '__main__':
    main()
