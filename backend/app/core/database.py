from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./data/airfare.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FareObservationRecord(Base):
    __tablename__ = "fare_observations"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, nullable=False)
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    route = Column(String(10), nullable=False, index=True)
    airline = Column(String(50), nullable=False)
    flight_number = Column(String(20), nullable=False)
    departure_datetime = Column(DateTime, nullable=False)
    collection_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    days_to_departure = Column(Integer, nullable=False)
    cabin_class = Column(String(20), default="Economy")
    base_fare = Column(Float, nullable=False)
    taxes_fees = Column(Float, nullable=False)
    total_fare = Column(Float, nullable=False)
    baggage_included_kg = Column(Integer, default=15)
    is_refundable = Column(Boolean, default=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()