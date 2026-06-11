# 🍃 Tea Estate Management — Backend API

A scalable FastAPI backend powered by Firebase Auth + Firestore.

---

## Project Structure

```
tea_estate_api/
├── app/
│   ├── main.py              ← App entry point, router registration
│   ├── config.py            ← Firebase init, settings
│   ├── dependencies.py      ← Token verification, role guards
│   ├── models/              ← Pydantic request/response schemas
│   │   ├── estate.py
│   │   ├── user.py
│   │   ├── worker.py
│   │   ├── tea_entry.py
│   │   └── attendance.py
│   ├── routers/             ← HTTP route handlers (thin layer)
│   │   ├── estates.py
│   │   ├── users.py
│   │   ├── workers.py
│   │   ├── tea_entries.py
│   │   ├── attendance.py
│   │   └── reports.py
│   ├── services/            ← Business logic + Firestore queries
│   │   ├── estate_service.py
│   │   ├── user_service.py
│   │   ├── worker_service.py
│   │   ├── tea_entry_service.py
│   │   ├── attendance_service.py
│   │   └── report_service.py
│   └── utils/
│       ├── permissions.py   ← Role constants
│       └── response.py      ← Standardised API responses
├── requirements.txt
├── .env.example
└── README.md
```

---

## Quick Start

### 1. Clone / set up a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com) → your project
2. **Authentication** → Sign-in method → Enable **Email/Password** and **Google**
3. **Project Settings** → **Service Accounts** → **Generate new private key**
4. Save the downloaded JSON as `firebase_credentials.json` in the project root
5. **Never commit this file to git!** Add it to `.gitignore`

### 3. Create your `.env` file
```bash
cp .env.example .env
# Open .env and fill in your FIREBASE_PROJECT_ID
```

### 4. Run the server
```bash
uvicorn app.main:app --reload
```
Open http://localhost:8000/docs for the interactive API documentation.

---

## Authentication Flow

```
Mobile App                     FastAPI Backend            Firebase
    │                                │                        │
    │── Sign in (email/password) ────────────────────────────►│
    │◄────────────────── ID Token ───────────────────────────┤
    │                                │                        │
    │── API Request + Bearer Token ─►│                        │
    │                           Verify Token ────────────────►│
    │                           ◄──── decoded UID ────────────┤
    │                           Load user from Firestore      │
    │◄──── Response ─────────────────│                        │
```

The mobile app:
1. Signs in via Firebase SDK → gets an **ID Token**
2. Sends `Authorization: Bearer <ID Token>` on every API request
3. The backend verifies the token server-side — no passwords needed

---

## Role Permissions Summary

| Action                        | Director | Supervisor |
|-------------------------------|----------|------------|
| Create / manage estates       | ✅       | ❌         |
| Create supervisor accounts    | ✅       | ❌         |
| Add workers                   | ✅       | ✅         |
| Add tea entries               | ✅       | ✅         |
| Add attendance                | ✅       | ✅         |
| View reports / summaries      | ✅       | ❌         |
| Delete records                | ✅       | ❌         |

---

## API Endpoints

All endpoints are prefixed with `/api/v1`

### Estates (Director only)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/estates/` | Create estate |
| GET | `/estates/` | List all estates |
| GET | `/estates/{id}` | Get estate |
| PATCH | `/estates/{id}` | Update estate |
| DELETE | `/estates/{id}` | Deactivate estate |

### Users (Director only)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/users/` | Create supervisor |
| GET | `/users/estate/{estateId}` | List users |
| GET | `/users/me` | My profile |
| PATCH | `/users/{uid}` | Update user |
| DELETE | `/users/{uid}` | Deactivate user |

### Workers (Both roles)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/workers/` | Add worker |
| GET | `/workers/estate/{estateId}` | List workers |
| PATCH | `/workers/{id}` | Update worker |
| DELETE | `/workers/{id}` | Deactivate (Director only) |

### Tea Entries (Both roles)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/tea-entries/` | Record tea harvest |
| GET | `/tea-entries/estate/{estateId}?date=YYYY-MM-DD` | List entries |
| PATCH | `/tea-entries/{id}` | Edit entry |
| DELETE | `/tea-entries/{id}` | Delete (Director only) |

### Attendance (Both roles)
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/attendance/` | Mark attendance |
| GET | `/attendance/estate/{estateId}?date=YYYY-MM-DD` | List records |
| PATCH | `/attendance/{id}` | Correct status |

### Reports (Director only)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/reports/tea-summary/{estateId}?year=2026&month=5` | Monthly harvest report |
| GET | `/reports/attendance-summary/{estateId}?from_date=...&to_date=...` | Attendance report |

---

## Adding New Features (Scalability Guide)

When you need to add a new feature (e.g. "Repairs", "Plucking Targets"):

1. **Add a Pydantic schema** in `app/models/new_feature.py`
2. **Add a service** in `app/services/new_feature_service.py`
3. **Add a router** in `app/routers/new_feature.py`
4. **Register the router** in `app/main.py` with `app.include_router(...)`

That's the entire pattern — no other files need changing.
