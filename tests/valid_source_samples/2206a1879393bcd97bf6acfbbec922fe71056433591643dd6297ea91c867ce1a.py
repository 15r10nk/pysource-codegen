lazy import x

lazy from . import y

if x:
    lazy from x import z

    z(y)
