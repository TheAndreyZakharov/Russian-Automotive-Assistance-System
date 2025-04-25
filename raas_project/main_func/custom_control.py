import carla
import pygame
import time
import sys

def main():
    pygame.init()
    pygame.display.set_caption("RAAS Control Panel")
    pygame.display.set_mode((400, 300))

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
    manual_gear = False

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    print("\n================= CONTROLS =================")
    print("W               - Throttle (Forward)")
    print("S               - Brake / Reverse (if stopped)")
    print("A / D           - Steer Left / Right")
    print("Space           - Handbrake")
    print("M               - Toggle Manual Gear Mode")
    print("R / N / 1-6     - Select Reverse / Neutral / Gear")
    print("Q / E / Z       - Turn Signals (Left / Right / Hazard)")
    print("L               - Toggle Headlights")
    print("P               - Toggle Autopilot")
    print("C               - Change Weather Preset")
    print("Esc or Ctrl+C   - Exit")
    print("============================================\n")

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

            keys = pygame.key.get_pressed()

            velocity = vehicle.get_velocity()
            speed = (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5

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

            control.steer = 0.0
            if keys[pygame.K_a]:
                control.steer = -0.5
            elif keys[pygame.K_d]:
                control.steer = 0.5

            control.hand_brake = keys[pygame.K_SPACE]

            # Turn signals
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

            # Toggle headlights
            if keys[pygame.K_l]:
                if lights & carla.VehicleLightState.Position:
                    lights &= ~carla.VehicleLightState.Position
                else:
                    lights |= carla.VehicleLightState.Position
                time.sleep(0.2)

            # Toggle autopilot
            if keys[pygame.K_p]:
                autopilot_enabled = not autopilot_enabled
                vehicle.set_autopilot(autopilot_enabled)
                print(f"[i] Autopilot {'enabled' if autopilot_enabled else 'disabled'}")
                time.sleep(0.2)

            # Toggle weather
            if keys[pygame.K_c]:
                current_weather = (current_weather + 1) % len(weather_presets)
                world.set_weather(weather_presets[current_weather])
                print(f"[i] Weather changed to preset {current_weather}")
                time.sleep(0.2)

            # Manual gear toggle
            if keys[pygame.K_m]:
                manual_gear = not manual_gear
                control.manual_gear_shift = manual_gear
                print(f"[i] Manual gear {'ENABLED' if manual_gear else 'DISABLED'}")
                time.sleep(0.2)

            if manual_gear:
                # Reverse
                if keys[pygame.K_r]:
                    control.gear = -1
                # Neutral
                elif keys[pygame.K_n]:
                    control.gear = 0
                # Forward gears
                elif keys[pygame.K_1]: control.gear = 1
                elif keys[pygame.K_2]: control.gear = 2
                elif keys[pygame.K_3]: control.gear = 3
                elif keys[pygame.K_4]: control.gear = 4
                elif keys[pygame.K_5]: control.gear = 5
                elif keys[pygame.K_6]: control.gear = 6

            # Apply control
            vehicle.set_light_state(carla.VehicleLightState(lights))
            vehicle.apply_control(control)

            # Draw info panel
            screen = pygame.display.get_surface()
            screen.fill((30, 30, 30))

            info_lines = [
                f"Speed: {round(speed * 3.6, 1)} km/h",
                f"Throttle: {round(control.throttle, 2)} | Brake: {round(control.brake, 2)}",
                f"Steer: {round(control.steer, 2)}",
                f"Gear Mode: {'Manual' if manual_gear else 'Auto'}",
                f"Current Gear: {control.gear}",
                f"Lights (L): {'ON' if lights & carla.VehicleLightState.Position else 'OFF'}",
                f"Left signal (Q/Z): {'ON' if lights & carla.VehicleLightState.LeftBlinker else 'OFF'}",
                f"Right signal (E/Z): {'ON' if lights & carla.VehicleLightState.RightBlinker else 'OFF'}",
                f"Autopilot (P): {'ON' if autopilot_enabled else 'OFF'}"
            ]

            for i, line in enumerate(info_lines):
                text = font.render(line, True, (200, 200, 200))
                screen.blit(text, (10, 10 + i * 25))

            pygame.display.flip()
            clock.tick(30)

    except KeyboardInterrupt:
        print("\n[!] Exiting custom control.")
    finally:
        pygame.quit()

if __name__ == '__main__':
    main()
