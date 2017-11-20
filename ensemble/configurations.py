import numpy as np


def coercion(func):
    def _coercion(value, default):
        try:
            return func(value)
        except:
            return default
    return _coercion


as_bscalar = coercion(bool)
as_iscalar = coercion(int)
as_fscalar = coercion(float)
as_scalar = as_fscalar

as_bvector = coercion(lambda value: np.array(value, dtype=np.bool_))
as_ivector = coercion(lambda value: np.array(value, dtype=np.int32))
as_fvector = coercion(lambda value: np.array(value, dtype=np.float32))
as_vector = as_fvector


class Object(object):
    _fields = []
    def __init__(self, data=None):
        for name, getter in self._fields:
            setattr(self, name, getter(data))

class Configuration(Object):
    class Audio(Object):
        class Format(Object):
            _fields = [
                ("channels", lambda data: as_iscalar(data.get("channels"), 2)),
            ]
        
        _fields = [
            ("format", lambda data: Configuration.Audio.Format(data.get("format", {}))),
        ]

    class Video(Object):
        class Global(Object):
            _fields = [
                ("resolution", lambda data: as_ivector(data.get("resolution"), np.array([1280, 720], dtype=np.int32))),
                ("shape", lambda data: as_ivector(data.get("shape"), np.array([1, 1], dtype=np.int32))),
            ]
        class Format(Object):
            _fields = [
                ("red", lambda data: as_iscalar(data.get("red"), 8)),
                ("green", lambda data: as_iscalar(data.get("green"), 8)),
                ("blue", lambda data: as_iscalar(data.get("blue"), 8)),
                ("alpha", lambda data: as_iscalar(data.get("red"), 8)),
                ("depth", lambda data: as_iscalar(data.get("depth"), 24)),
                ("stencil", lambda data: as_iscalar(data.get("stencil"), 8)),
            ]
        
        _fields = [
            ("global_", lambda data: Configuration.Video.Global(data.get("global", {}))),
            ("shape", lambda data: as_ivector(data.get("shape"), np.array([1, 1], dtype=np.int32))),
            ("index", lambda data: as_ivector(data.get("index"), np.array([0, 0], dtype=np.int32))),
            ("format", lambda data: Configuration.Video.Format(data.get("format", {}))),
            ("fullscreen", lambda data: as_bscalar(data.get("fullscreen"), False)),
            ("framelock", lambda data: as_bscalar(data.get("framelock"), False)),
            ("stereo", lambda data: as_bscalar(data.get("stereo"), False)),
            ("samples", lambda data: as_iscalar(data.get("samples"), 4)),
            ("vsync", lambda data: as_iscalar(data.get("vsync"), 0)),
        ]
    
    class Network(Object):
        _fields = [
            ("timeserver", lambda data: as_bscalar(data.get("timeserver"), False)),
            ("port", lambda data: as_iscalar(data.get("port"), 1234)),
        ]
    
    _fields = [
        ("audio", lambda data: Configuration.Audio(data.get("audio", {}))),
        ("video", lambda data: Configuration.Video(data.get("video", {}))),
        ("network", lambda data: Configuration.Network(data.get("network", {}))),
    ]
