import carla

def main():
    client = carla.Client("localhost", 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    actors = world.get_actors()

    vehicles = actors.filter('vehicle.*')
    walkers = actors.filter('walker.*')

    if not vehicles:
        print("[!] Нет ни одной машины для анализа.")
        return

    # Найдём машину с минимальным ID — это наше основное авто
    main_vehicle = min(vehicles, key=lambda v: v.id)
    print(f"[*] Сохраняем главное авто: {main_vehicle.type_id} (ID: {main_vehicle.id})")

    to_destroy = []

    for vehicle in vehicles:
        if vehicle.id != main_vehicle.id:
            to_destroy.append(vehicle)

    for walker in walkers:
        to_destroy.append(walker)

    if to_destroy:
        print(f"[!] Удаляем {len(to_destroy)} объектов трафика...")
        client.apply_batch([carla.command.DestroyActor(actor) for actor in to_destroy])
        print("[+] Готово.")
    else:
        print("[*] Нечего удалять — только главное авто осталось.")

if __name__ == '__main__':
    main()
