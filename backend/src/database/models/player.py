from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy import String, SmallInteger, ForeignKey, CheckConstraint
from typing import TYPE_CHECKING

from .base import Base
if TYPE_CHECKING:
    from .team import Team
    from .match_events import MatchEvent


class Player(Base):
    __tablename__ = "players"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    position: Mapped[str] = mapped_column(String(20), nullable=False)

    team_id: Mapped[str] = mapped_column(
        ForeignKey("teams.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    passing: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    shooting: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    dribbling: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    defending: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    pace: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    stamina: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    vision: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    team: Mapped["Team"] = relationship(back_populates="players")

    match_events: Mapped[list["MatchEvent"]] = relationship(
        back_populates="player",
        foreign_keys="MatchEvent.player_id",
    )
    match_events_related: Mapped[list["MatchEvent"]] = relationship(
        back_populates="related_player",
        foreign_keys="MatchEvent.related_player_id",
    )

    __table_args__ = (
        CheckConstraint(
            "passing BETWEEN 1 AND 100 AND "
            "shooting BETWEEN 1 AND 100 AND "
            "dribbling BETWEEN 1 AND 100 AND "
            "defending BETWEEN 1 AND 100 AND "
            "pace BETWEEN 1 AND 100 AND "
            "stamina BETWEEN 1 AND 100 AND "
            "vision BETWEEN 1 AND 100",
            name="ck_player_ratings_range",
        ),
    )
