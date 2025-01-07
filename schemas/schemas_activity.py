from typing import Optional, List
from pydantic import BaseModel


class ErrorModel(BaseModel):
    """Возвращает информацию об ошибке в операции"""
    result:bool
    error_type:str
    error_message:str


class ResultActivity(BaseModel):
    name: str
    parent_id: Optional[int] = None
    activity_build_id: int = None

class ResultAllActivities(BaseModel):
    activities: Optional[List[ResultActivity]]


class DeleteActivity(ResultActivity):
    result:str

class ResponseActivity(BaseModel):
    name:str