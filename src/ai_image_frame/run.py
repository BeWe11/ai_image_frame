import os
from distutils.util import strtobool
from pathlib import Path

import simpleaudio as sa
from dotenv import load_dotenv

load_dotenv()
from PIL import Image

from ai_image_frame.services import (
    audio_service,
    image_generation_service,
    image_manipulation_service,
    inky_service,
    logging_service,
    voice_service,
)
from ai_image_frame.services.common import get_absolute_asset_path

API_KEY = os.environ["OPENAI_API_KEY"]
RUN_MODE = os.environ["RUN_MODE"]
LOG_DIR = Path(os.environ["LOG_DIR"])
IMAGE_DIR = Path(os.environ["IMAGE_DIR"])


CHOSEN_IMAGE_LOG_PATH = LOG_DIR / "chosen_images.log"
GENERATED_IMAGE_LOG_PATH = LOG_DIR / "generated_images.log"

BUTTON_LABELS = ["1", "2", "3", "4"]
SHOW_FRAME = False
DEMO_MODE = bool(strtobool(os.environ["DEMO_MODE"]))
INPUT_VOICE = True
SATURATION = 0.5
DALLE_DIMENSIONS = image_manipulation_service.Dimensions(width=1024, height=1024)
# Inky is used in portrait mode, there dimensions are swapped
INKY_DIMENSIONS = image_manipulation_service.Dimensions(width=448, height=600)


def show_image(image: Image.Image) -> None:
    if RUN_MODE == "pi":
        inky_service.show_image(image, saturation=SATURATION)
    elif RUN_MODE == "mac":
        image.show()


def get_choice(message: str) -> int:
    chosen_label = None
    if RUN_MODE == "mac":
        while chosen_label is None:
            candidate_label = input(message)
            if candidate_label in BUTTON_LABELS:
                chosen_label = candidate_label
    elif RUN_MODE == "pi":
        print(message)
        while chosen_label is None:
            chosen_index = inky_service.get_pressed_button()
            if chosen_index is not None:
                chosen_label = BUTTON_LABELS[chosen_index]
    else:
        raise ValueError(f"Unsupported RUN_MODE {RUN_MODE}.")
    return BUTTON_LABELS.index(chosen_label)


def show_collage(
    image_paths: list[Path], prompts: list[str], play_obj: sa.PlayObject = None
) -> None:
    images = [Image.open(image_path) for image_path in image_paths]

    collage_image = image_manipulation_service.generate_collage_image(
        images,
        BUTTON_LABELS,
        INKY_DIMENSIONS,
        show_frame=SHOW_FRAME,
    )
    show_image(collage_image)
    # FIXME: play_obj should not be an argument to this function
    if play_obj is not None:
        play_obj.stop()

    # if INPUT_VOICE:
    if False:
        # FIXME: Buttons are cool, disable voice choice until voice and buttons can
        # be used simultaniously
        choice = voice_service.get_voice_choice()
    else:
        audio_service.play_sound("beep", blocking=False)
        choice = get_choice(
            f"Please choose one image to display ({', '.join(BUTTON_LABELS[:-1])} or {BUTTON_LABELS[-1]}): "
        )

    play_obj = audio_service.play_sound("waiting", blocking=False)
    chosen_image = images[choice]
    prompt = prompts[choice]
    logging_service.append_images_to_log(
        [image_paths[choice]], [prompt], CHOSEN_IMAGE_LOG_PATH
    )
    display_image = image_manipulation_service.generate_display_image(
        chosen_image,
        prompt,
        INKY_DIMENSIONS,
        show_frame=SHOW_FRAME,
    )

    show_image(display_image)
    play_obj.stop()


def handle_new_prompt() -> None:
    if INPUT_VOICE:
        print("Please say your prompt:")
        prompt = voice_service.get_voice_input()
        print(f"{prompt = }")
    else:
        prompt = input("Please enter a prompt: ")
    play_obj = audio_service.play_sound("waiting", blocking=False)
    image_paths = image_generation_service.generate_images_for_prompt(
        prompt, IMAGE_DIR, API_KEY, demo_mode=DEMO_MODE
    )
    logging_service.append_images_to_log(
        image_paths, [prompt] * len(image_paths), GENERATED_IMAGE_LOG_PATH
    )
    show_collage(image_paths, [prompt] * len(BUTTON_LABELS), play_obj=play_obj)


def handle_last_prompt() -> None:
    play_obj = audio_service.play_sound("waiting", blocking=False)
    image_paths, prompts = logging_service.get_images_from_log(
        GENERATED_IMAGE_LOG_PATH, IMAGE_DIR, len(BUTTON_LABELS)
    )
    show_collage(image_paths, prompts, play_obj=play_obj)


def handle_previous_choices() -> None:
    play_obj = audio_service.play_sound("waiting", blocking=False)
    image_paths, prompts = logging_service.get_images_from_log(
        CHOSEN_IMAGE_LOG_PATH, IMAGE_DIR, len(BUTTON_LABELS)
    )
    show_collage(image_paths, prompts, play_obj=play_obj)


def handle_clear() -> None:
    if RUN_MODE == "pi":
        inky_service.clear_screen()
    elif RUN_MODE == "mac":
        pass


def run_main_loop() -> None:
    if RUN_MODE == "pi":
        inky_service.init_gpio()

    while True:
        choice = get_choice(
            f"""Please choose an action:

{BUTTON_LABELS[0]}: Generate an image for a new prompt.
{BUTTON_LABELS[1]}: Choose again for the last prompt.
{BUTTON_LABELS[2]}: Choose from the last four previous choices.
{BUTTON_LABELS[3]}: Clear the display.
"""
        )
        if choice == 0:
            handle_new_prompt()
        elif choice == 1:
            handle_last_prompt()
        elif choice == 2:
            handle_previous_choices()
        elif choice == 3:
            handle_clear()


if __name__ == "__main__":
    run_main_loop()
