import numpy as np
import cv2
import logging

import carla

class Camera:
    def __init__(self, host_actor, world, width=800, height=600):
        self.world = world
        self.width = width
        self.height = height
        self.host_actor = host_actor

        cam_bp = world.get_blueprint_library().find('sensor.camera.rgb')
        cam_bp.set_attribute('image_size_x', f'{width}')
        cam_bp.set_attribute('image_size_y', f'{height}')
        cam_bp.set_attribute('fov', '110')
        # transform relative to host (will need to generalize input)
        cam = world.spawn_actor(cam_bp, carla.Transform(carla.Location(x=1.5, z=2.4)), attach_to=host_actor)
        cam.listen(self.listener)

        self.cam = cam

    def listener(self, image):
        img = np.array(image.raw_data).reshape((image.height, image.width, 4)) # 4 channels: RGB
        img = img[:, :, :3] # remove alpha channel
        cv2.imshow('image', img) # displays images as they come in
        cv2.waitKey(1)
