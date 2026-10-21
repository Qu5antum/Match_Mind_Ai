import enum
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Enum as SQLEnum,
    ForeignKey,
    JSON,
    SmallInteger,
    String,
    Text,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .match import Match


class InsightType(str, enum.Enum):
    KEY_MOMENT = "key_moment"
    TEAM_PERFORMANCE = "team_performance"
    PLAYER_PERFORMANCE = "player_performance"
    TACTICAL = "tactical"
    PREDICTION = "prediction"
    PLAYER = "player"
    RECAP = "recap"
    SUMMARy = "summary"


class Importance(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MatchInsight(Base):
    __tablename__ = "match_insights"

    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    match_: Mapped["Match"] = relationship(
        back_populates="match_insights",
    )

    insight_type: Mapped[InsightType] = mapped_column(
        SQLEnum(
            InsightType,
            name="insight_type",
            values_callable=lambda cls: [item.value for item in cls],
        ),
        default=InsightType.KEY_MOMENT,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    importance: Mapped[Importance] = mapped_column(
        SQLEnum(
            Importance,
            name="insight_importance",
            values_callable=lambda cls: [item.value for item in cls],
        ),
        default=Importance.LOW,
        nullable=False,
    )

    minute: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
    )

    evidence: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=False,
    )

    audience: Mapped[str] = mapped_column(
        String(20),
        default="casual",
        nullable=False,
    )
    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )
    model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    __table_args__ = (
        CheckConstraint(
            "minute IS NULL OR minute >= 0",
            name="ck_insight_nonnegative_minute",
        ),
    )
