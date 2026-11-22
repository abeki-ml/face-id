import os
import io
import psycopg
import uuid
from fastapi.staticfiles import StaticFiles
from supabase import create_client
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

import face_tools
load_dotenv()
app = FastAPI(title="Face ID")
DATABASE_URL = os.getenv("DATABASE_URL")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
def upload_embedding(person_id, fingerprint):
    file_path = f"{person_id}.npy"

    buffer = io.BytesIO()
    np.save(buffer, fingerprint)

    buffer.seek(0)

    supabase.storage.from_("face-embeddings").upload(
        file_path,
        buffer.getvalue(),
        {"content-type": "application/octet-stream"}
    )

def download_embedding(person_id):
    file_path = f"{person_id}.npy"

    file_data = supabase.storage.from_("face-embeddings").download(file_path)

    fingerprint = np.load(io.BytesIO(file_data))

    return fingerprint
# Let our React page (port 5173) talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# A score at or above this means "same person"
THRESHOLD = 0.40

def save_user(person_id, name):
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute(
            "INSERT INTO users (id, name) VALUES (%s, %s)",
            (person_id, name)
        )
def get_users():
    with psycopg.connect(DATABASE_URL) as connection:
        result = connection.execute(
            "SELECT id, name FROM users"
        )

        users = result.fetchall()

    return users
async def fingerprint_of(photo):
    """Read the uploaded photo and return the fingerprint of the face in it."""
    image = face_tools.read_image(await photo.read())
    if image is None:
        raise HTTPException(400, "That file is not a picture")
    fingerprint = face_tools.get_fingerprint(image)
    if fingerprint is None:
        raise HTTPException(400, "No face found. Look at the camera and try again.")
    return fingerprint

def find_best_match(fingerprint):
    best = None

    users = get_users()

    for person_id, name in users:
        saved_fingerprint = download_embedding(person_id)

        score = float(np.dot(saved_fingerprint, fingerprint))

        if best is None or score > best["score"]:
            best = {
                "id": person_id,
                "name": name,
                "score": score
            }

    return best

@app.post("/register")
async def register(name: str = Form(...), photo: UploadFile = File(...)):
    name = name.strip()
    if not 1 <= len(name) <= 40:
        raise HTTPException(400, "Name must be between 1 and 40 characters")

    fingerprint = await fingerprint_of(photo)

    # The same face must not be registered twice
    best = find_best_match(fingerprint)
    if best is not None and best["score"] >= THRESHOLD:
        raise HTTPException(409, f"This face is already registered as '{best['name']}'")

    # Give this person a unique ID, so two people can share the same name
    person_id = uuid.uuid4().hex[:8]

    upload_embedding(person_id, fingerprint)
    try:
        save_user(person_id, name)
    except Exception:
        supabase.storage.from_("face-embeddings").remove(
            [f"{person_id}.npy"]
        )
        raise HTTPException(500, "Registration failed. Please try again.")
    return {"message": f"{name} is registered"}


@app.post("/verify")
async def verify(photo: UploadFile = File(...)):
    fingerprint = await fingerprint_of(photo)

    best = find_best_match(fingerprint)
    if best is None:
        raise HTTPException(404, "Nobody is registered yet")

    match = best["score"] >= THRESHOLD
    return {
        "match": match,
        "name": best["name"] if match else None,
        "score": round(best["score"], 3),
    }
@app.get("/db-check")
def db_check():
    with psycopg.connect(DATABASE_URL) as connection:
        connection.execute("SELECT 1")

    return {"message": "Database connected successfully"}

@app.get("/storage-check")
def storage_check():
    test_data = b"Face ID storage test"

    supabase.storage.from_("face-embeddings").upload(
        "test.txt",
        test_data,
        {"content-type": "text/plain"}
    )

    downloaded = supabase.storage.from_("face-embeddings").download("test.txt")

    if downloaded == test_data:
        return {"message": "Storage upload and download successful"}

    return {"message": "Storage test failed"}

app.mount("/", StaticFiles(directory="../frontend/dist", html=True), name="site")