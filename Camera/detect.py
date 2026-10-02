import ncnn
import numpy as np

from .config import (
    INPUT_SIZE,
    MODEL_PARAM,
    MODEL_BIN
)


net = ncnn.Net()
net.opt.use_vulkan_compute = False

net.load_param(MODEL_PARAM)
net.load_model(MODEL_BIN)

print("NCNN ready")


def Detect(frame):
    mat = ncnn.Mat.from_pixels(
        frame,
        ncnn.Mat.PixelType.PIXEL_RGB,
        INPUT_SIZE,
        INPUT_SIZE
    )

    mat.substract_mean_normalize(
        [],
        [
            1 / 255.0,
            1 / 255.0,
            1 / 255.0
        ]
    )

    ex = net.create_extractor()

    ex.input("in0", mat)

    ret, out = ex.extract("out0")

    if ret != 0:
        print("NCNN error:", ret)
        return None

    return np.array(out)
