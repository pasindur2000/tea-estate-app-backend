# Tea Estate Management — Full Project Reference

This file is the single source of truth for both the backend and the frontend.
The backend is **complete**. The frontend should be built to match everything described here exactly.

---

## 1. Project Overview

A mobile application for managing tea estates. Two user roles exist:

| Role | What they can do |
|---|---|
| `director` | Full access — estates, supervisors, reports, and all field operations |
| `supervisor` | Field operations only — record tea pickings, mark attendance, view workers |

---

## 2. Backend (Reference — Already Built)

### Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.111.0 |
| Server | Uvicorn 0.29.0 |
| Database | Google Firestore (`firebase-admin` 6.5.0) |
| Auth | Firebase Authentication (JWT verification) |
| Validation | Pydantic v2.7.1 |
| Runtime | Python 3.12 |

### Running the backend

```bash
source venv/bin/activate
uvicorn app.main:app --reload
```

- API base URL (local): `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- All API routes are prefixed with `/api/v1`

---

## 3. Authentication (Frontend Must Implement This)

Authentication uses **Firebase Authentication** on both ends.

### Login Flow

1. User enters email + password in the app.
2. Frontend calls **Firebase Auth SDK** `signInWithEmailAndPassword()`.
3. Firebase returns a signed-in user object — call `.getIdToken()` on it to get a JWT string.
4. **Every API request** must include this token in the header:

```
Authorization: Bearer <firebase-id-token>
```

5. Tokens expire after 1 hour. Use `.getIdToken(true)` to force-refresh, or listen to `onIdTokenChanged`.

### After Login — Load User Profile

After getting the token, immediately call:
```
GET /api/v1/users/me
```
The response contains `role`, `estateId`, `name`, `email`, `status`. Store this in app state — everything else (which screens to show, which actions to allow) depends on `role`.

### Error Responses from Backend

| HTTP Status | Meaning |
|---|---|
| `401` | Token missing, invalid, or expired — send user to login screen |
| `403` | Token valid but user lacks permission (wrong role, or account deactivated) |
| `404` | Resource not found |
| `422` | Validation error — request body fields are wrong |

### Standard API Response Shape

Every endpoint returns this exact shape:

```json
{
  "success": true,
  "message": "Human-readable result",
  "data": { ... }
}
```

On error the backend raises an HTTP exception with a `detail` field — FastAPI's default error shape:
```json
{
  "detail": "Error message here"
}
```

---

## 4. Role-Based UI Rules

The frontend must hide/show screens and actions based on `current_user.role`.

### Director sees

- Estates management (create, edit, deactivate)
- Supervisor management (create, edit, deactivate)
- Workers (add, edit, deactivate)
- Tea entry (record, edit, delete)
- Attendance (mark, edit)
- Reports (monthly tea summary, attendance summary)

### Supervisor sees

- Workers (add, edit — no deactivate)
- Tea entry (record, edit — no delete)
- Attendance (mark, edit)
- Own profile (`/users/me`)
- No access to: Estates, Supervisor management, Reports

---

## 5. API Endpoints — Full Reference

All paths below are relative to `/api/v1`.

---

### 5.1 Users

#### GET `/users/me` — Get own profile
- Auth: Any logged-in user
- Request body: none
- Response `data`:
```json
{
  "uid": "firebase-uid",
  "name": "Saman",
  "email": "saman@example.com",
  "role": "supervisor",
  "estateId": "estate_a1b2c3d4",
  "status": "active",
  "createdAt": "2026-05-01T10:00:00",
  "updatedAt": "2026-05-01T10:00:00"
}
```

#### POST `/users/` — Create a supervisor account
- Auth: Director only
- Request body:
```json
{
  "name": "Saman",
  "email": "saman@example.com",
  "password": "min6chars",
  "role": "supervisor",
  "estateId": "estate_a1b2c3d4"
}
```
- Response `data`: same shape as user profile above

#### GET `/users/estate/{estate_id}` — List users in an estate
- Auth: Director only
- Response `data`: array of user profile objects

#### PATCH `/users/{uid}` — Update a user
- Auth: Director only
- Request body (all fields optional):
```json
{
  "name": "New Name",
  "status": "inactive"
}
```
- Response `data`: updated user profile object

#### DELETE `/users/{uid}` — Deactivate a user
- Auth: Director only
- Sets `status = "inactive"` — does not delete the Firebase Auth account
- Response `data`: null

---

### 5.2 Estates

#### POST `/estates/` — Create an estate
- Auth: Director only
- Request body:
```json
{
  "name": "Green Valley Tea Estate",
  "location": "Kandy",
  "status": "active"
}
```
- `status` is optional, defaults to `"active"`
- Response `data`:
```json
{
  "estateId": "estate_a1b2c3d4",
  "name": "Green Valley Tea Estate",
  "location": "Kandy",
  "status": "active",
  "createdAt": "2026-05-01T10:00:00",
  "updatedAt": "2026-05-01T10:00:00"
}
```

#### GET `/estates/` — List all estates
- Auth: Director only
- Response `data`: array of estate objects

#### GET `/estates/{estate_id}` — Get a single estate
- Auth: Director only
- Response `data`: single estate object

#### PATCH `/estates/{estate_id}` — Update an estate
- Auth: Director only
- Request body (all fields optional):
```json
{
  "name": "Updated Name",
  "location": "Nuwara Eliya",
  "status": "inactive"
}
```
- Response `data`: updated estate object

#### DELETE `/estates/{estate_id}` — Deactivate an estate
- Auth: Director only
- Soft-delete — sets `status = "inactive"`, does not remove the document
- Response `data`: null

---

### 5.3 Workers

#### POST `/workers/` — Add a worker
- Auth: Director or Supervisor
- Request body:
```json
{
  "name": "Kamal",
  "nic": "981234567V",
  "phone": "0771234567",
  "estateId": "estate_a1b2c3d4",
  "joinedDate": "2026-05-01",
  "status": "active"
}
```
- `nic`: 9–12 characters. `phone`: 10–15 characters. `joinedDate`: `YYYY-MM-DD` string.
- `status` is optional, defaults to `"active"`
- Response `data`:
```json
{
  "workerId": "worker_a1b2c3d4",
  "estateId": "estate_a1b2c3d4",
  "name": "Kamal",
  "nic": "981234567V",
  "phone": "0771234567",
  "joinedDate": "2026-05-01",
  "status": "active",
  "createdBy": "firebase-uid",
  "createdAt": "2026-05-01T10:00:00",
  "updatedAt": "2026-05-01T10:00:00"
}
```

#### GET `/workers/estate/{estate_id}` — List workers in an estate
- Auth: Any logged-in user
- Response `data`: array of worker objects

#### GET `/workers/{worker_id}` — Get a single worker
- Auth: Any logged-in user
- Response `data`: single worker object

#### PATCH `/workers/{worker_id}` — Update a worker
- Auth: Director or Supervisor
- Request body (all fields optional):
```json
{
  "name": "Kamal Updated",
  "phone": "0779999999",
  "status": "inactive"
}
```
- Response `data`: updated worker object

#### DELETE `/workers/{worker_id}` — Deactivate a worker
- Auth: Director only
- Soft-delete — sets `status = "inactive"`
- Response `data`: null

---

### 5.4 Tea Entries

#### POST `/tea-entries/` — Record a tea harvest entry
- Auth: Director or Supervisor
- Request body:
```json
{
  "estateId": "estate_a1b2c3d4",
  "workerId": "worker_a1b2c3d4",
  "workerName": "Kamal",
  "date": "2026-05-09",
  "kg": 24.5,
  "ratePerKg": 120.0
}
```
- **Do NOT send `totalAmount`** — the backend computes it automatically as `kg × ratePerKg`
- `date`: `YYYY-MM-DD` string. `kg` and `ratePerKg` must be greater than 0.
- Response `data`:
```json
{
  "teaEntryId": "tea_a1b2c3d4",
  "estateId": "estate_a1b2c3d4",
  "workerId": "worker_a1b2c3d4",
  "workerName": "Kamal",
  "date": "2026-05-09",
  "kg": 24.5,
  "ratePerKg": 120.0,
  "totalAmount": 2940.0,
  "createdBy": "firebase-uid",
  "createdAt": "2026-05-09T08:00:00",
  "updatedAt": "2026-05-09T08:00:00"
}
```

#### GET `/tea-entries/estate/{estate_id}` — List entries for an estate
- Auth: Any logged-in user
- Optional query param: `?date=2026-05-09` (filters by exact date)
- Response `data`: array of tea entry objects

#### GET `/tea-entries/{entry_id}` — Get a single entry
- Auth: Any logged-in user
- Response `data`: single tea entry object

#### PATCH `/tea-entries/{entry_id}` — Update a tea entry
- Auth: Director or Supervisor
- Request body (all fields optional — backend recomputes `totalAmount` if `kg` or `ratePerKg` changes):
```json
{
  "kg": 30.0,
  "ratePerKg": 125.0
}
```
- Response `data`: updated tea entry object

#### DELETE `/tea-entries/{entry_id}` — Delete a tea entry
- Auth: Director only
- Hard-delete — removes the document from Firestore
- Response `data`: null

---

### 5.5 Attendance

#### POST `/attendance/` — Mark attendance
- Auth: Director or Supervisor
- Request body:
```json
{
  "estateId": "estate_a1b2c3d4",
  "workerId": "worker_a1b2c3d4",
  "workerName": "Kamal",
  "date": "2026-05-09",
  "status": "present"
}
```
- `status` must be one of: `"present"`, `"absent"`, `"half_day"`. Defaults to `"present"`.
- `date`: `YYYY-MM-DD` string.
- Response `data`:
```json
{
  "attendanceId": "attendance_a1b2c3d4",
  "estateId": "estate_a1b2c3d4",
  "workerId": "worker_a1b2c3d4",
  "workerName": "Kamal",
  "date": "2026-05-09",
  "status": "present",
  "createdBy": "firebase-uid",
  "createdAt": "2026-05-09T07:00:00",
  "updatedAt": "2026-05-09T07:00:00"
}
```

#### GET `/attendance/estate/{estate_id}` — List attendance records
- Auth: Any logged-in user
- Optional query param: `?date=2026-05-09` (filters by exact date)
- Response `data`: array of attendance objects

#### PATCH `/attendance/{att_id}` — Update attendance status
- Auth: Director or Supervisor
- Request body:
```json
{
  "status": "half_day"
}
```
- Response `data`: updated attendance object

---

### 5.6 Reports (Director only)

#### GET `/reports/tea-summary/{estate_id}` — Monthly tea harvest summary
- Auth: Director only
- Required query params: `?year=2026&month=5`
- Response `data`:
```json
{
  "estateId": "estate_a1b2c3d4",
  "period": "2026-05",
  "workers": [
    {
      "workerId": "worker_a1b2c3d4",
      "workerName": "Kamal",
      "totalKg": 310.5,
      "totalEarnings": 37260.0
    }
  ],
  "grandTotalKg": 310.5,
  "grandTotalEarnings": 37260.0
}
```

#### GET `/reports/attendance-summary/{estate_id}` — Attendance summary for a date range
- Auth: Director only
- Required query params: `?from_date=2026-05-01&to_date=2026-05-31`
- Response `data`:
```json
{
  "estateId": "estate_a1b2c3d4",
  "fromDate": "2026-05-01",
  "toDate": "2026-05-31",
  "workers": [
    {
      "workerId": "worker_a1b2c3d4",
      "workerName": "Kamal",
      "present": 20,
      "absent": 3,
      "half_day": 2
    }
  ]
}
```

---

## 6. Data Field Reference

### Field formats

| Field | Format | Example |
|---|---|---|
| All `*Id` fields | string | `"estate_a1b2c3d4"` |
| `uid` (user) | Firebase UID string | `"abc123xyz"` |
| `date` | `"YYYY-MM-DD"` string | `"2026-05-09"` |
| `createdAt` / `updatedAt` | ISO 8601 datetime | `"2026-05-01T10:00:00"` |
| `status` (estate/worker/user) | `"active"` or `"inactive"` | `"active"` |
| `status` (attendance) | `"present"`, `"absent"`, `"half_day"` | `"present"` |
| `role` | `"director"` or `"supervisor"` | `"supervisor"` |
| `kg`, `ratePerKg`, `totalAmount` | float | `24.5`, `120.0`, `2940.0` |

### Validation constraints (enforce in frontend forms too)

| Field | Constraint |
|---|---|
| `name` (estate) | 2–100 characters |
| `location` | 2–200 characters |
| `name` (worker/user) | 2–100 characters |
| `nic` | 9–12 characters |
| `phone` | 10–15 characters |
| `password` | Minimum 6 characters |
| `kg` | Greater than 0 |
| `ratePerKg` | Greater than 0 |
| `month` (report) | 1–12 |

---

## 7. Suggested Screen Map (Frontend)

### Shared screens (both roles)

| Screen | Purpose |
|---|---|
| Login | Firebase email/password sign-in |
| Profile (`/users/me`) | View own name, email, role, estate |
| Worker List | `GET /workers/estate/{estateId}` |
| Worker Detail | `GET /workers/{workerId}` |
| Add Worker | `POST /workers/` |
| Edit Worker | `PATCH /workers/{workerId}` |
| Tea Entry List | `GET /tea-entries/estate/{estateId}?date=` |
| Add Tea Entry | `POST /tea-entries/` |
| Edit Tea Entry | `PATCH /tea-entries/{entryId}` |
| Attendance List | `GET /attendance/estate/{estateId}?date=` |
| Mark Attendance | `POST /attendance/` |
| Edit Attendance | `PATCH /attendance/{attId}` |

### Director-only screens

| Screen | Purpose |
|---|---|
| Estate List | `GET /estates/` |
| Create Estate | `POST /estates/` |
| Edit Estate | `PATCH /estates/{estateId}` |
| Supervisor List | `GET /users/estate/{estateId}` |
| Create Supervisor | `POST /users/` |
| Edit Supervisor | `PATCH /users/{uid}` |
| Monthly Tea Report | `GET /reports/tea-summary/{estateId}?year=&month=` |
| Attendance Report | `GET /reports/attendance-summary/{estateId}?from_date=&to_date=` |
| Delete Tea Entry | `DELETE /tea-entries/{entryId}` |
| Deactivate Worker | `DELETE /workers/{workerId}` |
| Deactivate User | `DELETE /users/{uid}` |

---

## 8. Backend Architecture Notes (for context)

- **Routers** — HTTP layer only, no logic (`app/routers/`)
- **Services** — All Firestore queries and business logic (`app/services/`)
- **Models** — Pydantic v2 schemas, one set per resource: Create / Update / Response
- **Soft deletes** — Estates, Workers, Users set `status = "inactive"`, documents are never removed
- **Hard delete** — Tea entries are permanently removed from Firestore
- **IDs** — Generated as `uuid4().hex[:8]` prefixed by resource name (e.g. `worker_a1b2c3d4`)
- **CORS** — Currently open to `*`; lock down to the production domain before release
