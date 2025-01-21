from fastapi import HTTPException, status


class APIException(HTTPException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "Bad Request"

    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, detail: str = "Bad Request"):
        self.status_code = status_code
        self.detail = detail
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(APIException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "Bad Request"

    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(APIException):
    status_code: int = status.HTTP_401_UNAUTHORIZED
    detail: str = "Unauthorized"

    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(APIException):
    status_code: int = status.HTTP_403_FORBIDDEN
    detail: str = "Forbidden"

    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(APIException):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "Not Found"

    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TokenExpiredException(APIException):
    status_code: int = 498
    detail: str = "Token Expired"

    def __init__(self, detail: str = "Token Expired"):
        super().__init__(status_code=498, detail=detail)


class InternalServerErrorException(APIException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal Server Error"

    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


def error_responses(err_types: list[APIException]) -> dict:
    responses = {}
    for err in err_types:
        if not responses.get(err.status_code):
            responses[err.status_code] = {
                'description': f'"{err.detail}"',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': err.detail
                        }
                    }
                }}
        else:
            # 同じステータスコードなら description へ追記
            responses[err.status_code]['description'] += f'<br>"{err.detail}"'
    return responses
