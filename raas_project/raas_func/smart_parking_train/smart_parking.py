import carla
import torch
import numpy as np
import cv2
import pygame
import time
from torchvision import transforms
from smart_parking_train.train_model import MultiCamNet

# === Константы ===
IMG_WIDTH, IMG_HEIGHT = 320, 240
MODEL_PATH = 'C:/Proj/raas_project/raas_func/smart_parking_train/models/best_model.pth'
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

SENSOR_TRANSFORMS = {
    'front': carla.Transform(carla.Location(x=2.42, z=0.9), carla.Rotation(yaw=0)),
    'back': carla.Transform(carla.Location(x=-2.47, z=1.15), carla.Rotation(yaw=180)),
    'left': carla.Transform(carla.Location(x=0.75, y=-1.1, z=1.1), carla.Rotation(yaw=-90)),
    'right': carla.Transform(carla.Location(x=0.75, y=1.1, z=1.1), carla.Rotation(yaw=90))
}

transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((IMG_HEIGHT, IMG_WIDTH)),
    transforms.ToTensor(),
])

normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                 std=[0.229, 0.224, 0.225])


class SmartParking:
    def __init__(self):
        self.client = carla.Client('localhost', 2000)
        self.client.set_timeout(5.0)
        self.world = self.client.get_world()
        self.vehicle = self._get_vehicle()
        self.bp_lib = self.world.get_blueprint_library()

        self.image_data = {k: None for k in SENSOR_TRANSFORMS}
        self.radar_data = {k: 8.0 for k in SENSOR_TRANSFORMS}

        self.model = MultiCamNet().to(DEVICE)
        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
        self.model.eval()

        pygame.init()
        self.display = pygame.display.set_mode((IMG_WIDTH * 2, IMG_HEIGHT * 2))
        pygame.display.set_caption("Smart Parking")

        self.sensors = []

    def _get_vehicle(self):
        vehicles = self.world.get_actors().filter('vehicle.*')
        if not vehicles:
            raise RuntimeError("[!] No vehicle found")
        return vehicles[0]

    def _camera_callback(self, image, key):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))[:, :, :3]
        self.image_data[key] = array

    def _radar_callback(self, radar_data, key):
        depths = [d.depth for d in radar_data]
        self.radar_data[key] = min(depths) if depths else 8.0

    def setup_sensors(self):
        cam_bp = self.bp_lib.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', str(IMG_WIDTH))
        cam_bp.set_attribute('image_size_y', str(IMG_HEIGHT))
        cam_bp.set_attribute('fov', '90')

        radar_bp = self.bp_lib.find('sensor.other.radar')
        radar_bp.set_attribute('range', '8')

        def make_cam_callback(k):
            return lambda image: self._camera_callback(image, k)

        def make_radar_callback(k):
            return lambda data: self._radar_callback(data, k)

        for key, tf in SENSOR_TRANSFORMS.items():
            cam = self.world.spawn_actor(cam_bp, tf, attach_to=self.vehicle)
            cam.listen(make_cam_callback(key))
            radar = self.world.spawn_actor(radar_bp, tf, attach_to=self.vehicle)
            radar.listen(make_radar_callback(key))
            self.sensors.extend([cam, radar])

    def predict_control(self):
        if not all(img is not None for img in self.image_data.values()):
            return None

        imgs = [normalize(transform(self.image_data[k])).to(DEVICE) for k in ['front', 'back', 'left', 'right']]
        img_tensor = torch.cat(imgs, dim=0).unsqueeze(0)
        radar_tensor = torch.tensor([
            self.radar_data['front'],
            self.radar_data['back'],
            self.radar_data['left'],
            self.radar_data['right']
        ], dtype=torch.float32).unsqueeze(0).to(DEVICE)

        with torch.no_grad():
            output = self.model(img_tensor, radar_tensor).cpu().squeeze().numpy()

        return output  # throttle, steer, brake

    def run(self):
        print("[*] Press P to activate autopark | ESC to exit")
        autopark = False

        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        raise KeyboardInterrupt
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            raise KeyboardInterrupt
                        elif event.key == pygame.K_p:
                            autopark = not autopark
                            print("[+] Autopark:", "ON" if autopark else "OFF")

                surface = pygame.display.get_surface()
                for i, key in enumerate(['front', 'back', 'left', 'right']):
                    if self.image_data[key] is not None:
                        img = cv2.cvtColor(self.image_data[key], cv2.COLOR_BGR2RGB)
                        surf = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
                        x = (i % 2) * IMG_WIDTH
                        y = (i // 2) * IMG_HEIGHT
                        surface.blit(surf, (x, y))

                pygame.display.update()

                if autopark:
                    output = self.predict_control()
                    if output is not None:
                        throttle, steer, brake = output

                        # === Усиление поведения ===
                        throttle *= 1.3
                        steer *= 1.5
                        brake *= 1.2

                        # === Минимальный порог газа ===
                        if throttle < 0.2 and brake < 0.05:
                            throttle = 0.2

                        throttle = float(np.clip(throttle, 0.0, 1.0))
                        steer = float(np.clip(steer, -1.0, 1.0))
                        brake = float(np.clip(brake, 0.0, 1.0))

                        control = carla.VehicleControl(
                            throttle=throttle,
                            steer=steer,
                            brake=brake,
                            manual_gear_shift=False
                        )
                        self.vehicle.apply_control(control)

                time.sleep(0.05)

        except KeyboardInterrupt:
            print("\n[*] Shutting down")
        finally:
            for sensor in self.sensors:
                sensor.stop()
                sensor.destroy()
            pygame.quit()


if __name__ == '__main__':
    app = SmartParking()
    app.setup_sensors()
    app.run()
