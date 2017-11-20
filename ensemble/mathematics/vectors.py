from __future__ import print_function

import functools as ft
import itertools as it

import numpy as np

from . import defaults


def zeros(n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return np.zeros(n, dtype=dtype)

def ones(n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return np.ones(n, dtype=dtype)

def unit(i, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    result = np.zeros(n, dtype=dtype)
    result[i] = 1
    return result

def vector(v, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    result = np.zeros(n, dtype=dtype)
    l0, u0 = 0, min(n, v.shape[0])
    result[l0:u0] = v[l0:u0]
    return result

def subvector(v, indices):
    result = np.zeros(indices.shape, dtype=v.dtype)
    for index in np.ndindex(*indices.shape):
        result = v[index]
    return result
