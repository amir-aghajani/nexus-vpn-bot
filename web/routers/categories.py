from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse

from web.helpers import login_required
from web.schemas.categories import CategoryModel
from data import json_storage
from database import db_client

router = APIRouter(
    prefix='/categories',
    tags=['categories'],
    dependencies=[Depends(login_required)],
)


@router.get('/')
def get_categories():
    categories = json_storage.get('categories')
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=categories
    )


@router.post('/')
def create_category(category_details: CategoryModel):
    category_dict = category_details.model_dump()
    created_category = db_client.create('categories', category_dict)
    json_storage.add('categories', created_category)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_category
    )


@router.put('/{category_id}/')
def update_category(category_id: str, category_details: CategoryModel):
    if not db_client.exists('categories', category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found.'
        )

    updated_category_dict = category_details.model_dump()
    updated_category = db_client.update('categories', category_id, updated_category_dict)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=updated_category
    )


@router.delete('/{category_id}/')
def delete_category(category_id: str):
    if not db_client.exists('categories', category_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found.'
        )

    db_client.delete('categories', category_id)
    json_storage.remove('categories', category_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
