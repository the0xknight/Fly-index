from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FareObservationCreate(BaseModel):
    source: str = Field(..., description="e.g., mock_generator, amadeus_api, makemytrip")
    origin: str = Field(..., max_length=3, description="IATA airport code (e.g., BOM)")
    destination: str = Field(..., max_length=3, description="IATA airport code (e.g., DEL)")
    route: str = Field(..., description="Canonical route: BOM-DEL")
    airline: str
    flight_number: str
    departure_datetime: datetime
    collection_timestamp: datetime = Field(default_factory=datetime.utcnow)
    days_to_departure: int
    cabin_class: str = "Economy"
    base_fare: float
    taxes_fees: float
    total_fare: float
    baggage_included_kg: int = 15
    is_refundable: bool = False

class FareObservationResponse(FareObservationCreate):
    id: int

    class Config:
        from_attributes = True