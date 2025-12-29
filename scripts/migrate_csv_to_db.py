import sys
from pathlib import Path

# 🔹 Add project root to Python path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

import pandas as pd
from sqlalchemy import text
from core import SessionLocal

CSV_PATH = BASE_DIR / "csv" / "lost_pets_pila_dataset.csv"

def migrate():
    print("📥 Loading CSV...")
    df = pd.read_csv(CSV_PATH)

    print(f"➡️  {len(df)} rows found")

    session = SessionLocal()
    inserted = 0

    try:
        for _, row in df.iterrows():
            session.execute(
                text("""
                    INSERT INTO lost_pets (
                        pet_type,
                        age_years,
                        days_missing,
                        near_water,
                        posted_on_fb,
                        barangay,
                        found
                    ) VALUES (
                        :pet_type,
                        :age_years,
                        :days_missing,
                        :near_water,
                        :posted_on_fb,
                        :barangay,
                        :found
                    )
                """),
                {
                    "pet_type": "unknown",
                    "age_years": float(row["age_years"]),
                    "days_missing": int(row["days_missing"]),
                    "near_water": bool(row["near_water"]),
                    "posted_on_fb": bool(row["posted_on_fb"]),
                    "barangay": row["barangay"],
                    "found": bool(row["found"]),
                }
            )
            inserted += 1

        session.commit()
        print(f"✅ Migration complete — {inserted} rows inserted")

    except Exception as e:
        session.rollback()
        print("❌ Migration failed:", e)

    finally:
        session.close()

if __name__ == "__main__":
    migrate()