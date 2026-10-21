# MatchMind AI

Backend for creating and simulating football matches, computing match analytics,
and generating evidence-based AI insights with Gemini.

## Match analysis flow

1. Create a match with `POST /api/matches`.
2. Simulate it with `POST /api/matches/{match_id}/simulate`.
3. Read its event timeline and computed analytics.
4. Generate insights with `POST /api/matches/{match_id}/insights/generate`.
5. Read the persisted insights or ask the agent to explain them.

Insight generation is allowed for matches in `ready` or `finished` status.
Repeated requests with the same match data, language, and audience return the
same saved insight records instead of calling Gemini and inserting duplicates.
The request locks the match row while it calculates, generates, and saves
insights so concurrent requests for that match are serialized.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/api/team` | Create a team |
| `GET` | `/api/team` | List teams |
| `GET`, `PATCH`, `DELETE` | `/api/team/{team_id}` | Read, update, or delete a team |
| `POST` | `/api/player` | Create a player |
| `GET` | `/api/team/{team_id}/players` | List players for a team |
| `GET`, `PATCH`, `DELETE` | `/api/player/{player_id}` | Read, update, or delete a player |
| `POST` | `/api/matches` | Create a match |
| `GET` | `/api/matches/{match_id}` | Read a match |
| `POST` | `/api/matches/{match_id}/simulate` | Run match simulation |
| `GET` | `/api/matches/{match_id}/events` | Get paginated match events |
| `GET` | `/api/matches/{match_id}/analytics` | Calculate match statistics and key moments |
| `POST` | `/api/matches/{match_id}/insights/generate` | Generate and persist AI insights |
| `GET` | `/api/matches/{match_id}/insights` | List and filter saved insights |
| `POST` | `/api/insights/{insight_id}/explain` | Explain an existing insight |
| `POST` | `/api/matches/{match_id}/agent/summary` | Generate a completed-match summary |
| `POST` | `/api/matches/{match_id}/agent/ask` | Ask a question about a match |

The insight-generation body accepts optional `language` and `audience` fields.
Agent generation uses asynchronous FastAPI endpoints and a Gemini HTTP timeout
of 30 seconds (`GEMINI_TIMEOUT_MS` can override it). Simulation and AI calls
currently run in the request lifecycle; move them to a job queue if operational
latency or retry requirements grow.

Set `GEMINI_API_KEY` and `GEMINI_MODEL` in the backend environment to enable AI
operations. Apply the database schema with Alembic before starting the API.