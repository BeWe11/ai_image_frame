import os

import pvcheetah
import pvrhino
from pvrecorder import PvRecorder

ACCESS_KEY = os.environ["PICOVOICE_ACCESS_KEY"]
INTENT_NAMES = ["chooseFirst", "chooseSecond", "chooseThird", "chooseFourth"]


def get_voice_choice() -> int:
    """Get a choice of four different values."""
    rhino = None
    recorder = None
    try:
        rhino = pvrhino.create(
            access_key=ACCESS_KEY,
            context_path="/Users/ben/Downloads/978e0d6c-3c37-4791-a312-13cedfed18cb/inky_en_mac_v2_1_0.rhn",
            endpoint_duration_sec=1.0,
        )
        recorder = PvRecorder(device_index=-1, frame_length=rhino.frame_length)
        recorder.start()
        print("Rhino ready")
        while True:
            is_finalized = rhino.process(recorder.read())
            if is_finalized:
                inference = rhino.get_inference()
                if inference.is_understood:
                    intent_name = inference.intent
                    break
    except KeyboardInterrupt:
        pass
    finally:
        if recorder is not None:
            recorder.stop()
        if rhino is not None:
            rhino.delete()
    return INTENT_NAMES.index(intent_name)


def get_voice_input() -> str:
    """Get transcribed voice input."""
    final_transcript = ""
    cheetah = None
    recorder = None
    try:
        cheetah = pvcheetah.create(access_key=ACCESS_KEY, endpoint_duration_sec=1.0)
        recorder = PvRecorder(device_index=-1, frame_length=cheetah.frame_length)
        recorder.start()
        print("Cheetah ready")
        while True:
            partial_transcript, is_endpoint = cheetah.process(recorder.read())
            final_transcript += partial_transcript
            if is_endpoint:
                final_transcript += cheetah.flush()
                break
    except KeyboardInterrupt:
        pass
    finally:
        if recorder is not None:
            recorder.stop()
        if cheetah is not None:
            cheetah.delete()
    return final_transcript
