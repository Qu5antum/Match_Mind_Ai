from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING
import uuid

from sqlalchemy import (
    CheckConstraint,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    SmallInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .match_events import MatchEvent
    from .match_insights import MatchInsight
    from .match_teams import MatchTeam
    from .team import Team


class MatchStatus(StrEnum):
    CREATED = "created"
    SIMULATING = "simulating"
    READY = "ready"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"
    FAILED = "failed"

    @property
    def allowed_transitions(self) -> set["MatchStatus"]:
        return _ALLOWED_TRANSITIONS.get(self, set())

    def can_transition_to(self, next_state: str | "MatchStatus") -> bool:
        try:
            target = MatchStatus(next_state)
            return target in self.allowed_transitions
        except ValueError:
            return False


_ALLOWED_TRANSITIONS: dict[MatchStatus, set[MatchStatus]] = {
    MatchStatus.CREATED: {MatchStatus.SIMULATING, MatchStatus.FAILED},
    MatchStatus.SIMULATING: {MatchStatus.READY, MatchStatus.FAILED},
    MatchStatus.READY: {MatchStatus.PLAYING, MatchStatus.FAILED},
    MatchStatus.PLAYING: {
        MatchStatus.PAUSED,
        MatchStatus.FINISHED,
        MatchStatus.FAILED,
    },
    MatchStatus.PAUSED: {
        MatchStatus.PLAYING,
        MatchStatus.FINISHED,
        MatchStatus.FAILED,
    },
    MatchStatus.FINISHED: set(),
    MatchStatus.FAILED: set(),
}


class Match(Base):
    __tablename__ = "matches"

    status: Mapped[MatchStatus] = mapped_column(
        SQLEnum(
            MatchStatus,
            name="match_status",
            values_callable=lambda cls: [item.value for item in cls],
        ),
        default=MatchStatus.CREATED,
        nullable=False,
    )

    home_team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    away_team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    home_team: Mapped["Team"] = relationship(
        back_populates="home_matches",
        foreign_keys=[home_team_id],
    )
    away_team: Mapped["Team"] = relationship(
        back_populates="away_matches",
        foreign_keys=[away_team_id],
    )

    home_score: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    away_score: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    current_minute: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    current_second: Mapped[int] = mapped_column(SmallInteger, default=0, nullable=False)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    scenario: Mapped[dict] = mapped_column(JSON, nullable=False)

    match_teams: Mapped[list["MatchTeam"]] = relationship(
        back_populates="match_",
        cascade="all, delete-orphan",
    )
    match_events: Mapped[list["MatchEvent"]] = relationship(
        back_populates="match_",
        cascade="all, delete-orphan",
    )
    match_insights: Mapped[list["MatchInsight"]] = relationship(
        back_populates="match_",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "home_team_id != away_team_id",
            name="ck_match_different_teams",
        ),
        CheckConstraint(
            "home_score >= 0 AND away_score >= 0",
            name="ck_match_nonnegative_scores",
        ),
        CheckConstraint(
            "current_minute >= 0 AND current_second BETWEEN 0 AND 59",
            name="ck_match_valid_time",
        ),
    )