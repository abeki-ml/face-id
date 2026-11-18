from insightface.app import FaceAnalysis
import cv2
import sys
from sklearn.metrics.pairwise import cosine_similarity

app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
app.prepare(ctx_id=-1)
print("Model loaded successfully!")

img1 = cv2.imread("Untitled.jpeg")
img2 = cv2.imread("second.jpeg")

if img1 is None or img2 is None:
    print("Image not found!")
    sys.exit()

face1 = app.get(img1)
face2 = app.get(img2)
if len(face1) != 1 or len(face2) != 1:
    print("no face detected")
    sys.exit()

embedding1 = face1[0].embedding
embedding2 = face2[0].embedding


similarity  = cosine_similarity(
    [embedding1],
    [embedding2]
)

# print(similarity[0][0])

score = similarity[0][0]
if score >= 0.5:
    print("match")
else:
    print("not a match")