FROM python:3.12-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       espeak-ng \
       libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /models \
    && curl -fL --retry 4 \
       https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx \
       -o /models/kokoro-v1.0.int8.onnx \
    && curl -fL --retry 4 \
       https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin \
       -o /models/voices-v1.0.bin

COPY app.py .

RUN useradd -m -u 10001 kokoro \
    && chown -R kokoro:kokoro /app /models

USER kokoro

EXPOSE 8000

CMD ["uvicorn", "app:api", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
