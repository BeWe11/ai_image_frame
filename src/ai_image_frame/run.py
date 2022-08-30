import os
from dataclasses import dataclass
from pathlib import Path

from dalle2 import Dalle2
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont

load_dotenv()
SESSION_TOKEN = os.getenv("DALLE2_SESSION_TOKEN")
RUN_MODE = os.getenv("RUN_MODE")


@dataclass(frozen=True)
class Dimensions:
    width: int
    height: int

    def as_tuple(self) -> tuple[int, int]:
        """Return dimensions as a tuple of (width, height)."""
        return (self.width, self.height)


dalle = Dalle2(f"sess-{SESSION_TOKEN}")
IMAGE_DIR = "images"
INKY_DIMENSIONS = Dimensions(width=600, height=448)
DALLE_DIMENSIONS = Dimensions(width=1024, height=1024)
SOLID_BLACK_COLOR_TUPLE = (0, 0, 0, 255)
SATURATION = 0.5

# Gpio pins for each button (from left to right, reverse alphabetical order)
BUTTON_PINS = [24, 16, 6, 5]
BUTTON_LABELS = ["A", "B", "C", "D"]


def get_font(font_size) -> ImageFont.ImageFont:
    return ImageFont.truetype(
        f"{Path(__file__).parent.resolve()}/Amsterdam.ttf", size=font_size
    )


def split_long_text(text: str, max_line_length: int) -> list[str]:
    lines = [
        text[i : i + max_line_length] for i in range(0, len(text), max_line_length)
    ]
    return "\n".join(lines)


def generate_images_for_prompt(prompt: str) -> list[Path]:
    # file_paths = dalle.generate_and_download(prompt, IMAGE_DIR)
    file_paths = [
        "images/generation-1a3d0cCM7s9fHGrBLm7KAp32.png",
        "images/generation-kVLiU7oNyr2x6d8YADm4xXP7.png",
        "images/generation-F3Aw2dDQWa4ugSftT7fntUNl.png",
        "images/generation-WO2TsfewLPhCEhZQzEC4KAka.png",
    ]
    return [Path(path_string) for path_string in file_paths]


def generate_text_box(
    text: str, dimensions: Dimensions, font_size=10, draw_grid_lines=False
) -> Image.Image:
    background_color = (0, 0, 0)
    text_color = "white"

    image = Image.new("RGB", dimensions.as_tuple(), background_color)
    draw = ImageDraw.Draw(image)
    if draw_grid_lines:
        draw.line(
            ((0, dimensions.height / 2), (dimensions.width, dimensions.height / 2)),
            "gray",
        )
        draw.line(
            ((dimensions.width / 2, 0), (dimensions.width / 2, dimensions.height)),
            "gray",
        )
    draw.text(
        (dimensions.width / 2, dimensions.height / 2),
        text,
        anchor="mm",
        align="center",
        fill=text_color,
        font=get_font(font_size=font_size),
    )
    return image


def pad_image(
    image: Image.Image,
    padding_top: int = 0,
    padding_right: int = 0,
    padding_bottom: int = 0,
    padding_left: int = 0,
) -> Image.Image:
    padded_image = Image.new("RGB", image.size)
    padded_image.paste(
        image.resize(
            (
                image.size[0] - (padding_left + padding_right),
                image.size[1] - -(padding_top + padding_bottom),
            )
        ),
        (padding_left, padding_top),
    )
    return padded_image


