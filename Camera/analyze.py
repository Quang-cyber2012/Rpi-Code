from .detect import Detect
from .postprocess import Decode, NMS


def Analyze_Frame(frame):

    output = Detect(frame)

    if output is None:
        return {
            "eye": None,
            "head": None,
            "yawn": None
        }

    detections = NMS(Decode(output))

    state = {
        "eye": None,
        "head": None,
        "yawn": None
    }

    for d in detections:

        label = d["label"]

        if label == "eye_open":
            state["eye"] = False

        elif label == "eye_closed":
            state["eye"] = True

        elif label == "head_straight":
            state["head"] = False

        elif label == "head_dropped":
            state["head"] = True

        elif label == "yawn":
            state["yawn"] = True

        elif label == "no_yawn":
            state["yawn"] = False

    return state
