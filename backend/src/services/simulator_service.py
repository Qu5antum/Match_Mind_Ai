import logging
import random
from dataclasses import dataclass
from typing import Any
from uuid import UUID
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.match import MatchStatus
from src.database.models.match_teams import MatchTeam
from src.repositories.match_repository import MatchRepository
from src.repositories.match_event_repository import MatchEventRepository
from src.services.match_service import MatchService
from src.services.match_event_service import MatchEventService
from src.exceptions_handlers.not_found_exception import NotFoundException
from src.exceptions_handlers.business_logic_exception import BusinessLogicException
from src.exceptions_handlers.database_exception import DatabaseException

logger = logging.getLogger(__name__)

FIELD_MIN = 0.0
FIELD_MAX = 100.0
SAVE_BATCH_SIZE = 100


@dataclass(frozen=True)
class PlayerProfile:
    id: UUID
    name: str
    position: str
    passing: int
    shooting: int
    dribbling: int
    defending: int
    pace: int
    stamina: int
    vision: int


@dataclass(frozen=True)
class TeamProfile:
    id: UUID
    side: str
    players: tuple[PlayerProfile, ...]
    tactics: dict[str, Any]


@dataclass(frozen=True)
class MatchContext:
    match_id: UUID
    home: TeamProfile
    away: TeamProfile
    duration_seconds: int
    seed: int


@dataclass
class MatchState:
    match_id: UUID
    current_second: int
    home_score: int
    away_score: int
    possession_team_id: UUID
    ball_x: float
    ball_y: float
    sequence: int


