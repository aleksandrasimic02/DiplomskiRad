#!/usr/bin/env bash
set -e

# obavezno: DATABASE_URL npr. postgresql+psycopg2://user:pass@db:5432/mediplan
if [ -z "$DATABASE_URL" ]; then
  echo "ERROR: DATABASE_URL env var nije setovan"; exit 1
fi

echo "📡 Čekam da se DB podigne..."
# najjednostavnije pingovanje preko psql (instaliran u bazi, ali ne u ovom imidžu),
# zato koristimo python pokušaj konekcije
python - <<'PY'
import os, time
from sqlalchemy import create_engine, text
url = os.environ["DATABASE_URL"]
for i in range(60):
    try:
        e = create_engine(url, pool_pre_ping=True)
        with e.connect() as c:
            c.execute(text("SELECT 1"))
        print("✅ DB je spreman"); break
    except Exception as ex:
        print("⏳ DB nije spreman još... ", ex)
        time.sleep(2)
else:
    raise SystemExit("❌ DB nije dostupan")
PY

echo "🛠️  init_db()"
python - <<'PY'
from app.db.init_db import init_db
init_db()
print("✅ init_db završeno")
PY

if [ "${RUN_SEED:-0}" = "1" ]; then
  echo "🌱 Seedujem (wipe=${WIPE_DB:-0})..."
  if [ "${WIPE_DB:-0}" = "1" ]; then
    python -m app.tools.seed --wipe
  else
    python -m app.tools.seed
  fi
  echo "✅ Seeding gotovo"
fi

echo "🚀 Uvicorn start (servira i /frontend)"
# Važno: app.main:app treba da postoji.
# Ako u app.main nema statike, vidi napomenu ispod.
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
