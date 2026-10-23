# MatchMind AI

MatchMind AI is a football match simulation and analytics application. Create teams and players, configure a match, simulate its events, inspect the resulting statistics, and ask an AI assistant to explain what happened.

This project was created during **Inside the Game: Developer Hackathon — Build the future of football with AI**, hosted by **Microsoft**.

## What it does

- Manages teams and their player rosters.
- Creates football matches with a configurable duration, difficulty, weather, formation, and random seed.
- Simulates a match and stores its event-by-event timeline and final score.
- Calculates team and player statistics, shot metrics, and key moments from recorded events.
- Generates and stores evidence-based match insights.
- Provides AI features including match summaries, questions and answers, tactical analysis, team comparisons, player analysis, and recommendations.
- Presents the data in a responsive React dashboard.

## Application architecture

```text
React + TypeScript frontend
          │ HTTP / JSON
          ▼
FastAPI backend ───── Gemini API
          │
          ▼
PostgreSQL
```

### Frontend

The frontend is a React 19 + TypeScript single-page application built with Vite. It uses Axios for HTTP requests and keeps navigation in the URL hash, so no frontend routing package is required.

The UI is organized into:

- `frontend/src/pages/` — dashboard, teams, team profile, players, matches, match creation, match details, and not-found screens.
- `frontend/src/components/` — shared navigation and page layout, team and player cards/forms, match score/statistics/timeline, insights, and AI chat/explanation components.
- `frontend/src/api/` — typed API clients for teams, players, matches, match events, analytics, insights, and agent operations.
- `frontend/src/types/` — TypeScript models corresponding to backend request and response schemas.

Routes use the browser hash:

| Route | Screen |
| --- | --- |
| `#/` | Dashboard |
| `#/teams` | Team directory |
| `#/teams/:id` | Team profile and roster |
| `#/players` | Players across teams |
| `#/matches` | Match library |
| `#/matches/new` | Match creation |
| `#/matches/:id` | Match score, events, statistics, and AI analysis |

By default, the browser API client calls `http://localhost:8080/api`. Set `VITE_API_URL` at frontend build time to use another API base URL.

### Backend

The backend is a Python 3.12 application using FastAPI, Pydantic, SQLAlchemy's async ORM, and PostgreSQL via `asyncpg`. Alembic manages database migrations. The application registers separate routers for teams, players, matches, events, analytics, insights, and AI-agent operations.

Backend code is separated into:

- `backend/src/api/endpoints/` — HTTP routes and dependency injection.
- `backend/src/api/schemas/` — validation and serialization for API requests and responses.
- `backend/src/services/` — match lifecycle, simulation, analytics, insights, and AI application logic.
- `backend/src/repositories/` — database access.
- `backend/src/database/models/` — SQLAlchemy entities and relationships.
- `backend/src/providers/` — AI provider integrations.
- `backend/migrations/` — Alembic migration history.

### Data model

- **Team** — unique name and short name; owns players and participates in matches.
- **Player** — team membership, position, and ratings for passing, shooting, dribbling, defending, pace, stamina, and vision. Ratings are constrained to 1–100.
- **Match** — home and away teams, score, status, elapsed time, seed, and scenario settings.
- **Match team** — a team's side in a match, with formation, tactics, and lineup information.
- **Match event** — ordered timeline entry with event type, match time, team/player references, optional pitch coordinates, outcome, and JSON payload.
- **Match insight** — persisted AI-generated or manually created insight, including evidence, importance, audience, language, and optional model name.

## How a match works

1. **Prepare teams.** Create at least two different teams and add players to both. A simulation cannot start if either team has no players.
2. **Create a fixture.** The client sends the two team IDs, a non-negative integer seed, and a scenario. The backend creates the match and its home/away participants in one service operation.
3. **Simulate.** The simulator checks that the match is still in `created` state, loads the team rosters and match configuration, and initializes Python's `random.Random` with the match seed.
4. **Generate events.** This is a simplified stochastic simulation, not a full rules engine. It advances simulated time in short intervals and selects a possession team, player, game phase, and action. Player ratings affect event outcomes; the simulation can produce passes, carries, shots, crosses, tackles, goals, and other events. Events are saved in batches, followed by the final score and transition to `ready`.
5. **Analyze.** Analytics are calculated from the saved event timeline. The service derives team and player statistics, shot metrics, and key moments. Possession is reported as unavailable when the timeline does not contain possession intervals.
6. **Generate AI insights.** For a `ready` or `finished` match, the backend builds an AI prompt from the analytics and requests structured output. Generated insights are persisted with their evidence, audience, language, and model metadata. Repeated generation for unchanged match data, language, and audience can reuse saved insights rather than call the model again.
7. **Explore and ask questions.** The frontend shows match events, statistics, and insights; it can also request a summary, answer a question, explain an insight, or generate tactical analysis.

### Reproducibility

The simulator uses the match's `seed` to initialize its pseudorandom number generator. Reusing a seed with the same match setup, player data, and simulator version is intended to reproduce the same simulation. Changing the seed changes the pseudorandom sequence. The seed is visible in the match creation form and match details.

The scenario schema accepts duration, difficulty, weather, formations, and tactics. Currently, duration and seed directly affect simulation, while player ratings influence event outcomes. Some other scenario options are stored with the match but are not yet fully applied to simulation behavior; tactics are also initialized to the backend's default match-team data.

### Match lifecycle

