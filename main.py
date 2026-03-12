import uvicorn

from app.core.config import settings
from app.utils.logger import get_uvicorn_logger_config


def main():
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=get_uvicorn_logger_config(),
    )


if __name__ == "__main__":
    main()
