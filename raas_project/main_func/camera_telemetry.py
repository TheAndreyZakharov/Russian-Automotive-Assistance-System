import carla
import cv2
import numpy as np
import time

def camera_callback(image, data_dict, key):
    array = np.frombuffer(image.raw_data, dtype=np.uint8)
    array = np.reshape(array, (image.height, image.width, 4))
    image_rgb = array[:, :, :3]
    data_dict[key] = image_rgb

def format_gear(gear):
    if gear == 0:
        return 'N'
    elif gear < 0:
        return 'R'
    else:
        return str(gear)

def draw_telemetry(image, vehicle):
    control = vehicle.get_control()
    velocity = vehicle.get_velocity()
    physics = vehicle.get_physics_control()

    # Вычисление скорости в км/ч
    speed = 3.6 * np.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

    telemetry_lines = [
        f"Steering: {control.steer:.2f}",
        f"Throttle: {control.throttle:.2f}",
        f"Brake: {control.brake:.2f}",
        f"Speed: {speed:.1f} km/h",
        f"Gear: {format_gear(vehicle.get_control().gear)}"
    ]

    y0, dy = 30, 30
    for i, line in enumerate(telemetry_lines):
        y = y0 + i * dy
        cv2.putText(image, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (0, 255, 0), 2, cv2.LINE_AA)
    return image

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(5.0)
    world = client.get_world()
    blueprint_library = world.get_blueprint_library()

    vehicles = world.get_actors().filter('vehicle.lincoln.mkz_2020')
    vehicle = min(vehicles, key=lambda v: v.id) if vehicles else None

    if not vehicle:
        print("Lincoln MKZ 2020 not found. Please spawn it first.")
        return

    print(f"[+] Vehicle found: {vehicle.type_id} (ID {vehicle.id})")

    camera_bp = blueprint_library.find('sensor.camera.rgb')
    camera_bp.set_attribute('image_size_x', '640')
    camera_bp.set_attribute('image_size_y', '480')
    camera_bp.set_attribute('fov', '90')

    transform_back = carla.Transform(carla.Location(x=-10, y=0, z=4), carla.Rotation(yaw=-1))
    back_camera = world.spawn_actor(camera_bp, transform_back, attach_to=vehicle)

    image_data = {'back': None}
    back_camera.listen(lambda image: camera_callback(image, image_data, 'back'))

    print("[*] 3rd person camera with full telemetry is active. Press Q to exit.")

    try:
        while True:
            if image_data['back'] is not None:
                frame = image_data['back'].copy()
                frame = draw_telemetry(frame, vehicle)
                cv2.imshow('3rd person with telemetry', frame)

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