Match status transitions are validated by the backend:

```text
created → simulating → ready → playing ⇄ paused → finished
created, simulating, ready, playing, or paused → failed
```

Simulation currently runs as part of the HTTP request rather than as a background job. Large simulations may therefore take longer to return; a job queue would be a future option if asynchronous execution and retries are needed.

## AI behavior and configuration

The active backend dependency currently creates a `GeminiProvider` for agent requests. The provider requests JSON matching the Pydantic response schema. Prompts tell the model to use only supplied match data, avoid inventing events or statistics, distinguish evidence from interpretation, and disclose limitations when evidence is insufficient.

Configure Gemini in the backend environment:

```dotenv
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=your-supported-gemini-model
GEMINI_TIMEOUT_MS=30000
```

Do not commit real API keys. AI operations require valid provider configuration; core team, player, match, simulation, and analytics features do not make AI calls.

The repository also contains a Manus provider implementation, but the current FastAPI dependency wiring selects Gemini. Setting Manus variables alone does not switch the active provider.

## API overview

The API is rooted at `/api`. Interactive OpenAPI documentation is available at `/docs` when the backend is running.

| Area | Main endpoints |
| --- | --- |
| Teams | `POST /team`, `GET /team`, `GET/PATCH/DELETE /team/{team_id}` |
| Players | `POST /player`, `POST /player/bulk`, `GET/PATCH/DELETE /player/{player_id}`, `GET /team/{team_id}/players` |
| Matches | `POST /matches`, `GET /matches`, `GET /matches/{match_id}`, `GET /matches/{match_id}/detail` |
| Match lifecycle | `POST /matches/{match_id}/simulate`, `/play`, `/pause`, `/finish` |
| Events | `GET/POST/DELETE /matches/{match_id}/events`, `POST /matches/{match_id}/events/bulk`, `GET /matches/{match_id}/events/count`, `GET /matches/{match_id}/events/by-type/{event_type}`, `GET /matches/{match_id}/events/by-player/{player_id}`, `GET /matches/{match_id}/events/after/{sequence}`, `GET /matches/events/{event_id}` |
| Analytics | `GET /matches/{match_id}/analytics`, `/analytics/statistics`, `/analytics/teams/{team_id}`, `/analytics/players/{player_id}`, `/analytics/shots`, `/analytics/key-moments`, `/analytics/possession`, `/analytics/team-performance` |
| Insights | `POST /matches/{match_id}/insights/generate`, `GET /matches/{match_id}/insights`, `GET /matches/{match_id}/insights/by-minute`, `POST /insights`, `POST /insights/bulk`, `GET /insights/{insight_id}` |
| AI agent | `POST /matches/{match_id}/agent/summary`, `/ask`, `/key-moments/explain`, `/tactical-analysis`, `/team-comparison`, `/player-analysis`, `/recommendations`; `POST /insights/{insight_id}/explain` and `/personalize` |

AI request schemas support a response language. The frontend currently requests English output (`language: "en"`).

## Run with Docker Compose

Requirements: Docker Desktop with Docker Compose.

From the repository root:

```bash
docker compose up --build
```

The compose configuration starts PostgreSQL, the FastAPI backend, and the static frontend. The backend container runs `alembic upgrade head` before starting Uvicorn.

| Service | Local address |
| --- | --- |
| Frontend | <http://localhost:3001> |
| Backend API | <http://localhost:8080/api> |
| OpenAPI docs | <http://localhost:8080/docs> |
| PostgreSQL | `localhost:5432` |

Compose database defaults are provided for local development. Override them with environment variables such as `DB_USER`, `DB_PASS`, and `DB_NAME`; do not use development defaults for a deployed environment. Add Gemini configuration to the backend environment when using AI features.

## Run locally

### 1. Start PostgreSQL

Start a PostgreSQL instance and create a database. The backend defaults to host `db`, which is the Compose service name; for a local host install, override `DB_HOST` to `localhost`.

### 2. Configure and run the backend

In `backend/`, create a `.env` file if you need to override settings:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=match_mind_db
APP_NAME=match_mind_ai
DEBUG=true
GEMINI_API_KEY=
GEMINI_MODEL=
GEMINI_TIMEOUT_MS=30000
```

Install dependencies, apply migrations, and start the API:

```bash
cd backend
python -m venv .venv
# Activate the virtual environment using the command for your shell.
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

### 3. Run the frontend

In a separate terminal:

```bash
cd frontend
npm install
npm run dev
```

Vite prints the local development URL in the terminal. To use a backend on a different address, set `VITE_API_URL` before starting/building the frontend, for example:

```dotenv
VITE_API_URL=http://localhost:8080/api
```

## Development commands

Frontend:

```bash
cd frontend
npm run dev
npm run build
npm run lint
```

Backend:

```bash
cd backend
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```

## Current limitations and notes

- Both teams need players before simulation; create players through the team profile or player API first.
- `play`, `pause`, and `finish` update the match lifecycle. They do not currently stream a live simulation clock or events to the browser.
- Possession analytics return an unavailable result if events lack possession time intervals.
- AI features require the configured Gemini API key and model.
- The backend CORS setting defaults to `["*"]`; configure allowed origins appropriately before public deployment.
- Redis-related settings exist in the backend configuration/Compose environment, but the current Compose file does not start a Redis service and the main application flow does not require Redis.
- No automated backend test suite is currently included in the repository.
