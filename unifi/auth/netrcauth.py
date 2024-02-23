from .authenticator import AuthenticationInterface, AuthenticatorError
import os.path
import netrc


class AuthNetRc(AuthenticationInterface):
    def __init__(self, server: str, file: str | None = None):
        if file is None:
            path = os.path.expanduser("~/.config/netrc")
            if os.path.exists(path):
                file = path

        nr = netrc.netrc(file)
        auth = nr.authenticators(server)
        if not auth:
            raise AuthenticatorError(
                f"authenticator not found: file '{file}' server '{server}'"
            )
        self.__auth = auth

    @property
    def user(self) -> str:
        return self.__auth[0]

    @property
    def password(self) -> str:
        return self.__auth[2]
