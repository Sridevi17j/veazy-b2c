# Dynamic Trips System - Discussion Notes

## Problem Statement
We want to replace static sidebar tabs with dynamic trip management like ChatGPT:
- Static tabs: "Fastest visa", "Thailand visa" 
- Dynamic trips: Auto-generated meaningful names based on conversations

## Trip Naming Timeline

### Phase 1: Before Information Collection
```
TRIPS
├── New Chat - Dec 1, 2024     [Temporary name]
├── Conversation - Dec 1, 2024  [Generic name]
└── + New Trip
```

### Phase 2: After Base Information (destination + purpose)
```
TRIPS  
├── Vietnam Tourism - Dec 1, 2024    [Auto-generated meaningful name]
├── Thailand Business - Nov 30, 2024
└── + New Trip
```

## ChatGPT Pattern Analysis

### Current State:
```
URL: /visa-genie
Sidebar: [Static tabs - Fastest visa, Thailand visa]
```

### Desired Flow:
```
1. Landing: /visa-genie
   Sidebar: [Clean - no active chats]

2. User types first message: "hi"
   URL: /visa-genie/c/3b25d758-3dca-4990-86f4-4f791d775e9c
   Sidebar: ├── New Chat - Dec 1, 2024

3. After base info collection: 
   URL: Same
   Sidebar: ├── Vietnam Tourism - Dec 1, 2024
```

## Database Schema for `trips` Collection

```python
{
    "trip_id": "3b25d758-3dca-4990-86f4-4f791d775e9c",  # Same as thread_id
    "user_id": "675a1234567890abcdef1234",
    "trip_name": "Vietnam Tourism - Dec 2024",           # Auto-generated display name
    "destination": "Vietnam",
    "visa_type": "Tourism Single Entry", 
    "purpose": "Tourism",
    "travel_dates": "20-25 Dec 2025",
    "status": "in_progress",                             # in_progress, completed, cancelled
    "conversation": [                                    # Full conversation history
        {
            "role": "human",
            "content": "I want to apply for Vietnam visa",
            "timestamp": "2024-12-01T10:30:00Z"
        },
        {
            "role": "ai", 
            "content": "Great! I'll help you with Vietnam visa...",
            "timestamp": "2024-12-01T10:30:15Z"
        }
    ],
    "application_status": {                              # Visa application progress
        "stage": "documents",
        "documents_uploaded": ["passport"],
        "forms_completed": false,
        "payment_status": "pending"
    },
    "created_at": "2024-12-01T10:30:00Z",
    "updated_at": "2024-12-01T11:45:00Z",
    "last_message_at": "2024-12-01T11:45:00Z"
}
```

## Implementation Strategy

### Initial Trip Creation:
```python
# When user starts chatting
trip = {
    "trip_name": f"New Chat - {current_date}",  # Temporary
    "status": "collecting_info",
    "destination": None,
    "visa_type": None
}
```

### After Base Info Collection:
```python
# When agent gets destination + purpose
def update_trip_name(trip_id: str, destination: str, purpose: str):
    meaningful_name = f"{destination} {purpose} - {date}"
    # Update: "New Chat - Dec 1" → "Vietnam Tourism - Dec 1"
    update_trip(trip_id, {"trip_name": meaningful_name})
```

### Key Triggers:
- **First message typed** → Create thread + trip entry + Update URL
- **Base info collected** → Update trip name from "New Chat" to meaningful name

## Timeline:
1. **Chat starts** → "New Chat - Dec 1, 2024"
2. **Info collected** → "Vietnam Tourism - Dec 1, 2024" 
3. **Application progresses** → Keep meaningful name

## Benefits:
1. **Complete conversation backup** - Never lose chat history
2. **Cross-device sync** - Access same conversations anywhere
3. **Trip management** - Easy to see all visa applications
4. **Resume conversations** - Continue where you left off
5. **Application tracking** - Know status of each visa

## Todo Items Created:
1. Create trips collection database model with conversation storage
2. Implement auto-naming logic for trips (destination + visa_type + date)
3. Replace static sidebar tabs with dynamic trips from database
4. Auto-save conversations to trips collection during chat
5. Create API endpoints for trip management (create, list, load)
6. Update frontend to load/switch between trip conversations
7. Implement trip status tracking (in_progress, completed, cancelled)