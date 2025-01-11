from typing import Optional, List
from pydantic import BaseModel


class ResultActivity(BaseModel):
    """
    Схема возвращающая наименования деятельности организации
    """
    name: str
    parent_id: Optional[int] = None
    activity_build_id: int = None

class ResultAllActivities(BaseModel):
    """
    Схема возвращает список всех дейтельностей организации или здания
    """
    activities: Optional[List[ResultActivity]]


class DeleteActivity(ResultActivity):
    """
    Схема возвращает ответ при удалении деятельности
    """
    result:str

class ResponseActivity(BaseModel):
    """
    Схема для проверки данных при создании деятельности
    """
    name:str