from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PositiveInt

from app.schemas.base import BaseSchema


class DonationBase(BaseModel):
    comment: Optional[str]
    full_amount: PositiveInt


class DonationDB(DonationBase):
    id: int
    create_date: datetime

    class Config:
        orm_mode = True


class AllDonations(BaseSchema, DonationDB):
    user_id: int