# app/tools/seed.py
from __future__ import annotations
import argparse
from datetime import date

from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine
from app.db.init_db import init_db
from app.core.security import get_password_hash

from app.models.korisnik import Korisnik
from app.models.admin import Administrator
from app.models.apoteka import Apoteka
from app.models.lek import Lek
from app.models.obavestenje import Obavestenje



# --- HARD WIPE: obori ceo public schema i vrati ga čistog ---
def hard_wipe_schema():
    with engine.begin() as conn:
        # skini sve iz public šeme
        conn.exec_driver_sql("DROP SCHEMA IF EXISTS public CASCADE;")
        conn.exec_driver_sql("CREATE SCHEMA public;")
        # osnovne privilegije
        conn.exec_driver_sql("GRANT ALL ON SCHEMA public TO CURRENT_USER;")
        conn.exec_driver_sql("GRANT ALL ON SCHEMA public TO public;")
        # ako koristiš citext u modelima
        conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS citext;")


def _seed_lekovi_for_apoteka1(db: Session, ap: Apoteka):
    """
    Ubaci 10 lekova za datu apoteku.
    - 7 bez recepta, 3 uz recept (npr. #3, #6, #9)
    - razumna cena i dostupnost True
    """
    items: list[Lek] = []
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Enalapril",
            dostupnost=True,
            cena=650,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Deksomen",
            dostupnost=True,
            cena=240,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Paracetamol",
            dostupnost=True,
            cena=200,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Panadol",
            dostupnost=True,
            cena=550,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Brufen",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Analgin",
            dostupnost=True,
            cena=150,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Kardiopirin",
            dostupnost=True,
            cena=300,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Diklofenak",
            dostupnost=True,
            cena=250,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Coldrex",
            dostupnost=True,
            cena=600,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fervex",
            dostupnost=True,
            cena=650,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Panklav",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Metoprolol",
            dostupnost=True,
            cena=550,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Losartan",
            dostupnost=True,
            cena=600,
            potreban_recept=True,
        )
    )


    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Simvastatin",
            dostupnost=True,
            cena=700,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Metformin",
            dostupnost=True,
            cena=500,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Levotiroksin",
            dostupnost=True,
            cena=450,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Sertralin",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fluoksetin",
            dostupnost=True,
            cena=850,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Diazepam",
            dostupnost=True,
            cena=400,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Alprazolam",
            dostupnost=True,
            cena=500,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Salbutamol inhalator",
            dostupnost=True,
            cena=1500,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Loratadin",
            dostupnost=True,
            cena=300,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Cetirizin",
            dostupnost=True,
            cena=320,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Omeprazol",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pantoprazol",
            dostupnost=True,
            cena=450,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Rivaroksaban",
            dostupnost=True,
            cena=1200,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pantenol krema",
            dostupnost=True,
            cena=300,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Belogent krema",
            dostupnost=True,
            cena=500,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Bepanthen",
            dostupnost=True,
            cena=700,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pavlovićeva mast",
            dostupnost=True,
            cena=250,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Sudocrem",
            dostupnost=True,
            cena=600,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Canesten krema",
            dostupnost=True,
            cena=800,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Akriderm",
            dostupnost=True,
            cena=850,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fucidin krema",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Dermatop krema",
            dostupnost=True,
            cena=950,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Nivea Soft",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Eucerin pH5 krema",
            dostupnost=True,
            cena=1800,
            potreban_recept=False,
        )
    )


    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Bioderma Atoderm",
            dostupnost=True,
            cena=2100,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Avene Cold Cream",
            dostupnost=True,
            cena=2000,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Hemofarm Panthenol krema",
            dostupnost=True,
            cena=350,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Cicaplast Baume",
            dostupnost=True,
            cena=2200,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="ZinCure krema",
            dostupnost=True,
            cena=900,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Mixa krema za ruke",
            dostupnost=True,
            cena=450,
            potreban_recept=False,
        )
    )

    db.add_all(items)
    db.commit()

