import os
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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

# SQLAlchemy ORM model (maps to DB table)
class EmergencyResponseDB(Base):
    __tablename__ = "emergency_responses"

    id = Column(Integer, primary_key=True, index=True)
    emergency_type = Column(String, nullable=False)
    person_profile = Column(JSON, nullable=False)  # dict stored as JSON
    location = Column(JSON, nullable=False)        # dict stored as JSON
    time_of_incident = Column(String, nullable=False)
    people_affected = Column(Integer, nullable=False)
    immediate_risks = Column(JSON, nullable=False)  # list stored as JSON
    resources_needed = Column(JSON, nullable=False) # list stored as JSON
    additional_notes = Column(String)

# # Create the table(s) in DB (run once)
# Base.metadata.create_all(bind=engine)

# Save an EmergencyResponse Pydantic object to DB
def save_emergency(data: EmergencyResponse) -> EmergencyResponseDB:
    db = SessionLocal()
    try:
        db_item = EmergencyResponseDB(**data.dict())
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    finally:
        db.close()

# Example usage (uncomment to test)
# response = EmergencyResponse(
#     emergency_type="Fire",
#     person_profile={"age": "45", "gender": "Male", "medical_conditions": "Asthma"},
#     location={"address": "123 Main St", "landmarks": "Near park", "coordinates": "40.7128,-74.0060"},
#     time_of_incident="2025-08-12T14:00:00Z",
#     people_affected=3,
#     immediate_risks=["Smoke inhalation", "Structural collapse"],
#     resources_needed=["Firetruck", "Ambulance"],
#     additional_notes="Caller reports trapped individuals"
# )
# saved = save_emergency(response)
# print(saved.id, saved.emergency_type)

