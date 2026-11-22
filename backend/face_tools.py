import cv2
import numpy as np
from insightface.app import FaceAnalysis

# Load the face model ONE time, when the server starts.
model = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"], providers=["CPUExecutionProvider"])
model.prepare(ctx_id=-1, det_size=(640, 640))


def read_image(file_bytes):
    """Turn an uploaded picture into an image. Gives None if it is not a picture."""
    pixels = np.frombuffer(file_bytes, dtype=np.uint8)
    return cv2.imdecode(pixels, cv2.IMREAD_COLOR)


def get_fingerprint(image):
    """Find the face in the image and return its fingerprint (512 numbers).
    Gives None if there is no face."""
    faces = model.get(image)
    if len(faces) == 0:
        return None
    biggest = max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
    return biggest.normed_embedding