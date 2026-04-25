import time
from fastapi import APIRouter, HTTPException, status
from typing import Optional
from app.models import (
    MonitorStatus, 
    MonitorCreate, 
    MonitorRecord, 
    MonitorResponse
)
from app.monitor_store import (
    add_monitor, 
    get_monitor, 
    get_all_monitors, 
    update_monitor, 
    delete_monitor
)

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=MonitorResponse)
async def register_monitor(payload: MonitorCreate):
    """Registers a new monitor. Returns 400 if the ID already exists."""
    if get_monitor(payload.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Monitor with this ID already exists."
        )
    now = time.time()
    record = MonitorRecord(
        id=payload.id,
        timeout=payload.timeout,
        alert_email=payload.alert_email,
        status=MonitorStatus.active,
        deadline=now + payload.timeout,
        created_at=now
    )
    add_monitor(record)
    return MonitorResponse(
        **record.model_dump(),
        seconds_remaining=int(record.deadline - now)
    )

@router.post("/{monitor_id}/heartbeat", response_model=MonitorResponse)
async def heartbeat(monitor_id: str):
    """Resets the monitor timer. Unpauses if paused. 409 if status is down."""
    record = get_monitor(monitor_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found.")
    if record.status == MonitorStatus.down:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Monitor is down and cannot be reset. Please re-register."
        )
    record.status = MonitorStatus.active
    record.deadline = time.time() + record.timeout
    update_monitor(record)
    return MonitorResponse(
        **record.model_dump(),
        seconds_remaining=int(record.deadline - time.time())
    )

@router.post("/{monitor_id}/pause")
async def pause_monitor(monitor_id: str):
    """Pauses an active monitor to stop the watchdog timer."""
    record = get_monitor(monitor_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found.")
    if record.status == MonitorStatus.paused:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Monitor is already paused.")
    if record.status == MonitorStatus.down:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail="Cannot pause a monitor that is already down."
        )
    record.status = MonitorStatus.paused
    update_monitor(record)
    return {"message": f"Monitor {monitor_id} has been paused.", "status": "paused"}

@router.get("/", response_model=list[MonitorResponse])
async def list_monitors(status: Optional[MonitorStatus] = None):
    """
    Returns a list of monitors. Optionally filters by status via query parameter.
    """
    records = get_all_monitors()
    response = []
    now = time.time()

    for r in records:
        # If status filter is provided, skip records that don't match
        if status and r.status != status:
            continue
            
        remaining = max(0, int(r.deadline - now)) if r.status == MonitorStatus.active else 0
        response.append(MonitorResponse(**r.model_dump(), seconds_remaining=remaining))
    
    return response

@router.get("/{monitor_id}", response_model=MonitorResponse)
async def get_single_monitor(monitor_id: str):
    """Retrieves details for a specific monitor by ID."""
    record = get_monitor(monitor_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found.")
    now = time.time()
    remaining = max(0, int(record.deadline - now)) if record.status == MonitorStatus.active else 0
    return MonitorResponse(**record.model_dump(), seconds_remaining=remaining)

@router.delete("/{monitor_id}")
async def remove_monitor(monitor_id: str):
    """Deletes a monitor from the system entirely."""
    if not get_monitor(monitor_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor not found.")
    delete_monitor(monitor_id)
    return {"message": f"Monitor {monitor_id} has been deleted."}