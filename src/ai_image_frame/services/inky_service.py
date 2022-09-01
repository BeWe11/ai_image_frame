"""All inky modules are imported in functions because the inky library cannot
be installed on MacOS right now, see https://github.com/pimoroni/inky/issues/147.
"""
from typing import Optional

from PIL import Image

# Gpio pins for each button (from left to right, reverse alphabetical order, in
# portrait mode)
BUTTON_PINS = [24, 16, 6, 5]


def show_image(
    image: Image, should_rotate: bool = True, saturation: float = 0.5
) -> None:
    """Show a given image on the Inky.

    By default, the image is rotated by 90 degrees, because the inky is used in
    portrait mode but its original orientation is landscape.
    """
    from inky import Inky7Colour as Inky

    inky = Inky()
    inky.set_border(Inky.BLACK)
    if should_rotate:
        image = image.rotate(90, expand=True)
    inky.set_image(image, saturation=saturation)
    inky.show()


def clear_screen() -> None:
    """Clear the Inky screen."""
    from inky import Inky7Colour as Inky

    inky = Inky()
    for y in range(inky.height - 1):
        for x in range(inky.width - 1):
            inky.set_pixel(x, y, Inky.CLEAN)
    inky.show()


def init_gpio() -> None:
    """Initialize the Inky buttons.

    This method should be called once before buttons are accessed.
    """
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PINS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def get_pressed_button() -> Optional[int]:
    import RPi.GPIO as GPIO

    for index, button_pin in enumerate(BUTTON_PINS):
        if GPIO.input(button_pin) == GPIO.LOW:
            return index
    return None
