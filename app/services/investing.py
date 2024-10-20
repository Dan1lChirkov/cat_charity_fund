from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.donation import donation_crud
from app.crud.charity_project import charity_project_crud
from app.models import CharityProject, Donation


async def get_open_charity_projects(
    session: AsyncSession
) -> List[CharityProject]:
    open_charity_projects = await charity_project_crud.get_opens(session)
    return open_charity_projects


async def get_open_donations(
    session: AsyncSession
) -> List[Donation]:
    donations = await donation_crud.get_opens(session)
    return donations


async def make_a_payment(
    session: AsyncSession
):
    charity_projects = await get_open_charity_projects(session)
    donations = await get_open_donations(session)
    if not charity_projects or not donations:
        return
    for donation in donations:
        free_money = donation.full_amount - donation.invested_amount
        for charity in charity_projects:
            if charity.fully_invested:
                continue
            need_money = charity.full_amount - charity.invested_amount
            if free_money > need_money:
                free_money = free_money - need_money
                charity.close()
                donation.invested_amount += need_money
            elif free_money < need_money:
                charity.invested_amount += free_money
                donation.close()
                free_money = 0
                break
            else:
                free_money = 0
                need_money = 0
                charity.close()
                donation.close()
                break
    session.add_all(charity_projects + donations)
    await session.commit()