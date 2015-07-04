# coding: utf-8
""" ctypes library of mxnet and helper functions """
from __future__ import absolute_import

import os
import sys
import ctypes
import platform
import numpy as np

#----------------------------
# library loading
#----------------------------
if sys.version_info[0] == 3:
    string_types = str,
else:
    string_types = basestring,


class MXNetError(Exception):
    """Error that will be throwed by all mxnet functions"""
    pass


def _load_lib():
    """load libary by searching possible path"""
    curr_path = os.path.dirname(os.path.abspath(os.path.expanduser(__file__)))
    api_path = os.path.join(curr_path, '../../')
    dll_path = [api_path, curr_path]
    if os.name == 'nt':
        if platform.architecture()[0] == '64bit':
            dll_path.append(os.path.join(api_path, '../windows/x64/Release/'))
        else:
            dll_path.append(os.path.join(api_path, '../windows/Release/'))
    if os.name == 'nt':
        dll_path = [os.path.join(p, 'mxnet.dll') for p in dll_path]
    else:
        dll_path = [os.path.join(p, 'libmxnet.so') for p in dll_path]
    lib_path = [p for p in dll_path if os.path.exists(p) and os.path.isfile(p)]
    if len(dll_path) == 0:
        raise MXNetError('cannot find find the files in the candicate path ' + str(dll_path))
    lib = ctypes.cdll.LoadLibrary(lib_path[0])

    # DMatrix functions
    lib.MXGetLastError.restype = ctypes.c_char_p
    return lib


# library instance of mxnet
lib = _load_lib()

# type definitions
mx_uint = ctypes.c_uint
mx_float = ctypes.c_float
NArrayHandle = ctypes.c_void_p
FunctionHandle = ctypes.c_void_p

#----------------------------
# helper function definition
#----------------------------

def check_call(ret):
    """Check the return value of C API call

    This function will raise exception when error occurs.
    Wrap every API call with this function

    Parameters
    ----------
    ret : int
        return value from API calls
    """
    if ret != 0:
        raise MXNetError(lib.MXGetLastError());


def c_str(string):
    """Create ctypes char * from a python string
    
    Parameters
    ----------
    string : string type
        python string

    Returns
    -------
    a char pointer that can be passed to C API
    """
    
    return ctypes.c_char_p(string.encode('utf-8'))


def c_array(ctype, values):
    """Create ctypes array from a python array
    
    Parameters
    ----------
    ctype : ctypes data type
        data type of the array we want to convert to

    values : tuple or list
        data content

    Returns
    -------
    created ctypes array
    """
    return (ctype * len(values))(*values)


def ctypes2numpy_shared(cptr, shape):
    """Convert a ctypes pointer to a numpy array 

    The result numpy array shares the memory with the pointer
    
    Parameters
    ----------
    cptr : ctypes.POINTER(mx_float)
        pointer to the memory region

    shape : tuple
        shape of target narray

    Returns
    -------
    a numpy array : numpy array
    """
    if not isinstance(cptr, ctypes.POINTER(mx_float)):
        raise RuntimeError('expected float pointer')
    size = 1
    for s in shape:
        size *= s
    dbuffer = (mx_float * size).from_address(ctypes.addressof(cptr.contents))
    return np.frombuffer(dbuffer, dtype = np.float32).reshape(shape)
