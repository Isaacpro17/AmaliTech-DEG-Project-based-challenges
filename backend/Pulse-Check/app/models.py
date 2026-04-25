from enum import Enum
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class MonitorStatus(str, Enum):
    """Enumeration of possible monitor states."""
    active = "active"
    paused = "paused"
    down = "down"

class MonitorCreate(BaseModel):
    """Schema for creating a new heartbeat monitor."""
    id: str = Field(..., description="Unique identifier for the monitor")
    timeout: int = Field(..., gt=0, description="Timeout interval in seconds")
    alert_email: EmailStr = Field(..., description="Email to notify when the monitor fails")

class MonitorRecord(BaseModel):
    """Schema representing the monitor record stored in memory."""
    id: str
    timeout: int
    alert_email: str
    status: MonitorStatus = MonitorStatus.active
    deadline: float
    created_at: float

class MonitorResponse(BaseModel):
    """Schema for API responses containing monitor status and metadata."""
    id: str
    status: MonitorStatus
    timeout: int
    alert_email: str
    seconds_remaining: int
    created_at: float