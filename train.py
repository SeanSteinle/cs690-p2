import carla
import logging
import time

MAP_NAME = 'Town03'
SPAWN_POINT_IDX = 250

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

        blueprint_library = world.get_blueprint_library()
        charger_blueprint = blueprint_library.filter('charger_police')[0]

        spawn_points = world.get_map().get_spawn_points()
        logging.info(f'Found {len(spawn_points)} spawn points.')


        spawn_point = spawn_points[SPAWN_POINT_IDX]
        logging.info(f'Spawning {charger_blueprint.id} at {spawn_point}')
        charger = world.spawn_actor(charger_blueprint, spawn_point)
        actor_list.append(charger)

        charger.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
        time.sleep(5)
    finally:
        logging.info('Cleaning up actors.')
        for actor in actor_list:
            actor.destroy()
        logging.info('All actors destroyed')
