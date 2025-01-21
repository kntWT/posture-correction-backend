from fastapi import FastAPI, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import schemas.http_exception as HTTPException
from routes.user import user
from routes.posture import posture

app = FastAPI()
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def handler(request: Request, exc: RequestValidationError):
    print(exc)
    return JSONResponse(content={}, status_code=status.HTTP_400_BAD_REQUEST)


@app.exception_handler(HTTPException.BadRequestException)
async def bad_request_handler(request: Request, exc: HTTPException.BadRequestException):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException.UnauthorizedException)
async def unauthorized_handler(request: Request, exc: HTTPException.UnauthorizedException):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException.ForbiddenException)
async def forbidden_handler(request: Request, exc: HTTPException.ForbiddenException):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException.NotFoundException)
async def not_found_handler(request: Request, exc: HTTPException.NotFoundException):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException.TokenExpiredException)
async def token_expired_handler(request: Request, exc: HTTPException.TokenExpiredException):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException.InternalServerErrorException)
async def intenal_server_errorhandler(request: Request, exc: HTTPException.InternalServerErrorException):
    return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)


routers_list = [user, posture]

for router in routers_list:
    app.include_router(router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        workers="auto"
    )
