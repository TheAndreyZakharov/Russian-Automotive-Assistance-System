import carla
import pygame
import time
import math
import numpy as np
import cv2
import sys
import signal

class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.prev_error = 0.0
        self.integral = 0.0

    def run(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0.0
        output = self.Kp * error + self.Ki * self.integral + self.Kd * derivative
        self.prev_error = error
        return output

# Глобальные переменные
running = True

def signal_handler(sig, frame):
    global running
    print("\n[!] Exiting...")
    running = False

def process_and_show_lane(image, lane_center_x=None):
    roi = image[240:, :]
    output = image.copy()
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 30, 90)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 25, np.array([]), minLineLength=30, maxLineGap=150)

    left_lines = []
    right_lines = []

    height, width = roi.shape[:2]
    cam_center = image.shape[1] // 2

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            slope = (y2 - y1) / (x2 - x1 + 1e-6)
            if abs(slope) < 0.3:
                continue
            midpoint = (x1 + x2) // 2
            if slope < 0 and midpoint < width // 2:
                left_lines.append((x1, y1, x2, y2))
                cv2.line(output[240:], (x1, y1), (x2, y2), (0, 0, 255), 2)  # красная
            elif slope > 0 and midpoint > width // 2:
                right_lines.append((x1, y1, x2, y2))
                cv2.line(output[240:], (x1, y1), (x2, y2), (0, 255, 0), 2)  # зелёная

    # Центр камеры (синий)
    cv2.line(output, (cam_center, 240), (cam_center, 480), (255, 0, 0), 2)

    # Центр полосы (жёлтая линия)
    if lane_center_x is not None:
        cv2.line(output, (lane_center_x, 240), (lane_center_x, 480), (0, 255, 255), 2)

    cv2.imshow("Lane View", output)

def camera_callback(image, data_dict):
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = np.reshape(array, (image.height, image.width, 4))
    image_rgb = array[:, :, :3]
    data_dict['image'] = image_rgb

