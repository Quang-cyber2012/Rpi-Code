import cv2
from picamera2 import Picamera2

from .config import CAMERA_SIZE, INPUT_SIZE, CROP_RATIO


picam2 = Picamera2()

picam2.configure(
    picam2.create_still_configuration(
        main={
            "size": CAMERA_SIZE,
            "format": "YUV420"
        }
    )
)

picam2.start()


def CameraRead():
    frame_yuv = picam2.capture_array()

    frame = cv2.cvtColor(
        frame_yuv,
        cv2.COLOR_YUV2RGB_I420
    )

    # Bỏ phần stride dư: 512 → 480
    frame = frame[:, :CAMERA_SIZE[0]]

    # Xoay 180°
    frame = cv2.rotate(
        frame,
        cv2.ROTATE_180
    )

    return frame


def PrepareFrame(frame):
    # Tăng sáng
    frame = cv2.convertScaleAbs(
        frame,
        alpha=1.15,
        beta=20
    )

    # Crop giữa
    h, w = frame.shape[:2]

    new_w = int(w * CROP_RATIO)
    new_h = int(h * CROP_RATIO)

    x1 = (w - new_w) // 2
    y1 = (h - new_h) // 2

    frame = frame[
        y1:y1 + new_h,
        x1:x1 + new_w
    ]

    # Resize cho model
    frame = cv2.resize(
        frame,
        (INPUT_SIZE, INPUT_SIZE)
    )

    return frame


def CameraStop():
    picam2.stop()
