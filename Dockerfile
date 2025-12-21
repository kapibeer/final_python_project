FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV ORT_LOGGING_LEVEL=ERROR

RUN python - <<'EOF'
from rembg import remove
from PIL import Image
import io, os

img = Image.new("RGB", (10, 10), color="white")
buf = io.BytesIO()
img.save(buf, format="PNG")
remove(buf.getvalue())

path = os.path.expanduser("~/.u2net/u2net.onnx")
assert os.path.exists(path), f"Model not found at {path}"
print("rembg model ok:", path)
EOF

COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
