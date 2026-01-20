# Student Authentication & Tracking System

**Status:** Planning
**Date:** January 19, 2026
**Project:** CHEM 361 - Inorganic Chemistry

---

## Overview

Add student registration, login, attendance tracking, and quiz progress to chem361.thebeakers.com. Extends the existing quiz backend at `/storage/quizzes/`.

---

## Current State

### Quiz System (`/storage/quizzes/`)
- **Backend:** FastAPI + SQLite (`/storage/quizzes/data/quiz.db`)
- **Models:** Student (id, name only), Concept, Question, QuestionAttempt, StudentConceptState
- **Features:** Adaptive difficulty, mastery tracking, Qdrant vector search
- **Auth:** None - students created by name only via `POST /students`

### Attendance System (`/storage/inorganic-chem-class/`)
- **Frontend:** `attendance.html` + `attendance.js`
- **Storage:** Browser localStorage (not persistent)
- **Features:** QR code generation, check-in codes, instructor view
- **Schedule:** `data/schedule.json` (30 class sessions)

### Problems
1. No real authentication - anyone can claim any name
2. Attendance data lost when browser cleared
3. No unified student dashboard
4. Quiz and attendance are disconnected systems

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Login credential | Student ID + password | Simpler for students (M12345678) |
| API location | `chem361.thebeakers.com/api/` | Single domain, no CORS issues |
| Instructor auth | Password: `chem361` | Keep simple, low-security context |
| Dashboard | Unified (attendance + quiz) | Single place for student progress |
| Backend | Extend existing quiz FastAPI | Reuse infrastructure |

---

## Database Schema Changes

### Modified: `students` table

```sql
-- current
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    name VARCHAR NOT NULL
);

-- new
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    student_id VARCHAR(20) UNIQUE NOT NULL,  -- e.g., M12345678
    name VARCHAR NOT NULL,
    password_hash VARCHAR(60) NOT NULL,       -- bcrypt
    email VARCHAR,                            -- optional, for notifications
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at DATETIME
);
```

### New: `class_sessions` table

```sql
CREATE TABLE class_sessions (
    id INTEGER PRIMARY KEY,
    session_date DATE NOT NULL UNIQUE,
    topic VARCHAR NOT NULL,
    unit INTEGER NOT NULL,                    -- 1, 2, or 3
    chapter VARCHAR,                          -- e.g., "Ch 2"
    attendance_code VARCHAR(6),               -- e.g., "ABC123"
    code_generated_at DATETIME,
    code_expires_at DATETIME,
    is_cancelled BOOLEAN DEFAULT FALSE
);
```

### New: `attendance_records` table

```sql
CREATE TABLE attendance_records (
    id INTEGER PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    session_id INTEGER NOT NULL REFERENCES class_sessions(id),
    check_in_time DATETIME NOT NULL,
    code_used VARCHAR(6),
    UNIQUE(student_id, session_id)            -- one check-in per student per class
);
```

---

## API Endpoints

### Authentication (`/api/auth/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Create student account | None |
| POST | `/api/auth/login` | Get JWT token | None |
| GET | `/api/auth/me` | Get current user info | JWT |
| POST | `/api/auth/logout` | Invalidate token (optional) | JWT |

**Register request:**
```json
{
    "student_id": "M12345678",
    "name": "Jane Doe",
    "password": "securepassword",
    "email": "jane@example.com"  // optional
}
```

**Login request:**
```json
{
    "student_id": "M12345678",
    "password": "securepassword"
}
```

**Login response:**
```json
{
    "access_token": "eyJ...",
    "token_type": "bearer",
    "student": {
        "id": 1,
        "student_id": "M12345678",
        "name": "Jane Doe"
    }
}
```

### Attendance (`/api/attendance/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/attendance/sessions` | List all class sessions | JWT |
| GET | `/api/attendance/my-records` | Student's attendance history | JWT |
| POST | `/api/attendance/checkin` | Check in with code | JWT |
| GET | `/api/attendance/today` | Get today's session info | JWT |

**Instructor only:**

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/attendance/generate-code` | Generate new attendance code | Instructor |
| GET | `/api/attendance/session/{id}/records` | Who attended a session | Instructor |
| GET | `/api/attendance/export` | Export CSV | Instructor |

**Check-in request:**
```json
{
    "code": "ABC123"
}
```

### Student Dashboard (`/api/dashboard/`)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/dashboard/summary` | Attendance + quiz stats | JWT |
| GET | `/api/dashboard/progress` | Detailed progress by concept | JWT |

**Summary response:**
```json
{
    "student": {
        "id": 1,
        "student_id": "M12345678",
        "name": "Jane Doe"
    },
    "attendance": {
        "present": 12,
        "absent": 3,
        "total": 15,
        "rate": 0.80
    },
    "quiz": {
        "concepts_started": 5,
        "concepts_mastered": 2,
        "total_questions": 47,
        "accuracy": 0.72
    }
}
```

---

## Frontend Changes

### New: Login/Register Page

