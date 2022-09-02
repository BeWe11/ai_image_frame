from pathlib import Path
from typing import Any


def remove_duplicates(input_list: list[Any]) -> list[Any]:
    """Keep last occurences of duplicate elements in a list."""
    return list(reversed(list(dict.fromkeys(reversed(input_list)))))


def append_images_to_log(
    image_paths: list[Path], prompts: list[str], log_path: Path
) -> None:
    """Append the image/prompt pairs to the given log."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        for image_path, prompt in zip(image_paths, prompts):
            f.write(f"{image_path.name},{prompt}\n")


def get_images_from_log(
    log_path: Path, image_dir: Path, num_entries: int
) -> tuple[list[Path], list[str]]:
    """Return a number of recent unique images in the given log as path/prompt pairs.

    The log is opened with `a+` mode so that the log file is created if it
    doens't exist.
    """
    if not log_path.is_file():
        return ([], [])
    with open(log_path, "a+") as f:
        f.seek(0)
        lines = f.read().splitlines()
    image_paths = []
    prompts = []
    for line in reversed(lines):
        image_path_string, prompt = line.split(",")
        image_path = image_dir / Path(image_path_string)
        if image_path not in image_paths:
            image_paths.append(image_path)
            prompts.append(prompt)
        if len(image_paths) >= num_entries:
            break
    return image_paths, prompts
