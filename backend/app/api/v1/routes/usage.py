from fastapi import APIRouter, Request, Depends

from app.api.deps import verify_demo_key, get_client_ip
from app.services.rate_limit_service import rate_limit_service


router = APIRouter()


@router.get("/usage")
def get_usage(
    request: Request,
    _: bool = Depends(verify_demo_key),
):
    client_ip = get_client_ip(request)
    return rate_limit_service.get_usage(client_ip)