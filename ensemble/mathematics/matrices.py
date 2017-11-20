from __future__ import print_function

import functools as ft
import itertools as it

import numpy as np

from . import defaults


def zeros(n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return np.zeros((n,n), dtype=dtype)

def ones(n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return np.ones((n,n), dtype=dtype)

def identity(n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return np.identity(n+1, dtype=dtype)

def matrix(m, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    result = np.zeros(n, dtype=dtype)
    l0, u0 = 0, min(n, m.shape[0])
    l1, u1 = 0, min(n, m.shape[1])
    result[l0:u0, l1:u1] = m[l0:u0, l1:u1]
    return result

def submatrix(m, indices):
    result = np.zeros(indices.shape, dtype=m.dtype)
    for index in np.ndindex(*indices.shape):
        result = m[index]
    return result

def direct_sum(m0, m1):
    result = np.zeros(np.add(m0.shape, m1.shape), dtype=np.find_common_type([m0.dtype, m1.dtype],[]))
    result[:m0.shape[0],:m0.shape[1]] = m0
    result[m0.shape[0]:,m0.shape[1]:] = m1
    return result

def translate(v, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    result = identity(n=n, dtype=dtype)
    for i in range(min(n, len(v))):
        result[-1, i] = v[i]
    return result

def scale(v, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    result = identity(n=n, dtype=dtype)
    for i in range(min(n, len(v))):
        result[i, i] = v[i]
    return result

def rotate_sa_ca_i_j(sa, ca, i, j, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    result = identity(n=n, dtype=dtype)
    
    if i != j:
        result[i, i] = ca
        result[i, j] = +sa
        result[j, i] = -sa
        result[j, j] = ca
    
    return result

def rotate_a_i_j(a, i, j, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    sa = np.sin(a)
    ca = np.cos(a)
    return rotate_sa_ca_i_j(sa, ca, i, j, n=n, dtype=dtype)

def rotate_euler_angles_vector(v, i=0, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    sa = np.sin(v)
    ca = np.cos(v)
    ms = (rotate_sa_ca_i_j(sa[j], ca[j], i, j, n=n, dtype=dtype) for j in range(n))
    #ms = (rotate_sa_ca_i_j(sa[i], ca[i], index[0], index[1], n=n, dtype=dtype) for i, index in enumerate(it.combinations(range(n), 2)))
    return ft.reduce(np.dot, ms)

def _rotate_euler_angles_matrix(m, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    sa = np.sin(m)
    ca = np.cos(m)
    ms = (rotate_sa_ca_i_j(sa[i,j], ca[i,j], i, j, n=n, dtype=dtype) for i, j in it.combinations(range(n), 2))
    return ft.reduce(np.dot, ms)

def rotate_euler_angles_matrix_upper(m, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return _rotate_euler_angles_matrix(m, n=n, dtype=dtype)

def rotate_euler_angles_matrix_lower(m, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return _rotate_euler_angles_matrix(-m.T, n=n, dtype=dtype)

def rotate_euler_angles_matrix(m, n=defaults.DEFAULT_N, dtype=defaults.DEFAULT_DTYPE):
    return _rotate_euler_angles_matrix(m - m.T, n=n, dtype=dtype)


def inversed(m):
    try:
        return np.linalg.inv(m)
    except np.linalg.LinAlgError:
        return np.zeros_like(m)

def transposed(m):
    return np.transpose(m)


'''
def rotate_euler_angles_1(a, dtype=defaults.DEFAULT_DTYPE):
    return np.array([1], dtype=dtype)

def rotate_euler_angles_2(a, dtype=defaults.DEFAULT_DTYPE):
    s = np.sin(a)
    c = np.cos(a)
    return np.array([
        [c[0], +s[0]],
        [-s[0], c[0]]
    ], dtype=dtype)

def rotate_euler_angles_3(a, dtype=defaults.DEFAULT_DTYPE):
    s = np.sin(a)
    c = np.cos(a)
    return np.array([
        [c[0]*c[1], -c[0]*s[1]*s[2] + c[2]*s[0], c[0]*c[2]*s[1] + s[0]*s[2]],
        [-c[1]*s[0], c[0]*c[2] + s[0]*s[1]*s[2], c[0]*s[2] - c[2]*s[0]*s[1]],
        [-s[1], -c[1]*s[2], c[1]*c[2]]
    ], dtype=dtype)

def rotate_euler_angles_4(a, dtype=defaults.DEFAULT_DTYPE):
    s = np.sin(a)
    c = np.cos(a)
    return np.array([
        [c[0]*c[1]*c[2], -c[0]*c[1]*s[2]*s[4] + c[4]*(-c[0]*s[1]*s[3] + c[3]*s[0]), c[5]*(c[0]*c[3]*s[1] + s[0]*s[3]) - s[5]*(c[0]*c[1]*c[4]*s[2] + s[4]*(-c[0]*s[1]*s[3] + c[3]*s[0])), c[5]*(c[0]*c[1]*c[4]*s[2] + s[4]*(-c[0]*s[1]*s[3] + c[3]*s[0])) + s[5]*(c[0]*c[3]*s[1] + s[0]*s[3])],
        [-c[1]*c[2]*s[0], c[1]*s[0]*s[2]*s[4] + c[4]*(c[0]*c[3] + s[0]*s[1]*s[3]), c[5]*(c[0]*s[3] - c[3]*s[0]*s[1]) - s[5]*(-c[1]*c[4]*s[0]*s[2] + s[4]*(c[0]*c[3] + s[0]*s[1]*s[3])), c[5]*(-c[1]*c[4]*s[0]*s[2] + s[4]*(c[0]*c[3] + s[0]*s[1]*s[3])) + s[5]*(c[0]*s[3] - c[3]*s[0]*s[1])],
        [-c[2]*s[1], -c[1]*c[4]*s[3] + s[1]*s[2]*s[4], c[1]*c[3]*c[5] - s[5]*(-c[1]*s[3]*s[4] - c[4]*s[1]*s[2]), c[1]*c[3]*s[5] + c[5]*(-c[1]*s[3]*s[4] - c[4]*s[1]*s[2])],
        [-s[2], -c[2]*s[4], -c[2]*c[4]*s[5], c[2]*c[4]*c[5]]
    ], dtype=dtype)

def rotate_euler_angles_5(a, dtype=defaults.DEFAULT_DTYPE):
    s = np.sin(a)
    c = np.cos(a)
    return np.array([
        [c[0]*c[1]*c[2]*c[3], -c[0]*c[1]*c[2]*s[3]*s[6] + c[6]*(-c[0]*c[1]*s[2]*s[5] + c[5]*(-c[0]*s[1]*s[4] + c[4]*s[0])), c[8]*(c[7]*(c[0]*c[4]*s[1] + s[0]*s[4]) - s[7]*(c[0]*c[1]*c[5]*s[2] + s[5]*(-c[0]*s[1]*s[4] + c[4]*s[0]))) - s[8]*(c[0]*c[1]*c[2]*c[6]*s[3] + s[6]*(-c[0]*c[1]*s[2]*s[5] + c[5]*(-c[0]*s[1]*s[4] + c[4]*s[0]))), c[9]*(c[7]*(c[0]*c[1]*c[5]*s[2] + s[5]*(-c[0]*s[1]*s[4] + c[4]*s[0])) + s[7]*(c[0]*c[4]*s[1] + s[0]*s[4])) - s[9]*(c[8]*(c[0]*c[1]*c[2]*c[6]*s[3] + s[6]*(-c[0]*c[1]*s[2]*s[5] + c[5]*(-c[0]*s[1]*s[4] + c[4]*s[0]))) + s[8]*(c[7]*(c[0]*c[4]*s[1] + s[0]*s[4]) - s[7]*(c[0]*c[1]*c[5]*s[2] + s[5]*(-c[0]*s[1]*s[4] + c[4]*s[0])))), c[9]*(c[8]*(c[0]*c[1]*c[2]*c[6]*s[3] + s[6]*(-c[0]*c[1]*s[2]*s[5] + c[5]*(-c[0]*s[1]*s[4] + c[4]*s[0]))) + s[8]*(c[7]*(c[0]*c[4]*s[1] + s[0]*s[4]) - s[7]*(c[0]*c[1]*c[5]*s[2] + s[5]*(-c[0]*s[1]*s[4] + c[4]*s[0])))) + s[9]*(c[7]*(c[0]*c[1]*c[5]*s[2] + s[5]*(-c[0]*s[1]*s[4] + c[4]*s[0])) + s[7]*(c[0]*c[4]*s[1] + s[0]*s[4]))],
        [-c[1]*c[2]*c[3]*s[0], c[1]*c[2]*s[0]*s[3]*s[6] + c[6]*(c[1]*s[0]*s[2]*s[5] + c[5]*(c[0]*c[4] + s[0]*s[1]*s[4])), c[8]*(c[7]*(c[0]*s[4] - c[4]*s[0]*s[1]) - s[7]*(-c[1]*c[5]*s[0]*s[2] + s[5]*(c[0]*c[4] + s[0]*s[1]*s[4]))) - s[8]*(-c[1]*c[2]*c[6]*s[0]*s[3] + s[6]*(c[1]*s[0]*s[2]*s[5] + c[5]*(c[0]*c[4] + s[0]*s[1]*s[4]))), c[9]*(c[7]*(-c[1]*c[5]*s[0]*s[2] + s[5]*(c[0]*c[4] + s[0]*s[1]*s[4])) + s[7]*(c[0]*s[4] - c[4]*s[0]*s[1])) - s[9]*(c[8]*(-c[1]*c[2]*c[6]*s[0]*s[3] + s[6]*(c[1]*s[0]*s[2]*s[5] + c[5]*(c[0]*c[4] + s[0]*s[1]*s[4]))) + s[8]*(c[7]*(c[0]*s[4] - c[4]*s[0]*s[1]) - s[7]*(-c[1]*c[5]*s[0]*s[2] + s[5]*(c[0]*c[4] + s[0]*s[1]*s[4])))), c[9]*(c[8]*(-c[1]*c[2]*c[6]*s[0]*s[3] + s[6]*(c[1]*s[0]*s[2]*s[5] + c[5]*(c[0]*c[4] + s[0]*s[1]*s[4]))) + s[8]*(c[7]*(c[0]*s[4] - c[4]*s[0]*s[1]) - s[7]*(-c[1]*c[5]*s[0]*s[2] + s[5]*(c[0]*c[4] + s[0]*s[1]*s[4])))) + s[9]*(c[7]*(-c[1]*c[5]*s[0]*s[2] + s[5]*(c[0]*c[4] + s[0]*s[1]*s[4])) + s[7]*(c[0]*s[4] - c[4]*s[0]*s[1]))],
        [-c[2]*c[3]*s[1], c[2]*s[1]*s[3]*s[6] + c[6]*(-c[1]*c[5]*s[4] + s[1]*s[2]*s[5]), c[8]*(c[1]*c[4]*c[7] - s[7]*(-c[1]*s[4]*s[5] - c[5]*s[1]*s[2])) - s[8]*(-c[2]*c[6]*s[1]*s[3] + s[6]*(-c[1]*c[5]*s[4] + s[1]*s[2]*s[5])), c[9]*(c[1]*c[4]*s[7] + c[7]*(-c[1]*s[4]*s[5] - c[5]*s[1]*s[2])) - s[9]*(c[8]*(-c[2]*c[6]*s[1]*s[3] + s[6]*(-c[1]*c[5]*s[4] + s[1]*s[2]*s[5])) + s[8]*(c[1]*c[4]*c[7] - s[7]*(-c[1]*s[4]*s[5] - c[5]*s[1]*s[2]))), c[9]*(c[8]*(-c[2]*c[6]*s[1]*s[3] + s[6]*(-c[1]*c[5]*s[4] + s[1]*s[2]*s[5])) + s[8]*(c[1]*c[4]*c[7] - s[7]*(-c[1]*s[4]*s[5] - c[5]*s[1]*s[2]))) + s[9]*(c[1]*c[4]*s[7] + c[7]*(-c[1]*s[4]*s[5] - c[5]*s[1]*s[2]))],
        [-c[3]*s[2], -c[2]*c[6]*s[5] + s[2]*s[3]*s[6], -c[2]*c[5]*c[8]*s[7] - s[8]*(-c[2]*s[5]*s[6] - c[6]*s[2]*s[3]), c[2]*c[5]*c[7]*c[9] - s[9]*(-c[2]*c[5]*s[7]*s[8] + c[8]*(-c[2]*s[5]*s[6] - c[6]*s[2]*s[3])), c[2]*c[5]*c[7]*s[9] + c[9]*(-c[2]*c[5]*s[7]*s[8] + c[8]*(-c[2]*s[5]*s[6] - c[6]*s[2]*s[3]))],
        [-s[3], -c[3]*s[6], -c[3]*c[6]*s[8], -c[3]*c[6]*c[8]*s[9], c[3]*c[6]*c[8]*c[9]]
    ], dtype=dtype)
'''