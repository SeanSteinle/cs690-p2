import math
import os
import random
import carla
import logging
import time
import cv2
import numpy as np
from collections import deque

import tensorflow as tf

class Environment:
    STEER_AMT = 1.0
    IMAGE_WIDTH = 800
    IMAGE_HEIGHT = 600
    EPISODE_TIME = 10.0
    front_image = None

    def __init__(self, client, staring_location, show_camera_preview=False):
        self.client = client
        self.client.set_timeout(2.0)
        self.world = self.client.get_world()
        self.blueprint_library = self.world.get_blueprint_library()
        self.charger_bp = self.blueprint_library.filter('charger_police')[0]
        self.transform = staring_location # always start at same spot
        self.show_preview = show_camera_preview
        logging.info('Connected to Carla server.')

    def create_camera(self):
        cam_bp = self.blueprint_library.find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', f'{self.IMAGE_WIDTH}')
        cam_bp.set_attribute('image_size_y', f'{self.IMAGE_HEIGHT}')
        cam_bp.set_attribute('fov', '110')
        # transform relative to host (will need to generalize input)
        cam = self.world.spawn_actor(cam_bp, carla.Transform(carla.Location(x=1.5, z=2.4)), attach_to=self.vehicle)
        cam.listen(self.image_listener)
        self.actor_list.append(cam)

    def image_listener(self, image):
        img = np.array(image.raw_data).reshape((image.height, image.width, 4)) # 4 channels: RGB
        img = img[:, :, :3] # remove alpha channel
        if self.show_preview:
            cv2.imshow('image', img) # displays images as they come in
            cv2.waitKey(1)
        self.front_image = img

    def reset(self):
        # reset environment
        self.collision_history = []
        self.actor_list = []

        # reset vehicle
        try:
            self.vehicle = self.world.spawn_actor(self.charger_bp, self.transform)
        except: # if it tries to spawn into another vehicle
            time.sleep(1)
            return self.reset()
        self.actor_list.append(self.vehicle)

        # add data sensor(s)
        self.create_camera()

        # add collision sensor
        colsensor = self.blueprint_library.find('sensor.other.collision')
        self.colsensor = self.world.spawn_actor(colsensor, carla.Transform(), attach_to=self.vehicle)
        self.colsensor.listen(lambda event: self.collision_history.append(event))
        self.actor_list.append(self.colsensor)

        # wait until we can control spawned in vehicle
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, brake=0.0))
        while self.front_image is None:
            time.sleep(0.01)

        self.episode_start = time.time()
        self.vehicle.apply_control(carla.VehicleControl(throttle=0.0, steer=0.0))

        return self.front_image



    def step(self, action):
        # perform action
        if action == 0: # turn left
            self.vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=-self.STEER_AMT))
        elif action == 1: # go straight
            self.vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=0.0))
        elif action == 2: # turn right
            self.vehicle.apply_control(carla.VehicleControl(throttle=1.0, steer=self.STEER_AMT))

        # get data about vehicle
        vel = self.vehicle.get_velocity()
        kph = int(3.6 * math.sqrt(vel.x**2 + vel.y**2 + vel.z**2))

        # calculate reward and done status
        if len(self.collision_history) > 0:
            done = True
            reward = -50
        elif kph < 5: # move it!
            done = False
            reward = -1
        elif kph < 50: # at least you are moving
            done = False
            reward = 1
        else: # we are rewarding for high speed
            done = False
            reward = 10

        if self.episode_start + self.EPISODE_TIME < time.time():
            done = True

        return self.front_image, reward, done, None

