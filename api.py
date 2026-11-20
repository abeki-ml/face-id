from fastapi import FastAPI, UploadFile, File, Form
import cv2
import numpy as np

from src.verification import verify_face
from src.registration import register_face

api = FastAPI()


def convert_image(file_bytes):
    image_array = np.frombuffer(file_bytes, np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    return image


@api.post("/register")
async def register(name: str = Form(...), file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = convert_image(image_bytes)

    success, message = register_face(name, image)

    return {"success": success, "message": message}


@api.post("/verify")
async def verify(file: UploadFile = File(...)):
    image_bytes = await file.read()
    image = convert_image(image_bytes)

    success, message = verify_face(image)

    return {"verified": success, "message": message}