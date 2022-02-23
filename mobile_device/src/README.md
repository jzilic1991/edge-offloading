# Prerequisites
- Download and install Python (version 3.6) and setup the Python virtual environment on your desktop/virtual machine
- Download and install Kivy mobile cross-platform framework (including Android mobile emulator) on your desktop/virtual machine
- Download and install the Kivy Launcher mobile application on your Android mobile device from the Google Play store
- Ensure that the Kubernetes cluster is reachable from your desktop or mobile device

# Run experiment
## Android mobile emulator
Execute locally the following command:

```
python3 main.py
```

The experiment will run with progress output on the terminal console until the experiment is completed. Results are stored in the logs directory.

## Real Android mobile device
Transfer all the source code files from this directory to your mobile device via the USB port and run the application. Follow the instructions for more details 
(https://kivy.org/doc/stable/guide/packaging-android.html#packaging-your-application-for-the-kivy-launcher).

## Plot result figures
Execute locally the following command:

```
python3 result_plotter.py
```

Result figures will be displayed on the screen.
