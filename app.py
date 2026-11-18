import numpy as np
import cv2
import streamlit as st
from PIL import Image
from src.verification import verify_face
from src.registration import register_face

st.set_page_config(
    page_title="Face Verification System",
    page_icon="🔐",
    layout="centered"
)

st.title("Face Verification System")

st.write(
    "Register your face and verify your identity securely."
)

menu = st.sidebar.selectbox(
    "Choose an option",
    ["Register Face", "Verify Face"]
)

if menu == "Register Face":
    st.header("Face Registration")
    st.write("Enter your name and capture your face to")

    name = st.text_input("Enter your full name")

    picture = st.camera_input("Capture your face")

    if st.button("Register"):
        if name and picture:
            image = Image.open(picture).convert("RGB")
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
         
            success, message = register_face(name, image)
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.warning("Please enter your name and capture your face.")

elif menu == "Verify Face":
    st.header("Face Verification")
    picture = st.camera_input("Capture your face")
    if st.button("Verify Identity"):
        if picture:
            image = Image.open(picture).convert("RGB")
            image = np.array(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            success, message = verify_face(image)
            if success:
                st.success(message)
            else:
                st.error(message)
        else:
            st.warning("Please capture your face for verification.")
