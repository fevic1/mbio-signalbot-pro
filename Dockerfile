FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc git && rm -rf /var/lib/apt/lists/*

ENV CURL_CFFI_DISABLE=1
ENV YF_DATA_NOVERIFY=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

CMD ["python", "main.py"]
# CACHE BUST 1782687580
