import carla
import pygame
import time
import sys

def main():
    pygame.init()
    pygame.display.set_mode((400, 200))

    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    weather_presets = [
        carla.WeatherParameters.ClearNoon,
        carla.WeatherParameters.WetNoon,
        carla.WeatherParameters.HardRainNoon,
        carla.WeatherParameters.SoftRainSunset
    ]
    current_weather = 0

    vehicles = world.get_actors().filter('vehicle.*')
    if not vehicles:
        print("[-] No vehicle found.")
        return

    vehicle = vehicles[0]
    print(f"[+] Connected to: {vehicle.type_id}")

    control = carla.VehicleControl()
    lights = carla.VehicleLightState.NONE
    autopilot_enabled = False
    telemetry_enabled = False

    clock = pygame.time.Clock()
    print("[*] Custom CARLA vehicle control ready.")

    print("\n================= CONTROLS =================")
    print("W               - Throttle (Forward)")
    print("S               - Brake / Reverse (if stopped)")
    print("A / D           - Steer Left / Right")
    print("Space           - Handbrake")
    print("Q               - Left Turn Signal")
    print("E               - Right Turn Signal")
    print("Z               - Hazard Lights (Both)")
    print("L               - Toggle Headlights")
    print("P               - Toggle Autopilot")
    print("C               - Change Weather Preset")
    print("O               - Open/Close All Doors")
    print("T               - Toggle Telemetry Output")
    print("Esc or Ctrl+C   - Exit")
    print("============================================\n")

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            keys = pygame.key.get_pressed()

            # ===== Movement =====
            velocity = vehicle.get_velocity()
            speed = (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5

            if keys[pygame.K_s]:
                if speed < 0.1:
                    control.throttle = 0.5
                    control.brake = 0.0
                    control.reverse = True
                else:
                    control.throttle = 0.0
                    control.brake = 1.0
                    control.reverse = False
            else:
                control.reverse = False
                control.brake = 0.0
                control.throttle = 1.0 if keys[pygame.K_w] else 0.0

            control.steer = 0.0
            if keys[pygame.K_a]:
                control.steer = -0.5
            elif keys[pygame.K_d]:
                control.steer = 0.5

            control.hand_brake = keys[pygame.K_SPACE]

            # ===== Turn Signals =====
            if keys[pygame.K_q]:
                lights |= carla.VehicleLightState.LeftBlinker
                lights &= ~carla.VehicleLightState.RightBlinker
            elif keys[pygame.K_e]:
                lights |= carla.VehicleLightState.RightBlinker
                lights &= ~carla.VehicleLightState.LeftBlinker
            elif keys[pygame.K_z]:
                lights |= carla.VehicleLightState.LeftBlinker | carla.VehicleLightState.RightBlinker
            else:
                lights &= ~(carla.VehicleLightState.LeftBlinker | carla.VehicleLightState.RightBlinker)

            # ===== Headlights =====
            if keys[pygame.K_l]:
                if lights & carla.VehicleLightState.Position:
                    lights &= ~carla.VehicleLightState.Position
                else:
                    lights |= carla.VehicleLightState.Position
                time.sleep(0.2)  # debounce

            # ===== Autopilot toggle =====
            if keys[pygame.K_p]:
                autopilot_enabled = not autopilot_enabled
                vehicle.set_autopilot(autopilot_enabled)
                print(f"[i] Autopilot {'enabled' if autopilot_enabled else 'disabled'}")
                time.sleep(0.2)

            # ===== Weather toggle =====
            if keys[pygame.K_c]:
                current_weather = (current_weather + 1) % len(weather_presets)
                world.set_weather(weather_presets[current_weather])
                print(f"[i] Weather changed to preset {current_weather}")
                time.sleep(0.2)

            # ===== Open/close doors =====
            if keys[pygame.K_o]:
                doors = carla.VehicleDoor
                for door in [doors.FRONT_LEFT, doors.FRONT_RIGHT, doors.REAR_LEFT, doors.REAR_RIGHT]:
                    if vehicle.is_door_open(door):
                        vehicle.close_door(door)
                    else:
                        vehicle.open_door(door)
                print("[i] Toggled all doors.")
                time.sleep(0.3)

            # ===== Toggle telemetry output =====
            if keys[pygame.K_t]:
                telemetry_enabled = not telemetry_enabled
                print(f"[i] Telemetry {'enabled' if telemetry_enabled else 'disabled'}")
                time.sleep(0.2)

            # ===== Apply everything =====
            vehicle.set_light_state(carla.VehicleLightState(lights))
            vehicle.apply_control(control)

            # ===== Show telemetry =====
            if telemetry_enabled:
                transform = vehicle.get_transform()
                print(f"Speed: {round(speed, 2)} m/s | Location: {transform.location}")

            clock.tick(30)

    except KeyboardInterrupt:
        print("\n[!] Exiting custom control.")
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
