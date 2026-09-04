# AnimAI backend — runnable alone or via docker-compose
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ANIMAI_HOST=0.0.0.0 \
    ANIMAI_PORT=8000 \
    ANIMAI_DATA_DIR=/app/data

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir .

RUN mkdir -p /app/data/images /app/data/masks /app/data/layers /app/data/exports

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
