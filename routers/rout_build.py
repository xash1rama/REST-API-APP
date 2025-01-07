from fastapi import APIRouter, Depends, HTTPException
from schemas.schemas_build import ErrorModel, ResultAllBuildings, ResultBuilding, CreateBuild
from schemas.schemas_build import CreateBuild as DeleteBuild
from schemas.schemas_organizations import GetCoordinates
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from setup import verify_token, get_session
from database.database import Build

router = APIRouter(tags=["buildings"])


@router.get("/api/build", response_model=ResultAllBuildings | ErrorModel)
async def get_buildings(
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может получить информацию о всех зданиях
    """
    try:
        result = await async_session.execute(select(Build))
        builds = result.scalars().all()
        if not builds:
            raise HTTPException(status_code=403,
                                detail="No buildings were found")
        buildings = [ResultBuilding(address=bld.address,
                                    coordinate_long=bld.coordinate_long,
                                    coordinate_lat=bld.coordinate_lat) for bld in builds]
        return ResultAllBuildings(buildings=buildings)

    except Exception as er:
        return ErrorModel(
            result=False,
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.post("/api/build", response_model=ResultBuilding | ErrorModel)
async def crate_build(
    data_build: ResultBuilding,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может создать новое здание
    """
    try:
        build = Build()
        build.address = data_build.address
        build.coordinate_long = data_build.coordinate_long
        build.coordinate_lat = data_build.coordinate_lat
        async_session.add(build)
        await async_session.commit()
        result = CreateBuild(result="Build added",
                             address=build.address,
                             coordinate_long=build.coordinate_long,
                             coordinate_lat=build.coordinate_lat)
        return result

    except Exception as er:
        return ErrorModel(
            result=False,
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.delete("/api/build/{id}", response_model=DeleteBuild | ErrorModel)
async def delete_building(
        id:int,
        api_key: str = Depends(verify_token),
        async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может 'cнести' здание
    """
    try:
        result = await async_session.execute(select(Build).where(Build.id == id))
        build = result.scalar_one_or_none()
        if not build:
            raise HTTPException(status_code=404,
                                detail="No buildings were found")
        await async_session.delete(build)
        await async_session.commit()
        result = DeleteBuild(result="Build deleted",
                             address=build.address,
                             coordinate_long=build.coordinate_long,
                             coordinate_lat=build.coordinate_lat)

        return result

    except Exception as er:
        return ErrorModel(
            result=False,
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.post("/api/build/location", response_model=ResultAllBuildings | ErrorModel)
async def get_organizations_by_location(
    data_coordinates:GetCoordinates,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может получить все здания в указанной точке и в необходимом радиусе
    """
    try:
        result = await async_session.execute(
            select(Build)
            .where(
                func.acos(
                    func.sin(func.radians(data_coordinates.latitude)) * func.sin(func.radians(Build.coordinate_lat)) +
                    func.cos(func.radians(data_coordinates.latitude)) * func.cos(func.radians(Build.coordinate_lat)) *
                    func.cos(func.radians(Build.coordinate_long) - func.radians(data_coordinates.longitude))
                ) * 6371000 <= data_coordinates.radius  # 6371000 - радиус Земли в метрах
            )
        )

        buildings_res = result.scalars().all()
        if not buildings_res:
            raise HTTPException(status_code=404,
                                detail="No organization were found")

        buildings = [ResultBuilding(address=bld.address,
                                    coordinate_long=bld.coordinate_long,
                                    coordinate_lat=bld.coordinate_lat) for bld in buildings_res]
        return ResultAllBuildings(buildings=buildings)

    except Exception as er:
        return ErrorModel(
            result=False,
            error_type=str(type(er).__name__),
            error_message=str(er),
        )
