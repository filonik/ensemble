import functools as ft
import itertools as it


def identity(x):
    return x

def constant(x):
    def _constant(*args, **kwargs):
        return x
    return _constant

def compose(*args):
    def _compose(f, g):
        def __compose(t):
            return f(g(t))
        return __compose
    return ft.reduce(_compose, args, identity)

def invertible(f, f_inv):
    f_inv.inv = f
    f.inv = f_inv
    return f
