import sys, traceback
sys.path.insert(0, r"D:/nigredo")
# 在 nigredo 自己的 cwd 语境下复现其 ASR 调用
try:
    from core import subtitle
    print("imported core.subtitle OK; WHISPER_DEVICE=", subtitle.WHISPER_DEVICE,
          "COMPUTE_TYPE=", subtitle.WHISPER_COMPUTE_TYPE)
    audio = r"D:/nigredo/data/cache/BV1AbPrzJEba.wav"
    print("calling transcribe_with_whisper on", audio)
    segs = subtitle.transcribe_with_whisper(audio)
    print("OK segments:", len(segs))
except Exception:
    print("=== FULL TRACEBACK (nigredo context) ===")
    traceback.print_exc()
    sys.exit(2)
