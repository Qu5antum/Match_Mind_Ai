import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
if TYPE_CHECKING:
    from .match import Match
    from .team import Team


class MatchTeam(Base):
    __tablename__ = "match_teams"

    match_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("matches.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )

    side: Mapped[str] = mapped_column(String(10), nullable=False)
    formation: Mapped[str] = mapped_column(String(20), nullable=False, default="4-3-3")
    tactics: Mapped[dict] = mapped_column(JSON, nullable=False)
    lineup: Mapped[dict] = mapped_column(JSON, nullable=False)

    match_: Mapped["Match"] = relationship(back_populates="match_teams")
    team: Mapped["Team"] = relationship(back_populates="match_teams")

    __table_args__ = (
        UniqueConstraint("match_id", "team_id", name="uq_match_team"),
        UniqueConstraint("match_id", "side", name="uq_match_side"),
    )