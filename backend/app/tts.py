"""
Azure Neural TTS — returns raw WAV bytes.
Falls back to None if keys are not set.
"""
import azure.cognitiveservices.speech as speechsdk
import io
from .config import get_settings


def synthesise(text: str) -> bytes | None:
    """Synthesise text to WAV bytes using Azure Neural TTS."""
    settings = get_settings()
    if not settings.speech_key:
        return None

    speech_config = speechsdk.SpeechConfig(
        subscription=settings.speech_key,
        region=settings.speech_region,
    )
    speech_config.speech_synthesis_voice_name = settings.speech_voice
    speech_config.set_speech_synthesis_output_format(
        speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
    )

    # Synthesise to in-memory stream
    audio_stream = speechsdk.audio.PushAudioOutputStream(
        speechsdk.audio.PushAudioOutputStreamCallback()
    )
    audio_config = speechsdk.audio.AudioOutputConfig(stream=audio_stream)
    synthesiser = speechsdk.SpeechSynthesizer(
        speech_config=speech_config,
        audio_config=audio_config,
    )

    result = synthesiser.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data
    return None
