from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from PIL import Image, ImageDraw, ImageFont

from .common import get_absolute_asset_path

SOLID_BLACK = (0, 0, 0)
SOLID_WHITE = (255, 255, 255)


@dataclass(frozen=True)
class Dimensions:
    """Represents a pair of width and height dimensions."""

    width: int
    height: int

    @property
    def is_portrait(self) -> bool:
        """Return whether the dimensions represent an image in portrait mode."""
        return self.height >= self.width

    def as_tuple(self) -> tuple[int, int]:
        """Return dimensions as a tuple of (width, height)."""
        return (self.width, self.height)

    def __repr__(self) -> str:
        return str(self.as_tuple())


def _get_font(font_size: int, font_name: str = "Silent Reaction.ttf") -> ImageFont.ImageFont:
    """Return the base font for image labels."""
    font_path = get_absolute_asset_path(Path("fonts") / font_name)
    return ImageFont.truetype(str(font_path), size=font_size)


def _split_long_text(text: str, max_line_length: int) -> str:
    """Split long text by adding newline characters for lines exceeding the
    maximum desired line length.
    """
    lines = [
        text[i : i + max_line_length] for i in range(0, len(text), max_line_length)
    ]
    return "\n".join(lines)


def _overlay_label_image(
    input_image: Image.Image,
    label_padding: int = 20,  # FIXME: hardcoded for the specific image file
    label_image_name: str = "label.png",
) -> Image.Image:
    """Overlay the label image on top of the input image.

    The label image is used a a backdrop for image text descriptions.
    """
    label_image = Image.open(get_absolute_asset_path(Path("images") / label_image_name))
    label_scale = input_image.width / label_image.width
    label_image = label_image.resize(
        (
            round(label_image.width * label_scale),
            round(label_image.height * label_scale),
        )
    )
    label_padding = round(label_padding * label_scale)
    label_image = pad_image(label_image, label_padding)
    output_image = input_image.copy()
    output_image.paste(label_image, (0, 0), label_image)
    return output_image


def generate_text_box(
    text: str,
    output_dimensions: Dimensions,
    font_size: int = 10,
    background_color: tuple[int, int, int] = SOLID_BLACK,
    text_color: tuple[int, int, int] = SOLID_BLACK,
    text_shift: tuple[int, int] = (0, 0),
) -> Image.Image:
    """Create a box containing text."""
    text_box_image = Image.new("RGB", output_dimensions.as_tuple(), background_color)

    text_box_image = _overlay_label_image(text_box_image)
    draw = ImageDraw.Draw(text_box_image)
    draw.text(
        (
            output_dimensions.width / 2 + text_shift[0],
            output_dimensions.height / 2 + text_shift[1],
        ),
        text,
        anchor="mm",
        align="center",
        fill=text_color,
        font=_get_font(font_size=font_size),
    )
    return text_box_image


def pad_image(
    input_image: Image.Image,
    padding_top: Optional[int] = None,
    padding_right: Optional[int] = None,
    padding_bottom: Optional[int] = None,
    padding_left: Optional[int] = None,
) -> Image.Image:
    """Return the input image with padding.

    If only `padding_top` is given (for example by using a positional parameter
    with `pad_image(image, 30)`), the padding value is interpreted to be a
    general padding for all directions.
    """
    if padding_top is not None and all(
        padding is None for padding in [padding_right, padding_bottom, padding_left]
    ):
        padding_right = padding_top
        padding_bottom = padding_top
        padding_left = padding_top
    else:
        padding_top = 0 if padding_top is None else padding_top
        padding_right = 0 if padding_right is None else padding_right
        padding_bottom = 0 if padding_bottom is None else padding_bottom
        padding_left = 0 if padding_left is None else padding_left

    assert padding_left + padding_right == padding_top + padding_bottom, (
        f"Paddings {padding_top=}, {padding_right=}, {padding_bottom=}, {padding_top=} "
        " would change the aspect ratio."
    )

    padded_image = Image.new("RGBA", input_image.size, SOLID_BLACK)
    padded_image.paste(
        input_image.resize(
            (
                input_image.size[0] - (padding_left + padding_right),
                input_image.size[1] - (padding_top + padding_bottom),
            )
        ),
        (padding_left, padding_top),
    )
    return padded_image


