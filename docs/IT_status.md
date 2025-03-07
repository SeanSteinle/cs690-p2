# In Search of an Actual Computer
*Sean Steinle*

This markdown documents the progress of our effort to configure the server which IT provided us.

- [X] Basic Server Access
    - (see `Connecting to the Server (Carla2)`)
- [/] Carla Server Installation
    - I've completed the first half of [this](https://carla.readthedocs.io/en/latest/build_linux/) setup guide -- however I've been unable to validate that the installation of UE4 worked because we don't have a virtual desktop setup.
        - You need a virtual desktop to test this because UE4 requires a graphical output buffer.
        - After configuring the virtual desktop, you can test the UE4 setup with: `cd ~/UnrealEngine_4.26/Engine/Binaries/Linux && ./UE4Editor`. Then you can do the second half of the guide.
- [/] Virtual Desktop Setup
    - As mentioned under 'Carla Server Installation', we need a virtual desktop which can act as a GUI for Carla/UE4's output.
    - IT has sent out some instructions via Daniel to us, the email is under `docs/vdi.txt`.
    - I have created a `.vnc` folder under `home/carla/`. The folder contains the `xstartup` file which IT specified we should create, along with a passwd of *Wednesday* in the `passwd` file. Per their instructions, you can run the server with `vncserver :1 -localhost no` and confirm that the server is running with `ps aux | grep Xtiger`. From this view you can tell which PID corresponds to the server, so if you want to restart the server just kill the process with `sudo kill <PID>` and rerun the start command.
    - The client instructions are less clear. IT seems to be telling us to create two different ssh tunnels with portforwarding on 5901 and then to install a local VNC client like RealVNC. I've followed these instructions and it seems like the port was forwarded successfully, but my RealVNC can't connect on `localhost:5901` or `10.192.127.96` for that matter.
- [] Python Environment Setup
    - Includes ML packages like tensorflow and the Carla Python client. Should involve setting up a Python version, a Python virtual environment, and package installs via pip -- ideally could streamline this with [pyenv](https://github.com/pyenv/pyenv).

After we complete these steps, we should be able to attempt to run what Joe's developed on his machine and we should even be able to train policies here.