def generate_collage_image(images: list[Image.Image]) -> Image.Image:
    collage_image = Image.new("RGB", (INKY_DIMENSIONS.width, INKY_DIMENSIONS.height))

    half_inky_width = round(INKY_DIMENSIONS.width / 2)
    half_inky_height = round(INKY_DIMENSIONS.height / 2)
    label_box_dimensions = Dimensions(
        width=round((INKY_DIMENSIONS.width - 2 * half_inky_height) / 2),
        height=half_inky_height,
    )

    x_offsets = [0, 0, half_inky_width, half_inky_width]
    y_offsets = [half_inky_height, 0, half_inky_height, 0]
    padding_value = 20
    paddings = [
        {
            "padding_top": padding_value,
            "padding_right": round(padding_value / 2),
            "padding_bottom": 0,
            "padding_left": padding_value,
        },
        {
            "padding_top": padding_value,
            "padding_right": padding_value,
            "padding_bottom": 0,
            "padding_left": round(padding_value / 2),
        },
        {
            "padding_top": 0,
            "padding_right": round(padding_value / 2),
            "padding_bottom": 0,
            "padding_left": padding_value,
        },
        {
            "padding_top": 0,
            "padding_right": padding_value,
            "padding_bottom": 0,
            "padding_left": round(padding_value / 2),
        },
    ]

    for image, label, x_offset, y_offset, padding in zip(
        images, BUTTON_LABELS, x_offsets, y_offsets, paddings
    ):
        collage_image.paste(
            pad_image(image, **padding)
            .resize((half_inky_height, half_inky_height))
            .rotate(90, expand=True),
            (x_offset, y_offset),
        )
        label_box = generate_text_box(label, label_box_dimensions)
        collage_image.paste(
            label_box.rotate(90, expand=False), (x_offset + half_inky_height, y_offset)
        )
    return collage_image


def generate_display_image(image: Image.Image, text: str) -> Image.Image:
    display_image = Image.new("RGB", (INKY_DIMENSIONS.width, INKY_DIMENSIONS.height))
    display_image.paste(
        image.resize((INKY_DIMENSIONS.height, INKY_DIMENSIONS.height)).rotate(
            90, expand=True
        ),
        (0, 0),
    )

    label_box_dimensions = Dimensions(
        width=INKY_DIMENSIONS.height,
        height=INKY_DIMENSIONS.width - INKY_DIMENSIONS.height,
    )
    text_box = generate_text_box(
        split_long_text(text, 50), label_box_dimensions, font_size=16
    )
    display_image.paste(text_box.rotate(90, expand=True), (INKY_DIMENSIONS.height, 0))

    return display_image


def enrich_prompt(prompt: str) -> str:
    return prompt + ", in the style of van gogh"


def show_image(image: Image.Image) -> None:
    if RUN_MODE == "pi":
        from inky import Inky7Colour as Inky

        inky = Inky()
        inky.set_border(Inky.BLACK)
        inky.set_image(image, saturation=SATURATION)
        inky.show()
    elif RUN_MODE == "mac":
        image.show()


def init_gpio() -> None:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PINS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def run_main_loop() -> None:
    if RUN_MODE == "pi":
        init_gpio()

    while True:
        prompt = input("Please enter a prompt: ")

        image_paths = generate_images_for_prompt(enrich_prompt(prompt))
        images = [Image.open(image_path) for image_path in image_paths]

        collage_image = generate_collage_image(images)
        show_image(collage_image)

        chosen_label = None
        while chosen_label is None:
            if RUN_MODE == "mac":
                candidate_image = input(
                    f"Please choose one image to display ({', '.join(BUTTON_LABELS[:-1])} or {BUTTON_LABELS[-1]}): "
                )
                if candidate_image in BUTTON_LABELS:
                    chosen_label = candidate_image
            elif RUN_MODE == "pi":
                import RPi.GPIO as GPIO

                print("Please choose one image to display (A, B, C or D): ")
                while chosen_label is None:
                    if GPIO.input(BUTTON_PINS[0]) == GPIO.LOW:
                        chosen_label = BUTTON_LABELS[0]
                    elif GPIO.input(BUTTON_PINS[1]) == GPIO.LOW:
                        chosen_label = BUTTON_LABELS[1]
                    elif GPIO.input(BUTTON_PINS[2]) == GPIO.LOW:
                        chosen_label = BUTTON_LABELS[2]
                    elif GPIO.input(BUTTON_PINS[3]) == GPIO.LOW:
                        chosen_label = BUTTON_LABELS[3]

        chosen_image = images[BUTTON_LABELS.index(chosen_label)]
        display_image = generate_display_image(chosen_image, prompt)

        show_image(display_image)


if __name__ == "__main__":
    run_main_loop()
