import os

from fastapi import APIRouter
from starlette.responses import RedirectResponse, Response

router = APIRouter()


@router.get("/")
async def root():
    return RedirectResponse(url='/gateway/dashboard')


@router.get("/gateway/dashboard")
async def dashboard():
    """dashboard"""
    index_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "assets/dashboard"
    )
    with open(os.path.join(index_dir, 'index.html')) as fh:
        data = fh.read()
    return Response(content=data, media_type="text/html")
