import carla
import cv2
import numpy as np
import pygame
import time
import csv
import os

SENSOR_TRANSFORMS = {
    'front': carla.Transform(carla.Location(x=2.42, z=0.9), carla.Rotation(yaw=0)),
    'back': carla.Transform(carla.Location(x=-2.47, z=1.15), carla.Rotation(yaw=180)),
    'left': carla.Transform(carla.Location(x=0.75, y=-1.1, z=1.1), carla.Rotation(yaw=-90)),
    'right': carla.Transform(carla.Location(x=0.75, y=1.1, z=1.1), carla.Rotation(yaw=90))
}

SAVE_EVERY_N_FRAMES = 5

class DataCollector:
    def __init__(self):
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(5.0)
        self.world = self.client.get_world()
        self.vehicle = self._get_vehicle()
        self.bp_lib = self.world.get_blueprint_library()

        self.image_data = {k: None for k in SENSOR_TRANSFORMS}
        self.radar_data = {k: [] for k in SENSOR_TRANSFORMS}
        self.camera_sensors = {}
        self.radar_sensors = {}
        self.frame_id = 0

        os.makedirs('dataset/images', exist_ok=True)
        self.csv_file = open('dataset/log.csv', 'a', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow([
            'frame', 'throttle', 'steer', 'brake', 'speed',
            'front_dist', 'back_dist', 'left_dist', 'right_dist'
        ])

        pygame.init()
        self.display = pygame.display.set_mode((640, 480))
        pygame.display.set_caption("Recording...")

    def _get_vehicle(self):
        vehicles = self.world.get_actors().filter('vehicle.*')
        if not vehicles:
            raise RuntimeError("[!] No vehicles found.")
        vehicle = min(vehicles, key=lambda v: v.id)
        print(f"[+] Connected to vehicle: {vehicle.type_id}")
        return vehicle

    def _camera_callback(self, image, key):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        bgr = array[:, :, :3]
        self.image_data[key] = bgr

    def _radar_callback(self, radar_data, key):
        self.radar_data[key] = [d.depth for d in radar_data]

    def setup_sensors(self):
        cam_bp = self.bp_lib.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', '320')
        cam_bp.set_attribute('image_size_y', '240')
        cam_bp.set_attribute('fov', '90')

        radar_bp = self.bp_lib.find('sensor.other.radar')
        radar_bp.set_attribute('horizontal_fov', '35')
        radar_bp.set_attribute('vertical_fov', '5')
        radar_bp.set_attribute('range', '8')

        for key, tf in SENSOR_TRANSFORMS.items():
            cam = self.world.spawn_actor(cam_bp, tf, attach_to=self.vehicle)
            cam.listen(lambda img, k=key: self._camera_callback(img, k))
            self.camera_sensors[key] = cam

            radar = self.world.spawn_actor(radar_bp, tf, attach_to=self.vehicle)
            radar.listen(lambda data, k=key: self._radar_callback(data, k))
            self.radar_sensors[key] = radar

    def record_loop(self):
        try:
            print("[*] Start driving. Press ESC to stop.")
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        raise KeyboardInterrupt

                self.frame_id += 1
                if self.frame_id % SAVE_EVERY_N_FRAMES != 0:
                    continue

                if not all(img is not None for img in self.image_data.values()):
                    continue

                control = self.vehicle.get_control()
                velocity = self.vehicle.get_velocity()
                speed = np.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

                dist_data = {
                    k: (min(self.radar_data[k]) if self.radar_data[k] else 8.0)
                    for k in SENSOR_TRANSFORMS
                }

                for key, img in self.image_data.items():
                    fname = f'dataset/images/{key}_{self.frame_id:05d}.png'
                    cv2.imwrite(fname, img)

                self.csv_writer.writerow([
                    self.frame_id,
                    control.throttle,
                    control.steer,
                    control.brake,
                    speed,
                    dist_data['front'],
                    dist_data['back'],
                    dist_data['left'],
                    dist_data['right']
                ])

                pygame.display.get_surface().fill((0, 0, 0))
                font = pygame.font.SysFont(None, 36)
                text = font.render(f"Recording Frame {self.frame_id}", True, (255, 255, 255))
                pygame.display.get_surface().blit(text, (10, 10))
                pygame.display.update()
                time.sleep(0.1)

        except KeyboardInterrupt:
            print("\n[*] Recording stopped.")
        finally:
            self.cleanup()

    def cleanup(self):
        self.csv_file.close()
        for cam in self.camera_sensors.values():
            cam.stop()
            cam.destroy()
        for radar in self.radar_sensors.values():
            radar.stop()
            radar.destroy()
        pygame.quit()

if __name__ == '__main__':
    recorder = DataCollector()
    recorder.setup_sensors()
    recorder.record_loop()
