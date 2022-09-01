import os
from pathlib import Path
from typing import Any, Union

from dotenv import load_dotenv
from PIL import Image

from ai_image_frame.services import image_generation_service, image_manipulation_service

load_dotenv()
SESSION_TOKEN = os.getenv("DALLE2_SESSION_TOKEN")
RUN_MODE = os.getenv("RUN_MODE")


CHOSEN_IMAGE_LOG_NAME = "chosen_images.log"
GENERATED_IMAGE_LOG_NAME = "generated_images.log"

# Gpio pins for each button (from left to right, reverse alphabetical order)
BUTTON_PINS = [24, 16, 6, 5]
BUTTON_LABELS = ["A", "B", "C", "D"]
DEMO_MODE = True
IMAGE_DIR = "images"
SATURATION = 0.5
DALLE_DIMENSIONS = image_manipulation_service.Dimensions(width=1024, height=1024)
# INKY_DIMENSIONS = image_manipulation_service.Dimensions(width=600, height=448)
INKY_DIMENSIONS = image_manipulation_service.Dimensions(width=448, height=600)


def show_image(image: Image.Image) -> None:
    if RUN_MODE == "pi":
        from inky import Inky7Colour as Inky

        inky = Inky()
        inky.set_border(Inky.BLACK)
        inky.set_image(image.rotate(90, expand=True), saturation=SATURATION)
        inky.show()
    elif RUN_MODE == "mac":
        image.show()


def init_gpio() -> None:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PINS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def append_to_chosen_image_log(image_path: Path, prompt: str) -> None:
    with open(CHOSEN_IMAGE_LOG_NAME, "a") as f:
        f.write(f"{image_path},{prompt}\n")


def append_to_generated_image_log(image_paths: list[Path], prompt: str) -> None:
    with open(GENERATED_IMAGE_LOG_NAME, "a") as f:
        for image_path in image_paths:
            f.write(f"{image_path},{prompt}\n")


def get_button_index(message: str) -> int:
    chosen_label = None
    if RUN_MODE == "mac":
        while chosen_label is None:
            candidate_label = input(message)
            if candidate_label in BUTTON_LABELS:
                chosen_label = candidate_label
    elif RUN_MODE == "pi":
        import RPi.GPIO as GPIO

        print(message)
        while chosen_label is None:
            if GPIO.input(BUTTON_PINS[0]) == GPIO.LOW:
                chosen_label = BUTTON_LABELS[0]
            elif GPIO.input(BUTTON_PINS[1]) == GPIO.LOW:
                chosen_label = BUTTON_LABELS[1]
            elif GPIO.input(BUTTON_PINS[2]) == GPIO.LOW:
                chosen_label = BUTTON_LABELS[2]
            elif GPIO.input(BUTTON_PINS[3]) == GPIO.LOW:
                chosen_label = BUTTON_LABELS[3]
    return BUTTON_LABELS.index(chosen_label)


def show_collage(image_paths: list[Path], prompt: Union[str, list[str]]) -> None:
    images = [Image.open(image_path) for image_path in image_paths]

    collage_image = image_manipulation_service.generate_collage_image(
        images, BUTTON_LABELS, INKY_DIMENSIONS
    )
    show_image(collage_image)

    button_index = get_button_index(
        f"Please choose one image to display ({', '.join(BUTTON_LABELS[:-1])} or {BUTTON_LABELS[-1]}): "
    )

    chosen_image = images[button_index]
    if isinstance(prompt, list):
        prompt = prompt[button_index]
    append_to_chosen_image_log(image_paths[button_index], prompt)
    display_image = image_manipulation_service.generate_display_image(
        chosen_image, prompt, INKY_DIMENSIONS
    )

    show_image(display_image)


def remove_duplicates(input_list: list[Any]) -> list[Any]:
    """Keep last occurences of elements."""
    return list(reversed(list(dict.fromkeys(reversed(input_list)))))


def handle_new_prompt() -> None:
    prompt = input("Please enter a prompt: ")
    image_paths = image_generation_service.generate_images_for_prompt(
        prompt, IMAGE_DIR, SESSION_TOKEN, demo_mode=DEMO_MODE
    )
    append_to_generated_image_log(image_paths, prompt)
    show_collage(image_paths, prompt)


def handle_last_prompt() -> None:
    with open(GENERATED_IMAGE_LOG_NAME, "a+") as f:
        f.seek(0)
        lines = list(f)
    prompt = (lines[-1].split(",")[1]).strip()
    image_paths = [Path(line.split(",")[0]) for line in lines][-len(BUTTON_LABELS) :]
    show_collage(image_paths, prompt)


def handle_previous_choices() -> None:
    with open(CHOSEN_IMAGE_LOG_NAME, "a+") as f:
        f.seek(0)
        lines = list(f)
    prompts = [line.split(",")[1] for line in lines]
    image_paths = [Path(line.split(",")[0]) for line in lines]
    last_images_paths = remove_duplicates(image_paths)[: len(BUTTON_LABELS)]
    show_collage(last_images_paths, prompts[-1].strip())  # FIXME


def handle_clear() -> None:
    if RUN_MODE == "pi":
        from inky import Inky7Colour as Inky

        inky = Inky()
        for y in range(inky.height - 1):
            for x in range(inky.width - 1):
                inky.set_pixel(x, y, Inky.CLEAN)
        inky.show()
    elif RUN_MODE == "mac":
        pass


def run_main_loop() -> None:
    if RUN_MODE == "pi":
        init_gpio()

    while True:
        button_index = get_button_index(
            """Please choose an action:

A: Generate an image for a new prompt.
B: Choose again for the last prompt.
C: Choose from the last four previous choices.
D: Clear the display.
"""
        )
        if button_index == 0:
            handle_new_prompt()
        elif button_index == 1:
            handle_last_prompt()
        elif button_index == 2:
            handle_previous_choices()
        elif button_index == 3:
            handle_clear()


if __name__ == "__main__":
    run_main_loop()
