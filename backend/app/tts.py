"""Azure Neural TTS → base64 WAV bytes."""
import base64
from app.config import settings


async def synthesize(text: str) -> str | None:
    """Returns base64-encoded WAV audio, or None if TTS not configured."""
    if not settings.speech_key:
        return None

    try:
        import azure.cognitiveservices.speech as speechsdk

        speech_config = speechsdk.SpeechConfig(
            subscription=settings.speech_key,
            region=settings.speech_region,
        )
        speech_config.speech_synthesis_voice_name = settings.speech_voice
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm
        )

        # Use in-memory stream, no file system needed
        audio_stream = speechsdk.audio.AudioOutputStream.create_pull_audio_output_stream()
        audio_config = speechsdk.audio.AudioOutputConfig(stream=audio_stream)

        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config,
        )
        result = synthesizer.speak_text_async(text).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return base64.b64encode(result.audio_data).decode("utf-8")
        return None
    except Exception as e:
        print(f"[tts] error: {e}")
        return None
