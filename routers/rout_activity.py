from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas_organizations import ResultOrganization, ResultAllOrganizations, ErrorModel, GetCoordinates
from schemas.schemas_activity import DeleteActivity, ResultActivity, ResultAllActivities, ResponseActivity
from setup import verify_token, get_session, get_all_subactivity_ids
from database.database import Build, Organization, Activity
from sqlalchemy.future import select
from setup import search_level
from sqlalchemy.orm import selectinload

router = APIRouter(tags=["activity"])


@router.get("/api/organizations/by_activity/{activity_name}",
            response_model=ResultAllOrganizations | ErrorModel)
async def get_organizations_by_activity(activity_name: str,
                                        async_session: AsyncSession = Depends(get_session)):
    """
    Пользователь может найти организацию по ее деятельности
    """
    try:
        result = await async_session.execute(
            select(Activity).options(selectinload(Activity.activity_orgs)).where(Activity.name == activity_name)
        )
        main_activity_list = result.scalars().all()

        if not main_activity_list:
            raise HTTPException(status_code=404, detail="Activity not found")
        main_activity = main_activity_list[0]

        result = await async_session.execute(
            select(Activity).options(selectinload(Activity.activity_orgs)).where(Activity.parent_id == main_activity.id)
        )
        lvl_2_activity = result.scalars().all()
        if not lvl_2_activity:
            return await search_level([main_activity.id], async_session)

        ids = [act.id for act in lvl_2_activity]
        ids.append(main_activity.id)

        result = await async_session.execute(
            select(Activity).options(selectinload(Activity.activity_orgs)).where(Activity.parent_id.in_(ids))
        )
        lvl_3_activity = result.scalars().all()
        if not lvl_3_activity:
            return await search_level(ids, async_session)

        ids_2 = [act.id for act in lvl_3_activity]
        ids += ids_2

        return await search_level(ids, async_session)

    except Exception as er:
        return ErrorModel(
            result=False,
            error_type=str(type(er).__name__),
            error_message=str(er),
        )


@router.post("/api/activity/",
          response_model=ResultActivity|ErrorModel,
             )
async def create_activity(activity: ResultActivity,
                          api_key: str = Depends(verify_token),
                          async_session: AsyncSession = Depends(get_session)):
    """
    Пользователь может создать новую деятельность
    """
    try:
        db_activity = Activity(name=activity.name, parent_id=activity.parent_id, activity_build_id=activity.activity_build_id)
        async_session.add(db_activity)
        await async_session.commit()
        await async_session.refresh(db_activity)
        return db_activity

    except Exception as er:
        return ErrorModel(
                result=False,
                error_type=str(type(er).__name__),
                error_message=str(er),
            )


@router.delete("/api/activity/{id}", response_model=DeleteActivity | ErrorModel)
async def add_activity(
    id:int,
    api_key: str = Depends(verify_token),
    async_session: AsyncSession = Depends(get_session),
):
    """
    Пользователь может удалить какую либо деятельность по её ID
    """
    try:
        result = await async_session.execute(select(Activity).where(Activity.id == id))
        activity = result.scalar_one_or_none()
        if not activity:
            raise HTTPException(status_code=404,
                                detail="No activity were found")
        await async_session.delete(activity)

        return DeleteActivity(
            name=activity.name,
            parent_id=activity.parent_id,
            activity_build_id=activity.activity_build_id,
            result="Activity deleted"
        )
    except Exception as er:
        return ErrorModel(
                result=False,
                error_type=str(type(er).__name__),
                error_message=str(er),
            )



