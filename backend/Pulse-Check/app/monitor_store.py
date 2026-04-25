from app.models import MonitorRecord

# The in-memory data store
monitors: dict[str, MonitorRecord] = {}

def add_monitor(record: MonitorRecord) -> None:
    """Adds a new monitor record to the in-memory store."""
    monitors[record.id] = record

def get_monitor(monitor_id: str) -> MonitorRecord | None:
    """Retrieves a monitor record by its ID. Returns None if not found."""
    return monitors.get(monitor_id)

def get_all_monitors() -> list[MonitorRecord]:
    """Returns a list of all monitor records currently in the store."""
    return list(monitors.values())

def update_monitor(record: MonitorRecord) -> None:
    """Overwrites an existing monitor record in the store using its ID."""
    monitors[record.id] = record

def delete_monitor(monitor_id: str) -> None:
    """Removes a monitor record from the store by its ID."""
    if monitor_id in monitors:
        del monitors[monitor_id]