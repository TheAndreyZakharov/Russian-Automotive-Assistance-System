import carla
import cv2
import numpy as np
import time

def camera_callback(image, data_dict, key):
    # Обработка изображения от камеры
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = np.reshape(array, (image.height, image.width, 4))
    image_rgb = array[:, :, :3]  # Убираем альфа-канал
    data_dict[key] = image_rgb

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

    # Точка размещения камеры (относительно автомобиля)
    transform_back = carla.Transform(carla.Location(x=-10, y=0, z=4), carla.Rotation(yaw=-1))

    # Спавним камеру и крепим к авто
    back_camera = world.spawn_actor(camera_bp, transform_back, attach_to=vehicle)

    # Словарь для изображений
    image_data = {'back': None}

    # Подключаем обработку кадров
    back_camera.listen(lambda image: camera_callback(image, image_data, 'back'))

    print("[*] 3rd person camera is active. Press Q to exit.")

    try:
        while True:
            if image_data['back'] is not None:
                combined = cv2.hconcat([image_data['back']])
                cv2.imshow('3rd person', combined)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.03)

    finally:
        print("[*] Shutting down...")
        back_camera.stop()
        back_camera.destroy()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