**Location:** `/storage/inorganic-chem-class/auth.html`

**Features:**
- Toggle between login and register forms
- Student ID + password fields
- Remember me checkbox (longer JWT expiry)
- Error handling with clear messages
- Redirect to dashboard after login

**Design notes (from CLAUDE.md):**
- Use distinctive fonts (not Inter/Roboto)
- Match existing dark theme with purple accents
- Consider JetBrains Mono for ID field (code aesthetic)

### Modified: Homepage (`index.html`)

Add navigation link:
```html
<a href="auth.html" class="nav-link">Login</a>
<!-- or if logged in -->
<a href="dashboard.html" class="nav-link">Dashboard</a>
```

### New: Student Dashboard (`dashboard.html`)

**Sections:**
1. **Header** - Student name, logout button
2. **Attendance card** - Today's class, check-in button, attendance rate
3. **Quiz progress card** - Concepts list with mastery bars
4. **Schedule** - Upcoming classes with attendance marks

### Modified: Attendance Page (`attendance.html`)

**Changes:**
- Remove localStorage logic
- Add API calls for check-in
- Require login to access
- Keep instructor mode with password prompt

---

## File Structure

```
/storage/quizzes/
├── app/
│   ├── main.py              # add auth + attendance routes
│   ├── models.py            # add new models
│   ├── schemas.py           # add new schemas
│   ├── auth.py              # NEW: JWT + password hashing
│   ├── attendance.py        # NEW: attendance logic
│   └── static/
│       └── index.html       # existing quiz UI
├── data/
│   └── quiz.db              # extended schema
└── requirements.txt         # add: python-jose, passlib, bcrypt

/storage/inorganic-chem-class/
├── index.html               # add login link
├── auth.html                # NEW: login/register page
├── dashboard.html           # NEW: student dashboard
├── attendance.html          # MODIFY: use API
├── attendance.js            # MODIFY: API calls
├── data/
│   └── schedule.json        # seed class_sessions table
└── docs/
    └── STUDENT_AUTH_PLAN.md # this file
```

---

## Implementation Phases

### Phase 1: Backend Auth
1. Add `auth.py` with JWT utilities
2. Extend `models.py` with new fields/tables
3. Add auth endpoints to `main.py`
4. Migrate existing students table (add columns)
5. Test with curl/httpie

### Phase 2: Backend Attendance
1. Add `attendance.py` with business logic
2. Seed `class_sessions` from `schedule.json`
3. Add attendance endpoints
4. Add instructor authentication check
5. Test API endpoints

### Phase 3: Frontend Auth
1. Create `auth.html` (login/register)
2. Create JS module for auth (token storage, API calls)
3. Add login link to `index.html`
4. Test login flow

### Phase 4: Frontend Dashboard
1. Create `dashboard.html`
2. Integrate attendance check-in
3. Show quiz progress
4. Update `attendance.html` to use API

### Phase 5: Integration & Polish
1. Protect quiz endpoints with JWT
2. Add proper error handling
3. Test full user flow
4. Deploy and configure nginx reverse proxy

---

## Security Considerations

- **Password hashing:** bcrypt with cost factor 12
- **JWT expiry:** 24 hours (or 7 days with "remember me")
- **JWT secret:** Environment variable, not in code
- **HTTPS:** Already handled by thebeakers.com
- **Rate limiting:** Consider for login endpoint (future)
- **Instructor password:** Simple but acceptable for low-stakes context

---

## Deployment Notes

### Nginx Configuration

Add to existing chem361 server block:
```nginx
location /api/ {
    proxy_pass http://localhost:8001/;  # or wherever quiz API runs
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}
```

### Environment Variables

```bash
JWT_SECRET=<generate-random-32-char-string>
DATABASE_URL=sqlite:////storage/quizzes/data/quiz.db
INSTRUCTOR_PASSWORD=chem361
```

---

## Migration Strategy

1. Back up existing `quiz.db`
2. Run Alembic migration (or manual SQL)
3. Existing students: Set `student_id` = `name`, require password reset
4. Seed `class_sessions` from `schedule.json`
5. Test thoroughly before switching frontend

---

## Open Questions

1. **Password reset:** Email-based? Or instructor resets manually?
2. **Session timeout:** How long before re-login required?
3. **Multiple devices:** Allow simultaneous logins?
4. **Late check-in:** Allow check-in after code expires with reduced credit?

---

## Dependencies to Add

```txt
# /storage/quizzes/requirements.txt
python-jose[cryptography]>=3.3.0  # JWT
passlib[bcrypt]>=1.7.4            # password hashing
python-multipart>=0.0.6           # form data parsing
```

---

## Related Files

- Quiz backend: `/storage/quizzes/app/main.py`
- Quiz models: `/storage/quizzes/app/models.py`
- Attendance UI: `/storage/inorganic-chem-class/attendance.html`
- Schedule data: `/storage/inorganic-chem-class/data/schedule.json`
- Design guidelines: `/storage/CLAUDE.md`
