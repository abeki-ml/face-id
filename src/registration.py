from insightface.app import FaceAnalysis
import numpy as np
import os
import re

app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1)

def register_face(name, image):

    if image is None:
        return False, "No image provided"
    
    faces = app.get(image)
    
    if len(faces) != 1:
        return False, "Please capture an image with exactly one face!"
    embedding = faces[0].embedding
    
    person_id = re.sub(r"[^a-zA-Z0-9_-]", "_", name.strip())
    if not person_id:
        return False, "Please provide a valid name!"

    folder = "data/registered_users"
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, person_id + ".npy")

    if os.path.exists(file_path):
        old_embeddings = np.load(file_path)
        embeddings = np.vstack((old_embeddings, [embedding]))
    else:
        embeddings = np.array([embedding])
    np.save(file_path, embeddings)
    return True, "Registration successful!"