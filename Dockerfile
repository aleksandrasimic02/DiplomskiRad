# ==== base ====
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# psycopg2 i Pillow zahtevaju build alate / libpq
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Ako imaš requirements.txt koristi njega; ako nemaš, ova linija je fallback
 COPY requirements.txt ./
 RUN pip install --timeout 10000 -r requirements.txt
#RUN pip install \
#    "fastapi>=0.110" "uvicorn[standard]>=0.29" \
#    "SQLAlchemy>=2.0" "psycopg2-binary>=2.9" \
#    "python-multipart>=0.0.9" "passlib[bcrypt]>=1.7" \
#    "python-dotenv>=1.0" "pydantic>=2.6"

# kopiramo backend kod
COPY app ./app
# kopiramo frontend (index.html)
COPY frontend ./frontend

# otvorimo port
EXPOSE 8000

# start skripta (cekamo DB, init, seeding)
COPY docker/backend/start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]
