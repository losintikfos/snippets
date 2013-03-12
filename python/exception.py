
class AccessException(Exception):
    message = 'An unknown exception'

    def __init__(self, msg=None, **kwargs):
        self.kwargs = kwargs
        if msg is None:
            msg = self.message

        try:
            msg = msg % kwargs
        except Exception:
            msg = self.message

        super(AccessException, self).__init__(msg)


class UnknownField(AccessException):
    message = 'unknown field %(field)x'


class MalformedMessage(AccessException):
    message = 'malformed message'