import carla
import cv2
import numpy as np
import time

def camera_callback(image, data_dict, key):
    # Обработка изображения от камеры
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = np.reshape(array, (image.height, image.width, 4))
    image_rgb = array[:, :, :3]  # Убираем альфа-канал
    mirrored = cv2.flip(image_rgb, 1)
    data_dict[key] = mirrored

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    # Получаем все машины
    vehicles = world.get_actors().filter('vehicle.lincoln.mkz_2020')
    vehicle = None

    if vehicles:
        # Выбираем машину с минимальным ID
        vehicle = min(vehicles, key=lambda v: v.id)

    if not vehicle:
        print("Lincoln MKZ 2020 not found. Please spawn it first.")
        return
    print(f"[+] Vehicle found: {vehicle.type_id} (ID {vehicle.id})")

    # Настройки камеры
    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '640')
    camera_bp.set_attribute('image_size_y', '480')
    camera_bp.set_attribute('fov', '90')

    # Точки размещения камер (относительно автомобиля)
    transform_left = carla.Transform(carla.Location(x=0.65, y=-0.9, z=1.1), carla.Rotation(yaw=-150))
    transform_right = carla.Transform(carla.Location(x=0.65, y=0.9, z=1.1), carla.Rotation(yaw=150))
    #x=0.8, y=-1.0, z=1.5, -150
    #x=0.8, y=1.0, z=1.5, =150


    # Спавним камеры и крепим к авто
    left_camera = world.spawn_actor(camera_bp, transform_left, attach_to=vehicle)
    right_camera = world.spawn_actor(camera_bp, transform_right, attach_to=vehicle)

    # Словарь для изображений
    image_data = {'left': None, 'right': None}

    # Подключаем обработку кадров
    left_camera.listen(lambda image: camera_callback(image, image_data, 'left'))
    right_camera.listen(lambda image: camera_callback(image, image_data, 'right'))

    print("[*] Mirror cameras are active. Press Q to exit.")

    try:
        while True:
            if image_data['left'] is not None and image_data['right'] is not None:
                combined = cv2.hconcat([image_data['left'], image_data['right']])
                cv2.imshow('Rear View Mirrors: Left | Right', combined)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.03)

    finally:
        print("[*] Shutting down...")
        left_camera.stop()
        right_camera.stop()
        left_camera.destroy()
        right_camera.destroy()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
