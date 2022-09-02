import os

import pvcheetah
from pvrecorder import PvRecorder

ACCESS_KEY = os.environ["PICOVOICE_ACCESS_KEY"]


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
