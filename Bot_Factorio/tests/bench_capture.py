# bench_capture.py
import mss
import numpy as np
import time

REGION = {"top": 0, "left": 0, "width": 2560, "height": 1600}

with mss.mss() as sct:
    # Chauffe
    for _ in range(5):
        sct.grab(REGION)

    # Bench
    times = []
    for i in range(30):
        t0 = time.perf_counter()
        raw = sct.grab(REGION)
        t1 = time.perf_counter()
        times.append((t1 - t0) * 1000)

    print(f"mss seul — moy={sum(times)/len(times):.1f}ms  "
          f"max={max(times):.1f}ms  min={min(times):.1f}ms")

    # Tester aussi une région réduite
    REGION_SMALL = {"top": 0, "left": 0, "width": 1280, "height": 800}
    times_small = []
    for i in range(30):
        t0 = time.perf_counter()
        raw = sct.grab(REGION_SMALL)
        t1 = time.perf_counter()
        times_small.append((t1 - t0) * 1000)

    print(f"mss 1280x800 — moy={sum(times_small)/len(times_small):.1f}ms  "
          f"max={max(times_small):.1f}ms  min={min(times_small):.1f}ms")