def main():
    global running
    signal.signal(signal.SIGINT, signal_handler)

    pygame.init()
    pygame.display.set_caption("RAAS Lane Assist Visualizer")
    pygame.display.set_mode((400, 300))

    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    map = world.get_map()

    vehicles = world.get_actors().filter('vehicle.*')
    if not vehicles:
        print("[-] No vehicle found.")
        return

    vehicle = vehicles[0]
    print(f"[+] Connected to: {vehicle.type_id}")

    # Камера
    blueprint_library = world.get_blueprint_library()
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '640')
    camera_bp.set_attribute('image_size_y', '480')
    camera_bp.set_attribute('fov', '90')
    camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
    camera = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)

    image_data = {'image': None}
    camera.listen(lambda image: camera_callback(image, image_data))

    control = carla.VehicleControl()
    lights = carla.VehicleLightState.NONE
    manual_gear = False
    autopilot_enabled = False
    lane_keeping_enabled = True
    pid = PIDController(Kp=1.2, Ki=0.0, Kd=0.3)

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            dt = clock.get_time() / 1000.0

            # Газ/тормоз
            if manual_gear:
                control.manual_gear_shift = True
                control.throttle = 0.5 if keys[pygame.K_w] and control.gear == -1 else 1.0 if keys[pygame.K_w] else 0.0
                control.brake = 1.0 if keys[pygame.K_s] else 0.0
            else:
                control.manual_gear_shift = False
                control.throttle = 1.0 if keys[pygame.K_w] else 0.0
                control.brake = 1.0 if keys[pygame.K_s] else 0.0

            control.hand_brake = keys[pygame.K_SPACE]

            # Поворотники
            if keys[pygame.K_q]:
                lights |= carla.VehicleLightState.LeftBlinker
                lights &= ~carla.VehicleLightState.RightBlinker
                lane_keeping_enabled = False
            elif keys[pygame.K_e]:
                lights |= carla.VehicleLightState.RightBlinker
                lights &= ~carla.VehicleLightState.LeftBlinker
                lane_keeping_enabled = False
            elif keys[pygame.K_z]:
                lights |= carla.VehicleLightState.LeftBlinker | carla.VehicleLightState.RightBlinker
                lane_keeping_enabled = False
            else:
                if lights & (carla.VehicleLightState.LeftBlinker | carla.VehicleLightState.RightBlinker):
                    lights &= ~(carla.VehicleLightState.LeftBlinker | carla.VehicleLightState.RightBlinker)
                    lane_keeping_enabled = True

            if keys[pygame.K_l]:
                if lights & carla.VehicleLightState.Position:
                    lights &= ~carla.VehicleLightState.Position
                else:
                    lights |= carla.VehicleLightState.Position
                time.sleep(0.2)

            if keys[pygame.K_p]:
                autopilot_enabled = not autopilot_enabled
                vehicle.set_autopilot(autopilot_enabled)
                print(f"[i] Autopilot {'enabled' if autopilot_enabled else 'disabled'}")
                time.sleep(0.2)

            if keys[pygame.K_m]:
                manual_gear = not manual_gear
                control.manual_gear_shift = manual_gear
                print(f"[i] Manual gear {'ENABLED' if manual_gear else 'DISABLED'}")
                time.sleep(0.2)

            if manual_gear:
                if keys[pygame.K_r]: control.gear = -1
                elif keys[pygame.K_n]: control.gear = 0
                elif keys[pygame.K_1]: control.gear = 1
                elif keys[pygame.K_2]: control.gear = 2
                elif keys[pygame.K_3]: control.gear = 3
                elif keys[pygame.K_4]: control.gear = 4
                elif keys[pygame.K_5]: control.gear = 5
                elif keys[pygame.K_6]: control.gear = 6

            # Lane keeping
            if lane_keeping_enabled:
                transform = vehicle.get_transform()
                location = transform.location
                rotation = transform.rotation
                waypoint = map.get_waypoint(location, project_to_road=True, lane_type=carla.LaneType.Driving)
                next_waypoint = waypoint.next(2.0)[0]
                dx = next_waypoint.transform.location.x - location.x
                dy = next_waypoint.transform.location.y - location.y
                yaw_rad = math.radians(rotation.yaw)
                error = -math.sin(yaw_rad) * dx + math.cos(yaw_rad) * dy
                steer_correction = pid.run(error, dt)
                control.steer = max(min(steer_correction, 1.0), -1.0)
            else:
                control.steer = 0.0
                if keys[pygame.K_a]: control.steer = -0.5
                elif keys[pygame.K_d]: control.steer = 0.5

            vehicle.set_light_state(carla.VehicleLightState(lights))
            vehicle.apply_control(control)

            # UI
            screen = pygame.display.get_surface()
            screen.fill((30, 30, 30))

            velocity = vehicle.get_velocity()
            speed = (velocity.x**2 + velocity.y**2 + velocity.z**2)**0.5

            info_lines = [
                f"Speed: {round(speed * 3.6, 1)} km/h",
                f"Throttle: {round(control.throttle, 2)} | Brake: {round(control.brake, 2)}",
                f"Steer: {round(control.steer, 2)}",
                f"Gear Mode: {'Manual' if manual_gear else 'Auto'}",
                f"Current Gear: {control.gear}",
                f"Lights (L): {'ON' if lights & carla.VehicleLightState.Position else 'OFF'}",
                f"Left signal (Q/Z): {'ON' if lights & carla.VehicleLightState.LeftBlinker else 'OFF'}",
                f"Right signal (E/Z): {'ON' if lights & carla.VehicleLightState.RightBlinker else 'OFF'}",
                f"Lane Assist: {'ON' if lane_keeping_enabled else 'OFF'}"
            ]

            for i, line in enumerate(info_lines):
                text = font.render(line, True, (200, 200, 200))
                screen.blit(text, (10, 10 + i * 25))

            pygame.display.flip()
            clock.tick(30)

            # Центр текущей полосы через waypoint
            lane_center_x = None
            if image_data['image'] is not None:
                try:
                    transform = vehicle.get_transform()
                    location = transform.location
                    forward = transform.get_forward_vector()
                    center_point = location + forward * 5.0
                    wp = map.get_waypoint(center_point, project_to_road=True, lane_type=carla.LaneType.Driving)

                    dx = wp.transform.location.x - location.x
                    dy = wp.transform.location.y - location.y
                    yaw = math.radians(transform.rotation.yaw)
                    rel_angle = math.atan2(dy, dx) - yaw
                    lane_center_x = int(image_data['image'].shape[1] / 2 + rel_angle * 300)
                except:
                    pass

                process_and_show_lane(image_data['image'], lane_center_x=lane_center_x)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                running = False

    finally:
        print("[*] Cleaning up camera and UI...")
        camera.stop()
        camera.destroy()
        pygame.quit()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
