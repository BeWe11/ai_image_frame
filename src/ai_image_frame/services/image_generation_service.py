import base64
from io import BytesIO
from pathlib import Path

from PIL import Image


def _enrich_prompt(prompt: str) -> str:
    """Append stylistic instructions to the prompt to achieve a uniform style
    that looks good on the inky display.
    """
    styles = [
        "in the style of thomas kinkade",
    ]
    prompt_and_styles = [prompt] + styles
    return ", ".join(prompt_and_styles)


def generate_images_for_prompt(
    prompt: str, image_dir: Path, api_key: str, demo_mode: bool = False
) -> list[Path]:
    if demo_mode:
        file_paths = [
            Path(f"{image_dir}/generation-nkkmR7oHwVLFVBjDAzF0LQzn.png"),
            Path(f"{image_dir}/generation-npDqQCEtvXG0L5lM5jfPkmXZ.png"),
            Path(f"{image_dir}/generation-Or0d74d5Ry8ltvbliUgkJOZb.png"),
            Path(f"{image_dir}/generation-Z4Uqw7G5JtPJCskogQibFuub.png"),
        ]
        return file_paths
    import openai

    openai.api_key = api_key
    enriched_prompt = _enrich_prompt(prompt)
    response = openai.Image.create(
        prompt=enriched_prompt, n=4, size="512x512", response_format="b64_json"
    )
    file_paths = []
    for i, obj in enumerate(response["data"]):
        image = Image.open(BytesIO(base64.b64decode(obj["b64_json"])))
        file_path = image_dir / f"generation_{response['created']}_{i}.png"
        image.save(file_path)
        file_paths.append(file_path)
    return file_paths
