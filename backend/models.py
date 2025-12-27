from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Log(SQLModel, table=True):
    __tablename__ = "logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    event: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    comments: Optional[str] = None
    end_timestamp: Optional[datetime] = Field(default=None)
    orientation: Optional[str] = None
    feed_id: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
