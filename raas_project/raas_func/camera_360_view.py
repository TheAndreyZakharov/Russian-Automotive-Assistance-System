import carla
import numpy as np
import pygame
import cv2

class Camera360:
    def __init__(self, world, vehicle):
        self.world = world
        self.vehicle = vehicle
        self.image_data = {'front': None, 'back': None, 'left': None, 'right': None}
        self.cameras = []

    def camera_callback(self, image, key):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        bgr = array[:, :, :3]
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
        self.image_data[key] = surface

    def start(self):
        blueprint_library = self.world.get_blueprint_library()
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '320')
        camera_bp.set_attribute('image_size_y', '240')
        camera_bp.set_attribute('fov', '120')

        transforms = {
            'front': carla.Transform(carla.Location(x=2.6, z=1.2), carla.Rotation(yaw=0)),
            'back': carla.Transform(carla.Location(x=-2.5, z=1.9), carla.Rotation(yaw=180)),
            'left': carla.Transform(carla.Location(x=0.8, y=-1.2, z=1.5), carla.Rotation(yaw=-90)),
            'right': carla.Transform(carla.Location(x=0.8, y=1.2, z=1.5), carla.Rotation(yaw=90)),
        }

        for key, tf in transforms.items():
            cam = self.world.spawn_actor(camera_bp, tf, attach_to=self.vehicle)
            cam.listen(lambda img, k=key: self.camera_callback(img, k))  # 🔸 фикс захвата key
            self.cameras.append(cam)

    def get_surface(self):
        if all(self.image_data.values()):
            top = pygame.Surface((640, 240))
            bottom = pygame.Surface((640, 240))
            top.blit(self.image_data['left'], (0, 0))
            top.blit(self.image_data['right'], (320, 0))
            bottom.blit(self.image_data['front'], (0, 0))
            bottom.blit(self.image_data['back'], (320, 0))
            combined = pygame.Surface((640, 480))
            combined.blit(top, (0, 0))
            combined.blit(bottom, (0, 240))
            return combined
        return None

    def stop(self):
        for cam in self.cameras:
            cam.stop()
            cam.destroy()
        self.cameras.clear()
