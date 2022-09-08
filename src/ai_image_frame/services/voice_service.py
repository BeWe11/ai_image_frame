import os
from types import TracebackType
from typing import Optional

import pvcheetah
import pvrhino
from pvrecorder import PvRecorder

from . import audio_service

ACCESS_KEY = os.environ["PICOVOICE_ACCESS_KEY"]
INTENT_NAMES = ["chooseFirst", "chooseSecond", "chooseThird", "chooseFourth"]
RHINO_CONTEXT_FILE = os.environ["RHINO_CONTEXT_FILE"]
ENDPOINT_DURATION_SEC = 1.0

_RHINO = pvrhino.create(
    access_key=ACCESS_KEY,
    context_path=RHINO_CONTEXT_FILE,
    endpoint_duration_sec=ENDPOINT_DURATION_SEC,
)

_CHEETAH = pvcheetah.create(
    access_key=ACCESS_KEY,
    endpoint_duration_sec=ENDPOINT_DURATION_SEC,
)


class AudioRecorder:
    """Wrapper class around the `PvRecorder` class that makes it accessable as
    a context manager.
    """
    def __init__(self, frame_length: int):
        self.recorder = PvRecorder(device_index=-1, frame_length=frame_length)

    def __enter__(self) -> PvRecorder:
        self.recorder.start()
        return self.recorder

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.recorder.stop()
        self.recorder.delete()


def get_voice_choice() -> int:
    """Get a choice of four different values."""
    with AudioRecorder(_RHINO.frame_length) as recorder:
        audio_service.play_sound("beep")
        print("Rhino ready")
        while True:
            is_finalized = _RHINO.process(recorder.read())
            if is_finalized:
                inference = _RHINO.get_inference()
                if inference.is_understood:
                    intent_name = inference.intent
                    break
    return INTENT_NAMES.index(intent_name)


def get_voice_input() -> str:
    """Get transcribed voice input."""
    final_transcript = ""
    with AudioRecorder(_CHEETAH.frame_length) as recorder:
        audio_service.play_sound("beep")
        print("Cheetah ready")
        while True:
            partial_transcript, is_endpoint = _CHEETAH.process(recorder.read())
            final_transcript += partial_transcript
            if is_endpoint:
                final_transcript += _CHEETAH.flush()
                break
    return final_transcript
