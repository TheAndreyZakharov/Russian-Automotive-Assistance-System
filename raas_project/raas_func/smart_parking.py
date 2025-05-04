import carla
import numpy as np
import cv2
import time
import math
import json

class SmartParkingModule:
    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.running = False
        self.image_data = {"front": None, "back": None, "left": None, "right": None}
        self.WIDTH, self.HEIGHT = 640, 480
        self.VALID_PARKING_POINT = None
        self.PARKING_SIDE = None

        self.SENSOR_TRANSFORMS = {
            'front': carla.Transform(carla.Location(x=2.42, z=1), carla.Rotation(yaw=0)),
            'back':  carla.Transform(carla.Location(x=-2.47, z=1.25), carla.Rotation(yaw=180)),
            'left':  carla.Transform(carla.Location(x=0.75, y=-1.1, z=1.2), carla.Rotation(yaw=-90)),
            'right': carla.Transform(carla.Location(x=0.75, y=1.1, z=1.2), carla.Rotation(yaw=90))
        }

        self.PARKING_SPOTS = [
            {"spot": carla.Transform(carla.Location(x=280.42, y=-213.94, z=0.21), carla.Rotation(yaw=-2.27)), "id": 1},
            {"spot": carla.Transform(carla.Location(x=290.56, y=-200.85, z=0.23), carla.Rotation(yaw=179.34)), "id": 2}
        ]

        self.camera_intrinsics = {}
        self.sensors = []
        self.setup_cameras()

    def setup_cameras(self):
        blueprint_library = self.world.get_blueprint_library()
        cam_bp = blueprint_library.find("sensor.camera.rgb")
        cam_bp.set_attribute("image_size_x", str(self.WIDTH))
        cam_bp.set_attribute("image_size_y", str(self.HEIGHT))
        cam_bp.set_attribute("fov", "120")

        for name, tf in self.SENSOR_TRANSFORMS.items():
            cam = self.world.spawn_actor(cam_bp, tf, attach_to=self.vehicle)
            cam.listen(lambda image, n=name: self.process_image(image, n))
            self.sensors.append(cam)
            self.camera_intrinsics[name] = self.get_camera_matrix(self.WIDTH, self.HEIGHT, 120)

    def process_image(self, image, cam_name):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        image_rgb = array[:, :, :3].copy()
        self.image_data[cam_name] = image_rgb

    def get_camera_matrix(self, width, height, fov):
        focal = width / (2.0 * math.tan(fov * math.pi / 360.0))
        K = np.identity(3)
        K[0, 0] = K[1, 1] = focal
        K[0, 2] = width / 2.0
        K[1, 2] = height / 2.0
        return K

    def detect_lines(self, image, cam_name):
        roi = image[300:, :].copy()
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask_white = cv2.inRange(hsv, (0, 0, 220), (180, 30, 255))
        mask_yellow = cv2.inRange(hsv, (20, 120, 120), (35, 255, 255))
        mask = cv2.bitwise_or(mask_white, mask_yellow)
        blur = cv2.GaussianBlur(mask, (5, 5), 0)
        edges = cv2.Canny(blur, 70, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 30, minLineLength=80, maxLineGap=50)
        if lines is not None:
            for x1, y1, x2, y2 in lines[:, 0]:
                cv2.line(roi, (x1, y1), (x2, y2), (0, 255, 0), 2)

        M = cv2.moments(mask)
        if M["m00"] > 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(roi, (cx, cy), 5, (255, 0, 0), -1)

        car_loc = self.vehicle.get_location()
        self.VALID_PARKING_POINT = None
        self.PARKING_SIDE = None

        for spot in self.PARKING_SPOTS:
            spot_loc = spot["spot"].location
            dist = car_loc.distance(spot_loc)
            if dist < 8.0:
                self.VALID_PARKING_POINT = spot["spot"]
                self.PARKING_SIDE = 'left' if spot["id"] == 1 else 'right'
                break

        if self.PARKING_SIDE == cam_name:
            text = "Parking Spot Found"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.7
            color = (0, 255, 255)
            thickness = 2
            text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
            text_x = (roi.shape[1] - text_size[0]) // 2
            text_y = (roi.shape[0] + text_size[1]) // 2
            cv2.putText(roi, text, (text_x, text_y), font, font_scale, color, thickness, cv2.LINE_AA)

        image[300:, :] = roi
        return image

    def get_processed_images(self):
        output = {}
        for name, img in self.image_data.items():
            if img is not None:
                output[name] = self.detect_lines(img.copy(), name)
        return output

    def cleanup(self):
        for s in self.sensors:
            s.stop()
            s.destroy()

    def execute_parking(self, thread=None):
        if not self.VALID_PARKING_POINT or not self.PARKING_SIDE:
            print("[!] No valid parking point detected.")
            return

        path_file = f"C:/Proj/raas_project/world_setup/path{1 if self.PARKING_SIDE == 'left' else 2}.json"
        path_data = self.load_parking_path(path_file)
        if not path_data:
            print("[!] Path not found.")
            return

        self.drive_to_start(path_data[0]['x'], path_data[0]['y'])

        print("[*] Starting parking maneuver...")

        start_ts = path_data[0]['timestamp']
        for step in path_data:
            step["timestamp"] -= start_ts

        start_time = time.time()
        i = 0

        while i < len(path_data):
            if thread and getattr(thread, "stop_requested", False):
                print("[!] Parking cancelled by user.")
                self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
                self.world.tick()
                return


            current_time = time.time() - start_time
            target_time = path_data[i]["timestamp"]

            if current_time >= target_time:
                step = path_data[i]

                control = carla.VehicleControl(
                    throttle=step["throttle"],
                    steer=step["steer"],
                    brake=step["brake"],
                    reverse=step["reverse"],
                    hand_brake=step.get("hand_brake", False)
                )

                if step.get("manual_gear", False):
                    control.manual_gear_shift = True
                    control.gear = step.get("gear", 0)
                else:
                    control.manual_gear_shift = False

                self.vehicle.apply_control(control)
                self.world.tick()
                i += 1
            else:
                self.world.tick()

        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
        self.world.tick()
        print("[*] Parking complete.")

    def drive_to_start(self, start_x, start_y, tolerance=1.0):
        while True:
            loc = self.vehicle.get_location()
            dx = start_x - loc.x
            dy = start_y - loc.y
            if math.sqrt(dx**2 + dy**2) < tolerance:
                break
            self.vehicle.apply_control(carla.VehicleControl(throttle=0.4, steer=0.0))
            time.sleep(0.1)
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=1.0))
        time.sleep(1.0)

    def load_parking_path(self, file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[!] Failed to load path: {e}")
            return None
