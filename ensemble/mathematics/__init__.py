from . import defaults

def configure(n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    defaults.DEFAULT_DTYPE = dtype
    defaults.DEFAULT_BASIS = tuple(range(n))
    defaults.DEFAULT_N = n
