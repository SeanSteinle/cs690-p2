import carla
import logging
import time

from camera import Camera

MAP_NAME = 'Town03'
SPAWN_POINT_IDX = 250
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600

def spawn_actor_by_point(world, actor_name, spawn_point_idx):
    blueprint_library = world.get_blueprint_library()
    charger_blueprint = blueprint_library.filter(actor_name)[0]
    spawn_points = world.get_map().get_spawn_points()
    logging.debug(f'Found {len(spawn_points)} spawn points.')
    spawn_point = spawn_points[spawn_point_idx]
    logging.info(f'Spawning {charger_blueprint.id} at {spawn_point}')
    return world.spawn_actor(charger_blueprint, spawn_point)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    actor_list = []
    try:
        # Setup client
        client = carla.Client('127.0.0.1', 2000)
        client.set_timeout(2.0)
        world = client.get_world()
        logging.info('Connected to Carla server.')

        # List available maps
        # available_maps = client.get_available_maps()
        # logging.info(f'Available maps: {available_maps}')

        # Load chosen map
        # client.set_timeout(30.0)
        # world = client.load_world(MAP_NAME)
        # client.set_timeout(2.0)
        # logging.info(f'Loaded {MAP_NAME} map.')

        # Spawn vehicle]
        charger = spawn_actor_by_point(world, 'charger_police', SPAWN_POINT_IDX)
        actor_list.append(charger)

        # Spawn vehicle sensor(s)
        logging.info('Spawning an RGB camera sensor on the charger')
        cam = Camera(charger, world, IMAGE_WIDTH, IMAGE_HEIGHT).cam
        actor_list.append(cam)

        charger.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
        time.sleep(5)
    finally:
        logging.info('Cleaning up actors.')
        for actor in actor_list:
            actor.destroy()
        logging.info('All actors destroyed')
