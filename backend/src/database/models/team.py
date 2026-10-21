from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from .base import Base
if TYPE_CHECKING:
    from .match import Match
    from .match_teams import MatchTeam
    from .match_events import MatchEvent
    from .player import Player


class Team(Base):
    __tablename__ = "teams"

    name: Mapped[str] = mapped_column(unique=True)
    short_name: Mapped[str] = mapped_column(unique=True)

    home_matches: Mapped[list["Match"]] = relationship(
        back_populates="home_team",
        foreign_keys="Match.home_team_id"
    )

    away_matches: Mapped[list["Match"]] = relationship(
        back_populates="away_team",
        foreign_keys="Match.away_team_id",
    )

    match_teams: Mapped[list["MatchTeam"]] = relationship(
        back_populates="team"
    )

    match_events: Mapped[list["MatchEvent"]] = relationship(
        back_populates="team"
    )

    players: Mapped[list["Player"]] = relationship(
        back_populates="team",
        cascade="all, delete-orphan",
    )
    