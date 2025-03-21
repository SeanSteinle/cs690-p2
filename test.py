import os
import random
import time
import carla
import logging
from threading import Thread

import numpy as np
import tensorflow as tf
from tqdm import tqdm

from reinforcement_learning import Environment, Agent

MAP_NAME = 'Town03' #our map is 'CS690Project2'
LOAD_MODEL_PATH = 'models/town3_100e/' #the model path should be a directory
SPAWN_POINT_IDX = 250

FPS = 20
EPISODES = 100
AGGREGATE_STATS_EVERY = 10
MODEL_NAME = 'Xception'


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Setup client
    client = carla.Client('127.0.0.1', 3000)
    client.set_timeout(2.0)
    world = client.get_world()
    logging.info('Connected to Carla server.')

    # List available maps
    # available_maps = client.get_available_maps()
    # logging.info(f'Available maps: {available_maps}')

    # Load chosen map
    client.set_timeout(30.0)
    world = client.load_world(MAP_NAME)
    client.set_timeout(2.0)
    logging.info(f'Loaded {MAP_NAME} map.')

    # Call an external Python function via shell
    traffic_thread = Thread(target=os.system, args=('py -3.7 generate_traffic.py -n 125 -p 3000',))
    traffic_thread.start()

    # set seed for repeat results
    random.seed(0)
    np.random.seed(0)
    tf.random.set_seed(0)

    # limit GPU memory usage
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            tf.config.experimental.set_virtual_device_configuration(
                gpus[0],
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=3500)])  # Set memory limit in MB
        except RuntimeError as e:
            print(e)

    if not os.path.exists('models'):
        os.makedirs('models')

    # setup environment and agent to train
    spawn_location = world.get_map().get_spawn_points()[SPAWN_POINT_IDX]
    env = Environment(client, spawn_location, show_camera_preview=False, random_spawns=True)
    agent = Agent()
    agent.model = tf.keras.models.load_model(LOAD_MODEL_PATH)

    for episode in tqdm(range(1, EPISODES+1), ascii=True, unit="episodes"):
        agent.tensorboard.step = episode
        episode_reward = 0
        step = 1
        current_state = env.reset()
        done = False
        episode_start = time.time()

        while True:
            action = np.argmax(agent.get_qs(current_state)) #only take steps according to policy

            new_state, reward, done, _ = env.step(action)
            episode_reward += reward
            agent.update_replay_memory((current_state, action, reward, new_state, done))
            current_state = new_state

            step += 1
            if done:
                break

        for actor in env.actor_list:
            actor.destroy()

    agent.terminate = True
    # traffic_thread.join()
    logging.info('Evaluation complete.')