# Project II: Training An Autonoumous Vehicle

## Training a Vehicle

[Documentation](https://carla.readthedocs.io/en/0.9.15/ref_sensors/#rgb-camera) on sensors.

First start the Carla server. You can do this by running the `carla_server` command from a Git Bash terminal.
    - This doesn't work anymore. What did Joe change?

Then you can start training! It should also load the map and generate traffic (included the example in the directory)

```bash
py -3.7 train.py
```

You can view the model statistic by running the `tboard` alias in Git Bash or the following:

```bash
tensorboard --logdir logs
```

The code is basically straight from the linked video tutorial. There is some tweaks to parameters and rewards. It also currently starts in the same location every time.

## Testing a Vehicle

After you've trained a vehicle, you can load it with `py -3.7 test.py`. It's very similar to the training script but it does not take random actions and doesn't bother saving many statistics. You'll need to set the model path of your model and the map of choice at the top of the file (like the training script).

## Next Steps

### Training / Testing

Turnover:
- show how to run
- show training, testing scripts
- show tensorboard (to both!)
- show map1, how to toggle maps

Todo:
- Train a long policy (~5,000 steps or until convergence!)
- Test on 3-4 different maps (Carla maps like town1, town2, etc. then our map)
- Capture images of our policy training, testing. Jot down basic behavior for shahriar to elaborate on in report.

### Paper Writeup

For our report I think we should write 3 main sections:
- environment/infrastructure setup
    - we spent a lot of time struggling on this so i'd go into detail describing what we've tried.
        - setup on IT system vs. setup on Joe's
        - building from source vs. building from binary package.
        - struggles with remote desktops
    - describe we were able to import maps but they kind of break (could put this in another section if you want)
    - describe our final development setup
- model design and training
    - here we describe the methodology of our model. hint -- it's very simple!
        - you should look at reinforcement_learning.py and train.py for this. describe epsilon greedy strategy, what observations we use, what the gym/environment looks like, etc.
    - we took almost all of it from the youtube series, i would mention it explicitly and mention we modified a few things:
        - added loading maps
        - add saving / loading models for rollouts/eval on different maps
    - can describe some of the things we'd improve
        - better observations? or training on simple map first, then larger ones (kind of like curriculum learning), etc.
- model performance and analysis
    - summarize our performance quantitatively (via tensorboard stats)
        - how did reward evolve, how to loss evolve, did we ever converge or should we have kept training, etc
    - summarize our performance qualitatively (with the help of Sanjay's notes during training / testing)
        - does the car know how to drive? does it learning an interpretable policy (like 'drive in circles')? if so, why do you think it did this (hint it was probably our reward structure!)


## Appendix

### Importing a Map

[This](https://carla.readthedocs.io/en/0.9.15/core_map/#custom-maps) is a good place to start when adding a new map. You will quickly notice that the instructions for loading a map depend on whether or not you built Carla from source or installed it from a binary. If you built Carla from source, you have three options:
1. Use the automatic make import process. Guide [here](https://carla.readthedocs.io/en/0.9.15/tuto_M_add_map_source/), comes as the recommended technique.
2. Use the Roadrunner plugin. Guide [here](https://carla.readthedocs.io/en/0.9.15/tuto_M_add_map_alternative/#roadrunner-plugin-import).
3. Manual import. Guide [here](https://carla.readthedocs.io/en/0.9.15/tuto_M_add_map_alternative/#manual-import).

Unfortunately, if y## Installations

### Matlab RoadRunner (Optional)

This service is used to design the map in which we'll train our vehicle. You can access it by:
1. Accessing your Matlab/Mathworks account at your GMU email.
2. Go through 'My Account' > 'Licenses' > 'RoadRunner / Overview' to download and run the installer.
3. After the install finishes, you need to activate your license which you can do under 'Install and Activate'. Then you're good to go!

### VPN Installation

1. Follow Canvas thread.

## Working with RoadRunner

Basic map editing tutorials can be found on [MathWorks](https://www.mathworks.com/videos/series/getting-started-with-roadrunner.html).

[This](https://carla.readthedocs.io/en/latest/tuto_M_generate_map/) is the documentation on how to transfer your scene (map) from RoadRunner into Carla.ou installed Carla as a binary package you only have a single option: building the Unreal Emgine in a Docker image and compile Carla with that image. The challenge with this approach is that it has some serious requirements, the most strenuous of which is 700GB of available disk space for building container images. You can find the full guide [here](https://carla.readthedocs.io/en/0.9.15/tuto_M_add_map_package/).

We've installed from a binary package. That leaves us limited options since we likely do not have 700GB of space on Joe's machine. Our next best bet is likely to install from source, but that requires completely ditching the Carla server we have now which is a big committment. Given this, I am going to ask Daniel what his thoughts are.

