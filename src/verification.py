from insightface.app import FaceAnalysis
import cv2
import numpy as np
import os
import re
from sklearn.metrics.pairwise import cosine_similarity  

app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1)

def verify_face(image):
    if image is None:
        return False, "No image provided"
    faces = app.get(image)
    
    if len(faces) != 1:
        return False, "Please capture an image with exactly one face!"
    embedding = faces[0].embedding
    files = os.listdir("data/registered_users")
    if not files:
        return False, "No registered users found."
    for file in files:
        similarity_score = []
        embedding_path = os.path.join("data/registered_users", file)
        registered_embeddings = np.load(embedding_path)
        for saved_embeding in registered_embeddings:
            similarity = cosine_similarity(
                [embedding],
                [saved_embeding]
            )[0][0]
            similarity_score.append(similarity)
        max_similarity = max(similarity_score)
        if max_similarity >= 0.5:
            return True, f"Identity verified! Matched with {file.split('.')[0]}."
    return False, "Identity not recognized."
