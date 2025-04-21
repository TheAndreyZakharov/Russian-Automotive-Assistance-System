import carla
import cv2
import numpy as np
import time
import os

def draw_alert_icon(img, icon, position="left"):
    icon_resized = cv2.resize(icon, (130, 130))
    h, w, _ = img.shape
    x, y = (20, 20) if position == "left" else (w - 150, 20)

    if icon.shape[2] == 4:
        alpha = icon_resized[:, :, 3] / 255.0
        for c in range(3):
            img[y:y+130, x:x+130, c] = (
                icon_resized[:, :, c] * alpha + img[y:y+130, x:x+130, c] * (1 - alpha)
            )
    else:
        img[y:y+130, x:x+130] = icon_resized

def camera_callback(image, store, key):
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = np.reshape(array, (image.height, image.width, 4))
    store[key] = array[:, :, :3]

def radar_callback(detections, state_dict, key):
    danger = any(abs(d.depth) < 10 for d in detections)
    state_dict[key] = danger

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()
    bp_lib = world.get_blueprint_library()

    # 🟢 Выбор машины с минимальным ID
    vehicles = list(world.get_actors().filter('vehicle.*'))
    if not vehicles:
        print("❗ Машина не найдена.")
        return
    vehicle = sorted(vehicles, key=lambda v: v.id)[0]
    print(f"[+] Подключено к машине: {vehicle.type_id} (ID {vehicle.id})")

    # 📁 Иконка
    icon_path = os.path.join("..", "static", "photos", "alert_icon.png")
    icon = cv2.imread(icon_path, cv2.IMREAD_UNCHANGED)
    if icon is None:
        print("❗ alert_icon.png не найден.")
        return

    # 🎥 Камеры
    cam_bp = bp_lib.find('sensor.camera.rgb')
    cam_bp.set_attribute('image_size_x', '640')
    cam_bp.set_attribute('image_size_y', '480')
    cam_bp.set_attribute('fov', '90')
    cam_tf_left = carla.Transform(carla.Location(x=0.8, y=-1.0, z=1.5), carla.Rotation(yaw=-150))
    cam_tf_right = carla.Transform(carla.Location(x=0.8, y=1.0, z=1.5), carla.Rotation(yaw=150))

    left_cam = world.spawn_actor(cam_bp, cam_tf_left, attach_to=vehicle)
    right_cam = world.spawn_actor(cam_bp, cam_tf_right, attach_to=vehicle)

    images = {'left': None, 'right': None}
    left_cam.listen(lambda img: camera_callback(img, images, 'left'))
    right_cam.listen(lambda img: camera_callback(img, images, 'right'))

    # 📡 Радары
    radar_bp = bp_lib.find('sensor.other.radar')
    radar_bp.set_attribute('horizontal_fov', '8')
    radar_bp.set_attribute('vertical_fov', '5')
    radar_bp.set_attribute('range', '7')

    radar_tf_left = carla.Transform(carla.Location(x=-0.5, y=-1.0, z=1), carla.Rotation(yaw=-150))
    radar_tf_right = carla.Transform(carla.Location(x=-0.5, y=1.0, z=1), carla.Rotation(yaw=150))

    radar_states = {'left': False, 'right': False}
    radar_left = world.spawn_actor(radar_bp, radar_tf_left, attach_to=vehicle)
    radar_right = world.spawn_actor(radar_bp, radar_tf_right, attach_to=vehicle)
    radar_left.listen(lambda data: radar_callback(data, radar_states, 'left'))
    radar_right.listen(lambda data: radar_callback(data, radar_states, 'right'))

    print("[*] Нажми Q для выхода.")

    try:
        while True:
            if images['left'] is not None and images['right'] is not None:
                left_img = images['left'].copy()
                right_img = images['right'].copy()

                if radar_states['left']:
                    draw_alert_icon(left_img, icon, position='left')
                if radar_states['right']:
                    draw_alert_icon(right_img, icon, position='right')

                combined = cv2.hconcat([left_img, right_img])
                cv2.imshow("Rear View Mirrors (Alert): Left | Right", combined)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.03)

    finally:
        print("[*] Завершение...")
        left_cam.stop(), right_cam.stop()
        radar_left.stop(), radar_right.stop()
        left_cam.destroy(), right_cam.destroy()
        radar_left.destroy(), radar_right.destroy()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
