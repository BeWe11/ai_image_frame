import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image

from ai_image_frame.services import (
    image_generation_service,
    image_manipulation_service,
    inky_service,
    logging_service,
)

load_dotenv()
SESSION_TOKEN = os.environ["DALLE2_SESSION_TOKEN"]
RUN_MODE = os.environ["RUN_MODE"]
LOG_DIR = Path(os.environ["LOG_DIR"])
IMAGE_DIR = Path(os.environ["IMAGE_DIR"])


CHOSEN_IMAGE_LOG_PATH = LOG_DIR / "chosen_images.log"
GENERATED_IMAGE_LOG_PATH = LOG_DIR / "generated_images.log"

BUTTON_LABELS = ["A", "B", "C", "D"]
DEMO_MODE = True
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


def show_collage(image_paths: list[Path], prompts: list[str]) -> None:
    images = [Image.open(image_path) for image_path in image_paths]

    collage_image = image_manipulation_service.generate_collage_image(
        images, BUTTON_LABELS, INKY_DIMENSIONS
    )
    show_image(collage_image)

    choice = get_choice(
        f"Please choose one image to display ({', '.join(BUTTON_LABELS[:-1])} or {BUTTON_LABELS[-1]}): "
    )

    chosen_image = images[choice]
    prompt = prompts[choice]
    logging_service.append_images_to_log(
        [image_paths[choice]], [prompt], CHOSEN_IMAGE_LOG_PATH
    )
    display_image = image_manipulation_service.generate_display_image(
        chosen_image, prompt, INKY_DIMENSIONS
    )

    show_image(display_image)


def handle_new_prompt() -> None:
    prompt = input("Please enter a prompt: ")
    image_paths = image_generation_service.generate_images_for_prompt(
        prompt, IMAGE_DIR, SESSION_TOKEN, demo_mode=DEMO_MODE
    )
    logging_service.append_images_to_log(
        image_paths, [prompt] * len(image_paths), GENERATED_IMAGE_LOG_PATH
    )
    show_collage(image_paths, [prompt] * len(BUTTON_LABELS))


def handle_last_prompt() -> None:
    image_paths, prompts = logging_service.get_images_from_log(
        GENERATED_IMAGE_LOG_PATH, len(BUTTON_LABELS)
    )
    show_collage(image_paths, prompts)


def handle_previous_choices() -> None:
    image_paths, prompts = logging_service.get_images_from_log(
        CHOSEN_IMAGE_LOG_PATH, len(BUTTON_LABELS)
    )
    show_collage(image_paths, prompts)


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
            """Please choose an action:

A: Generate an image for a new prompt.
B: Choose again for the last prompt.
C: Choose from the last four previous choices.
D: Clear the display.
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
