import carla
import pygame
import time
import signal
import os

# === Globals ===
running = True
OUTPUT_FILE = "vehicle_coords.txt"

# === Signal Handling ===
def signal_handler(sig, frame):
    global running
    print("\n[!] Exiting...")
    running = False

# === Main ===
def main():
    global running
    signal.signal(signal.SIGINT, signal_handler)
    pygame.init()
    pygame.display.set_caption("Get Coordinates of Existing Vehicle")
    pygame.display.set_mode((400, 200))

    client = carla.Client("localhost", 2000)
    client.set_timeout(5.0)
    world = client.get_world()

    vehicles = world.get_actors().filter("vehicle.*")
    if not vehicles:
        print("[-] No vehicle found in the scene.")
        return

    vehicle = vehicles[0]
    print(f"[+] Connected to vehicle: {vehicle.type_id}")
    print("[i] Use 'C' to save current location to vehicle_coords.txt")

    clock = pygame.time.Clock()

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_c]:
                location = vehicle.get_location()
                rotation = vehicle.get_transform().rotation

                line = (
                    f"x={location.x:.2f}, y={location.y:.2f}, z={location.z:.2f}, "
                    f"yaw={rotation.yaw:.2f}\n"
                )

                with open(OUTPUT_FILE, "a") as f:
                    f.write(line)

                print(f"[+] Saved: {line.strip()}")
                time.sleep(0.3)  # prevent repeat on long press

            clock.tick(30)

    finally:
        print("[*] Exiting and closing pygame.")
        pygame.quit()

if __name__ == "__main__":
    main()
