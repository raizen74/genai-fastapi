import csv
import time
from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import (
    FastAPI,
    Request,
    Response,
)

from building_genai_services.auth import router as auth_router
from building_genai_services.generate import router as generate_router
from building_genai_services.common.session import engine, init_db
from building_genai_services.conversations import (
    router as conversations_router,
)

########### Model loaded in memory for the entire app lifespan #################

# models = {}

# @asynccontextmanager
# async def lifespan(_: FastAPI) -> AsyncIterator[None]:
#     models["text2image"] = load_image_model()
#     models["text2text"] = load_text_model()

#     yield

#     ...  # Run cleanup code here


#     models.clear()

@asynccontextmanager
async def lifespan(_: FastAPI):
    # await init_db()
    # Database schema is managed by Alembic migrations
    # Run: alembic upgrade head
    # other startup operations within the lifespan
    ...
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
# app = FastAPI()

app.include_router(conversations_router)
app.include_router(auth_router)
app.include_router(generate_router)



################################################################################


csv_header = [
    "Request ID",
    "Datetime",
    "Endpoint Triggered",
    "Client IP Address",
    "Response Time",
    "Status Code",
    "Successful",
]


@app.middleware("http")
async def monitor_service(
    req: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = uuid4().hex
    request_datetime = datetime.now(timezone.utc).isoformat()
    start_time = time.perf_counter()
    response: Response = await call_next(req)
    response_time = round(time.perf_counter() - start_time, 4)
    response.headers["X-Response-Time"] = str(response_time)
    response.headers["X-API-Request-ID"] = request_id
    with open("usage.csv", "a", newline="") as file:
        writer = csv.writer(file)
        if file.tell() == 0:
            writer.writerow(csv_header)
        writer.writerow(
            [
                request_id,
                request_datetime,
                req.url,
                req.client.host,
                response_time,
                response.status_code,
                response.status_code < 400,
            ],
        )
    return response
