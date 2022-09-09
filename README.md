## Installation

### Raspberry Pi

- Turn on `ssh` functionality on the pi.
- For audio support, install the following packages:
```
sudo apt-get install libasound-dev portaudio19-dev
```
- Run the following command to install all required Pimoroni libraries as well as the `inky` Python Package
```
curl https://get.pimoroni.com/inky | bash
```
- Copy a [Rhino context file](https://picovoice.ai/docs/quick-start/rhino-python/) to `~/ai_image_frame` onto the pi
- Copy `.env.dist` as `~/ai_image_frame/.env` onto the pi, fill out all values
- Follow [this tutorial](https://iotbytes.wordpress.com/connect-configure-and-test-usb-microphone-and-speaker-with-raspberry-pi/) to setup audio on the pi. Make sure to increase mic input volume in `alsamixer` to 100%.

To install the systemd that autostarts the main script:
- `scp ai_image_frame.service {user}@{pi_location}:`
On the pi:
- `sudo mv ai_image_frame.service /etc/systemd/user`
- `sudo systemctl --user daemon-reload`
- `sudo systemctl --user enable ai_image_frame.service`
- `sudo reboot`

### Mac

- run `poetry install`

## Test microphone

- `arecord --format=S16_LE --rate=16000 | aplay --format=S16_LE --rate=16000`

## Deploy changes

Run `deploy.sh`

## Run the program

A `run_image_frame_loop` script is installed.

## TODO

- Implement state machine with possibility to go back to main state at any point
- Refactor `run.py`, it's way too imperative
- Allow button and voice choices simultaniously
- Decrease image frame width, it takes away too many valuable pixels
- Put Text-to-label-fitting algorithm into its own function
- Maybe: use picovoice porcupine for hotword instead of button press for initial action
- Use script arguments to `run.py` instead of global and environment variables to define behaviour
- Remove all sensitive data (pi username etc)
- Don't check in assets, only reference in readme that these have to be downloaded
