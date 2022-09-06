import os

import pvcheetah
import pvrhino
from pvrecorder import PvRecorder

ACCESS_KEY = os.environ["PICOVOICE_ACCESS_KEY"]
INTENT_NAMES = ["chooseFirst", "chooseSecond", "chooseThird", "chooseFourth"]
RHINO_CONTEXT_FILE = os.environ["RHINO_CONTEXT_FILE"]

_rhino = pvrhino.create(
    access_key=ACCESS_KEY,
    context_path=RHINO_CONTEXT_FILE,
    endpoint_duration_sec=1.0,
)


def get_voice_choice() -> int:
    """Get a choice of four different values."""
    recorder = None
    try:
        recorder = PvRecorder(device_index=-1, frame_length=_rhino.frame_length)
        recorder.start()
        print("Rhino ready")
        while True:
            is_finalized = _rhino.process(recorder.read())
            if is_finalized:
                inference = _rhino.get_inference()
                if inference.is_understood:
                    intent_name = inference.intent
                    break
    except KeyboardInterrupt:
        pass
    finally:
        if recorder is not None:
            recorder.stop()
            recorder.delete()
    return INTENT_NAMES.index(intent_name)


_cheetah = pvcheetah.create(access_key=ACCESS_KEY, endpoint_duration_sec=1.0)


def get_voice_input() -> str:
    """Get transcribed voice input."""
    final_transcript = ""
    recorder = None
    try:
        recorder = PvRecorder(device_index=-1, frame_length=_cheetah.frame_length)
        recorder.start()
        print("Cheetah ready")
        while True:
            partial_transcript, is_endpoint = _cheetah.process(recorder.read())
            final_transcript += partial_transcript
            if is_endpoint:
                final_transcript += _cheetah.flush()
                break
    except KeyboardInterrupt:
        pass
    finally:
        if recorder is not None:
            recorder.stop()
            recorder.delete()
    return final_transcript
