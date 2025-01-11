from typing import Optional, List
from pydantic import BaseModel


class ResultBuilding(BaseModel):
    """
    Схема возврата данных одного здания
    """
    address:str
    coordinate_long:float
    coordinate_lat: float

class ResultAllBuildings(BaseModel):
    """
    Схема возвращающая результат списка всех зданий
    """

    buildings:Optional[List[ResultBuilding]]


class CreateBuild(ResultBuilding):
    """
    Схема проверки ответа данных при созданного здания
    """

    result:str




