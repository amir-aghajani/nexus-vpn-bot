from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from web.helpers import login_required
from web.schemas.plans import PlanModel
from data import json_storage
from database import db_client

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    dependencies=[Depends(login_required)],
)


@router.get('/')
def fetch_plans():
    plans = json_storage.get('plans')
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=plans
    )


@router.post('/')
def create_plan(plan_details: PlanModel):
    plan_dict = plan_details.model_dump()
    created_plan = db_client.create('plans', plan_dict)
    json_storage.add('plans', created_plan)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_plan
    )
