Meeting System
==============

Simple Django + DRF meeting room booking API.

Quick setup
-----------
- Create and activate a virtualenv (recommended):

Windows (PowerShell):

```powershell
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

Windows (cmd):

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

- Install dependencies from the included `requirements.txt`:

```bash
pip install -r requirements.txt
```

- Database: the project ships configured for MySQL in `Meeting_System/settings.py`.
  For a quick local run using SQLite (no DB server), replace the `DATABASES` setting in
  `Meeting_System/settings.py` with the following snippet:

```python
- SQLLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

-MYSQLs
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "Db_Name",
        "USER": "root",
        "PASSWORD": "your_password",
        "HOST": "localhost",
        "PORT": "3306",
    }
}
```

- Apply migrations, create a superuser (optional), and run the server:

```bash
python manage.py migrate
python manage.py createsuperuser  
python manage.py runserver
```

- Run tests:

```bash
python manage.py test
```

API Endpoints
-------------
Base path: `/api/v1/`

1) Book a room
- URL: `/api/v1/meeting-rooms/<room_id>/book/`
- Method: `POST`
- Body (JSON):
  - `start_time`: ISO8601 datetime (e.g. `2026-01-28T10:00:00Z`)
  - `end_time`: ISO8601 datetime
  - `purpose` (optional)
- Success: 201 Created, JSON with `booking` details
- Conflict: 409 Conflict if room unavailable

Example curl:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/meeting-rooms/1/book/ \
  -H "Content-Type: application/json" \
  -d '{"start_time":"2026-01-28T10:00:00Z","end_time":"2026-01-28T11:00:00Z","purpose":"Team sync"}'
```

2) List available rooms
- URL: `/api/v1/meeting-rooms/available/`
- Method: `GET`
- Query params (optional): `start_time`, `end_time` (ISO8601)
- Success: 200 OK, JSON `{ "available_rooms": [ ... ] }`

Example curl:

```bash
curl "http://127.0.0.1:8000/api/v1/meeting-rooms/available/?start_time=2026-01-28T10:00:00Z&end_time=2026-01-28T11:00:00Z"
```

3) Cancel a booking
- URL: `/api/v1/bookings/<booking_id>/cancel/`
- Method: `POST`
- Success: 200 OK

Example curl:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/bookings/42/cancel/
```

Notes & assumptions
-------------------
- Authentication is not required by the current implementation.
- Timezone handling: API expects ISO8601 datetimes; datetimes should be timezone-aware (UTC `Z`) or the server's timezone will apply.
- The models include `MeetingRoom`, `Booking`, and `History`. Booking validation prevents overlaps and disallows past bookings.

Next steps (optional)
---------------------
- Add `requirements.txt` and include pinned versions.
- Add authentication and permission checks.
- Add more tests (edge cases, auth, cancellation rules).
- Add API docs (Swagger / ReDoc).
