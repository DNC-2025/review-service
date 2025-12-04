# app/schemas/pagination.py
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginatedResponse(GenericModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int
    total_pages: int
    current_page: int
    next_offset: Optional[int]
    prev_offset: Optional[int]


