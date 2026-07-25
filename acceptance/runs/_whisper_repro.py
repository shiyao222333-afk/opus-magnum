import traceback, sys
wav = r"D:/nigredo/data/cache/BV1AbPrzJEba.wav"
print("numpy:", __import__("numpy").__version__)
print("faster_whisper:", __import__("faster_whisper").__version__)
try:
    from faster_whisper import WhisperModel
    m = WhisperModel("D:/nigredo/data/models/faster-whisper-large-v3", device="cuda",
                     compute_type="float16", cpu_threads=4)
    print("model loaded")
    segs, info = m.transcribe(wav, beam_size=5, language="zh", vad_filter=True)
    print("transcribe returned; collecting segments...")
    out = []
    n = 0
    for s in segs:
        n += 1
        out.append((s.start, s.end, s.text))
    print("OK segments:", n, "lang=", info.language)
except Exception:
    print("=== FULL TRACEBACK ===")
    traceback.print_exc()
    sys.exit(2)
