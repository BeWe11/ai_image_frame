from pathlib import Path

from dalle2 import Dalle2


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
    prompt: str, image_dir: Path, session_token: str, demo_mode: bool = False
) -> list[Path]:
    if demo_mode:
        file_paths = [
            f"{image_dir}/generation-nkkmR7oHwVLFVBjDAzF0LQzn.png",
            f"{image_dir}/generation-npDqQCEtvXG0L5lM5jfPkmXZ.png",
            f"{image_dir}/generation-Or0d74d5Ry8ltvbliUgkJOZb.png",
            f"{image_dir}/generation-Z4Uqw7G5JtPJCskogQibFuub.png",
        ]
    else:
        dalle_client = Dalle2(f"sess-{session_token}")
        enriched_prompt = _enrich_prompt(prompt)
        file_paths = dalle_client.generate_and_download(enriched_prompt, image_dir)
    return [Path(path_string) for path_string in file_paths]
