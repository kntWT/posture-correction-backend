from fastapi import HTTPException, status


class APIException(HTTPException):
    def __init__(self, status_code: int = status.HTTP_400_BAD_REQUEST, detail: str = "Bad Request"):
        super().__init__(status_code=status_code, detail=detail)


class BadRequestException(APIException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class UnauthorizedException(APIException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ForbiddenException(APIException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(APIException):
    def __init__(self, detail: str = "Not Found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class TokenExpiredException(APIException):
    def __init__(self, detail: str = "Token Expired"):
        super().__init__(status_code=498, detail=detail)


class InternalServerErrorException(APIException):
    def __init__(self, detail: str = "Internal Server Error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


def error_responses(err_types: list[type[APIException]]) -> dict:
    responses = {}
    for err_cls in err_types:
        err_instance = err_cls()
        if err_instance.status_code not in responses:
            responses[err_instance.status_code] = {
                'description': f'"{err_instance.detail}"',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': err_instance.detail
                        }
                    }
                }}
        else:
            responses[err_instance.status_code]['description'] += f'<br>"{err_instance.detail}"'
    return responses
