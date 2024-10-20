from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.schemas.charity_project import (
    CharityProjectDB,
    CharityProjectCreate,
    CharityProjectUpdate
)
from app.services.investing import make_a_payment
from app.api.validators import (
    check_unique_name, check_project_exists,
    check_project_invested, check_project_fully_invested
)

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_all_projects(
    session: AsyncSession = Depends(get_async_session)
):
    return await charity_project_crud.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)]
)
async def create_project(
    charity_project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session)
):
    await check_unique_name(charity_project.name, session)
    new_project = await charity_project_crud.create(charity_project, session)
    await make_a_payment(session)
    await session.refresh(new_project)
    return new_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    charity_project = await check_project_exists(project_id, session)
    await check_project_invested(charity_project)
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
):
    await check_unique_name(obj_in.name, session)
    charity_project = await check_project_exists(project_id, session)
    await check_project_fully_invested(charity_project)
    if (
        obj_in.full_amount is not None and
        obj_in.full_amount < charity_project.invested_amount
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                'Нельзя установить значение full_amount меньше уже '
                'вложенной суммы.'
            )
        )
    charity_project = await charity_project_crud.update(
        charity_project, obj_in, session
    )
    await make_a_payment(session)
    await session.refresh(charity_project)
    return charity_project