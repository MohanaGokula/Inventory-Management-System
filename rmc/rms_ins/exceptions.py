from rest_framework.exceptions import APIException

class EntityNotFoundException(APIException):

    def __init__(self, detail=None, code=None):
        super().__init__(detail, 404)

class DataValidationException(APIException):

    def __init__(self, detail=None, code=409, exception=None):
        super().__init__(detail, code)
        self.code = code
        self.exception = None
        if exception is not None:
            self.exception = exception
