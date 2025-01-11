from typing import List, Optional
from pydantic import BaseModel


class ResultOrganization(BaseModel):
    """
    Схема вовращает данные одной организации
    """
    name: str
    number_phone: List[str]
    address: str


class ResultAllOrganizations(BaseModel):
    """
    Схема возвращает список всех отрагизаций
    """
    organizations: Optional[List[ResultOrganization]]


class GetCoordinates(BaseModel):
    """
    Схема получения координат и радиуса
    """
    latitude: float  #широта
    longitude: float #долгота
    radius: int


class AddOrganization(BaseModel):
    """
    Схема проверки данных при создании оргинизации
    """
    name: str
    number_phone: List[str]
    build: int
    activities_id:int

class CreateOrganization(BaseModel):
    """
    Схема данных созданной организации
    """
    result: str
    name: str
    number_phone: List[str]
    activity: str


class DeleteOrganization(BaseModel):
    """
    Схема данных удаленной организации
    """
    name: str
    number_phone: List[str]
    build: str
    result: str

