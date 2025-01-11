from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from schemas.schemas_organizations import ResultOrganization, ResultAllOrganizations, \
     GetCoordinates, CreateOrganization, AddOrganization, DeleteOrganization
from schemas.schemas_error import ErrorModel
from setup import verify_token, get_session
from database.model import Build, Organization, Activity
from sqlalchemy.future import select


router = APIRouter(tags=["organizations"])


@router.get("/api/organization/{id}", response_model=ResultAllOrganizations | ErrorModel)
async def get_organizations_by_build(
        id: int,
        api_key: str = Depends(verify_token),
        async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может получить все организации, находящиеся в указанном здании:
    """
    try:
        result = await async_session.execute(select(Build).where(Build.id == id))
        build = result.scalar_one_or_none()
        if not build:
            raise HTTPException(status_code=404,
                                detail="No buildings were found")
        result = await async_session.execute(
            select(Organization).join(Organization.organization_build)
            .options(selectinload(Organization.orgs_activities))
            .where(Organization.build == id)
        )
        organizations_res = result.scalars().all()
        if not organizations_res:
            raise HTTPException(status_code=404,
                                detail="The building has no organizations")
        organization = []
        for org in organizations_res:
            organization.append(
                ResultOrganization(
                    name=org.name,
                    number_phone=org.number_phone,
                    address=org.organization_build.address,
                ))
        return ResultAllOrganizations(organizations=organization)

    except Exception as er:
        return ErrorModel(
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.get("/api/organization/activity/{activity_var}", response_model=ResultAllOrganizations | ErrorModel)
async def get_organizations(
    activity_var:str,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может получить все оргианизации c указанной деятельностью
    """
    try:
        result = await async_session.execute(
            select(Organization).join(Organization.orgs_activities).join(Organization.organization_build).where(
                Activity.name==activity_var))
        organizations_res = result.scalars().all()
        if not organizations_res:
            raise HTTPException(status_code=404,
                                detail="No organization were found")
        organization = [
        ResultOrganization(
            name=org.name,
            number_phone=org.number_phone,
            address=org.organization_build.address,
        )
        for org in organizations_res
    ]
        return ResultAllOrganizations(organizations=organization)

    except Exception as er:
        return ErrorModel(
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.post("/api/organization", response_model=ResultAllOrganizations | ErrorModel)
async def get_organizations_by_location(
    data_coordinates:GetCoordinates,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может получить все оргианизации в указанной точке и в необходимом радиусе
    """
    try:
        result = await async_session.execute(
            select(Organization)
            .join(Organization.organization_build)
            .options(joinedload(Organization.organization_build))
            .where(
                func.acos(
                    func.sin(func.radians(data_coordinates.latitude)) * func.sin(func.radians(Build.coordinate_lat)) +
                    func.cos(func.radians(data_coordinates.latitude)) * func.cos(func.radians(Build.coordinate_lat)) *
                    func.cos(func.radians(Build.coordinate_long) - func.radians(data_coordinates.longitude))
                ) * 6371000 <= data_coordinates.radius  # 6371000 - радиус Земли в метрах
            )
        )

        organizations_res = result.scalars().all()
        if not organizations_res:
            raise HTTPException(status_code=404,
                                detail="No organization were found")
        organization = [
        ResultOrganization(
            name=org.name,
            number_phone=org.number_phone,
            address=org.organization_build.address,
        )
        for org in organizations_res
    ]
        return ResultAllOrganizations(organizations=organization)

    except Exception as er:
        return ErrorModel(
            error_type=str(type(er).__name__),
            error_message=str(er),
        )



@router.get("/api/organization/info/{id}", response_model=ResultOrganization | ErrorModel)
async def get_info_organizations(
    id:int,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может получить информацию об организации по её идентификатору (ID)
    """
    try:
        result = await async_session.execute(
            select(Organization).join(Organization.orgs_activities).join(Organization.organization_build).where(
                Organization.id==id))
        organizations = result.scalars().one_or_none()
        if not organizations:
            raise HTTPException(status_code=404,
                                detail="No organization were found")
        return ResultOrganization(
            name=organizations.name,
            number_phone=organizations.number_phone,
            address=organizations.organization_build.address,
        )

    except Exception as er:
        return ErrorModel(
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.get("/api/organization/info/name/{name}", response_model=ResultOrganization | ErrorModel)
async def get_info_organizations_for_name(
    name:str,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может получить информацию об организации по её названию
    """
    try:
        result = await async_session.execute(
            select(Organization).join(Organization.orgs_activities).join(Organization.organization_build).where(
                Organization.name == name))
        organizations = result.scalar_one_or_none()
        if not organizations:
            raise HTTPException(status_code=404,
                                detail="No organization were found")
        return ResultOrganization(
            name=organizations.name,
            number_phone=organizations.number_phone,
            address=organizations.organization_build.address,
        )

    except Exception as er:
        return ErrorModel(
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.post("/api/organization/create", response_model=CreateOrganization|ErrorModel)
async def create_organization(
    data_organization:AddOrganization,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session)
):
    """
    Пользователь может создать новую организацию
    """
    try:
        new_organization = Organization(
            name=data_organization.name,
            number_phone= data_organization.number_phone,
            build= data_organization.build,
            activities_id= data_organization.activities_id
            )
        async_session.add(new_organization)
        result = await async_session.execute(select(Activity).where(Activity.id==data_organization.activities_id))
        activity = result.scalar_one_or_none()
        await async_session.commit()
        return CreateOrganization(result="Organization added",
                                  name=new_organization.name,
                                  number_phone=new_organization.number_phone,
                                  activity=activity.name)
    except Exception as er:
        return ErrorModel(
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.delete("/api/organization/{id}", response_model=DeleteOrganization | ErrorModel)
async def delete_organization_by_id(
    id:int,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может удалить организацию
    """
    try:
        result = await async_session.execute(select(Organization).join(Organization.organization_build).where(Organization.id == id))
        organization = result.scalar_one_or_none()
        if not organization:
            raise HTTPException(status_code=404,
                                detail="No activity were found")
        await async_session.delete(organization)

        return DeleteOrganization(
            name=organization.name,
            number_phone=organization.number_phone,
            build=organization.organization_build.address,
            result="Оrganization deleted"
        )
    except Exception as er:
        return ErrorModel(
                error_type=str(type(er).__name__),
                error_message=str(er),
            )