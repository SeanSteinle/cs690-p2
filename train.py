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

MAP_NAME = 'Town03'
SPAWN_POINT_IDX = 250

FPS = 20
EPISODES = 100
AGGREGATE_STATS_EVERY = 10
MODEL_NAME = 'Xception'

EPSILON = 1 # how much to favor exploration over exploitation
EPSILON_DECAY = 0.95 # decrease epsilon over time
MIN_EPSILON = 0.01


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    # Setup client
    client = carla.Client('127.0.0.1', 2000)
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
                [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=8192)])  # Set memory limit in MB
        except RuntimeError as e:
            print(e)

    if not os.path.exists('models'):
        os.makedirs('models')

    # setup environment and agent to train
    spawn_location = world.get_map().get_spawn_points()[SPAWN_POINT_IDX]
    env = Environment(client, spawn_location, show_camera_preview=False)
    agent = Agent()
    epsiode_rewards = [-200]
    epsilon = EPSILON

    # start training thread
    training_thread = Thread(target=agent.train_in_loop, daemon=True)
    training_thread.start()

    # wait and start prediction thread
    while not agent.training_initialized:
        time.sleep(0.01)
    agent.get_qs(np.ones((env.IMAGE_HEIGHT, env.IMAGE_WIDTH, 3))) # initial dummy state

    for episode in tqdm(range(1, EPISODES+1), ascii=True, unit="episodes"):
        agent.tensorboard.step = episode
        episode_reward = 0
        step = 1
        current_state = env.reset()
        done = False
        episode_start = time.time()

        while True:
            if np.random.random() > epsilon: # take random actions more when epsilon is high
                action = np.argmax(agent.get_qs(current_state))
            else:
                action = np.random.randint(0, 3)
                time.sleep(1/FPS)

            new_state, reward, done, _ = env.step(action)
            episode_reward += reward
            agent.update_replay_memory((current_state, action, reward, new_state, done))
            current_state = new_state

            step += 1
            if done:
                break

        for actor in env.actor_list:
            actor.destroy()

        epsiode_rewards.append(episode_reward)
        if not episode % AGGREGATE_STATS_EVERY or episode == 1:
            average_reward = sum(epsiode_rewards[-AGGREGATE_STATS_EVERY:])/len(epsiode_rewards[-AGGREGATE_STATS_EVERY:])
            min_reward = min(epsiode_rewards[-AGGREGATE_STATS_EVERY:])
            max_reward = max(epsiode_rewards[-AGGREGATE_STATS_EVERY:])
            agent.tensorboard.update_stats(reward_avg=average_reward, reward_min=min_reward, reward_max=max_reward, epsilon=epsilon)

            if min_reward >= 200:
                agent.model.save(f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')

        if epsilon > MIN_EPSILON:
            epsilon *= EPSILON_DECAY
            epsilon = max(MIN_EPSILON, epsilon)

    agent.terminate = True
    training_thread.join()
    logging.info('Training complete.')
    agent.model.save(f'models/{MODEL_NAME}__{max_reward:_>7.2f}max_{average_reward:_>7.2f}avg_{min_reward:_>7.2f}min__{int(time.time())}.model')
