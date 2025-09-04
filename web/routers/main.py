from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from web.templates import html_templates

router = APIRouter()


@router.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return html_templates.TemplateResponse(
        request=request,
        name='index.html',
        context={'id': '232131asd'}
    )
