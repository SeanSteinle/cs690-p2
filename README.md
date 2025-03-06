# Project II: Training An Autonoumous Vehicle

## Installations

### Matlab RoadRunner (Optional)

This service is used to design the map in which we'll train our vehicle. You can access it by:
1. Accessing your Matlab/Mathworks account at your GMU email.
2. Go through 'My Account' > 'Licenses' > 'RoadRunner / Overview' to download and run the installer.
3. After the install finishes, you need to activate your license which you can do under 'Install and Activate'. Then you're good to go!

### VPN Installation

1. Follow Canvas thread.

## Working with RoadRunner

Basic map editing tutorials can be found on [MathWorks](https://www.mathworks.com/videos/series/getting-started-with-roadrunner.html).

[This](https://carla.readthedocs.io/en/latest/tuto_M_generate_map/) is the documentation on how to transfer your scene (map) from RoadRunner into Carla.

## Training a Vehicle

[Documentation](https://carla.readthedocs.io/en/0.9.15/ref_sensors/#rgb-camera) on sensors.

First start Carla.

Next create some traffic.

```bash
py -3.7 generate_traffic.py -n 80
```

Start training.

```bash
py -3.7 train.py
```

You can view the model statistic by running the following:

```bash
tensorboard --logdir logs
```
