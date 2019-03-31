from typing import Callable, TypeVar

T = TypeVar('T')

class ParamException(Exception):
    pass


def cli_arg(constructor: Callable[[str], T]) -> Callable[[str], T]:
    def c(x):
        try:
            return constructor(x)
        except ParamException as p:
            raise Exception("yay") from p
    return c

class Pies:
    def __init__(self, a: str):
        if a == "0":
            self.a = a
        else:
            raise ParamException("złe a")

pies = cli_arg(Pies)("0")
print(pies.a)

