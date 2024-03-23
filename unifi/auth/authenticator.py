import abc


class AuthenticatorError(Exception):
    pass


class AuthenticationInterface(metaclass=abc.ABCMeta):

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "user")
            and callable(subclass.usr)
            and hasattr(subclass, "password")
            and callable(subclass.password)
        )

    @property
    @abc.abstractmethod
    def user(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def password(self) -> str:
        raise NotImplementedError
