from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint.
    Returns 200 OK when the service is running.
    """
    return {"status": "ok"}
