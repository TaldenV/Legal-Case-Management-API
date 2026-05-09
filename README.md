# Legal Case Management API

A REST API for managing clients, incidents, cases, and claims in a legal services context — built with FastAPI, PostgreSQL, SQLAlchemy, and Docker.

This project was built to demonstrate normalized relational database design, per-partner API key authentication, and production-grade backend engineering patterns in a traditional code stack.

---

## Background

The schema design in this project mirrors a real normalization problem I helped solve at a personal injury law firm.
When I joined, all client, case, claim, and incident data were stored in a single denormalized record. If a client opened a second claim, the entire record had to be duplicated. Something as simple as a client changing their phone number required updates in multiple places, often resulting in data inconsistencies.
This project attempts to recreate the core data relationship into distinct, related entities so that a client can have multiple cases, an incident can represent multiple people involved in an accident, and a single case can have multiple claims — with no data duplication.

---

## Tech Stack

- **FastAPI** — REST API framework
- **PostgreSQL** — relational database
- **SQLAlchemy** — ORM for database models and queries
- **Alembic** — database migration management
- **Docker + docker-compose** — containerized local development
- **Pydantic** — request and response validation

---

## Schema Design

![Relationship Schema](./assets/Relationship%20Schema.png)

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/TaldenV/Legal-Case-Management-API
cd Legal-Case-Management-API

# 2. Copy the environment template and fill in your values
cp .env.example .env

# 3. Build and start the containers
docker-compose up --build

# 4. Run database migrations
docker-compose exec app alembic upgrade head
```

The API will be running at `http://localhost:8000`.

Auto-generated interactive docs are available at `http://localhost:8000/docs`.

---

## Authentication

Every endpoint (except `/health`) requires an API key passed in the request header:

```
X-API-Key: your-key-here
```

### Generate your first API key

```bash
curl -X POST "http://localhost:8000/api-keys?partner_name=your_name"
```

**Save the returned key immediately — it is shown once and not stored.**

### Revoke a key

```bash
curl -X DELETE "http://localhost:8000/api-keys/{key_id}" \
  -H "X-API-Key: your-key-here"
```

---

## API Endpoints

### Clients
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/clients` | Create a new client |
| GET | `/clients` | List all clients |
| GET | `/clients/{id}` | Get a client by ID |
| PATCH | `/clients/{id}` | Update a client |
| DELETE | `/clients/{id}` | Delete a client |

### Cases
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/cases` | Open a new case |
| GET | `/cases` | List cases (filter by `?client_id=`) |
| GET | `/cases/{id}` | Get a case by ID |
| PATCH | `/cases/{id}` | Update a case (closing sets `closed_at` automatically) |
| DELETE | `/cases/{id}` | Delete a case |

### Claims
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/claims` | File a claim against an open case |
| GET | `/claims` | List claims (filter by `?case_id=`) |
| GET | `/claims/{id}` | Get a claim by ID |
| PATCH | `/claims/{id}` | Update a claim |
| DELETE | `/claims/{id}` | Delete a claim |

### Incidents
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/incidents` | Create an incident against a case |
| GET | `/incidents` | List incidents (filter by `?claim_id=`) |
| GET | `/incidents/{id}` | Get an incident by ID |
| PATCH | `/incidents/{id}` | Update an incident |
| DELETE | `/incidents/{id}` | Delete an incident |

### API Keys
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api-keys` | Generate a new API key |
| DELETE | `/api-keys/{id}` | Revoke a key |

---

## Database Migrations

Migrations are managed with Alembic. Every schema change is versioned and tracked.

```bash
# Apply all pending migrations
docker-compose exec app alembic upgrade head

# Generate a new migration after changing a model
docker-compose exec app alembic revision --autogenerate -m "description of change"

# Roll back the last migration
docker-compose exec app alembic downgrade -1

# Check current migration status
docker-compose exec app alembic current
```

Migration files live in `alembic/versions/` and are committed to Git — anyone cloning the repo can recreate the exact database schema by running `alembic upgrade head`.

---

## Postman Collection

A Postman collection is included in the `postman/` folder. Import it directly into Postman to test all endpoints without manual setup.

Set up a Postman environment variable `api_key` with your generated key, then use `{{api_key}}` in the `X-API-Key` header across all requests.

---

## Project Structure

```
├── app/
│   ├── main.py              # FastAPI app entry point, router registration
│   ├── database.py          # SQLAlchemy engine, session, and Base
│   ├── middleware/
│   │   └── auth.py          # API key validation dependency
│   ├── models/              # SQLAlchemy table definitions
│   │   ├── client.py
│   │   ├── case.py
│   │   ├── claim.py
│   │   ├── incident.py
│   │   └── api_key.py
│   ├── routers/             # Route handlers grouped by resource
│   │   ├── clients.py
│   │   ├── cases.py
│   │   ├── claims.py
│   │   └── incidents.py
│   └── schemas/             # Pydantic request/response validation
│       ├── client.py
│       ├── case.py
│       ├── claim.py
│       └── incident.py
├── assets/                  # Images for README
├── alembic/                 # Migration configuration and history
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── postman/                 # Postman collection for API testing
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env.example
└── .gitignore
```