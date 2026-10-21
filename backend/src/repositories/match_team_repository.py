
from .base_repository import BaseRepository
from src.database.models.match_teams import MatchTeam


class MatchTeamRepository(BaseRepository):
    model = MatchTeam