class Agent:
    REPLAY_MEMORY_SIZE = 5_000
    MIN_REPLAY_MEMORY_SIZE = 1_000 # start training after this many steps
    MINIBATCH_SIZE = 16 # number of experiences we want to sample from replay memory
    PREDICTION_BATCH_SIZE = 1
    TRAINING_BATCH_SIZE = MINIBATCH_SIZE // 4
    UPDATE_TARGET_EVERY = 5 # how often to update target model

    DISCOUNT = 0.99 # determines importance of future rewards

    def __init__(self):
        self.model = self.create_model()
        self.target_model = self.create_model()
        self.target_model.set_weights(self.model.get_weights())

        self.replay_memory = deque(maxlen=self.REPLAY_MEMORY_SIZE)

        self.tensorboard = ModifiedTensorBoard(log_dir=f'logs/Xception-{int(time.time())}')
        self.target_update_counter = 0
        # self.graph = tf.compat.v1.get_default_graph()

        self.terminate = False
        self.last_logged_episode = 0
        self.training_initialized = False

    def create_model(self):
        # create a convolutional neural network using Xception architecture (predict categories based on image data (matrix))
        base_model = tf.keras.applications.Xception(weights=None, include_top=False, input_shape=(Environment.IMAGE_HEIGHT, Environment.IMAGE_WIDTH, 3))

        x = base_model.output
        x = tf.keras.layers.GlobalAveragePooling2D()(x)

        # predict 1 of three options (left, straight, right)
        predictions = tf.keras.layers.Dense(3, activation='linear')(x)
        model = tf.keras.Model(inputs=base_model.input, outputs=predictions)
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mse', metrics=['accuracy'])

        return model

    def update_replay_memory(self, transition):
        # transition is a tuple of (current_state, action, reward, new_state, done)
        self.replay_memory.append(transition)

    def train(self):
        if len(self.replay_memory) < self.MIN_REPLAY_MEMORY_SIZE:
            return

        minibatch = random.sample(self.replay_memory, self.MINIBATCH_SIZE)

        current_states = np.array([transition[0] for transition in minibatch]) / 255
        current_qs_list = self.model.predict(current_states, self.PREDICTION_BATCH_SIZE)

        new_current_states = np.array([transition[3] for transition in minibatch]) / 255
        future_qs_list = self.target_model.predict(new_current_states, self.PREDICTION_BATCH_SIZE)

        X = []
        y = []

        for index, (current_state, action, reward, _, done) in enumerate(minibatch):
            if not done:
                max_future_q = np.max(future_qs_list[index])
                new_q = reward + self.DISCOUNT * max_future_q
            else:
                new_q = reward

            current_qs = current_qs_list[index]
            current_qs[action] = new_q

            X.append(current_state)
            y.append(current_qs)

        log_this_step = False
        if self.tensorboard.step > self.last_logged_episode:
            self.last_logged_episode = self.tensorboard.step
            log_this_step = True

        self.model.fit(np.array(X) / 255, np.array(y), batch_size=self.TRAINING_BATCH_SIZE, verbose=0, shuffle=False, callbacks=[self.tensorboard] if log_this_step else None)

        if log_this_step:
            self.target_update_counter += 1

        if self.target_update_counter > self.UPDATE_TARGET_EVERY:
            self.target_model.set_weights(self.model.get_weights())
            self.target_update_counter = 0

    def get_qs(self, state):
        return self.model.predict(np.array(state).reshape(-1, *state.shape) / 255)[0]

    def train_in_loop(self):
        # intial fit to create model
        X = np.random.uniform(size=(1, Environment.IMAGE_HEIGHT, Environment.IMAGE_WIDTH, 3)).astype(np.float32)
        y = np.random.uniform(size=(1, 3)).astype(np.float32)
        self.model.fit(X, y, verbose=False, batch_size=1)

        self.training_initialized = True

        while True:
            if self.terminate:
                return
            self.train()
            time.sleep(0.01)

class ModifiedTensorBoard(tf.keras.callbacks.TensorBoard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.step = 1
        self.writer = tf.summary.create_file_writer(self.log_dir)
        self._log_write_dir = self.log_dir

    def set_model(self, model):
        self.model = model

        self._train_dir = os.path.join(self._log_write_dir, 'train')
        self._train_step = self.model._train_counter

        self._val_dir = os.path.join(self._log_write_dir, 'validation')
        self._val_step = self.model._test_counter

        self._should_write_train_graph = False

    def on_epoch_end(self, epoch, logs=None):
        self.update_stats(**logs)

    def on_batch_end(self, batch, logs=None):
        pass

    def on_train_end(self, _):
        pass

    def update_stats(self, **stats):
        with self.writer.as_default():
            for key, value in stats.items():
                tf.summary.scalar(key, value, step = self.step)
                self.writer.flush()
