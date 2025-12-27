from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, computed_field

class LogBase(BaseModel):
    event: str
    details: Optional[str] = None
    timestamp: Optional[datetime] = None
    comments: Optional[str] = None
    end_timestamp: Optional[datetime] = None
    orientation: Optional[str] = None
    feed_id: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None

class LogCreate(LogBase):
    pass

class LogRead(LogBase):
    id: int

    @computed_field
    @property
    def duration_minutes(self) -> float:
        if not self.details or ":" not in self.details or self.details == "ongoing":
            return 0.0
        try:
            parts = list(map(int, self.details.split(':')))
            return round(float(parts[0]*60 + parts[1] + parts[2]/60), 2)
        except (ValueError, IndexError, TypeError):
            return 0.0

    class Config:
        from_attributes = True

class DailyStats(BaseModel):
    today_count: int
    yesterday_count: int
    delta: int

class FeedStats(BaseModel):
    today_count: int
    today_duration: float
    today_avg: float
    yesterday_count: int
    yesterday_duration: float
    yesterday_avg: float
    count_delta: int
    duration_delta: float
    avg_delta: float

class DiaperStats(BaseModel):
    pee: DailyStats
    poop: DailyStats
    mixed: DailyStats
    total: DailyStats
    last_type: Optional[str]
    last_time_str: Optional[str]
    last_pee_str: Optional[str] = None
    last_poop_str: Optional[str] = None

class TrendPoint(BaseModel):
    date: str
    count: int
    details: Optional[dict] = None

class PredictionPoint(BaseModel):
    time: str
    is_predicted: bool

class DashboardData(BaseModel):
    feeding: FeedStats
    diapers: DiaperStats
    ongoing_feed: Optional[LogRead]
    ongoing_sleep: Optional[LogRead]
    last_completed_feed: Optional[LogRead]
    predictions: Optional[dict] = None
    history: Optional[dict] = None
