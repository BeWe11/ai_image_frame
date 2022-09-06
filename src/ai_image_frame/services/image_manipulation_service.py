from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


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


def _get_font(font_size: int, font_name: str = "Amsterdam.ttf") -> ImageFont.ImageFont:
    """Return the base font for image labels."""
    return ImageFont.truetype(
        f"{Path(__file__).parent.resolve()}/../{font_name}", size=font_size
    )


def _split_long_text(text: str, max_line_length: int) -> str:
    """Split long text by adding newline characters for lines exceeding the
    maximum desired line length.
    """
    lines = [
        text[i : i + max_line_length] for i in range(0, len(text), max_line_length)
    ]
    return "\n".join(lines)


def generate_text_box(
    text: str,
    dimensions: Dimensions,
    font_size: int = 10,
    background_color: tuple[int, int, int] = (0, 0, 0),  # black
    text_color: tuple[int, int, int] = (255, 255, 255),  # white
) -> Image.Image:
    """Create a box containing text."""
    output_image = Image.new("RGB", dimensions.as_tuple(), background_color)
    draw = ImageDraw.Draw(output_image)
    draw.text(
        (dimensions.width / 2, dimensions.height / 2),
        text,
        anchor="mm",
        align="center",
        fill=text_color,
        font=_get_font(font_size=font_size),
    )
    return output_image


def pad_image(
    input_image: Image.Image,
    padding_top: int = 0,
    padding_right: int = 0,
    padding_bottom: int = 0,
    padding_left: int = 0,
) -> Image.Image:
    """Return the input image with padding."""
    padded_image = Image.new("RGB", input_image.size)
    padded_image.paste(
        input_image.resize(
            (
                input_image.size[0] - (padding_left + padding_right),
                input_image.size[1] - -(padding_top + padding_bottom),
            )
        ),
        (padding_left, padding_top),
    )
    return padded_image


def generate_collage_image(
    input_images: list[Image.Image],
    labels: list[str],
    output_dimensions: Dimensions,
    grid_padding: int = 20,
) -> Image.Image:
    """Generate a collage of the input images with labels as subtitles.

    This function is written for a maximum of four images.
    """
    assert output_dimensions.is_portrait, "Image must be in portrait orientation"
    assert (
        len(input_images) <= 4
    ), "Cannot display a collage with more than four images."

    collage_image = Image.new("RGB", output_dimensions.as_tuple())

    half_output_width = round(output_dimensions.width / 2)
    half_output_height = round(output_dimensions.height / 2)
    label_box_dimensions = Dimensions(
        width=half_output_width,
        height=round((output_dimensions.height - 2 * half_output_width) / 2),
    )

    x_offsets = [0, half_output_width, 0, half_output_width]
    y_offsets = [0, 0, half_output_height, half_output_height]
    paddings = [
        {
            "padding_top": grid_padding,
            "padding_right": round(grid_padding / 2),
            "padding_bottom": 0,
            "padding_left": grid_padding,
        },
        {
            "padding_top": grid_padding,
            "padding_right": grid_padding,
            "padding_bottom": 0,
            "padding_left": round(grid_padding / 2),
        },
        {
            "padding_top": 0,
            "padding_right": round(grid_padding / 2),
            "padding_bottom": 0,
            "padding_left": grid_padding,
        },
        {
            "padding_top": 0,
            "padding_right": grid_padding,
            "padding_bottom": 0,
            "padding_left": round(grid_padding / 2),
        },
    ]

    for input_image, label, x_offset, y_offset, padding in zip(
        input_images, labels, x_offsets, y_offsets, paddings
    ):
        collage_image.paste(
            pad_image(input_image, **padding).resize(
                (half_output_width, half_output_width)
            ),
            (x_offset, y_offset),
        )
        label_box = generate_text_box(label, label_box_dimensions)
        collage_image.paste(
            label_box,
            (x_offset, y_offset + half_output_height - label_box_dimensions.height),
        )
    return collage_image


def generate_display_image(
    input_image: Image.Image, text: str, output_dimensions: Dimensions
) -> Image.Image:
    """Return the input image with a subtitle."""
    assert output_dimensions.is_portrait, "Image must be in portrait orientation"

    display_image = Image.new("RGB", output_dimensions.as_tuple())
    display_image.paste(
        input_image.resize((output_dimensions.width, output_dimensions.width)),
        (0, 0),
    )

    label_box_dimensions = Dimensions(
        width=output_dimensions.width,
        height=output_dimensions.height - output_dimensions.width,
    )
    label_box = generate_text_box(
        _split_long_text(text, 50), label_box_dimensions, font_size=16
    )
    display_image.paste(label_box, (0, output_dimensions.width))
    return display_image
