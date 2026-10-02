from .camera import CameraRead, PrepareFrame, CameraStop
from .analyze import Analyze_Frame


if __name__ == "__main__":

    try:
        while True:
            frame = CameraRead()
            frame = PrepareFrame(frame)

            result = Analyze_Frame(frame)

            print(result)

    except KeyboardInterrupt:
        print("Stopping AI test...")

    finally:
        CameraStop()
