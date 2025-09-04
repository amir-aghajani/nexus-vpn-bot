from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import JSONResponse

from web.helpers import login_required
from web.schemas import servers
from api_client.sanaei import SanaeiClient
from data import json_storage
from database import db_client

router = APIRouter(
    prefix='/servers',
    tags=['servers'],
    dependencies=[Depends(login_required)]
)


@router.get('/')
async def get_servers():
    return json_storage.get('servers')


def test_server_connection(server_detials: servers.ServerModel):
    if server_detials.panelType == 'sanaei':
        client = SanaeiClient(
            panel_url=server_detials.panelUrl,
            username=server_detials.panelUsername,
            password=server_detials.panelPassword
        )

        if not client.test_client_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Failed to connect to the Sanaei panel. Please check your credentials and URL.'
            )

    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail='Panel type not supported yet.'
        )

    return


@router.post('/')
async def create_server(server_detials: servers.ServerModel):
    test_server_connection(server_detials)

    server_dict = server_detials.model_dump()
    server_data = db_client.create('servers', server_dict)
    json_storage.add('servers', server_data)

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=server_data
    )


@router.put('/{server_id}/')
async def update_server(server_id: str, server_details: servers.ServerModel):
    if not db_client.exists('servers', server_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Server not found.'
        )

    test_server_connection(server_details)

    updated_server_dict = server_details.model_dump()
    updated_server = db_client.update('servers', server_id, updated_server_dict)
    json_storage.update('servers', server_id, updated_server)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=json_storage.get('servers', server_id)
    )


@router.delete('/{server_id}/')
async def delete_server(server_id: str):
    if not db_client.exists('servers', server_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Server not found.'
        )

    db_client.delete('servers', server_id)
    json_storage.remove('servers', server_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
