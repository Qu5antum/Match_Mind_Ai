import enum
import uuid
import enum
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .match import Match
    from .player import Player
    from .team import Team


class EventType(str, enum.Enum):
    GENERAL = "general"
    PERIOD_START = "period_start"
    PERIOD_END = "period_end"
    KICK_OFF = "kick_off"
    HALF_TIME = "half_time"
    ADDED_TIME = "added_time"
    EXTRA_TIME_START = "extra_time_start"
    EXTRA_TIME_END = "extra_time_end"
    SUBSTITUTION = "substitution"
    PASS = "pass"
    CARRY = "carry"
    DRIBBLE = "dribble"
    BALL_RECOVERY = "ball_recovery"
    MISCONTROL = "miscontrol"
    DISPOSSESSED = "dispossessed"
    SHOT = "shot"
    GOAL = "goal"
    OWN_GOAL = "own_goal"
    CROSS = "cross"
    HIT_WOODWORK = "hit_woodwork"
    OFFSIDE = "offside"
    TACKLE = "tackle"
    INTERCEPTION = "interception"
    CLEARANCE = "clearance"
    BLOCK = "block"
    PRESSURE = "pressure"
    DUEL = "duel"
    AERIAL_DUEL = "aerial_duel"
    SAVE = "save"
    THROW_IN = "throw_in"
    FREE_KICK = "free_kick"
    PENALTY = "penalty"
    PENALTY_SCORED = "penalty_scored"
    PENALTY_MISSED = "penalty_missed"
    PENALTY_SAVED = "penalty_saved"
    GOAL_KICK = "goal_kick"
    CORNER = "corner"
    FOUL = "foul"
    YELLOW_CARD = "yellow_card"
    RED_CARD = "red_card"
    INJURY = "injury"
    VAR_REVIEW = "var_review"
    PENALTY_SHOOTOUT = "penalty_shootout"



class MatchEvent(Base):
    __tablename__ = "match_events"

    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_time_second: Mapped[int] = mapped_column(Integer, nullable=False)

    event_type: Mapped[EventType] = mapped_column(
        SQLEnum(
            EventType,
            name="match_event_type",
            values_callable=lambda cls: [item.value for item in cls],
        ),
        default=EventType.GENERAL,
        nullable=False,
        index=True,
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    player_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    related_player_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("players.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    start_x: Mapped[float | None]
    start_y: Mapped[float | None]
    end_x: Mapped[float | None]
    end_y: Mapped[float | None]

    outcome: Mapped[str | None] = mapped_column(String(30), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)

    match_: Mapped["Match"] = relationship(back_populates="match_events")
    team: Mapped["Team"] = relationship(back_populates="match_events")

    player: Mapped["Player | None"] = relationship(
        back_populates="match_events",
        foreign_keys=[player_id],
    )
    related_player: Mapped["Player | None"] = relationship(
        back_populates="match_events_related",
        foreign_keys=[related_player_id],
    )

    __table_args__ = (
        UniqueConstraint("match_id", "sequence", name="uq_match_sequence"),
        CheckConstraint(
            "event_time_second >= 0",
            name="ck_event_nonnegative_time",
        ),
        CheckConstraint(
            "(start_x IS NULL OR start_x BETWEEN 0 AND 100) AND "
            "(start_y IS NULL OR start_y BETWEEN 0 AND 100) AND "
            "(end_x IS NULL OR end_x BETWEEN 0 AND 100) AND "
            "(end_y IS NULL OR end_y BETWEEN 0 AND 100)",
            name="ck_event_coordinates_range",
        ),
    )