
class BadStatusCodeException(Exception):
    def __init(self, arg):
        self.args = arg

class BadStatusException(Exception):
    def __init(self, arg):
        self.argCodes = arg

class PathIsDirException(Exception):
    def __init(self, arg):
        self.argCodes = arg

class ParamInvalidException(Exception):
    def __init(self, arg):
        self.argCodes = arg

class LoginFailedException(Exception):
    def __init(self, arg):
        self.argCodes = arg

class UserNotExistException(Exception):
    def __init(self, arg):
        self.argCodes = arg
