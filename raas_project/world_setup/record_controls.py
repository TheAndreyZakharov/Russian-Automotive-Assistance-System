import carla
import pygame
import json
import os

SAVE_PATH = r"C:\Proj\raas_project\world_setup\path.json"
recorded_path = []

def main():
    pygame.init()
    pygame.display.set_caption("RAAS Full Recorder")
    pygame.display.set_mode((400, 300))

    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    vehicles = world.get_actors().filter('vehicle.*')
    if not vehicles:
        print("[-] No vehicles found.")
        return

    vehicle = sorted(vehicles, key=lambda v: v.id)[0]
    print(f"[+] Using vehicle: {vehicle.type_id} (id={vehicle.id})")

    control = carla.VehicleControl()
    manual_gear = False
    font = pygame.font.SysFont("consolas", 18)
    sim_time = 0.0  # собственный сим-временной счётчик

    try:
        while True:
            # === Tick симуляции ===
            world.tick()
            sim_time += 1.0 / 30.0  # фиксированная частота

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            keys = pygame.key.get_pressed()

            # Управление
            if manual_gear:
                control.manual_gear_shift = True
                if control.gear == -1:
                    control.throttle = 0.5 if keys[pygame.K_w] else 0.0
                else:
                    control.throttle = 1.0 if keys[pygame.K_w] else 0.0
                control.brake = 1.0 if keys[pygame.K_s] else 0.0
            else:
                control.reverse = False
                control.throttle = 1.0 if keys[pygame.K_w] else 0.0
                control.brake = 1.0 if keys[pygame.K_s] else 0.0

            control.steer = -0.5 if keys[pygame.K_a] else 0.5 if keys[pygame.K_d] else 0.0
            control.hand_brake = keys[pygame.K_SPACE]

            if keys[pygame.K_m]:
                manual_gear = not manual_gear
                control.manual_gear_shift = manual_gear
                print(f"[i] Manual gear {'ENABLED' if manual_gear else 'DISABLED'}")
                pygame.time.wait(200)

            if manual_gear:
                if keys[pygame.K_r]: control.gear = -1
                elif keys[pygame.K_n]: control.gear = 0
                elif keys[pygame.K_1]: control.gear = 1
                elif keys[pygame.K_2]: control.gear = 2
                elif keys[pygame.K_3]: control.gear = 3
                elif keys[pygame.K_4]: control.gear = 4
                elif keys[pygame.K_5]: control.gear = 5
                elif keys[pygame.K_6]: control.gear = 6

            vehicle.apply_control(control)

            loc = vehicle.get_location()
            rot = vehicle.get_transform().rotation

            # === Запись ===
            recorded_path.append({
                "timestamp": round(sim_time, 4),
                "x": round(loc.x, 3),
                "y": round(loc.y, 3),
                "z": round(loc.z, 3),
                "yaw": round(rot.yaw, 2),
                "pitch": round(rot.pitch, 2),
                "roll": round(rot.roll, 2),
                "steer": round(control.steer, 2),
                "throttle": round(control.throttle, 2),
                "brake": round(control.brake, 2),
                "reverse": control.reverse,
                "gear": control.gear,
                "manual_gear": control.manual_gear_shift,
                "hand_brake": control.hand_brake
            })

            # === UI ===
            screen = pygame.display.get_surface()
            screen.fill((30, 30, 30))
            lines = [
                f"x = {loc.x:.2f}", f"y = {loc.y:.2f}", f"z = {loc.z:.2f}",
                f"Yaw = {rot.yaw:.1f}", f"Throttle: {control.throttle:.2f}",
                f"Brake: {control.brake:.2f}", f"Steer: {control.steer:.2f}",
                f"Gear: {control.gear} | Reverse: {'Yes' if control.reverse else 'No'}",
                f"Handbrake: {'Yes' if control.hand_brake else 'No'}",
                f"Manual Gear: {'ON' if control.manual_gear_shift else 'OFF'}"
            ]
            for i, line in enumerate(lines):
                screen.blit(font.render(line, True, (200, 200, 200)), (10, 10 + i * 25))
            pygame.display.flip()

    except KeyboardInterrupt:
        print("\n[!] Stopped. Saving path...")

    finally:
        pygame.quit()
        os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
        with open(SAVE_PATH, "w") as f:
            json.dump(recorded_path, f, indent=2)
        print(f"[+] Path saved to {SAVE_PATH}")


if __name__ == "__main__":
    main()
