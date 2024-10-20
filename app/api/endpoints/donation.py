from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud.donation import donation_crud
from app.schemas.donation import DonationBase, DonationDB, AllDonations
from app.models import User
from app.services.investing import make_a_payment

router = APIRouter()


@router.get(
    '/',
    response_model=list[AllDonations],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session)
):
    return await donation_crud.get_multi(session)


@router.post(
    '/',
    response_model_exclude_none=True,
    response_model=DonationDB
)
async def create_donation(
    donation: DonationBase,
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    new_donation = await donation_crud.create(donation, session, user)
    await make_a_payment(session)
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/my',
    response_model=list[DonationDB]
)
async def get_my_donations(
    user: User = Depends(current_user),
    session: AsyncSession = Depends(get_async_session)
):
    return await donation_crud.get_user_donations(user, session)
