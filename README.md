# CarePoint Hospital Management System

A Python-first, server-rendered Hospital Management System built with FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, and Jinja2. Business rules, authentication, validation, CRUD, and persistence live in Python. JavaScript is restricted to a small table filter and confirmation helper.

## Features

- JWT cookie authentication with registration, login, and logout
- Complete patient, doctor, appointment, and medical-record create/read/update/delete workflows
- Appointment scheduling with patient/doctor validation, future-date validation, status/cancellation support
- Browser cookie authentication plus Bearer-token authentication for API clients
- Responsive Bootstrap dashboard with statistics, recent activity, sidebar navigation, profile page, search, validation, notifications, and mobile navigation
- Installable Progressive Web App (PWA) for Android, desktop browsers, and iOS home screens; static assets are available offline without storing patient data locally
- Layered repository/service design and Alembic PostgreSQL migration

## Quick start

```bash
cp .env.example .env
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
createdb hospital_db  # create user/database as configured in .env
alembic upgrade head
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000/register`, create the first account (it is assigned the `admin` role), then sign in. Interactive API docs are at `/docs`; the health endpoint is `/health`.

### Install as an app

Deploy over HTTPS (or use `localhost` during development). In Chrome, Edge, or Android Chrome, use the **Install app** button when it appears. On iPhone/iPad Safari, use **Share → Add to Home Screen**. CarePoint intentionally does not cache authenticated pages or API responses, so patient information is not retained by the offline cache.

### PostgreSQL quick setup

Create a PostgreSQL role and database matching `DATABASE_URL`, or change that variable in `.env`:

```sql
CREATE USER hospital WITH PASSWORD 'hospital';
CREATE DATABASE hospital_db OWNER hospital;
```

Run `alembic upgrade head` after any database reset. Never use the example JWT secret in production.

## Architecture

- `domain/`: entities and repository contracts (ports)
- `application/services/`: business use cases
- `infrastructure/`: SQLAlchemy models, repositories, password/JWT adapters
- `presentation/`: FastAPI routers, Pydantic DTOs, Jinja templates, small static assets
- `database/`, `alembic/`: connection and schema migration

## API

All resource APIs require authentication. Use `POST /api/v1/auth/register`, then `POST /api/v1/auth/login`. The login response includes `access_token`; send it as `Authorization: Bearer <token>` for non-browser clients, or let the browser use the secure HTTP-only cookie. CRUD endpoints are available under `/api/v1/patients`, `/doctors`, `/appointments`, and `/records`.

| Resource | API path |
| --- | --- |
| Patients | `/api/v1/patients` |
| Doctors | `/api/v1/doctors` |
| Appointments | `/api/v1/appointments` |
| Medical records | `/api/v1/records` |

## Tests

```bash
pytest -q
```