def generate_collage_image(
    input_images: list[Image.Image],
    labels: list[str],
    output_dimensions: Dimensions,
    grid_padding: int = 4,
) -> Image.Image:
    """Generate a collage of the input images with labels as subtitles.

    This function is written for a maximum of four images.
    """
    assert output_dimensions.is_portrait, "Image must be in portrait orientation."
    assert (
        len(input_images) <= 4
    ), "Cannot display a collage with more than four images."
    assert grid_padding % 2 == 0, "`grid_padding` must be an even number."

    collage_image = Image.new("RGB", output_dimensions.as_tuple())

    half_output_width = round(output_dimensions.width / 2)
    half_output_height = round(output_dimensions.height / 2)
    half_grid_padding = round(grid_padding / 2)

    x_offsets = [0, half_output_width, 0, half_output_width]
    y_offsets = [0, 0, half_output_height, half_output_height]
    paddings = [
        {
            "padding_top": 0,
            "padding_right": half_grid_padding,
            "padding_bottom": half_grid_padding,
            "padding_left": 0,
        },
        {
            "padding_top": 0,
            "padding_right": 0,
            "padding_bottom": half_grid_padding,
            "padding_left": half_grid_padding,
        },
        {
            "padding_top": 0,
            "padding_right": half_grid_padding,
            "padding_bottom": half_grid_padding,
            "padding_left": 0,
        },
        {
            "padding_top": 0,
            "padding_right": 0,
            "padding_bottom": half_grid_padding,
            "padding_left": half_grid_padding,
        },
    ]

    small_dimensions = Dimensions(width=half_output_width, height=half_output_height)
    for input_image, label, x_offset, y_offset, padding in zip(
        input_images, labels, x_offsets, y_offsets, paddings
    ):
        # FIXME: The hardcoded y-shift of 4 is necessary because the label
        # letters are not perfectly centered inside the label image. It's not
        # clear whether this is due to the image itself or whether its an
        # artefact of some calculations inside this function.
        image = generate_display_image(
            input_image, label, small_dimensions, text_shift=(0, 4)
        )
        collage_image.paste(pad_image(image, **padding), (x_offset, y_offset))
    return collage_image


def _overlay_frame_image(
    input_image: Image.Image,
    image_padding: int = 30,  # FIXME: hardcoded for the specific image file
    frame_image_name: str = "frame.png",
) -> Image.Image:
    """Overlay the frame image on top of the input image.

    The input image is padded so that the frame does not conceal the outer
    parts of the image.
    """
    frame_image = Image.open(get_absolute_asset_path(Path("images") / frame_image_name))
    frame_scale = input_image.width / frame_image.width
    frame_image = frame_image.resize(
        (
            round(frame_image.width * frame_scale),
            round(frame_image.height * frame_scale),
        )
    )
    image_padding = round(image_padding * frame_scale)
    output_image = pad_image(input_image, image_padding)
    output_image.paste(frame_image, (0, 0), frame_image)
    return output_image


def generate_display_image(
    input_image: Image.Image, text: str, output_dimensions: Dimensions, **kwargs: Any
) -> Image.Image:
    """Return the input image with a subtitle.

    All extra keywords arguments are passed to `generate_text_box`.
    """
    assert output_dimensions.is_portrait, "Image must be in portrait orientation"

    display_image = Image.new("RGB", output_dimensions.as_tuple(), SOLID_BLACK)
    display_image.paste(
        input_image.resize((output_dimensions.width, output_dimensions.width)),
        (0, 0),
    )
    display_image = _overlay_frame_image(display_image)

    label_box_dimensions = Dimensions(
        width=output_dimensions.width,
        height=output_dimensions.height - output_dimensions.width,
    )
    label_box = generate_text_box(
        _split_long_text(text, 50), label_box_dimensions, font_size=32, **kwargs
    )
    display_image.paste(label_box, (0, output_dimensions.width))
    return display_image
