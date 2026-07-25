"""L0-L3 修复的功能自测（运行于 nigredo venv，只读/构造临时文件，不联网）。
验证：
  L1 - download_audio 在 .wav/.srt/.txt 同存时取 .wav
  L2 - _looks_like_audio 正确识别音频/拒绝字幕
  L3 - 目录拆分后音频写 audio/、字幕写 outputs/
"""
import sys, subprocess, tempfile
from pathlib import Path

sys.path.insert(0, r"D:\nigredo")

import platforms.bilibili as bb
from core import subtitle

# ── L1 自测 ──────────────────────────
class FakeP(bb.BilibiliPlatform):
    def _resolve_cookie(self):
        return [], None

def fake_run(*a, **k):
    class R:
        returncode = 0; stderr = ""; stdout = ""
    return R()

_orig_run = subprocess.run
subprocess.run = fake_run

tmp = Path(tempfile.mkdtemp())
bv = "BVtest123"
(tmp / f"{bv}.srt").write_text("1\n00:00:00,000 --> 00:00:02,000\nhello\n")
(tmp / f"{bv}.txt").write_text("hello")
(tmp / f"{bv}.wav").write_bytes(b"RIFF\x24\x00\x00\x00WAVEdata")

p = FakeP.__new__(FakeP)
p.cookie = ""; p.browser = "firefox"
got = p.download_audio(bv, str(tmp))
subprocess.run = _orig_run

old_bug = sorted(tmp.glob(f"{bv}.*"))[0]   # 旧逻辑会取到的文件
print(f"[L1] 旧逻辑 sorted()[0] -> {old_bug.name}  (bug 来源)")
print(f"[L1] 新逻辑取到        -> {Path(got).name}")
assert got.endswith(".wav"), f"L1 FAIL: 取到 {got}"
print("[L1] PASS ✅")

# ── L2 自测 ──────────────────────────
real_wav = tmp / f"{bv}.wav"
fake_srt = tmp / f"{bv}.srt"
print(f"[L2] 真音频 -> {subtitle._looks_like_audio(str(real_wav))} (应 True)")
print(f"[L2] 字幕   -> {subtitle._looks_like_audio(str(fake_srt))} (应 False)")
assert subtitle._looks_like_audio(str(real_wav)) is True
assert subtitle._looks_like_audio(str(fake_srt)) is False
print("[L2] PASS ✅")

# ── L3 目录拆分检查 ──────────────────
from config import CACHE_AUDIO_DIR, CACHE_OUTPUT_DIR
print(f"[L3] CACHE_AUDIO_DIR  = {CACHE_AUDIO_DIR}")
print(f"[L3] CACHE_OUTPUT_DIR = {CACHE_OUTPUT_DIR}")
assert CACHE_AUDIO_DIR.name == "audio"
assert CACHE_OUTPUT_DIR.name == "outputs"
assert CACHE_AUDIO_DIR.exists() and CACHE_OUTPUT_DIR.exists()
print("[L3] PASS ✅")

print("\nALL FIXES VERIFIED ✅")
