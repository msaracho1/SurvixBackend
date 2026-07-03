"""One-off script: create the resenia_guia table used by guide reviews.

Uses the existing GuideReview SQLAlchemy model, so the generated DDL always
matches app/models/entities.py regardless of whether the DB is MySQL,
Postgres, etc. Safe to re-run: checkfirst=True skips creation if the table
already exists.

Usage (from the backend project root, with your .env / DATABASE_URL set):

    python create_guide_review_table.py
"""
from app.database import engine
from app.models.entities import GuideReview

if __name__ == "__main__":
    GuideReview.__table__.create(bind=engine, checkfirst=True)
    print("resenia_guia table created (or already existed).")
