import os, time
print("TINY_PROBE_START pid=%d" % os.getpid(), flush=True)
t0 = time.time()
try:
    import numpy as np
    print("numpy=%s" % np.__version__, flush=True)
    from faster_whisper import WhisperModel
    m = WhisperModel(r"D:\nigredo\data\models\faster-whisper-tiny", device="cpu", compute_type="int8")
    print("TINY_CPU_LOAD_OK %.1fs" % (time.time() - t0), flush=True)
except BaseException as e:
    print("TINY_CPU_EXC %r" % (e,), flush=True)
print("TINY_PROBE_DONE", flush=True)
