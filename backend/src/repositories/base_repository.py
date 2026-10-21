from abc import ABC, abstractmethod
from sqlalchemy import select, func
from uuid import UUID
from typing import Dict, Any, Sequence

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def create(self, data: dict):
        raise NotImplementedError
    
    @abstractmethod
    async def get(self, id: UUID):
        raise NotImplementedError
    
    @abstractmethod
    async def get_all(self, limit: int, offset: int):
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: UUID, data: Dict[str, Any]):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: UUID):
        raise NotImplementedError

    @abstractmethod
    async def get_obj(self, id: UUID):
        raise NotImplementedError

    @abstractmethod
    async def add_all(self, obj_list: Sequence[Any]):
        raise NotImplementedError

    @abstractmethod
    async def check_all_ids_exist(self, id_list: list[UUID]) -> bool:
        raise NotImplementedError


class BaseRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs):
        try:
            new_object = self.model(**kwargs)  
            self.session.add(new_object)

        except:
            await self.session.rollback()
            raise

        return new_object

    async def get(self, id: UUID):
        obj = await self.session.get(self.model, id)

        return obj
    
    async def get_obj(self, id: UUID):
        obj = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )

        return obj.scalar_one_or_none()
     
    async def get_all(self, limit: int, offset: int):
        result = await self.session.execute(
            select(self.model)
            .offset(offset)
            .limit(limit)
        )

        return result.scalars().all()
    
    async def update(self, obj: Any, data: Dict[str, Any]):
        try:
            if obj: 
                for key, value in data.items():
                    if hasattr(obj, key):
                        setattr(obj, key, value)
            
            return obj

        except:
            await self.session.rollback()
            raise

    async def delete(self, id: UUID):
        try:
            obj = await self.session.get(self.model, id)

            if not obj:
                return None

            await self.session.delete(obj)

            return obj
        
        except:
            raise

    async def add_all(self, obj_list: Sequence[Any]) -> None:
        self.session.add_all(obj_list)
        return None

    async def check_all_ids_exist(self, id_list: list[UUID]) -> bool:
        unique_ids = list(set(id_list))

        if not unique_ids:
            return True

        stmt = (
            select(func.count(self.model.id))
            .where(self.model.id._in(unique_ids))
        )

        existing_count = self.session.scalar(stmt)

        return existing_count == len(unique_ids)