def _seed_lekovi_for_apoteka2(db: Session, ap: Apoteka):
    """
    Ubaci 10 lekova za datu apoteku.
    - 7 bez recepta, 3 uz recept (npr. #3, #6, #9)
    - razumna cena i dostupnost True
    """
    items: list[Lek] = []
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Enalapril",
            dostupnost=True,
            cena=650,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Deksomen",
            dostupnost=True,
            cena=240,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Paracetamol",
            dostupnost=True,
            cena=200,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Brufen",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Analgin",
            dostupnost=True,
            cena=150,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Kardiopirin",
            dostupnost=True,
            cena=300,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Diklofenak",
            dostupnost=True,
            cena=250,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Coldrex",
            dostupnost=True,
            cena=600,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fervex",
            dostupnost=True,
            cena=650,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Panklav",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Amlodipin",
            dostupnost=True,
            cena=500,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Losartan",
            dostupnost=True,
            cena=600,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Atorvastatin",
            dostupnost=True,
            cena=800,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Simvastatin",
            dostupnost=True,
            cena=700,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Insulin glargin",
            dostupnost=True,
            cena=2500,
            potreban_recept=True,
        )
    )


    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fluoksetin",
            dostupnost=True,
            cena=850,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Diazepam",
            dostupnost=True,
            cena=400,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Salbutamol inhalator",
            dostupnost=True,
            cena=1500,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Budesonid inhalator",
            dostupnost=True,
            cena=2000,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Cetirizin",
            dostupnost=True,
            cena=320,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Omeprazol",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pantoprazol",
            dostupnost=True,
            cena=450,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Varfarin",
            dostupnost=True,
            cena=350,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pantenol krema",
            dostupnost=True,
            cena=300,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Belogent krema",
            dostupnost=True,
            cena=500,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pavlovićeva mast",
            dostupnost=True,
            cena=250,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Sudocrem",
            dostupnost=True,
            cena=600,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Canesten krema",
            dostupnost=True,
            cena=800,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fucidin krema",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Dermatop krema",
            dostupnost=True,
            cena=950,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Nivea Soft",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Eucerin pH5 krema",
            dostupnost=True,
            cena=1800,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="La Roche-Posay Lipikar",
            dostupnost=True,
            cena=2200,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Avene Cold Cream",
            dostupnost=True,
            cena=2000,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Mustela Hydra Bébé",
            dostupnost=True,
            cena=1700,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Hemofarm Panthenol krema",
            dostupnost=True,
            cena=350,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="ZinCure krema",
            dostupnost=True,
            cena=900,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Mixa krema za ruke",
            dostupnost=True,
            cena=450,
            potreban_recept=False,
        )
    )

    db.add_all(items)
    db.commit()

