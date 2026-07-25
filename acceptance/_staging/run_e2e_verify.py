import sys
sys.path.insert(0, "D:/nigredo")
from core.asr import get_asr_backend

audio = "D:/opus-magnum/acceptance/_staging/funasr_test_clip.wav"

# 这一步与下载器「字幕三级回退链」的第三级完全一致：
# self._bilibili 联网取不到 CC/AI 字幕后，即调用 get_asr_backend().transcribe(audio_path)
segs = get_asr_backend("funasr").transcribe(audio, "zh")


def fmt(ts: float) -> str:
    ms = int(round(ts * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


lines = []
for i, s in enumerate(segs, 1):
    lines.append(str(i))
    lines.append(f"{fmt(s['start'])} --> {fmt(s['end'])}")
    lines.append(s["text"])
    lines.append("")
srt = "\n".join(lines)

out_path = "D:/opus-magnum/acceptance/_staging/funasr_test_clip.srt"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(srt)

print(srt)
print("\n=== STATS ===")
print("segments:", len(segs))
print("first_start:", segs[0]["start"], "last_end:", segs[-1]["end"])
print("subtitle_span_s:", round(segs[-1]["end"] - segs[0]["start"], 2))
print("SRT saved:", out_path)
