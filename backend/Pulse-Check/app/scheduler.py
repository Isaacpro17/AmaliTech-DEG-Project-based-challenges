import threading
import time
import json
from datetime import datetime
from app.models import MonitorStatus
from app.monitor_store import get_all_monitors, update_monitor

def check_monitors() -> None:
    """
    Iterates through all monitors and updates status to 'down' if the deadline has passed.
    """
    records = get_all_monitors()
    current_time = time.time()

    for record in records:
        # Only check monitors that are currently active
        if record.status == MonitorStatus.active:
            if current_time > record.deadline:
                # Update status in the store
                record.status = MonitorStatus.down
                update_monitor(record)
                
                # Print the JSON alert to console
                alert_payload = {
                    "ALERT": f"Device {record.id} is down!",
                    "time": datetime.now().isoformat()
                }
                print(json.dumps(alert_payload))

def start_scheduler() -> None:
    """
    Starts the monitor checker in a background daemon thread.
    """
    def run_loop():
        while True:
            check_monitors()
            time.sleep(1)

    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()