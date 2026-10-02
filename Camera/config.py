CAMERA_SIZE = (480, 480)
INPUT_SIZE = 320

CROP_RATIO = 0.85

CONF_THRESHOLD = 0.5
NMS_THRESHOLD = 0.45

CLASS_NAMES = [
    "eye_closed",
    "eye_open",
    "head_dropped",
    "head_straight",
    "no_yawn",
    "yawn"
]

MODEL_PARAM = "b_ncnn_model/model.ncnn.param"
MODEL_BIN = "b_ncnn_model/model.ncnn.bin"
