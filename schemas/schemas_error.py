from pydantic import BaseModel

class ErrorModel(BaseModel):
    """Возвращает информацию об ошибке в операции"""
    error_type:str
    error_message:str
