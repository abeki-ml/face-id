FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install the libraries, then install insightface WITHOUT its extra libraries
# (they would bring a second, bigger copy of OpenCV)
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --no-deps insightface

# Download the face model now, then delete the parts we don't use and the leftover zip
RUN python -c "from insightface.app import FaceAnalysis; FaceAnalysis(name='buffalo_l', allowed_modules=['detection', 'recognition'], providers=['CPUExecutionProvider'])" \
    && cd /root/.insightface/models \
    && rm -f buffalo_l.zip buffalo_l/1k3d68.onnx buffalo_l/2d106det.onnx buffalo_l/genderage.onnx

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]