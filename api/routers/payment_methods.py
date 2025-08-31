from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse

from api.helpers import login_required
from api.schemas.payment_methods import PaymentMethodBase
from data import json_storage
from database import db_client

router = APIRouter(
    prefix="/payment-methods",
    tags=["Payment Methods"],
    dependencies=[Depends(login_required)]
)


@router.get('/')
async def list_payment_methods():
    payment_methods = json_storage.get('paymentMethods')
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payment_methods
    )


@router.post('/')
async def create_payment_method(method_details: PaymentMethodBase):
    payment_method_dict = method_details.model_dump()
    created_payment_method = db_client.create('paymentMethods', payment_method_dict)

    json_storage.add('paymentMethods', created_payment_method)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=created_payment_method
    )


@router.put('/{method_id}/')
def update_category(method_id: str, method_details: PaymentMethodBase):
    if not db_client.exists('paymentMethods', method_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Payment Method not found.'
        )

    updated_payment_method_dict = method_details.model_dump()
    updated_payment_method = db_client.update('paymentMethods', method_id, updated_payment_method_dict)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=updated_payment_method
    )


@router.delete('/{method_id}/')
def delete_category(method_id: str):
    if not db_client.exists('paymentMethods', method_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Payment Method not found.'
        )

    db_client.delete('paymentMethods', method_id)
    json_storage.remove('paymentMethods', method_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
