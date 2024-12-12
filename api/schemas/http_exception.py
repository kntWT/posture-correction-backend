from fastapi import HTTPException


class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail=detail)


class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=404, detail=detail)


class TokenExpiredException(HTTPException):
    def __init__(self, detail: str = "Token Expired"):
        super().__init__(status_code=498, detail=detail)


class InternalServerErrorException(HTTPException):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(status_code=500, detail=detail)
