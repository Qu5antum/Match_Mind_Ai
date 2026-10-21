import logging
from collections import defaultdict
from typing import Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.match_event_service import MatchEventService
from .helper import Helper
from src.exceptions_handlers.business_logic_exception import BusinessLogicException

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 500

PASS_TYPES = {"pass"}
SHOT_TYPES = {"shot"}
DRIBBLE_TYPES = {"dribble", "carry"}
TACKLE_TYPES = {"tackle"}
INTERCEPTION_TYPES = {"interception", "intercept"}
FOUL_TYPES = {"foul"}
CORNER_TYPES = {"corner", "corner_kick"}
YELLOW_CARD_TYPES = {"yellow_card"}
RED_CARD_TYPES = {"red_card"}

SUCCESS_OUTCOMES = {"success", "successful", "completed"}
SHOT_ON_TARGET_OUTCOMES = {"goal", "saved", "on_target"}
GOAL_OUTCOMES = {"goal"}


class AnalyticsService:
    def __init__(
        self,
        session: AsyncSession,
        match_event_service: MatchEventService,
    ):
        self.session = session
        self.match_event_service = match_event_service
        self.helper = Helper(self.session)

    async def run_match_analysis(
        self,
        match_id: UUID,
    ) -> dict[str, Any]:
        match = await self.helper.get_match_or_404(match_id)
        events = await self._load_all_events(match_id)

        home_team_id = match.home_team_id
        away_team_id = match.away_team_id

        if home_team_id == away_team_id:
            raise BusinessLogicException("Home and away teams must be different")

        team_ids = {home_team_id, away_team_id}

        invalid_events = [
            event
            for event in events
            if event.team_id is not None
            and event.team_id not in team_ids
        ]
        if invalid_events:
            raise BusinessLogicException("Some match events reference teams outside this match")

        home_stats = self._calculate_team_stats(
            events, home_team_id
        )
        away_stats = self._calculate_team_stats(
            events, away_team_id
        )
        player_stats = self._calculate_player_stats(
            events, team_ids
        )
        shot_stats = self._calculate_shot_stats(
            events, team_ids
        )
        key_moments = self._detect_key_moments(
            events, team_ids
        )

        result = {
            "match_id": match_id,
            "teams": {
                "home": {
                    "team_id": home_team_id,
                    "statistics": home_stats,
                },
                "away": {
                    "team_id": away_team_id,
                    "statistics": away_stats,
                },
            },
            "players": player_stats,
            "shots": shot_stats,
            "key_moments": key_moments,
            "metadata": {
                "events_analyzed": len(events),
                "algorithm_version": "1.0",
                "possession_available": False,
            },
        }

        logger.info(
            "Match analysis completed",
            extra={
                "match_id": str(match_id),
                "events_analyzed": len(events),
                "key_moments": len(key_moments),
            },
        )

        return result

    async def calculate_match_statistics(
        self,
        match_id: UUID,
    ) -> dict[str, Any]:
        result = await self.run_match_analysis(match_id)
        return result["teams"]

    async def calculate_team_statistics(
        self,
        match_id: UUID,
        team_id: UUID,
    ) -> dict[str, Any]:
        match = await self.helper.get_match_or_404(match_id)

        if team_id not in {
            match.home_team_id,
            match.away_team_id,
        }:
            raise BusinessLogicException("Team does not participate in this match")

        events = await self._load_all_events(match_id)
        return self._calculate_team_stats(events, team_id)

    async def calculate_player_statistics(
        self,
        match_id: UUID,
        player_id: UUID,
    ) -> dict[str, Any]:
        await self.helper.get_match_or_404(match_id)
        events = await self._load_all_events(match_id)

        player_events = [
            event
            for event in events
            if event.player_id == player_id
        ]

        if not player_events:
            raise BusinessLogicException("No events found for this player in the match")

        stats = self._calculate_single_player_stats(player_events)
        stats["player_id"] = player_id
        stats["match_id"] = match_id
        return stats

    async def calculate_shot_statistics(
        self,
        match_id: UUID,
    ) -> dict[str, Any]:
        match = await self.helper.get_match_or_404(match_id)
        events = await self._load_all_events(match_id)

        return self._calculate_shot_stats(
            events,
            {match.home_team_id, match.away_team_id},
        )

    async def detect_key_moments(
        self,
        match_id: UUID,
    ) -> list[dict[str, Any]]:
        match = await self.helper.get_match_or_404(match_id)
        events = await self._load_all_events(match_id)

        return self._detect_key_moments(
            events,
            {match.home_team_id, match.away_team_id},
        )

    async def calculate_possession_statistics(
        self,
        match_id: UUID,
    ) -> dict[str, Any]:
        await self.helper.get_match_or_404(match_id)
        events = await self._load_all_events(match_id)

        # Эта базовая версия намеренно не выводит владение
        # из количества передач: это было бы недостоверно.
        has_possession_data = any(
            self._payload(event).get("possession_start_second") is not None
            and self._payload(event).get("possession_end_second") is not None
            for event in events
        )

        if not has_possession_data:
            return {
                "available": False,
                "reason": (
                    "Events do not contain possession time intervals"
                ),
            }

        possession_seconds: dict[UUID, float] = defaultdict(float)

        for event in events:
            payload = self._payload(event)
            start = payload.get("possession_start_second")
            end = payload.get("possession_end_second")

            if start is None or end is None or event.team_id is None:
                continue

            if end < start:
                raise BusinessLogicException("Possession interval end cannot precede start")

            possession_seconds[event.team_id] += end - start

        total = sum(possession_seconds.values())

        if total == 0:
            return {
                "available": False,
                "reason": "No measurable possession duration",
            }

        return {
            "available": True,
            "possession_seconds": dict(possession_seconds),
            "possession_percent": {
                team_id: round(seconds / total * 100, 2)
                for team_id, seconds in possession_seconds.items()
            },
            "total_seconds": total,
        }

    async def analyze_team_performance(
        self,
        match_id: UUID,
    ) -> dict[str, Any]:
        """Сравнивает показатели команд без генерации текстовых выводов."""
        result = await self.run_match_analysis(match_id)

        home = result["teams"]["home"]["statistics"]
        away = result["teams"]["away"]["statistics"]

        metrics = (
            "goals",
            "shots",
            "shots_on_target",
            "passes_attempted",
            "passes_completed",
            "tackles",
            "interceptions",
        )

        comparison = {}

        for metric in metrics:
            home_value = home[metric]
            away_value = away[metric]

            comparison[metric] = {
                "home": home_value,
                "away": away_value,
                "difference_home_minus_away": home_value - away_value,
            }

        return {
            "match_id": match_id,
            "comparison": comparison,
        }

    async def _load_all_events(
        self,
        match_id: UUID,
    ) -> list[Any]:
        events = []
        offset = 0

        while True:
            page = await self.match_event_service.get_match_events(
                match_id=match_id,
                offset=offset,
                limit=DEFAULT_PAGE_SIZE,
            )

            events.extend(page)

            if len(page) < DEFAULT_PAGE_SIZE:
                break

            offset += len(page)

        events.sort(
            key=lambda event: (
                event.sequence,
                event.event_time_second,
            )
        )

        return events

    def _calculate_team_stats(
        self,
        events: list[Any],
        team_id: UUID,
    ) -> dict[str, Any]:
        team_events = [
            event for event in events
            if event.team_id == team_id
        ]

        passes = [
            event for event in team_events
            if self._event_type(event) in PASS_TYPES
        ]
        shots = [
            event for event in team_events
            if self._event_type(event) in SHOT_TYPES
        ]
        dribbles = [
            event for event in team_events
            if self._event_type(event) in DRIBBLE_TYPES
        ]

        completed_passes = sum(
            self._is_success(event) for event in passes
        )
        completed_dribbles = sum(
            self._is_success(event) for event in dribbles
        )

        shots_on_target = sum(
            self._outcome(event) in SHOT_ON_TARGET_OUTCOMES
            for event in shots
        )

        goals = self._count_goals(team_events)

        return {
            "goals": goals,
            "shots": len(shots),
            "shots_on_target": shots_on_target,
            "shots_off_target": sum(
                self._outcome(event) in {
                    "off_target",
                    "wide",
                    "missed",
                }
                for event in shots
            ),
            "passes_attempted": len(passes),
            "passes_completed": completed_passes,
            "pass_accuracy_percent": self._percentage(
                completed_passes, len(passes)
            ),
            "dribbles_attempted": len(dribbles),
            "dribbles_completed": completed_dribbles,
            "dribble_success_percent": self._percentage(
                completed_dribbles, len(dribbles)
            ),
            "tackles": sum(
                self._event_type(event) in TACKLE_TYPES
                for event in team_events
            ),
            "interceptions": sum(
                self._event_type(event) in INTERCEPTION_TYPES
                for event in team_events
            ),
            "fouls": sum(
                self._event_type(event) in FOUL_TYPES
                for event in team_events
            ),
            "corners": sum(
                self._event_type(event) in CORNER_TYPES
                for event in team_events
            ),
            "yellow_cards": sum(
                self._event_type(event) in YELLOW_CARD_TYPES
                for event in team_events
            ),
            "red_cards": sum(
                self._event_type(event) in RED_CARD_TYPES
                for event in team_events
            ),
        }

    def _calculate_shot_stats(
        self,
        events: list[Any],
        team_ids: set[UUID],
    ) -> dict[str, Any]:
        result = {}

        for team_id in team_ids:
            team_shots = [
                event for event in events
                if event.team_id == team_id
                and self._event_type(event) in SHOT_TYPES
            ]

            on_target = [
                event for event in team_shots
                if self._outcome(event) in SHOT_ON_TARGET_OUTCOMES
            ]

            goals = self._count_goals(team_shots)

            xg_values = [
                self._payload(event).get("xg")
                for event in team_shots
            ]
            valid_xg = [
                value for value in xg_values
                if isinstance(value, (int, float))
                and not isinstance(value, bool)
                and 0 <= value <= 1
            ]

            result[str(team_id)] = {
                "shots": len(team_shots),
                "shots_on_target": len(on_target),
                "goals": goals,
                "shot_accuracy_percent": self._percentage(
                    len(on_target), len(team_shots)
                ),
                "conversion_percent": self._percentage(
                    goals, len(team_shots)
                ),
                "xg": round(sum(valid_xg), 3) if valid_xg else None,
                "xg_shots_count": len(valid_xg),
            }

        return result

    def _calculate_player_stats(
        self,
        events: list[Any],
        team_ids: set[UUID],
    ) -> list[dict[str, Any]]:
        player_events: dict[UUID, list[Any]] = defaultdict(list)

        for event in events:
            if (
                event.player_id is not None
                and event.team_id in team_ids
            ):
                player_events[event.player_id].append(event)

        result = []

        for player_id, items in player_events.items():
            stats = self._calculate_single_player_stats(items)
            stats["player_id"] = player_id
            result.append(stats)

        result.sort(key=lambda item: str(item["player_id"]))
        return result

    def _calculate_single_player_stats(
        self,
        events: list[Any],
    ) -> dict[str, Any]:
        passes = [
            event for event in events
            if self._event_type(event) in PASS_TYPES
        ]
        shots = [
            event for event in events
            if self._event_type(event) in SHOT_TYPES
        ]
        dribbles = [
            event for event in events
            if self._event_type(event) in DRIBBLE_TYPES
        ]

        completed_passes = sum(
            self._is_success(event) for event in passes
        )
        goals = self._count_goals(shots)

        return {
            "events_count": len(events),
            "goals": goals,
            "shots": len(shots),
            "shots_on_target": sum(
                self._outcome(event) in SHOT_ON_TARGET_OUTCOMES
                for event in shots
            ),
            "passes_attempted": len(passes),
            "passes_completed": completed_passes,
            "pass_accuracy_percent": self._percentage(
                completed_passes, len(passes)
            ),
            "dribbles_attempted": len(dribbles),
            "dribbles_completed": sum(
                self._is_success(event) for event in dribbles
            ),
            "tackles": sum(
                self._event_type(event) in TACKLE_TYPES
                for event in events
            ),
            "interceptions": sum(
                self._event_type(event) in INTERCEPTION_TYPES
                for event in events
            ),
        }

    def _detect_key_moments(
        self,
        events: list[Any],
        team_ids: set[UUID],
    ) -> list[dict[str, Any]]:
        moments = []

        for event in events:
            if event.team_id not in team_ids:
                continue

            event_type = self._event_type(event)
            outcome = self._outcome(event)
            payload = self._payload(event)

            if event_type == "goal" or (
                event_type in SHOT_TYPES
                and outcome in GOAL_OUTCOMES
            ):
                moments.append(
                    self._make_moment(
                        event,
                        moment_type="goal",
                        importance="critical",
                        reason="A goal was recorded",
                    )
                )

            elif (
                event_type in SHOT_TYPES
                and outcome in {"saved", "on_target"}
            ):
                xg = payload.get("xg")
                importance = (
                    "high"
                    if isinstance(xg, (int, float)) and xg >= 0.3
                    else "medium"
                )

                moments.append(
                    self._make_moment(
                        event,
                        moment_type="shot_on_target",
                        importance=importance,
                        reason="A shot on target was recorded",
                    )
                )

            elif (
                event_type in DRIBBLE_TYPES
                and self._is_success(event)
            ):
                moments.append(
                    self._make_moment(
                        event,
                        moment_type="successful_dribble",
                        importance="low",
                        reason="A successful dribble was recorded",
                    )
                )

        moments.sort(
            key=lambda item: (
                item["event_time_second"],
                item["sequence"],
            )
        )

        return moments

    @staticmethod
    def _make_moment(
        event: Any,
        moment_type: str,
        importance: str,
        reason: str,
    ) -> dict[str, Any]:
        return {
            "type": moment_type,
            "importance": importance,
            "reason": reason,
            "event_ids": [event.id],
            "sequence": event.sequence,
            "event_time_second": event.event_time_second,
            "team_id": event.team_id,
            "player_id": event.player_id,
            "evidence": {
                "event_type": AnalyticsService._event_type(event),
                "outcome": AnalyticsService._outcome(event),
                "payload": AnalyticsService._payload(event),
            },
        }

    @staticmethod
    def _count_goals(events: list[Any]) -> int:
        explicit_goals = [
            event for event in events
            if AnalyticsService._event_type(event) == "goal"
        ]

        if explicit_goals:
            return len(explicit_goals)

        return sum(
            AnalyticsService._event_type(event) in SHOT_TYPES
            and AnalyticsService._outcome(event) in GOAL_OUTCOMES
            for event in events
        )

    @staticmethod
    def _event_type(event: Any) -> str:
        value = event.event_type
        return str(getattr(value, "value", value)).lower()

    @staticmethod
    def _outcome(event: Any) -> str:
        value = event.outcome
        if value is None:
            return ""
        return str(getattr(value, "value", value)).lower()

    @staticmethod
    def _payload(event: Any) -> dict[str, Any]:
        payload = event.payload
        return payload if isinstance(payload, dict) else {}

    @classmethod
    def _is_success(cls, event: Any) -> bool:
        return cls._outcome(event) in SUCCESS_OUTCOMES

    @staticmethod
    def _percentage(
        numerator: int,
        denominator: int,
    ) -> float | None:
        if denominator == 0:
            return None

        return round(numerator / denominator * 100, 2)
