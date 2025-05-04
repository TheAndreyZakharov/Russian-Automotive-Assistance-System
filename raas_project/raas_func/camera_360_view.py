import carla
import numpy as np
import pygame
import cv2
import os
from camera_recorder import CameraBufferRecorder

class Camera360:
    def __init__(self, world, vehicle, recorder=None):
        self.world = world
        self.vehicle = vehicle
        self.image_data = {'front': None, 'back': None, 'left': None, 'right': None}
        self.cameras = []
        self.car_img_path = os.path.join(os.path.dirname(__file__), "..", "static", "photos", "car_above.jpg")
        self.recorder = recorder

    def camera_callback(self, image, key):
        array = np.frombuffer(image.raw_data, dtype=np.uint8)
        array = np.reshape(array, (image.height, image.width, 4))
        bgr = array[:, :, :3]
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        surface = pygame.surfarray.make_surface(rgb.swapaxes(0, 1))
        self.image_data[key] = surface
        array_rgb = cv2.cvtColor(pygame.surfarray.array3d(surface).swapaxes(0, 1), cv2.COLOR_RGB2BGR)
        if self.recorder:
            self.recorder.add_frame(key, array_rgb)

    def start(self):
        blueprint_library = self.world.get_blueprint_library()
        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_bp.set_attribute('image_size_x', '320')
        camera_bp.set_attribute('image_size_y', '240')
        camera_bp.set_attribute('fov', '120')

        transforms = {
            'front': carla.Transform(carla.Location(x=2.42, z=0.9), carla.Rotation(yaw=0)),
            'back': carla.Transform(carla.Location(x=-2.47, z=1.15), carla.Rotation(yaw=180)),
            'left': carla.Transform(carla.Location(x=0.75, y=-1.1, z=1.1), carla.Rotation(yaw=-90)),
            'right': carla.Transform(carla.Location(x=0.75, y=1.1, z=1.1), carla.Rotation(yaw=90)),
        }
        #x=2.6, z=1.2, 0
        #x=-2.5, z=1.9, 180
        #x=0.8, y=-1.2, z=1.5, -90
        #x=0.8, y=1.2, z=1.5  90

        for key, tf in transforms.items():
            cam = self.world.spawn_actor(camera_bp, tf, attach_to=self.vehicle)
            cam.listen(lambda img, k=key: self.camera_callback(img, k))
            self.cameras.append(cam)

    def get_surface(self):
        if not all(isinstance(surf, pygame.Surface) for surf in self.image_data.values()):
            return None

        def surf_to_array(surf):
            return pygame.surfarray.array3d(surf).swapaxes(0, 1)

        def perspective_warp(image, src_pts, dst_pts, size):
            M = cv2.getPerspectiveTransform(np.float32(src_pts), np.float32(dst_pts))
            return cv2.warpPerspective(image, M, size)

        def warp_arc(img, arc_offset, horizontal=True, invert=False):
            h, w = img.shape[:2]
            src = [(0, 0), (w, 0), (w, h), (0, h)]
            if horizontal:
                if not invert:
                    dst = [(arc_offset, 0), (w - arc_offset, 0), (w, h), (0, h)]  # сужается сверху
                else:
                    dst = [(0, 0), (w, 0), (w - arc_offset, h), (arc_offset, h)]  # сужается снизу
            else:
                if not invert:
                    dst = [(0, arc_offset), (w, 0), (w, h - arc_offset), (0, h)]  # сужается слева
                else:
                    dst = [(0, 0), (w, arc_offset), (w, h), (0, h - arc_offset)]  # сужается справа
            return perspective_warp(img, src, dst, (w, h))

        # === Машина сверху ===
        car = cv2.cvtColor(cv2.imread(self.car_img_path), cv2.COLOR_BGR2RGB)
        car = cv2.resize(car, (300, 150))
        car = cv2.rotate(car, cv2.ROTATE_90_COUNTERCLOCKWISE)

        canvas = np.zeros((800, 1000, 3), dtype=np.uint8)
        cx, cy = 280, 400

        car_x, car_y = cx - car.shape[1] // 2, cy - car.shape[0] // 2
        canvas[car_y:car_y + car.shape[0], car_x:car_x + car.shape[1]] = car

        # === Камеры ===
        front = cv2.resize(surf_to_array(self.image_data["front"]), (350, 120))
        back = cv2.flip(cv2.resize(surf_to_array(self.image_data["back"]), (350, 120)), -1)
        left = cv2.resize(surf_to_array(self.image_data["left"]), (400, 120))
        right = cv2.resize(surf_to_array(self.image_data["right"]), (400, 120))

        # === Повороты и искажения ===
        front_warped = warp_arc(front, 40, horizontal=True, invert=True)     # сужение снизу
        back_warped = warp_arc(back, 40, horizontal=True, invert=False)      # сужение сверху

        # Боковые — как трапеции
        left_rot = cv2.rotate(left, cv2.ROTATE_90_COUNTERCLOCKWISE)
        right_rot = cv2.rotate(right, cv2.ROTATE_90_CLOCKWISE)

        def warp_trapezoid(img, shrink_side="right"):
            h, w = img.shape[:2]
            src = [(0, 0), (w, 0), (w, h), (0, h)]
            offset = w // 2 
            if shrink_side == "right":
                dst = [(0, 0), (w, offset), (w, h - offset), (0, h)]
            elif shrink_side == "left":
                dst = [(0, offset), (w, 0), (w, h), (0, h - offset)]
            else:
                dst = src
            return perspective_warp(img, src, dst, (w, h))

        left_warped = warp_trapezoid(left_rot, shrink_side="right")
        right_warped = warp_trapezoid(right_rot, shrink_side="left")


        # === Размеры
        fw, fh = front_warped.shape[1], front_warped.shape[0]
        bw, bh = back_warped.shape[1], back_warped.shape[0]
        lh, lw = left_warped.shape[:2]
        rh, rw = right_warped.shape[:2]

        # === Вставка в канвас
        # Передняя камера
        canvas[cy - 150 - fh:cy - 150, cx - fw // 2:cx + fw // 2] = front_warped

        # Задняя камера
        canvas[cy + 150:cy + 150 + bh, cx - bw // 2:cx + bw // 2] = back_warped

        # Левая камера
        x1_l = cx - 150 - lw
        x2_l = cx - 150
        if x1_l < 0:
            diff = abs(x1_l)
            left_warped = left_warped[:, diff:]
            x1_l = 0
        canvas[cy - lh // 2:cy + lh // 2, x1_l:x2_l] = left_warped

        # Правая камера
        x1_r = cx + 150
        x2_r = cx + 150 + rw
        if x2_r > canvas.shape[1]:
            rw = canvas.shape[1] - x1_r
            right_warped = right_warped[:, :rw]
            x2_r = canvas.shape[1]
        canvas[cy - rh // 2:cy + rh // 2, x1_r:x2_r] = right_warped

        return pygame.surfarray.make_surface(canvas.swapaxes(0, 1))

    def stop(self):
        for cam in self.cameras:
            cam.stop()
            cam.destroy()
        self.cameras.clear()
