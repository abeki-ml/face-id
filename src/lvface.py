# import cv2
# import numpy as np
# import onnxruntime as ort
# from insightface.app import FaceAnalysis
# from insightface.utils import face_align
# model = ort.InferenceSession("src/lvface.onnx", providers=["CPUExecutionProvider"])
# app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"])
# app.prepare(ctx_id=-1)
# def get_lvface_embedding(image):
#         if image is None:
#               return None, "No image provided"
#         faces = app.get(image)
#         if len(faces) != 1:
#           return None, "Please capture exactly one face"
#         face_image = face_align.norm_crop(image,landmark=faces[0].kps)
#         # face_image = cv2.resize(face_image, (112, 112))
#         face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
#         face_image = face_image.astype(np.float32)
#         face_image = (face_image - 127.5) / 128.0


        