## System Architecture

### Heartbeat Sequence Flow
```mermaid
sequenceDiagram
    participant Device as External Device/Service
    participant API as Pulse-Check-API
    participant BS as Background Scheduler

    Device->>API: POST /monitors (Initial Setup)
    API-->>API: Start countdown timer
    
    loop Monitoring
        Device->>API: POST /monitors/{id}/heartbeat
        API-->>API: Reset timer to full timeout
    end

    BS->>BS: Check deadlines (every 1s)
    Note over BS: If deadline < current_time
    BS->>BS: Log Alert + Mark Status "down"

    Device->>API: POST /monitors/{id}/pause
    API-->>API: Stop/Remove timer

    Device->>API: Heartbeat (on paused monitor)
    API-->>API: Set status "active" + Restart timer


    stateDiagram-v2
    [*] --> active: Monitor Created
    active --> down: Timer Expires
    active --> paused: /pause called
    paused --> active: Heartbeat received
    down --> active: Heartbeat received


    