from typing import List, Optional
from pydantic import BaseModel
from .schemas_activity import ResultAllActivities

class ErrorModel(BaseModel):
    """Возвращает информацию об ошибке в операции"""
    result: bool
    error_type: str
    error_message: str



class ResultOrganization(BaseModel):
    name: str
    number_phone: List[str]
    address: str


class ResultAllOrganizations(BaseModel):
    organizations: Optional[List[ResultOrganization]]


class GetCoordinates(BaseModel):
    latitude: float  #широта
    longitude: float #долгота
    radius: int


class AddOrganization(BaseModel):
    name: str
    number_phone: List[str]
    build: int
    activities_id:int

class CreateOrganization(BaseModel):
    result: str
    name: str
    number_phone: List[str]
    activity: str


class DeleteOrganization(BaseModel):
    name: str
    number_phone: List[str]
    build: str
    result: str

