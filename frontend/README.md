# MatchMind AI frontend

MatchMind AI is a React + TypeScript dashboard for football match simulation, team and player management, match events, statistics, and AI-generated analysis.

## Development

```bash
npm install
npm run dev
```

The frontend expects the backend API at `http://localhost:8080/api` by default. Set `VITE_API_URL` to override the API base URL.

## Application structure

- `src/api/` contains typed API clients for teams, players, matches, analytics, insights, and the AI agent.
- `src/components/` contains shared layout, team, player, match, insight, and agent UI.
- `src/pages/` contains dashboard, team, player, and match screens.
- Client-side routes use the URL hash: `#/`, `#/teams`, `#/players`, `#/matches`, `#/matches/new`, `#/teams/:id`, and `#/matches/:id`.

Run `npm run build` for a production build and TypeScript validation, or `npm run lint` to check the frontend source.
