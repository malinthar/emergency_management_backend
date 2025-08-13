import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URI")  

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

# ----------------------
# Pydantic model
# ----------------------
class EmergencyResponse(BaseModel):
    emergency_type: str
    person_profile: Dict[str, str]
    location: Dict[str, str]
    time_of_incident: str
    people_affected: int
    immediate_risks: List[str]
    resources_needed: List[str]
    additional_notes: str
    severity: str | None = None  # Added so Pydantic matches DB


# ----------------------
# ORM Models
# ----------------------
class EmergencyReportDB(Base):
    __tablename__ = "emergency_reports"

    report_id = Column(String, primary_key=True)
    generated_at = Column(DateTime, default=datetime.datetime.utcnow)
    emergency_details = Column(JSON)  # Store ExtractedEmergencyData as dict
    response_details = Column(JSON, nullable=True)
    status = Column(String, default="open")


class RawQuery(Base):
    __tablename__ = "user_query"

    id = Column(Integer, primary_key=True, autoincrement=True)
    query = Column(JSON, nullable=False)
    transcript = Column(String, nullable=True)
    response = Column(JSON, nullable=True)

    emergency_responses = relationship("EmergencyResponseDB", back_populates="raw_query")


class EmergencyResponseDB(Base):
    __tablename__ = "emergency_responses"

    id = Column(Integer, primary_key=True, index=True)
    raw_query_id = Column(Integer, ForeignKey("user_query.id"), nullable=False)
    emergency_type = Column(String, nullable=False)
    person_profile = Column(JSON, nullable=False)
    location = Column(JSON, nullable=False)
    time_of_incident = Column(String, nullable=False)
    people_affected = Column(Integer, nullable=False)
    immediate_risks = Column(JSON, nullable=False)
    resources_needed = Column(JSON, nullable=False)
    additional_notes = Column(String)
    severity = Column(String, nullable=True)  # <-- Added to match ExtractedEmergencyData

    raw_query = relationship("RawQuery", back_populates="emergency_responses")


# ----------------------
# Create Tables (Dev Only)
# # ----------------------
# Base.metadata.drop_all(bind=engine)   # Dev only — wipes DB
# Base.metadata.create_all(bind=engine) # Creates all tables with current models


# ----------------------
# Save Functions
# ----------------------
def save_emergency(data: EmergencyResponse, raw_query_id: int) -> EmergencyResponseDB:
    db = SessionLocal()
    try:
        db_item = EmergencyResponseDB(raw_query_id=raw_query_id, **data.model_dump())  # Pydantic v2 fix
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item
    finally:
        db.close()


def save_report_to_db(report_data: dict):
    session = SessionLocal()
    try:
        db_report = EmergencyReportDB(
            report_id=report_data["report_id"],
            generated_at=datetime.datetime.fromisoformat(report_data["generated_at"]),
            emergency_details=(
                report_data["emergency_details"].model_dump()
                if hasattr(report_data["emergency_details"], "model_dump")
                else report_data["emergency_details"]
            ),
            response_details=(
                report_data["response_details"].model_dump()
                if hasattr(report_data["response_details"], "model_dump")
                else report_data["response_details"]
            ),
            status=report_data["status"]
        )
        session.add(db_report)
        session.commit()
        print(f"✅ Report {db_report.report_id} saved successfully")
    except Exception as e:
        session.rollback()
        print(f"❌ Error saving report: {e}")
    finally:
        session.close()


# ----------------------
# Test Functions
# ----------------------
def testDB():
    db = SessionLocal()
    try:
        raw_query = RawQuery(
            query={"text": "Help! Fire at 123 Main St."},
            transcript="Help fire at one two three Main Street",
            response=None
        )
        db.add(raw_query)
        db.commit()
        db.refresh(raw_query)

        response = EmergencyResponse(
            emergency_type="Fire",
            person_profile={"age": "45", "gender": "Male", "medical_conditions": "Asthma"},
            location={"address": "123 Main St", "landmarks": "Near park", "coordinates": "40.7128,-74.0060"},
            time_of_incident="2025-08-12T14:00:00Z",
            people_affected=3,
            immediate_risks=["Smoke inhalation", "Structural collapse"],
            resources_needed=["Firetruck", "Ambulance"],
            additional_notes="Caller reports trapped individuals",
            severity="high"
        )

        saved = save_emergency(response, raw_query_id=raw_query.id)

        print(f"RawQuery ID: {raw_query.id}")
        print(f"Saved EmergencyResponse ID: {saved.id}, Type: {saved.emergency_type}")
    finally:
        db.close()


# def test_full_flow():
#     db = SessionLocal()
#     try:
#         raw_query = RawQuery(
#             query={"text": "There is flooding near my home"},
#             transcript="Flooding near my home at 456 Elm Street",
#             response=None
#         )
#         db.add(raw_query)
#         db.commit()
#         db.refresh(raw_query)

#         emergency_data = ExtractedEmergencyData(
#             emergency_type="Hungry",
#             person_profile={"age": "32", "gender": "Female", "medical_conditions": "None"},
#             location={"address": "456 Elm St", "landmarks": "Opposite grocery store", "coordinates": "40.7128,-74.0060"},
#             time_of_incident="2025-08-13T09:00:00Z",
#             people_affected=12,
#             immediate_risks=["Water contamination", "Electrical hazards"],
#             resources_needed=["Rescue boat", "Medical team"],
#             additional_notes="Rising water levels in residential area",
#             severity="high"
#         )

#         saved_response = save_emergency(emergency_data, raw_query_id=raw_query.id)

#         report_data = EmergencyTools.generate_report(emergency_data)


#         save_report_to_db(report_data)

#         print(f"✅ Test flow complete")
#         print(f"RawQuery ID: {raw_query.id}")
#         print(f"EmergencyResponse ID: {saved_response.id}")
#         print(f"Report ID: {report_data['report_id']}")
#     finally:
#         db.close()


# # Run test
# test_full_flow()