from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Header
from fastapi.exceptions import HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_organizations import ResultAllOrganizations, ResultOrganization
from database.model import engine, Base, session, Activity, Build, Organization
from dotenv import load_dotenv
import os
from sqlalchemy import select
from random import randint


load_dotenv(".env")


API_KEY = os.getenv("API_KEY")


@asynccontextmanager
async def lifespan(main_app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_session = session()
    async with async_session:
        await create_datas_in_database(async_session)
    yield
    await engine.dispose()


async def get_session() -> AsyncSession:
    """
    Создание сессии базы данных
    """
    async with session() as async_session:
        yield async_session


header_api_key = APIKeyHeader(name="x-api-key")


async def get_session() -> AsyncSession:
    """
    Создание сессии базы данных
    """
    async with session() as async_session:
        yield async_session


async def verify_token(
    x_api_key: str = Depends(header_api_key),):
    """
    Принимает и проверяет получаемый хедер
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")


async def get_all_subactivity_ids(session, activity_id):
    # Получаем все дочерние виды деятельности для данного вида деятельности
    subactivity_ids = []
    activity = await session.execute(select(Activity).where(Activity.id == activity_id))
    activity = activity.scalar_one_or_none()

    if activity:
        subactivity_ids.append(activity.id)
        if activity.subactivities:
            for subactivity in activity.subactivities:
                subactivity_ids.extend(await get_all_subactivity_ids(session, subactivity.id))

    return subactivity_ids


async def search_level(ids: list, async_session):
    result = await async_session.execute(
        select(Organization).join(Organization.orgs_activities).join(Organization.organization_build).where(
            Organization.activities_id.in_(ids))
    )
    organizations_all_levels = result.scalars().all()

    return ResultAllOrganizations(organizations=[
        ResultOrganization(
            name=org.name,
            number_phone=org.number_phone,
            address=org.organization_build.address if org.organization_build else "No address"
        ) for org in organizations_all_levels
    ])


async def create_datas_in_database(async_session: AsyncSession = Depends(get_session)):
    build_1 = Build(
            address="Build 1",
            coordinate_long=3333,
            coordinate_lat=3333
        )
    build_2 = Build(
            address="Build 2",
            coordinate_long=2222,
            coordinate_lat=2222
        )
    build_3 = Build(
            address="Build 3",
            coordinate_long=1111,
            coordinate_lat=1111
        )

    activity_1 = Activity(
            name="food",
            activity_build_id=1,
            parent_id=None
        )
    activity_2 = Activity(
            name="food",
            activity_build_id=2,
            parent_id=None
        )
    activity_3 = Activity(
            name="book",
            activity_build_id=3,
            parent_id=None
        )

    organization_1 = Organization(
            name="Papa Jons",
            number_phone=[str(randint(1111111, 9999999))],
            build=1,
            activities_id=1
        )

    organization_2 = Organization(
            name="Oz",
            number_phone=[str(randint(1111111, 9999999))],
            build=2,
            activities_id=3
        )

    organization_3 = Organization(
            name="DoDo",
            number_phone=[str(randint(1111111, 9999999))],
            build=2,
            activities_id=2
        )

    organization_4 = Organization(
            name="Minsk Library",
            number_phone=[str(randint(1111111, 9999999))],
            build=3,
            activities_id=3
        )

    async_session.add(build_1)
    async_session.add(build_2)
    async_session.add(build_3)
    async_session.add(activity_1)
    async_session.add(activity_2)
    async_session.add(activity_3)
    async_session.add(organization_1)
    async_session.add(organization_2)
    async_session.add(organization_3)
    async_session.add(organization_4)
    await async_session.commit()
