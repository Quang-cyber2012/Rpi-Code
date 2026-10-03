import time
from Camera import CameraRead, PrepareFrame, Analyze_Frame, CameraStop

try:
    start = time.monotonic()

    for _ in range(50):
        frame = CameraRead()
        frame = PrepareFrame(frame)
        result = Analyze_Frame(frame)

        print(
            f"eye={result['eye']} "
            f"head={result['head']} "
            f"yawn={result['yawn']}"
        )

    elapsed = time.monotonic() - start
    fps = 50 / elapsed

    print(f"FPS: {fps:.2f}")

finally:
    CameraStop()
