from pathlib import Path

import simpleaudio as sa

from .common import get_absolute_asset_path


def play_sound(sound_name: str, blocking: bool = False) -> sa.PlayObject:
    """Play a sound file in the `sounds` assets given the file name without
    extensions.

    The PlayObject is returned so that the sound can be stopped by the caller.
    """
    wave_path = get_absolute_asset_path(Path(f"sounds/{sound_name}.wav"))
    wave_obj = sa.WaveObject.from_wave_file(str(wave_path))
    play_obj = wave_obj.play()
    if blocking:
        play_obj.wait_done()
    return play_obj
