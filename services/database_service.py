import os
from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URI")  # e.g. postgresql+psycopg2://user:pass@localhost/dbname

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# Pydantic model (for validation & typing)
class EmergencyResponse(BaseModel):
    emergency_type: str
    person_profile: Dict[str, str]
    location: Dict[str, str]
    time_of_incident: str
    people_affected: int
    immediate_risks: List[str]
    resources_needed: List[str]
    additional_notes: str

#ORM Models
class RawQuery(Base):
    __tablename__ = "user_query"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(JSON, nullable=False)
    transcript = Column(String, nullable=True)
    response = Column(JSON, nullable=True)

    # Backref from EmergencyResponseDB
    emergency_responses = relationship("EmergencyResponseDB", back_populates="raw_query")


class EmergencyResponseDB(Base):
    __tablename__ = "emergency_responses"

    id = Column(Integer, primary_key=True, index=True)
    raw_query_id = Column(Integer, ForeignKey("user_query.id"), nullable=False)  # FK to RawQuery.id
    emergency_type = Column(String, nullable=False)
    person_profile = Column(JSON, nullable=False)
    location = Column(JSON, nullable=False)
    time_of_incident = Column(String, nullable=False)
    people_affected = Column(Integer, nullable=False)
    immediate_risks = Column(JSON, nullable=False)
    resources_needed = Column(JSON, nullable=False)
    additional_notes = Column(String)

    # Relationship back to RawQuery
    raw_query = relationship("RawQuery", back_populates="emergency_responses")

# Create the table in DB (run frst time only)
Base.metadata.drop_all(bind=engine)   # Drops all tables
Base.metadata.create_all(bind=engine) # Creates all tables with current models

# Save an EmergencyResponse Pydantic object to DB
def save_emergency(data: EmergencyResponse, raw_query_id: int) -> EmergencyResponseDB:
    db = SessionLocal()
    try:
        db_item = EmergencyResponseDB(raw_query_id=raw_query_id, **data.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    finally:
        db.close()

#Just to test it works/show how to use

def testDB():
    db = SessionLocal()
    try:
        # 1. Create and save a RawQuery
        raw_query = RawQuery(
            query={"text": "Help! Fire at 123 Main St."},
            transcript="Help fire at one two three Main Street",
            response=None
        )
        db.add(raw_query)
        db.commit()
        db.refresh(raw_query)

        # 2. Create Pydantic EmergencyResponse
        response = EmergencyResponse(
            emergency_type="Fire",
            person_profile={"age": "45", "gender": "Male", "medical_conditions": "Asthma"},
            location={"address": "123 Main St", "landmarks": "Near park", "coordinates": "40.7128,-74.0060"},
            time_of_incident="2025-08-12T14:00:00Z",
            people_affected=3,
            immediate_risks=["Smoke inhalation", "Structural collapse"],
            resources_needed=["Firetruck", "Ambulance"],
            additional_notes="Caller reports trapped individuals"
        )

        # 3. Save EmergencyResponse with raw_query_id FK
        saved = save_emergency(response, raw_query_id=raw_query.id)

        print(f"RawQuery ID: {raw_query.id}")
        print(f"Saved EmergencyResponse ID: {saved.id}, Type: {saved.emergency_type}")
    finally:
        db.close()




testDB()


