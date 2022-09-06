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

### Mac

- run `poetry install`

## Deploy changes

Run `deploy.sh`

## Run the program

A `run_image_frame_loop` script is installed.
