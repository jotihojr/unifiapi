from .authenticator import AuthenticationInterface, AuthenticatorError
import os.path
import netrc


class AuthNetRc(AuthenticationInterface):
    def __init__(self, server: str, file: str | None = None):
        nrfile = None
        if file is None:
            nrfile = self.__getdefaultfile()
        else:
            path = os.path.expanduser(file)
            if os.path.exists(path):
                nrfile = path

        nr = netrc.netrc(nrfile)
        auth = nr.authenticators(server)
        if not auth:
            raise AuthenticatorError(
                f"authenticator not found: file '{nrfile}' server {server}'"
            )
        self.__auth = auth

    def __getdefaultfile(self) -> str | None:
        nrfile = None
        for path in "~/.config/netrc", "~/.netrc":
            p = os.path.expanduser(path)
            if os.path.exists(p):
                nrfile = p
        return nrfile

    @property
    def user(self) -> str:
        return self.__auth[0]

    @property
    def password(self) -> str:
        return self.__auth[2]
