class HttpException(Exception):
    status_code = 500
    status = None
    message = None
    err = None
    show_type_html = None

    def __init__(self, status=None, message=None, err=None, show_type_html=None):
        Exception.__init__(self)
        self.status = status
        self.message = message
        self.err = err
        self.show_type_html = show_type_html


class BadRequestException(HttpException):
    status_code = 400


class NotFoundException(HttpException):
    status_code = 404


class AccessDeniedException(HttpException):
    status_code = 403


class MethodNotAllowedException(HttpException):
    status_code = 405


class SQLException(HttpException):
    status_code = 400