def _seed_lekovi_for_apoteka3(db: Session, ap: Apoteka):
    """
    Ubaci 10 lekova za datu apoteku.
    - 7 bez recepta, 3 uz recept (npr. #3, #6, #9)
    - razumna cena i dostupnost True
    """
    items: list[Lek] = []
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Enalapril",
            dostupnost=True,
            cena=650,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Deksomen",
            dostupnost=True,
            cena=240,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Paracetamol",
            dostupnost=True,
            cena=200,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Panadol",
            dostupnost=True,
            cena=550,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Brufen",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Analgin",
            dostupnost=True,
            cena=150,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Kardiopirin",
            dostupnost=True,
            cena=300,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Coldrex",
            dostupnost=True,
            cena=600,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fervex",
            dostupnost=True,
            cena=650,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Panklav",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Metoprolol",
            dostupnost=True,
            cena=550,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Losartan",
            dostupnost=True,
            cena=600,
            potreban_recept=True,
        )
    )


    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Simvastatin",
            dostupnost=True,
            cena=700,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Metformin",
            dostupnost=True,
            cena=500,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Levotiroksin",
            dostupnost=True,
            cena=450,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Sertralin",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fluoksetin",
            dostupnost=True,
            cena=850,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Diazepam",
            dostupnost=True,
            cena=400,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Alprazolam",
            dostupnost=True,
            cena=500,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Salbutamol inhalator",
            dostupnost=True,
            cena=1500,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Budesonid inhalator",
            dostupnost=True,
            cena=2000,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Cetirizin",
            dostupnost=True,
            cena=320,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Omeprazol",
            dostupnost=True,
            cena=400,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pantoprazol",
            dostupnost=True,
            cena=450,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Varfarin",
            dostupnost=True,
            cena=350,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pantenol krema",
            dostupnost=True,
            cena=300,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Belogent krema",
            dostupnost=True,
            cena=500,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Bepanthen",
            dostupnost=True,
            cena=700,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Pavlovićeva mast",
            dostupnost=True,
            cena=250,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Sudocrem",
            dostupnost=True,
            cena=600,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Canesten krema",
            dostupnost=True,
            cena=800,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Akriderm",
            dostupnost=True,
            cena=850,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Fucidin krema",
            dostupnost=True,
            cena=900,
            potreban_recept=True,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Dermatop krema",
            dostupnost=True,
            cena=950,
            potreban_recept=True,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Eucerin pH5 krema",
            dostupnost=True,
            cena=1800,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="La Roche-Posay Lipikar",
            dostupnost=True,
            cena=2200,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Avene Cold Cream",
            dostupnost=True,
            cena=2000,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Mustela Hydra Bébé",
            dostupnost=True,
            cena=1700,
            potreban_recept=False,
        )
    )

    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Cicaplast Baume",
            dostupnost=True,
            cena=2200,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="ZinCure krema",
            dostupnost=True,
            cena=900,
            potreban_recept=False,
        )
    )
    items.append(
        Lek(
            id_apoteke=ap.id,
            naziv="Mixa krema za ruke",
            dostupnost=True,
            cena=450,
            potreban_recept=False,
        )
    )

    db.add_all(items)
    db.commit()


def create_sample_data(db: Session) -> dict:
    out: dict = {}

    # === Obavestenja ===
    obavestenje1 = Obavestenje(
        naziv="Kreirana nova pretplata",
        opis="Proverite svoju sekciju sa pretplatama"
    )
    db.add(obavestenje1)

    obavestenje2 = Obavestenje(
        naziv="Odobrena pretplata",
        opis="Proverite svoju sekciju sa pretplatama"
    )
    db.add(obavestenje2)

    obavestenje3 = Obavestenje(
        naziv="Pretplata ceka aktivaciju",
        opis="Proverite svoju sekciju sa pretplatama"
    )
    db.add(obavestenje3)

    obavestenje4 = Obavestenje(
        naziv="Staratelj odobren",
        opis=""
    )
    db.add(obavestenje4)

    obavestenje5 = Obavestenje(
        naziv="Registrovan novi staratelj",
        opis=""
    )
    db.add(obavestenje5)

    obavestenje6 = Obavestenje(
        naziv="Staratelj uklonjen",
        opis="Proverite svoj profil"
    )
    db.add(obavestenje6)

    obavestenje7 = Obavestenje(
        naziv="Pretplata otkazana",
        opis="Proverite svoju sekciju sa pretplatama"
    )
    db.add(obavestenje7)


    # === Administrator ===
    admin = Administrator(
        ime="Admin",
        prezime="Glavni",
        email="admin@example.com",
        sifra_hash=get_password_hash("admin123!"),
    )
    db.add(admin)

    # === Apoteke (3 kom) ===
    ap1 = Apoteka(
        naziv="Apoteka Zvezda",
        mejl="zvezda@pharm.rs",
        adresa="Kragujevac",
        sifra_hash=get_password_hash("apoteka123"),
    )
    ap2 = Apoteka(
        naziv="Apoteka Sunce",
        mejl="sunce@pharm.rs",
        adresa="Niš",
        sifra_hash=get_password_hash("sunce123"),
    )
    ap3 = Apoteka(
        naziv="Apoteka Dunav",
        mejl="dunav@pharm.rs",
        adresa="Beograd",
        sifra_hash=get_password_hash("dunav123"),
    )
    db.add_all([ap1, ap2, ap3])

    # === Korisnici (3 kom) ===
    k1 = Korisnik(
        ime="Petar",
        prezime="Petrović",
        datum_rodjenja=date(1990, 5, 1),
        adresa="Ulica 1, Kragujevac",
        email="petar@example.com",
        broj_telefona="+381641234567",
        sifra_hash=get_password_hash("user123"),
    )
    k2 = Korisnik(
        ime="Ana",
        prezime="Anić",
        datum_rodjenja=date(1992, 9, 12),
        adresa="Ulica 2, Niš",
        email="ana@example.com",
        broj_telefona="+38160111222",
        sifra_hash=get_password_hash("user123"),
    )
    k3 = Korisnik(
        ime="Marko",
        prezime="Marković",
        datum_rodjenja=date(1988, 3, 20),
        adresa="Ulica 3, Beograd",
        email="marko@example.com",
        broj_telefona="+381621234567",
        sifra_hash=get_password_hash("user123"),
    )
    db.add_all([k1, k2, k3])

    db.commit()
    # refresh da dobijemo ID-jeve
    db.refresh(admin)
    for ap in (ap1, ap2, ap3):
        db.refresh(ap)
    for k in (k1, k2, k3):
        db.refresh(k)

    # === Lekovi: po 10 za svaku apoteku ===
    _seed_lekovi_for_apoteka1(db, ap1)
    _seed_lekovi_for_apoteka2(db, ap2)
    _seed_lekovi_for_apoteka3(db, ap3)

    # --- izlaz za konzolu ---
    out["admin"] = {"email": admin.email, "password": "admin123!"}
    out["apoteke"] = [
        {"mejl": ap1.mejl, "password": "apoteka123"},
        {"mejl": ap2.mejl, "password": "sunce123"},
        {"mejl": ap3.mejl, "password": "dunav123"},
    ]
    out["korisnici"] = [
        {"email": k1.email, "password": "user123"},
        {"email": k2.email, "password": "user123"},
        {"email": k3.email, "password": "user123"},
    ]
    return out


