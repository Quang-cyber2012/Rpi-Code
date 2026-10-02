import cv2

from .config import (
    CLASS_NAMES,
    CONF_THRESHOLD,
    NMS_THRESHOLD
)


def Decode(output):
    if output is None:
        return []

    if output.ndim == 3:
        output = output[0]

    if output.shape[0] > output.shape[1]:
        output = output.T

    boxes = output[:4, :]
    scores = output[4:, :]

    detections = []

    for i in range(boxes.shape[1]):
        class_scores = scores[:, i]

        class_id = int(class_scores.argmax())
        confidence = float(class_scores[class_id])

        if confidence < CONF_THRESHOLD:
            continue

        cx, cy, w, h = boxes[:, i]

        detections.append({
            "box": [
                float(cx),
                float(cy),
                float(w),
                float(h)
            ],
            "class_id": class_id,
            "label": CLASS_NAMES[class_id],
            "score": confidence
        })

    return detections


def NMS(detections):
    results = []

    for class_id in range(len(CLASS_NAMES)):

        class_detections = [
            d for d in detections
            if d["class_id"] == class_id
        ]

        if not class_detections:
            continue

        boxes = []
        scores = []

        for d in class_detections:
            cx, cy, w, h = d["box"]

            boxes.append([
                float(cx - w / 2),
                float(cy - h / 2),
                float(w),
                float(h)
            ])

            scores.append(d["score"])

        indices = cv2.dnn.NMSBoxes(
            boxes,
            scores,
            CONF_THRESHOLD,
            NMS_THRESHOLD
        )

        if len(indices) == 0:
            continue

        for i in indices.flatten():
            results.append(class_detections[i])

    return results
