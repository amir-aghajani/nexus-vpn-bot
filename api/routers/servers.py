from fastapi import APIRouter, HTTPException, status

from api.schemas import servers
from api_client.sanaei import SanaeiClient

router = APIRouter(
    prefix="/servers",
    tags=["servers"],
)


@router.post("/")
async def create_server(server_detials: servers.ServerCreateModel):
    if server_detials.panelType == "sanaei":
        client = SanaeiClient(
            panel_url=server_detials.panelUrl,
            username=server_detials.panelUsername,
            password=server_detials.panelPassword
        )

        if not client.test_client_connection():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to connect to the Sanaei panel. Please check your credentials and URL."
            )

        server_data = server_detials.model_dump()

        return server_data

    else:
        return {"error": "Unsupported panel type."}