def main():
    parser = argparse.ArgumentParser(description="MediPlan seeder")
    parser.add_argument(
        "--wipe",
        action="store_true",
        help="Nuclear wipe: DROP SCHEMA public CASCADE; pa init_db() i seeding",
    )
    parser.add_argument(
        "--no-data",
        action="store_true",
        help="Samo reset + init_db() bez ubacivanja test podataka",
    )
    args = parser.parse_args()

    # Ako želiš “apsolutno prazno” – prvo obori šemu
    if args.wipe:
        hard_wipe_schema()

    # Uvek zatim kreiraj sve objekte (tabele, trigere, indekse…)
    init_db()

    if args.no_data:
        print("\n✅ Baza resetovana i inicijalizovana (bez seeding podataka).")
        return

    # Ubaci primer podatke
    with SessionLocal() as db:
        data = create_sample_data(db)

    print("\n✅ Seeder završen. Test nalozi:")
    print(f"- Admin:       {data['admin']['email']} / {data['admin']['password']}")
    for ap in data["apoteke"]:
        print(f"- Apoteka:     {ap['mejl']} / {ap['password']}")
    for k in data["korisnici"]:
        print(f"- Korisnik:    {k['email']} / {k['password']}")
    print("\nPrimeri login poziva:")
    print('  POST /auth/login/admin     {"email":"admin@example.com","lozinka":"admin123!"}')
    print('  POST /auth/login/apoteka   {"mejl":"zvezda@pharm.rs","lozinka":"apoteka123"}')
    print('  POST /auth/login/apoteka   {"mejl":"sunce@pharm.rs","lozinka":"sunce123"}')
    print('  POST /auth/login/apoteka   {"mejl":"dunav@pharm.rs","lozinka":"dunav123"}')
    print('  POST /auth/login/korisnik  {"email":"petar@example.com","lozinka":"user123"}')
    print('  POST /auth/login/korisnik  {"email":"ana@example.com","lozinka":"user123"}')
    print('  POST /auth/login/korisnik  {"email":"marko@example.com","lozinka":"user123"}')


if __name__ == "__main__":
    main()
