from typing import Optional, List, Dict
from pydantic import BaseModel


class ErrorModel(BaseModel):
    """Возвращает информацию об ошибке в операции"""
    result:bool
    error_type:str
    error_message:str



class ResultBuilding(BaseModel):
    address:str
    coordinate_long:float
    coordinate_lat: float

class ResultAllBuildings(BaseModel):
    buildings:Optional[List[ResultBuilding]]


class CreateBuild(ResultBuilding):
    result:str




