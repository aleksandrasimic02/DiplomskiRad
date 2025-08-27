# app/db/init_db.py

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.models import *  # noqa
from app.core.config import settings

# --- Ekstenzije ---
DDL_CREATE_CITEXT = "CREATE EXTENSION IF NOT EXISTS citext;"

# --- Bezbedna verzija: set_updated_at() ---
# Ako tabela nema kolonu 'updated_at', funkcija samo vrati NEW bez izmene.
DDL_UPDATED_AT_FN_SAFE = """
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
DECLARE
  has_col boolean;
BEGIN
  SELECT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = TG_TABLE_SCHEMA
      AND table_name   = TG_TABLE_NAME
      AND column_name  = 'updated_at'
  ) INTO has_col;

  IF has_col THEN
    NEW.updated_at := NOW();
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

# --- Recept provera (ostaje kao kod tebe; zadrži '%%' u poruci) ---
DDL_CHECK_RECEPT_FN = """
CREATE OR REPLACE FUNCTION trg_pretplata_lek_provera_recepta()
RETURNS TRIGGER AS $$
DECLARE
    v_potreban BOOLEAN;
BEGIN
    SELECT potreban_recept INTO v_potreban FROM lekovi WHERE id = NEW.id_leka;

    IF v_potreban IS TRUE AND (NEW.recept_dokument IS NULL OR length(trim(NEW.recept_dokument)) = 0) THEN
        RAISE EXCEPTION 'Lek (id=%%) zahteva recept: recept_dokument je obavezan.', NEW.id_leka
            USING ERRCODE = '23514';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""

DDL_CHECK_RECEPT_TRIGGER = """
DROP TRIGGER IF EXISTS trg_check_recept ON pretplata_lek;
CREATE TRIGGER trg_check_recept
BEFORE INSERT OR UPDATE ON pretplata_lek
FOR EACH ROW EXECUTE FUNCTION trg_pretplata_lek_provera_recepta();
"""

DDL_ONE_GUARDIAN_PER_USER = """
CREATE UNIQUE INDEX IF NOT EXISTS uq_one_guardian_per_user
ON staratelji (id_korisnika)
WHERE id_korisnika IS NOT NULL;
"""

# Flag iz .env; podrazumevano isključeno
ENABLE_UPDATED_AT_TRIGGERS = getattr(settings, "ENABLE_UPDATED_AT_TRIGGERS", False)

def _sync_updated_at_triggers(enable: bool):
    """
    Ako je enable=False:
      - obriši sve set_updated_at trigere i funkciju (ako postoji).
    Ako je enable=True:
      - napravi bezbednu funkciju i trigere SAMO na tabelama koje imaju 'updated_at'.
    """
    # Pokupi realna imena tabela iz SQLAlchemy metadata
    table_names = list(Base.metadata.tables.keys())

    with engine.begin() as conn:
        if not enable:
            # Drop svih potencijalnih trigera i funkcije
            for tbl in table_names:
                conn.exec_driver_sql(f"DROP TRIGGER IF EXISTS set_{tbl}_updated_at ON {tbl};")
                conn.exec_driver_sql(f"DROP TRIGGER IF EXISTS trg_{tbl}_set_updated_at ON {tbl};")  # fallback ako si menjao ime
                conn.exec_driver_sql(DDL_ONE_GUARDIAN_PER_USER)
            conn.exec_driver_sql("DROP FUNCTION IF EXISTS set_updated_at() CASCADE;")
            return

        # Enable grana: napravi bezbednu funkciju
        conn.exec_driver_sql(DDL_UPDATED_AT_FN_SAFE)

        # Za svaku tabelu: obriši postojeći trigger; napravi ga samo ako kolona postoji
        for tbl in table_names:
            conn.exec_driver_sql(f"DROP TRIGGER IF EXISTS set_{tbl}_updated_at ON {tbl};")
            conn.exec_driver_sql(f"DROP TRIGGER IF EXISTS trg_{tbl}_set_updated_at ON {tbl};")
            conn.exec_driver_sql(f"""
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_schema='public' AND table_name='{tbl}' AND column_name='updated_at'
  ) THEN
    CREATE TRIGGER set_{tbl}_updated_at
    BEFORE UPDATE ON {tbl}
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
  END IF;
END $$;
""")

def init_db():
    # 1) Ekstenzije
    with engine.begin() as conn:
        conn.exec_driver_sql(DDL_CREATE_CITEXT)

    # 2) Tabele
    Base.metadata.create_all(bind=engine)

    # 3) Triger za recept (uvek postoji, nevezano za updated_at kolonu)
    with engine.begin() as conn:
        conn.exec_driver_sql(DDL_CHECK_RECEPT_FN)
        conn.exec_driver_sql(DDL_CHECK_RECEPT_TRIGGER)

    # 4) set_updated_at trigere uskladi sa željenim stanjem (env flag)
    _sync_updated_at_triggers(ENABLE_UPDATED_AT_TRIGGERS)