class SimulatorService:
    def __init__(
        self,
        session: AsyncSession,
        match_service: MatchService,
        match_event_service: MatchEventService
    ):
        self.session = session
        self.match_service = match_service
        self.match_event_service = match_event_service
        self.match_repo = MatchRepository(session=self.session)
        self.match_event_repo = MatchEventRepository(session=self.session)

    async def simulate_match(self, match_id: UUID) -> None:
        context = await self.load_match_context(match_id)

        if context.duration_seconds <= 0:
            raise BusinessLogicException("Match duration must be greater than zero")

        try:
            await self.match_service.start_simulation(match_id)

            rng = random.Random(context.seed)
            state = self.initialize_state(context, rng)
            pending_events: list[dict[str, Any]] = []

            kickoff = self._build_event(
                state=state,
                event_type="kick_off",
                team_id=state.possession_team_id,
                outcome="success",
            )
            pending_events.append(kickoff)

            while state.current_second < context.duration_seconds:
                event = self.simulate_tick(
                    context=context,
                    state=state,
                    rng=rng,
                )
                pending_events.append(event)

                if len(pending_events) >= SAVE_BATCH_SIZE:
                    await self._save_events(pending_events)
                    pending_events.clear()

            if pending_events:
                await self._save_events(pending_events)

            await self._save_final_score(state)
            await self.match_service.set_ready(match_id)

            logger.info(
                "Match simulation completed",
                extra={
                    "match_id": str(match_id),
                    "home_score": state.home_score,
                    "away_score": state.away_score,
                    "events": state.sequence,
                },
            )

        except Exception as exc:
            await self.session.rollback()

            logger.exception(
                "Match simulation failed",
                extra={"match_id": str(match_id)},
            )

            try:
                await self.match_service.fail_match(match_id)
            except Exception:
                logger.exception(
                    "Failed to mark match as FAILED",
                    extra={"match_id": str(match_id)},
                )

            if isinstance(exc, (NotFoundException, BusinessLogicException)):
                raise

            if isinstance(exc, SQLAlchemyError):
                raise DatabaseException("Database error during match simulation") from exc

            raise

    async def load_match_context(self, match_id: UUID) -> MatchContext:
        match = await self.match_repo.load_match_with_match_teams_players(match_id)

        if match is None:
            raise NotFoundException("Match not found")

        if MatchStatus(match.status) != MatchStatus.CREATED:
            raise BusinessLogicException(f"Cannot simulate match with status {match.status}")

        participants = {
            participant.side: participant
            for participant in match.match_teams
        }

        if "home" not in participants or "away" not in participants:
            raise BusinessLogicException("Match must have both home and away participants")

        home = self._build_team_profile(participants["home"])
        away = self._build_team_profile(participants["away"])

        if home.id != match.home_team_id or away.id != match.away_team_id:
            raise BusinessLogicException("Match participants do not match home/away team IDs")

        if home.id == away.id:
            raise BusinessLogicException("Home team and away team must be different")

        if not home.players or not away.players:
            raise BusinessLogicException("Both teams must have players before simulation")

        scenario = match.scenario or {}

        if not isinstance(scenario, dict):
            raise BusinessLogicException("Match scenario must be a JSON object")

        duration_minutes = scenario.get("duration_minutes", 90)
        if not isinstance(duration_minutes, int) or isinstance(
            duration_minutes, bool
        ):
            raise BusinessLogicException("duration_minutes must be an integer")

        seed = match.seed
        if seed is None:
            seed = scenario.get("seed", 42)

        if not isinstance(seed, int) or isinstance(seed, bool):
            raise BusinessLogicException("seed must be an integer")

        return MatchContext(
            match_id=match.id,
            home=home,
            away=away,
            duration_seconds=duration_minutes * 60,
            seed=seed,
        )

    def _build_team_profile(self, participant: MatchTeam) -> TeamProfile:
        team = participant.team
        lineup_ids = participant.lineup or []

        if lineup_ids:
            allowed_ids = {UUID(str(player_id)) for player_id in lineup_ids}
            players = [
                player for player in team.players
                if player.id in allowed_ids
            ]

            if len(players) != len(allowed_ids):
                raise BusinessLogicException(f"Invalid lineup for team {team.name}")
        else:
            players = list(team.players)

        if len({player.id for player in players}) != len(players):
            raise BusinessLogicException(f"Duplicate players in lineup for team {team.name}")

        profiles = tuple(
            PlayerProfile(
                id=player.id,
                name=player.name,
                position=player.position,
                passing=player.passing,
                shooting=player.shooting,
                dribbling=player.dribbling,
                defending=player.defending,
                pace=player.pace,
                stamina=player.stamina,
                vision=player.vision,
            )
            for player in sorted(players, key=lambda item: str(item.id))
        )

        tactics = participant.tactics or {}

        return TeamProfile(
            id=team.id,
            side=participant.side,
            players=profiles,
            tactics=tactics,
        )

    def initialize_state(
        self,
        context: MatchContext,
        rng: random.Random,
    ) -> MatchState:
        kickoff_team = rng.choice([context.home, context.away])

        return MatchState(
            match_id=context.match_id,
            current_second=0,
            home_score=0,
            away_score=0,
            possession_team_id=kickoff_team.id,
            ball_x=50.0,
            ball_y=50.0,
            sequence=0,
        )

    def simulate_tick(
        self,
        context: MatchContext,
        state: MatchState,
        rng: random.Random,
    ) -> dict[str, Any]:
        attacking = self._get_team(context, state.possession_team_id)
        defending = self._get_opponent(context, attacking.id)

        elapsed = rng.randint(5, 20)
        state.current_second = min(
            state.current_second + elapsed,
            context.duration_seconds,
        )

        player = self._choose_player(attacking, rng)
        phase = self._get_phase(attacking, state)
        action = self._choose_action(phase, attacking, rng)

        start_x = state.ball_x
        start_y = state.ball_y

        if action == "pass":
            event = self._resolve_pass(
                context, state, attacking, defending, player, rng
            )
        elif action == "carry":
            event = self._resolve_carry(
                context, state, attacking, defending, player, rng
            )
        elif action == "shot":
            event = self._resolve_shot(
                context, state, attacking, defending, player, rng
            )
        elif action == "cross":
            event = self._resolve_cross(
                context, state, attacking, defending, player, rng
            )
        else:
            event = self._resolve_tackle(
                context, state, attacking, defending, player, rng
            )

        event["start_x"] = start_x
        event["start_y"] = start_y
        event["event_time_second"] = state.current_second

        return event

    def _get_phase(
        self,
        team: TeamProfile,
        state: MatchState,
    ) -> str:
        attacking_right = team.side == "home"
        progress = state.ball_x if attacking_right else 100.0 - state.ball_x

        if progress < 35:
            return "BUILD_UP"
        if progress < 70:
            return "PROGRESSION"
        return "FINAL_THIRD"

    def _choose_action(
        self,
        phase: str,
        team: TeamProfile,
        rng: random.Random,
    ) -> str:
        options = {
            "BUILD_UP": [
                ("pass", 0.72),
                ("carry", 0.23),
                ("tackle", 0.05),
            ],
            "PROGRESSION": [
                ("pass", 0.48),
                ("carry", 0.27),
                ("cross", 0.12),
                ("shot", 0.08),
                ("tackle", 0.05),
            ],
            "FINAL_THIRD": [
                ("pass", 0.28),
                ("carry", 0.18),
                ("cross", 0.20),
                ("shot", 0.29),
                ("tackle", 0.05),
            ],
        }

        tactics = str(team.tactics.get("style", "balanced"))

        weights = dict(options[phase])
        if tactics == "possession":
            weights["pass"] *= 1.25
            weights["carry"] *= 0.9
        elif tactics == "counter_attack":
            weights["carry"] *= 1.2
            weights["shot"] *= 1.15
        elif tactics == "high_press":
            weights["tackle"] *= 1.15

        return rng.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=1,
        )[0]

    def _resolve_pass(
        self,
        context: MatchContext,
        state: MatchState,
        attacking: TeamProfile,
        defending: TeamProfile,
        player: PlayerProfile,
        rng: random.Random,
    ) -> dict[str, Any]:
        receiver = self._choose_player(attacking, rng, exclude=player.id)
        distance = rng.uniform(5.0, 25.0)
        pressure = rng.uniform(0.0, 1.0)

        probability = self._clamp(
            0.94
            + (player.passing - 75) * 0.002
            + (player.vision - 75) * 0.001
            - distance * 0.008
            - pressure * 0.15,
            0.45,
            0.98,
        )

        success = rng.random() < probability

        if success:
            state.ball_x, state.ball_y = self._advance_ball(
                attacking, state, distance, rng
            )
            related_player_id = receiver.id
            outcome = "success"
        else:
            state.possession_team_id = defending.id
            related_player_id = None
            outcome = "intercepted"

        return self._build_event(
            state=state,
            event_type="pass",
            team_id=attacking.id,
            player_id=player.id,
            related_player_id=related_player_id,
            outcome=outcome,
            end_x=state.ball_x,
            end_y=state.ball_y,
            payload={
                "distance": round(distance, 2),
                "under_pressure": pressure > 0.65,
                "probability": round(probability, 3),
            },
        )

    def _resolve_carry(
        self,
        context: MatchContext,
        state: MatchState,
        attacking: TeamProfile,
        defending: TeamProfile,
        player: PlayerProfile,
        rng: random.Random,
    ) -> dict[str, Any]:
        defender = self._choose_player(defending, rng)
        probability = self._clamp(
            0.58
            + (player.dribbling - defender.defending) * 0.006
            + (player.pace - defender.pace) * 0.002,
            0.15,
            0.90,
        )

        success = rng.random() < probability

        if success:
            state.ball_x, state.ball_y = self._advance_ball(
                attacking, state, rng.uniform(3.0, 14.0), rng
            )
            outcome = "success"
        else:
            state.possession_team_id = defending.id
            outcome = "dispossessed"

        return self._build_event(
            state=state,
            event_type="carry",
            team_id=attacking.id,
            player_id=player.id,
            related_player_id=defender.id if not success else None,
            outcome=outcome,
            end_x=state.ball_x,
            end_y=state.ball_y,
            payload={"probability": round(probability, 3)},
        )

    def _resolve_shot(
        self,
        context: MatchContext,
        state: MatchState,
        attacking: TeamProfile,
        defending: TeamProfile,
        player: PlayerProfile,
        rng: random.Random,
    ) -> dict[str, Any]:
        keeper = next(
            (p for p in defending.players if p.position == "GK"),
            None,
        )

        progress = (
            state.ball_x
            if attacking.side == "home"
            else 100.0 - state.ball_x
        )
        distance_factor = self._clamp((progress - 55.0) / 45.0, 0.0, 1.0)

        keeper_defending = keeper.defending if keeper else 60
        goal_probability = self._clamp(
            0.02
            + distance_factor * 0.24
            + (player.shooting - 70) * 0.003
            - (keeper_defending - 60) * 0.002,
            0.01,
            0.45,
        )

        roll = rng.random()

        if roll < goal_probability:
            outcome = "goal"
            if attacking.side == "home":
                state.home_score += 1
            else:
                state.away_score += 1

        elif roll < goal_probability + 0.25:
            outcome = "saved"
            state.possession_team_id = defending.id

        elif roll < goal_probability + 0.45:
            outcome = "blocked"
            state.possession_team_id = defending.id

        else:
            outcome = "off_target"
            state.possession_team_id = defending.id

        state.ball_x = 50.0
        state.ball_y = 50.0

        return self._build_event(
            state=state,
            event_type="shot",
            team_id=attacking.id,
            player_id=player.id,
            related_player_id=keeper.id if keeper and outcome == "saved" else None,
            outcome=outcome,
            end_x=state.ball_x,
            end_y=state.ball_y,
            payload={
                "goal_probability": round(goal_probability, 3),
                "score": {
                    "home": state.home_score,
                    "away": state.away_score,
                },
            },
        )

    def _resolve_cross(
        self,
        context: MatchContext,
        state: MatchState,
        attacking: TeamProfile,
        defending: TeamProfile,
        player: PlayerProfile,
        rng: random.Random,
    ) -> dict[str, Any]:
        success = rng.random() < self._clamp(
            0.45 + (player.passing - 70) * 0.004,
            0.20,
            0.75,
        )

        if success:
            state.ball_x, state.ball_y = self._advance_ball(
                attacking, state, rng.uniform(8.0, 18.0), rng
            )
            outcome = "successful_cross"
        else:
            state.possession_team_id = defending.id
            outcome = "cleared"

        return self._build_event(
            state=state,
            event_type="cross",
            team_id=attacking.id,
            player_id=player.id,
            outcome=outcome,
            end_x=state.ball_x,
            end_y=state.ball_y,
        )

    def _resolve_tackle(
        self,
        context: MatchContext,
        state: MatchState,
        attacking: TeamProfile,
        defending: TeamProfile,
        player: PlayerProfile,
        rng: random.Random,
    ) -> dict[str, Any]:
        defender = self._choose_player(defending, rng)
        success = rng.random() < self._clamp(
            0.45 + (defender.defending - player.dribbling) * 0.005,
            0.15,
            0.85,
        )

        if success:
            state.possession_team_id = defending.id
            outcome = "success"
        else:
            outcome = "failed"

        return self._build_event(
            state=state,
            event_type="tackle",
            team_id=defending.id,
            player_id=defender.id,
            related_player_id=player.id,
            outcome=outcome,
            end_x=state.ball_x,
            end_y=state.ball_y,
        )

    def _advance_ball(
        self,
        team: TeamProfile,
        state: MatchState,
        distance: float,
        rng: random.Random,
    ) -> tuple[float, float]:
        direction = 1.0 if team.side == "home" else -1.0
        x = self._clamp(
            state.ball_x + direction * distance,
            FIELD_MIN,
            FIELD_MAX,
        )
        y = self._clamp(
            state.ball_y + rng.uniform(-distance, distance),
            FIELD_MIN,
            FIELD_MAX,
        )
        return x, y

    def _build_event(
        self,
        state: MatchState,
        event_type: str,
        team_id: UUID,
        player_id: UUID | None = None,
        related_player_id: UUID | None = None,
        outcome: str | None = None,
        end_x: float | None = None,
        end_y: float | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        state.sequence += 1

        return {
            "match_id": state.match_id,
            "sequence": state.sequence,
            "event_time_second": state.current_second,
            "event_type": event_type,
            "team_id": team_id,
            "player_id": player_id,
            "related_player_id": related_player_id,
            "start_x": state.ball_x,
            "start_y": state.ball_y,
            "end_x": end_x,
            "end_y": end_y,
            "outcome": outcome,
            "payload": payload or {},
        }

    async def _save_events(
        self,
        events: list[dict[str, Any]],
    ) -> None:
        if not events:
            return

        await self.match_event_service.create_events(events)

    async def _save_final_score(self, state: MatchState) -> None:
        try:
            match = await self.match_repo.get(state.match_id)

            if match is None:
                raise NotFoundException("Match not found")

            match.home_score = state.home_score
            match.away_score = state.away_score
            match.current_minute = state.current_second // 60
            match.current_second = state.current_second % 60

            await self.session.commit()

        except SQLAlchemyError:
            await self.session.rollback()
            raise

    def _get_team(
        self,
        context: MatchContext,
        team_id: UUID,
    ) -> TeamProfile:
        if context.home.id == team_id:
            return context.home
        if context.away.id == team_id:
            return context.away
        raise BusinessLogicException("Unknown team in match state")

    def _get_opponent(
        self,
        context: MatchContext,
        team_id: UUID,
    ) -> TeamProfile:
        return (
            context.away
            if context.home.id == team_id
            else context.home
        )

    def _choose_player(
        self,
        team: TeamProfile,
        rng: random.Random,
        exclude: UUID | None = None,
    ) -> PlayerProfile:
        candidates = [
            player for player in team.players
            if player.id != exclude
        ]

        if not candidates:
            raise BusinessLogicException(
                f"No eligible players for team {team.id}"
            )

        return rng.choice(candidates)

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(value, maximum))
