from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
import logging

import config

# Ensure Whisper can find ffmpeg regardless of the terminal's PATH.
# Prefer an explicit folder, else fall back to the ffmpeg bundled with imageio-ffmpeg.
_FFMPEG_DIR = r"C:\ffmpeg\bin"
if os.path.isfile(os.path.join(_FFMPEG_DIR, "ffmpeg.exe")):
    os.environ["PATH"] = _FFMPEG_DIR + os.pathsep + os.environ.get("PATH", "")
else:
    try:
        import imageio_ffmpeg
        _exe = imageio_ffmpeg.get_ffmpeg_exe()
        _dir = os.path.dirname(_exe)
        # imageio names it ffmpeg-win-*.exe; whisper calls plain "ffmpeg"
        _alias = os.path.join(_dir, "ffmpeg.exe")
        if not os.path.isfile(_alias):
            import shutil
            shutil.copy(_exe, _alias)
        os.environ["PATH"] = _dir + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
async def transcribe_voice(audio: UploadFile = File(...)):
    """Accept audio file, transcribe with Whisper, return text + detected language."""
    if not audio.content_type.startswith("audio/"):
        raise HTTPException(status_code=400, detail="File must be an audio file")

    try:
        import whisper
    except ImportError:
        raise HTTPException(status_code=503, detail="Whisper not installed. Run: pip install openai-whisper")

    # Save uploaded audio to temp file
    suffix = os.path.splitext(audio.filename)[1] if audio.filename else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await audio.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        model = whisper.load_model(config.WHISPER_MODEL_SIZE)
        result = model.transcribe(tmp_path)
        transcript = result["text"].strip()
        detected_language = result.get("language", "en")

        # Translate to English if needed
        if detected_language != "en":
            try:
                from deep_translator import GoogleTranslator
                translator = GoogleTranslator(source=detected_language, target="en")
                transcript_en = translator.translate(transcript)
            except Exception:
                transcript_en = transcript
        else:
            transcript_en = transcript

        return {
            "transcript": transcript,
            "transcript_english": transcript_en,
            "detected_language": detected_language,
        }
    finally:
        os.unlink(tmp_path)
