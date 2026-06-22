# Serviço de IA (FastAPI + Uvicorn) — Fase 3.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/ai-service

# Bibliotecas de sistema: OpenCV/Ultralytics (libgl1, libglib2.0-0) e WeasyPrint para o PDF do
# relatório automático (Pango/cairo/gdk-pixbuf + fontes) — Fase 6 (F6-03). Sem estas libs, o
# relatório degrada para HTML sem quebrar (design DD7).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 \
        libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 libffi-dev \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app/ai-service

COPY requirements.txt ./
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
