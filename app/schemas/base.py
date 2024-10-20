from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, PositiveInt

TIME_EXAMPLE = "2010-10-10T00:00:00"


class BaseSchema(BaseModel):
    full_amount: PositiveInt
    invested_amount: int = 0
    fully_invested: bool
    create_date: datetime = Field(..., example=TIME_EXAMPLE)
    close_date: Optional[datetime] = Field(None, example=TIME_EXAMPLE)