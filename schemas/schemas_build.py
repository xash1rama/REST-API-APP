from typing import Optional, List
from pydantic import BaseModel


class ResultBuilding(BaseModel):
    address:str
    coordinate_long:float
    coordinate_lat: float

class ResultAllBuildings(BaseModel):
    buildings:Optional[List[ResultBuilding]]


class CreateBuild(ResultBuilding):
    result:str




