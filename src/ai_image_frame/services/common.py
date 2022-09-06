from pathlib import Path

import ai_image_frame


def get_absolute_asset_path(relative_asset_path: Path) -> Path:
    """Return the absolute file path to an asset file.

    Assets are installed along the module and are loaded from installed module
    directory.
    """
    module_path = Path(ai_image_frame.__file__)
    asset_base_path = module_path.parent / "assets"
    return asset_base_path / relative_asset_path
