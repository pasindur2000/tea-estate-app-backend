# Tea Estate Management API — CLAUDE.md

## Project Overview

FastAPI backend for a Tea Estate Management mobile application. Manages estates, workers, tea harvest entries, attendance, and reports. Uses Firebase Auth for authentication and Firestore as the database.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111.0 |
| Server | Uvicorn 0.29.0 (with `[standard]` extras for uvloop) |
| Database | Google Firestore (via `firebase-admin` 6.5.0) |
| Auth | Firebase Authentication (JWT verification) |
| Validation | Pydantic v2.7.1 |
| Settings | `pydantic-settings` 2.2.1 + `python-dotenv` |
| Runtime | Python 3.12 (venv at `./venv`) |

## How to Run

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
uvicorn app.main:app --reload
```

API runs at `http://127.0.0.1:8000`  
Swagger UI at `http://127.0.0.1:8000/docs`

## Environment Setup

Copy `.env.example` to `.env` and fill in:

```
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_CREDENTIALS_PATH=firebase_credentials.json
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

`firebase_credentials.json` must be a valid Firebase service account key (download from Firebase Console → Project Settings → Service Accounts).

## Project Structure

```
app/
├── main.py                  # FastAPI app, CORS, router registration
├── config.py                # Settings, Firebase Admin SDK init, Firestore client
├── dependencies.py          # Auth dependencies: get_current_user, director_only
├── models/
│   ├── base.py              # TimestampMixin (createdAt/updatedAt), StatusEnum
│   ├── estate.py            # EstateCreate, EstateUpdate, EstateResponse
│   ├── worker.py            # WorkerCreate, WorkerUpdate, WorkerResponse
│   ├── tea_entry.py         # TeaEntryCreate (auto-computes totalAmount), TeaEntryUpdate, TeaEntryResponse
│   ├── attendance.py        # AttendanceCreate, AttendanceUpdate, AttendanceResponse
│   └── user.py              # UserCreate, UserUpdate, UserResponse
├── routers/
│   ├── estates.py           # /api/v1/estates — Director only
│   ├── workers.py           # /api/v1/workers — Director + Supervisor
│   ├── tea_entries.py       # /api/v1/tea-entries — Director + Supervisor (delete: Director only)
│   ├── attendance.py        # /api/v1/attendance — Director + Supervisor
│   ├── users.py             # /api/v1/users — create/update/deactivate: Director only
│   └── reports.py           # /api/v1/reports — Director only
├── services/
│   ├── estate_service.py    # Firestore CRUD for Estates collection
│   ├── worker_service.py    # Firestore CRUD for Workers collection
│   ├── tea_entry_service.py # Firestore CRUD for Tea_entries collection
│   ├── attendance_service.py# Firestore CRUD for Attendance collection
│   ├── user_service.py      # Firebase Auth + Firestore CRUD for Users collection
│   └── report_service.py    # Aggregation reports (monthly tea summary, attendance summary)
└── utils/
    ├── response.py          # success_response() / error_response() wrappers
    └── permissions.py       # (reserved for future permission helpers)
```

## Authentication & Authorization

All routes require a Firebase ID token in the header:
```
Authorization: Bearer <firebase-id-token>
```

Two dependency functions in `dependencies.py`:
- `get_current_user` — verifies token, loads Firestore user doc, rejects inactive accounts
- `director_only` — wraps `get_current_user`, rejects non-directors with 403

Roles stored in Firestore `Users` collection: `"director"` or `"supervisor"`.

## Firestore Collections

| Collection | Document ID format | Key fields |
|---|---|---|
| `Estates` | `estate_<8hex>` | estateId, name, location, status, createdBy |
| `Workers` | `worker_<8hex>` | workerId, estateId, name, nic, phone, joinedDate, status, createdBy |
| `Tea_entries` | `tea_<8hex>` | teaEntryId, estateId, workerId, workerName, date (YYYY-MM-DD str), kg, ratePerKg, totalAmount, createdBy |
| `Attendance` | `attendance_<8hex>` | attendanceId, estateId, workerId, workerName, date (YYYY-MM-DD str), status (present/absent/half_day), createdBy |
| `Users` | Firebase UID | uid, name, email, role, estateId, status |

## API Endpoints Summary

All routes prefixed with `/api/v1`.

| Method | Path | Auth | Notes |
|---|---|---|---|
| GET | `/` | None | Health check |
| POST | `/estates/` | Director | Create estate |
| GET | `/estates/` | Director | List all estates |
| GET | `/estates/{id}` | Director | Get estate |
| PATCH | `/estates/{id}` | Director | Update estate |
| DELETE | `/estates/{id}` | Director | Soft-delete (status → inactive) |
| POST | `/users/` | Director | Create supervisor account (Firebase Auth + Firestore) |
| GET | `/users/me` | Any | Get own profile |
| GET | `/users/estate/{id}` | Director | List users in estate |
| PATCH | `/users/{uid}` | Director | Update user |
| DELETE | `/users/{uid}` | Director | Deactivate user |
| POST | `/workers/` | Any | Add worker |
| GET | `/workers/estate/{id}` | Any | List workers in estate |
| GET | `/workers/{id}` | Any | Get worker |
| PATCH | `/workers/{id}` | Any | Update worker |
| DELETE | `/workers/{id}` | Director | Deactivate worker |
| POST | `/tea-entries/` | Any | Record tea entry (totalAmount auto-computed) |
| GET | `/tea-entries/estate/{id}` | Any | List entries (optional `?date=YYYY-MM-DD`) |
| GET | `/tea-entries/{id}` | Any | Get entry |
| PATCH | `/tea-entries/{id}` | Any | Update entry |
| DELETE | `/tea-entries/{id}` | Director | Delete entry |
| POST | `/attendance/` | Any | Mark attendance |
| GET | `/attendance/estate/{id}` | Any | List attendance (optional `?date=YYYY-MM-DD`) |
| PATCH | `/attendance/{id}` | Any | Update attendance status |
| GET | `/reports/tea-summary/{id}` | Director | Monthly tea harvest + earnings (`?year=&month=`) |
| GET | `/reports/attendance-summary/{id}` | Director | Attendance summary (`?from_date=&to_date=`) |

## Standard Response Shape

Every endpoint returns:
```json
{
  "success": true,
  "message": "Human-readable result",
  "data": { ... }
}
```

## Architecture Patterns

- **Routers** handle HTTP only — no business logic
- **Services** contain all Firestore queries and business logic
- **Models** are Pydantic v2 schemas — Create / Update / Response per resource
- `totalAmount` in `TeaEntryCreate` is computed server-side via `@model_validator(mode="after")`, not sent by client
- Soft-deletes: estates and workers set `status = "inactive"` instead of deleting documents
- IDs are `uuid4().hex[:8]` prefixed with the resource name (e.g. `tea_a1b2c3d4`)

## Known Pydantic v2 Gotcha

Do NOT use a field name that shadows its own type annotation. Example that breaks:
```python
from datetime import date

class Model(BaseModel):
    date: date = Field(...)  # 'date' field name shadows 'date' type → PydanticUserError
```

Fix — alias the import:
```python
from datetime import date as Date

class Model(BaseModel):
    date: Date = Field(...)  # OK
```

This was the root cause of the startup crash in `models/tea_entry.py` and `models/attendance.py`.
