import glob
import os
import sys
import time
import carla
from carla import VehicleLightState as vls
import argparse
import logging
from numpy import random

def get_actor_blueprints(world, filter, generation):
    bps = world.get_blueprint_library().filter(filter)
    if generation.lower() == "all":
        return bps
    if len(bps) == 1:
        return bps
    try:
        int_generation = int(generation)
        if int_generation in [1, 2]:
            bps = [x for x in bps if int(x.get_attribute('generation')) == int_generation]
            return bps
        else:
            print("   Warning! Actor Generation is not valid. No actor will be spawned.")
            return []
    except:
        print("   Warning! Actor Generation is not valid. No actor will be spawned.")
        return []

def main():
    argparser = argparse.ArgumentParser(description="Spawn vehicles and walkers in Carla")
    argparser.add_argument('--host', default='127.0.0.1')
    argparser.add_argument('-p', '--port', default=2000, type=int)
    argparser.add_argument('-n', '--number-of-vehicles', default=30, type=int)
    argparser.add_argument('-w', '--number-of-walkers', default=10, type=int)
    argparser.add_argument('--filterv', default='vehicle.*')
    argparser.add_argument('--generationv', default='All')
    argparser.add_argument('--filterw', default='walker.pedestrian.*')
    argparser.add_argument('--generationw', default='2')
    args = argparser.parse_args()

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    vehicles_list = []
    walkers_list = []
    all_id = []

    client = carla.Client(args.host, args.port)
    client.set_timeout(10.0)

    world = client.get_world()
    blueprints = get_actor_blueprints(world, args.filterv, args.generationv)
    walker_blueprints = get_actor_blueprints(world, args.filterw, args.generationw)

    spawn_points = world.get_map().get_spawn_points()
    random.shuffle(spawn_points)
    number_of_spawn_points = len(spawn_points)

    if args.number_of_vehicles < number_of_spawn_points:
        spawn_points = spawn_points[:args.number_of_vehicles]

    batch = []
    for transform in spawn_points:
        blueprint = random.choice(blueprints)
        if blueprint.has_attribute('color'):
            color = random.choice(blueprint.get_attribute('color').recommended_values)
            blueprint.set_attribute('color', color)
        blueprint.set_attribute('role_name', 'autopilot')
        batch.append(carla.command.SpawnActor(blueprint, transform).then(
            carla.command.SetAutopilot(carla.command.FutureActor, True)))

    responses = client.apply_batch_sync(batch, True)
    for response in responses:
        if not response.error:
            vehicles_list.append(response.actor_id)

    walker_spawn_points = []
    max_attempts = args.number_of_walkers * 5
    spawned = 0
    attempts = 0
    while spawned < args.number_of_walkers and attempts < max_attempts:
        loc = world.get_random_location_from_navigation()
        if loc:
            walker_spawn_points.append(carla.Transform(loc))
            spawned += 1
        attempts += 1

    print(f"[INFO] Successfully found spawn locations for {spawned} walkers (after {attempts} attempts).")

    batch = []
    walker_speed = []
    for spawn_point in walker_spawn_points:
        walker_bp = random.choice(walker_blueprints)
        if walker_bp.has_attribute('is_invincible'):
            walker_bp.set_attribute('is_invincible', 'false')
        if walker_bp.has_attribute('speed'):
            walker_speed.append(walker_bp.get_attribute('speed').recommended_values[1])
        else:
            walker_speed.append('1.0')
        batch.append(carla.command.SpawnActor(walker_bp, spawn_point))

    results = client.apply_batch_sync(batch, True)
    walker_speed2 = []
    for i in range(len(results)):
        if not results[i].error:
            walkers_list.append({"id": results[i].actor_id})
            walker_speed2.append(walker_speed[i])

    walker_speed = walker_speed2
    batch = []
    controller_bp = world.get_blueprint_library().find('controller.ai.walker')
    for i in range(len(walkers_list)):
        batch.append(carla.command.SpawnActor(controller_bp, carla.Transform(), walkers_list[i]["id"]))

    results = client.apply_batch_sync(batch, True)
    for i in range(len(results)):
        if not results[i].error:
            walkers_list[i]["con"] = results[i].actor_id

    all_id = []
    for i in range(len(walkers_list)):
        all_id.append(walkers_list[i]["con"])
        all_id.append(walkers_list[i]["id"])

    all_actors = world.get_actors(all_id)
    for i in range(0, len(all_id), 2):
        try:
            all_actors[i].start()
            all_actors[i].go_to_location(world.get_random_location_from_navigation())
            all_actors[i].set_max_speed(float(walker_speed[int(i/2)]))
        except RuntimeError as e:
            print(f"[!] Skipping walker controller due to error: {e}")

    print(f"[+] Spawned {len(vehicles_list)} vehicles and {len(walkers_list)} walkers")

    try:
        while True:
            world.wait_for_tick()
    finally:
        print('\nDestroying actors...')
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])
        client.apply_batch([carla.command.DestroyActor(x) for x in all_id])
        print('Done.')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted.')
